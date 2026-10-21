<?php
defined('ABSPATH') || exit;

// Deliberately not exposed as a web endpoint. Run from the migration tool or
// WP-CLI as an administrator. Stable IDs make repeat imports non-destructive.
function lpdj_import_legacy($records, $figures, $history = []) {
    if (!lpdj_admin()) return lpdj_error('Administrator access required.', 403);
    $result = ['created' => [], 'skipped' => []];
    foreach ($records as $p) {
        $legacy_id = $p['id'] ?? '';
        if (!preg_match('/^[a-z0-9-]{1,100}$/D', $legacy_id)) return lpdj_error('Invalid legacy identifier.');
        $existing = get_posts(['post_type'=>'lpdj_problem','post_status'=>'private','fields'=>'ids','posts_per_page'=>1,'meta_key'=>'_lpdj_legacy_id','meta_value'=>$legacy_id]);
        if ($existing) { $result['skipped'][$legacy_id] = $existing[0]; continue; }
        $categories = ['algebra'=>'Algebra','geometry'=>'Geometry','number_theory'=>'Number Theory','combinatorics'=>'Combinatorics','logic'=>'Logic'];
        if (!isset($categories[$p['topic'] ?? '']) || !is_int($p['difficulty'] ?? null) || $p['difficulty']<1 || $p['difficulty']>5 || empty($p['sources'])) return lpdj_error('Invalid legacy metadata: '.$legacy_id);
        $versions = [];
        foreach (['en','fr'] as $lang) {
            $v = $p['versions'][$lang] ?? null;
            if (!is_array($v) || !is_string($v['title'] ?? null) || !is_string($v['statement'] ?? null) || mb_strlen($v['title'])>300 || strlen($v['statement'])>60000) return lpdj_error('Invalid legacy version: '.$legacy_id);
            $versions[$lang] = ['title'=>$v['title'],'latex'=>$v['statement'],'approved'=>(bool)$v['approved']];
        }
        $images = [];
        foreach ($p['assets'] ?? [] as $name) {
            $uri = $figures[$name] ?? '';
            if (!preg_match('~^data:(image/(?:svg\+xml|png|jpeg));base64,(.+)$~s', $uri, $m)) return lpdj_error('Missing legacy figure: '.$name);
            $content = base64_decode($m[2], true);
            if ($content === false || strlen($content)>2*1024*1024) return lpdj_error('Invalid legacy figure: '.$name);
            if ($m[1] === 'image/svg+xml') {
                $content = lpdj_clean_svg($content); if (is_wp_error($content)) return $content;
            } else {
                $info = @getimagesizefromstring($content);
                if (!$info || $info['mime']!==$m[1] || $info[0]>8000 || $info[1]>8000) return lpdj_error('Invalid legacy image: '.$name);
            }
            $images[$name] = ['mime'=>$m[1],'data'=>base64_encode($content)];
        }
        $id = wp_insert_post(wp_slash(['post_type'=>'lpdj_problem','post_status'=>'private','post_author'=>get_current_user_id(),'post_title'=>$versions['en']['title'] ?: $versions['fr']['title'] ?: 'Untitled']),true);
        if (is_wp_error($id)) return $id;
        $assets = [];
        foreach ($images as $name=>$image) {
            $asset_id = wp_insert_post(wp_slash(['post_type'=>'lpdj_asset','post_status'=>'private','post_author'=>get_current_user_id(),'post_parent'=>$id,'post_title'=>$name,'post_content'=>wp_json_encode($image)]),true);
            if (is_wp_error($asset_id)) {
                foreach ($assets as $asset) wp_delete_post($asset['id'],true);
                wp_delete_post($id,true); return $asset_id;
            }
            $assets[$name] = ['id'=>$asset_id,'mime'=>$image['mime']];
        }
        $entries = $history[$legacy_id] ?? [];
        $last = $entries ? end($entries) : null;
        $draft = ['id'=>$id,'revision'=>1,'state'=>'submitted','category'=>$categories[$p['topic']],'difficulty'=>$p['difficulty'],
            'source'=>$p['sourceGroup'],'keywords'=>[],'reviewNote'=>'','assets'=>$assets,'updated'=>$last['saved_at'] ?? gmdate('c'),'versions'=>$versions];
        lpdj_json_meta($id,'_lpdj_draft',$draft);
        // Never store external provenance URLs; keep title/number/page only.
        if (!empty($p['sources'])) lpdj_strip_source_urls($p['sources']);
        foreach ($entries as &$entry) {
            if (empty($entry['json'])) continue;
            $snapshot = json_decode($entry['json'], true);
            if (is_array($snapshot) && !empty($snapshot['sources']) && lpdj_strip_source_urls($snapshot['sources'])) $entry['json'] = wp_json_encode($snapshot, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        }
        unset($entry);
        lpdj_json_meta($id,'_lpdj_legacy',$p);
        lpdj_json_meta($id,'_lpdj_legacy_history',$entries);
        update_post_meta($id,'_lpdj_legacy_id',$legacy_id);
        // No published snapshot or notification event is created, even when a
        // version was verified in the old editorial workspace.
        $result['created'][$legacy_id]=$id;
    }
    if ($result['created']) lpdj_catalogue_changed();
    return $result;
}

// One-time cleanup: remove external provenance URLs (sources[].url) from imported
// legacy metadata and its history snapshots. Source citations keep title/number/page;
// no external reference remains in the database. Idempotent and safe to re-run.
function lpdj_strip_source_urls(&$sources) {
    if (!is_array($sources)) return false;
    $changed = false;
    foreach ($sources as &$source) {
        if (is_array($source) && array_key_exists('url', $source)) { unset($source['url']); $changed = true; }
    }
    unset($source);
    return $changed;
}
function lpdj_strip_legacy_urls($limit = 300) {
    $cursor = (int) get_option('_lpdj_url_cleanup_cursor', 0);
    $ids = get_posts(['post_type' => 'lpdj_problem', 'post_status' => 'private', 'posts_per_page' => -1, 'orderby' => 'ID', 'order' => 'ASC', 'fields' => 'ids']);
    $pending = array_values(array_filter($ids, fn($id) => $id > $cursor));
    $batch = array_slice($pending, 0, max(1, $limit));
    $cleaned = 0;
    foreach ($batch as $id) {
        $legacy = get_post_meta($id, '_lpdj_legacy', true);
        if (is_array($legacy) && !empty($legacy['sources']) && lpdj_strip_source_urls($legacy['sources'])) {
            lpdj_json_meta($id, '_lpdj_legacy', $legacy); $cleaned++;
        }
        $history = get_post_meta($id, '_lpdj_legacy_history', true);
        if (is_array($history)) {
            $changed = false;
            foreach ($history as &$entry) {
                if (empty($entry['json'])) continue;
                $snapshot = json_decode($entry['json'], true);
                if (is_array($snapshot) && !empty($snapshot['sources']) && lpdj_strip_source_urls($snapshot['sources'])) {
                    $entry['json'] = wp_json_encode($snapshot, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES); $changed = true;
                }
            }
            unset($entry);
            if ($changed) lpdj_json_meta($id, '_lpdj_legacy_history', $history);
        }
        $cursor = $id;
    }
    update_option('_lpdj_url_cleanup_cursor', $cursor, false);
    $remaining = max(0, count($pending) - count($batch));
    if ($remaining === 0) { update_option('_lpdj_legacy_urls_stripped', 1, true); if ($cleaned) lpdj_catalogue_changed(); }
    elseif ($cleaned) lpdj_catalogue_changed();
    return ['cleaned' => $cleaned, 'processed' => count($batch), 'remaining' => $remaining, 'done' => $remaining === 0];
}
// Run the cleanup in small batches as an administrator browses wp-admin, so it needs
// no WP-CLI and cannot time out. It also runs once more after re-importing, since an
// import clears the completion flag below.
add_action('admin_init', function () {
    if (wp_doing_ajax() || !current_user_can('manage_options') || get_option('_lpdj_legacy_urls_stripped')) return;
    lpdj_strip_legacy_urls();
});
