<?php
defined('ABSPATH') || exit;

function lpdj_problem_post($id) {
    $post = get_post(absint($id));
    return $post && $post->post_type === 'lpdj_problem' ? $post : null;
}
function lpdj_can_edit($post) { return $post && (lpdj_admin() || (int) $post->post_author === get_current_user_id()); }
function lpdj_json_meta($id, $key, $value) { return update_post_meta($id, $key, wp_slash($value)); }
function lpdj_source_name($source) { return $source === 'Communauté' ? 'Community' : ($source ?: 'Community'); }
function lpdj_language_name($key, $version) { return $version['language'] ?? (['en'=>'English','fr'=>'French'][$key] ?? strtoupper($key)); }
function lpdj_draft($post) {
    $data = get_post_meta($post->ID, '_lpdj_draft', true);
    $data['id'] = $post->ID;
    $data['source'] = lpdj_source_name($data['source']);
    $data['author'] = get_the_author_meta('display_name', $post->post_author) ?: 'Deleted account';
    $data['hasPublished'] = (bool) get_post_meta($post->ID, '_lpdj_published', true);
    return $data;
}
function lpdj_present($data, $editor = false) {
    $data['source'] = lpdj_source_name($data['source']);
    foreach ($data['versions'] as $key => &$version) $version['language'] = lpdj_language_name($key, $version);
    unset($version);
    foreach (($data['assets'] ?? []) as $name => $asset) $data['assets'][$name]['url'] = lpdj_asset_url($asset['id']);
    $data['progress'] = get_user_meta(get_current_user_id(), '_lpdj_progress_' . $data['id'], true) ?: 'unseen';
    $data['editable'] = lpdj_can_edit(lpdj_problem_post($data['id']));
    if (!$editor) unset($data['reviewNote']);
    return $data;
}
function lpdj_problems_list($r) {
    $scope = $r['scope'] ?: 'published';
    if (!in_array($scope, ['published','mine','review'], true)) return lpdj_error('Unknown list.');
    if ($scope === 'review' && !lpdj_admin()) return lpdj_error('Administrator access required.', 403);
    $args = ['post_type' => 'lpdj_problem', 'post_status' => 'private', 'posts_per_page' => -1, 'orderby' => 'ID', 'order' => 'DESC'];
    if ($scope === 'mine') $args['author'] = get_current_user_id();
    $items = []; $counts = []; $published = 0;
    foreach (get_posts($args) as $post) {
        $pub = get_post_meta($post->ID, '_lpdj_published', true);
        if ($pub) { $published++; $source = lpdj_source_name($pub['source']); $counts[$source] = ($counts[$source] ?? 0) + 1; }
        $data = $scope === 'published' ? $pub : lpdj_draft($post);
        if (!$data) continue;
        $data = lpdj_present($data, $scope !== 'published');
        if ($scope === 'review') $data['references'] = lpdj_problem_references(get_post_meta($post->ID, '_lpdj_legacy', true));
        // Overview records do not include full statements or image data.
        foreach ($data['versions'] as &$version) unset($version['latex']);
        unset($version, $data['assets']);
        $items[] = $data;
    }
    return ['items' => $items, 'total' => count($items), 'published' => $published, 'sources' => $counts];
}
function lpdj_problem_get($r) {
    $post = lpdj_problem_post($r['id']);
    if (!$post) return lpdj_error('Problem not found.', 404);
    $edit = $r['context'] === 'edit';
    if ($edit && !lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    $data = $edit ? lpdj_draft($post) : get_post_meta($post->ID, '_lpdj_published', true);
    if (!$data) return lpdj_error('This problem is not published.', 404);
    $data = lpdj_present($data, $edit);
    if ($edit && lpdj_admin() && ($legacy = get_post_meta($post->ID, '_lpdj_legacy', true))) {
        $data['references'] = lpdj_problem_references($legacy);
        $data['legacy'] = ['id'=>$legacy['id'],'revision'=>$legacy['revision'],'sources'=>$legacy['sources'],'occurrences'=>$legacy['occurrences'],'note'=>$legacy['note'],
            'reviewUrl'=>'https://le-probleme-du-jour-review.msfr935475.chatgpt.site/validation?problem='.rawurlencode($legacy['id'])];
    }
    return $data;
}
function lpdj_problem_create() {
    if (($t = lpdj_throttle('create', 30)) !== true) return $t;
    $id = wp_insert_post(['post_type' => 'lpdj_problem', 'post_status' => 'private', 'post_title' => 'New problem', 'post_author' => get_current_user_id()], true);
    if (is_wp_error($id)) return lpdj_error('Could not create the problem.', 500);
    $data = ['id' => $id, 'revision' => 1, 'state' => 'draft', 'category' => 'Algebra', 'difficulty' => 1,
        'source' => 'Community', 'keywords' => [], 'reviewNote' => '', 'assets' => [],
        'updated' => gmdate('c'), 'versions' => ['en' => ['language'=>'English', 'title' => '', 'latex' => '', 'approved' => false]]];
    lpdj_json_meta($id, '_lpdj_draft', $data);
    return lpdj_present(lpdj_draft(get_post($id)), true);
}
function lpdj_validate_problem($r, $old) {
    $category = (string) $r['category']; $difficulty = filter_var($r['difficulty'], FILTER_VALIDATE_INT);
    if (!in_array($category, ['Algebra','Geometry','Number Theory','Combinatorics','Logic'], true) || $difficulty < 1 || $difficulty > 5) return lpdj_error('Choose a category and a difficulty from 1 to 5.');
    $source = sanitize_text_field((string) $r['source']);
    if (mb_strlen($source) > 160) return lpdj_error('The source is too long.');
    $keywords = array_values(array_unique(array_filter(array_map('sanitize_text_field', (array) $r['keywords']))));
    if (count($keywords) > 15 || strlen(implode(',', $keywords)) > 400) return lpdj_error('Use up to 15 short keywords.');
    $data = $old;
    $data['category'] = $category; $data['difficulty'] = $difficulty; $data['source'] = $source ?: 'Community'; $data['keywords'] = $keywords;
    $versions = $r['versions'];
    if (!is_array($versions) || count($versions)<1 || count($versions)>20) return lpdj_error('Use between 1 and 20 language versions.');
    $data['versions'] = []; $languages = []; $total_size = 0;
    $metadata_changed = $old['category'] !== $category || $old['difficulty'] !== $difficulty || $old['source'] !== $data['source'] || $old['keywords'] !== $keywords;
    foreach ($versions as $lang => $version) {
        if (!is_string($lang) || !preg_match('/^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/D', $lang) || strlen($lang)>40 || !is_array($version)) return lpdj_error('Invalid language version.');
        foreach (['title','latex','language'] as $field) if (isset($version[$field]) && !is_string($version[$field])) return lpdj_error('Invalid language text.');
        $name = sanitize_text_field(lpdj_language_name($lang, $version));
        if (!$name || mb_strlen($name)>60) return lpdj_error('Give each language a name of up to 60 characters.');
        $canonical = mb_strtolower(trim($name));
        if (in_array($canonical,$languages,true)) return lpdj_error('Each language can appear only once.');
        $languages[] = $canonical;
        $title = sanitize_text_field((string) ($version['title'] ?? ''));
        $latex = str_replace("\0", '', (string) ($version['latex'] ?? ''));
        if (mb_strlen($title) > 300 || strlen($latex) > 60000) return lpdj_error('Limit: 300 characters for a title and 60 KB for a statement.');
        $total_size += strlen($latex);
        if ($total_size>600000) return lpdj_error('The combined statements must fit within 600 KB.');
        $previous = $old['versions'][$lang] ?? ['title'=>'','latex'=>'','approved'=>false];
        $changed = $metadata_changed || $title !== $previous['title'] || $latex !== $previous['latex'] || $name !== lpdj_language_name($lang, $previous);
        $approved = lpdj_admin() ? !empty($version['approved']) : (!$changed && !empty($old['versions'][$lang]['approved']));
        if ($approved && (!$title || !trim($latex))) return lpdj_error('A verified version needs a title and a statement.');
        $data['versions'][$lang] = ['language'=>$name, 'title' => $title, 'latex' => $latex, 'approved' => $approved];
    }
    if (lpdj_admin()) $data['reviewNote'] = sanitize_textarea_field((string) $r['reviewNote']);
    if (strlen($data['reviewNote']) > 5000) return lpdj_error('The review note is too long.');
    unset($data['hasPublished'], $data['editable'], $data['progress'], $data['references'], $data['legacy']);
    return $data;
}
function lpdj_check_figures($version, $assets) {
    preg_match_all('/\\\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}/', $version['latex'], $matches);
    foreach ($matches[1] as $name) if (!isset($assets[$name])) return lpdj_error('Missing figure: ' . $name);
    preg_match_all('/\\\\label\{([^}]+)\}/', $version['latex'], $labels);
    if (count($labels[1]) !== count(array_unique($labels[1]))) return lpdj_error('Labels must be unique within each version.');
    preg_match_all('/\\\\ref\{([^}]+)\}/', $version['latex'], $refs);
    foreach ($refs[1] as $ref) if (!in_array($ref, $labels[1], true)) return lpdj_error('Unknown reference: ' . $ref);
    return true;
}
function lpdj_lock($id) {
    $name = '_lpdj_lock_' . $id; $existing = (int) get_option($name, 0);
    if ($existing && $existing < time() - 120) delete_option($name);
    return add_option($name, time(), '', false);
}
function lpdj_problem_save($r) {
    $post = lpdj_problem_post($r['id']);
    if (!lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    $id = $post->ID;
    if (!lpdj_lock($id)) return lpdj_error('A save is in progress. Please try again.', 409);
    try {
        $old = lpdj_draft($post);
        if ((int) $r['revision'] !== (int) $old['revision']) return lpdj_error('This problem was changed elsewhere. Copy your changes, then reload the page.', 409);
        $action = (string) ($r['action'] ?: 'save');
        if (!in_array($action, ['save','submit','publish','return','unpublish'], true)) return lpdj_error('Unknown action.');
        if (in_array($action, ['publish','return','unpublish'], true) && !lpdj_admin()) return lpdj_error('Only an administrator can publish or return a problem.', 403);
        $data = lpdj_validate_problem($r, $old); if (is_wp_error($data)) return $data;
        $complete = false;
        foreach ($data['versions'] as $version) {
            if ($version['title'] && trim($version['latex'])) $complete = true;
            if ($action === 'submit' || ($action === 'publish' && $version['approved'])) {
                $check = lpdj_check_figures($version, $data['assets']); if (is_wp_error($check)) return $check;
            }
        }
        if (in_array($action, ['submit','publish'], true) && !$complete) return lpdj_error('Complete at least one title and statement.');
        $data['revision']++; $data['updated'] = gmdate('c'); $data['author'] = $old['author'];
        $previous_pub = get_post_meta($id, '_lpdj_published', true);
        if ($action === 'publish') {
            $approved = array_filter($data['versions'], fn($v) => $v['approved']);
            if (!$approved) return lpdj_error('Verify at least one language version before publishing.');
            $pub = $data; $pub['versions'] = $approved; $pub['state'] = 'published'; $pub['publishedAt'] = gmdate('c');
            unset($pub['reviewNote']);
            $names = [];
            foreach ($approved as $version) { preg_match_all('/\\\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}/', $version['latex'], $m); $names = array_merge($names, $m[1]); }
            $pub['assets'] = array_intersect_key($data['assets'], array_flip($names));
            lpdj_json_meta($id, '_lpdj_published', $pub); $data['state'] = 'published';
            if (!$previous_pub) wp_schedule_single_event(time() + 5, 'lpdj_notify_published', [$id]);
        } elseif ($action === 'unpublish') {
            delete_post_meta($id, '_lpdj_published'); $data['state'] = 'draft';
        } elseif ($action === 'return') {
            if (!trim($data['reviewNote'])) return lpdj_error('Add a note explaining the requested changes.');
            $data['state'] = 'returned';
        } elseif ($action === 'submit') {
            $data['state'] = 'submitted';
        } else $data['state'] = 'draft';
        lpdj_json_meta($id, '_lpdj_draft', $data);
        $titles = array_filter(array_column($data['versions'], 'title'));
        $title = ($data['versions']['en']['title'] ?? '') ?: (reset($titles) ?: 'New problem');
        wp_update_post(['ID' => $id, 'post_title' => wp_slash($title)]);
        wp_insert_post(wp_slash(['post_type' => 'lpdj_history', 'post_status' => 'private', 'post_parent' => $id, 'post_author' => get_current_user_id(),
            'post_title' => $action, 'post_content' => wp_json_encode($data, JSON_UNESCAPED_UNICODE)]));
        if ($action === 'submit' && $old['state'] !== 'submitted') lpdj_admin_alert('submission', $id, $data['revision']);
        return lpdj_present(lpdj_draft(get_post($id)), true);
    } finally { delete_option('_lpdj_lock_' . $id); }
}
function lpdj_problem_history($r) {
    $post = lpdj_problem_post($r['id']); if (!lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    $entries = array_map(function ($entry) {
        return ['id' => $entry->ID, 'action' => $entry->post_title, 'date' => $entry->post_date_gmt . 'Z',
            'by' => get_the_author_meta('display_name', $entry->post_author) ?: 'Deleted account', 'snapshot' => json_decode($entry->post_content, true)];
    }, get_posts(['post_type' => 'lpdj_history', 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => 50, 'orderby' => 'ID', 'order' => 'DESC']));
    if (lpdj_admin()) foreach (array_reverse(get_post_meta($post->ID, '_lpdj_legacy_history', true) ?: []) as $entry) {
        $snapshot = json_decode($entry['json'], true);
        foreach ($snapshot['versions'] as &$version) { $version['latex'] = $version['statement']; unset($version['statement']); } unset($version);
        $entries[] = ['id'=>'legacy-'.$entry['revision'],'action'=>'Original review','date'=>$entry['saved_at'],'by'=>$entry['actor'],'snapshot'=>$snapshot];
    }
    return $entries;
}
function lpdj_problem_delete($r) {
    $post = lpdj_problem_post($r['id']);
    if (!lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    if (!lpdj_lock($post->ID)) return lpdj_error('A save is in progress. Please try again.', 409);
    try {
        if (get_post_meta($post->ID, '_lpdj_published', true)) return lpdj_error('An administrator must unpublish this problem first.');
        foreach (get_posts(['post_type' => ['lpdj_asset','lpdj_history'], 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => -1]) as $child) wp_delete_post($child->ID, true);
        wp_delete_post($post->ID, true);
        return ['ok' => true];
    } finally { delete_option('_lpdj_lock_' . $post->ID); }
}
function lpdj_progress_save($r) {
    if (!get_post_meta(absint($r['id']), '_lpdj_published', true)) return lpdj_error('Problem not found.', 404);
    if (!in_array($r['progress'], ['unseen','bookmarked','attempted','solved'], true)) return lpdj_error('Unknown progress value.');
    update_user_meta(get_current_user_id(), '_lpdj_progress_' . absint($r['id']), $r['progress']);
    return ['progress' => $r['progress']];
}
add_action('lpdj_notify_published', function ($id) {
    $pub = get_post_meta($id, '_lpdj_published', true); if (!$pub || get_post_meta($id, '_lpdj_notified', true)) return;
    $version = $pub['versions']['en'] ?? reset($pub['versions']);
    $users = get_users(['meta_key' => '_lpdj_notifications', 'meta_value' => '1']);
    $sent = get_post_meta($id, '_lpdj_notified_users', true) ?: []; $failed = false;
    foreach ($users as $user) {
        if (get_user_meta($user->ID, '_lpdj_verification', true) === 'pending') continue;
        if (in_array($user->ID, $sent, true)) continue;
        if (wp_mail($user->user_email, 'New problem : ' . $version['title'], $version['title'] . "\n\nA new problem is available:\n" . home_url('/#/probleme/' . $id) . "\n\nTo stop these notifications, uncheck the option in your profile:\n" . home_url('/#/profil'))) {
            $sent[] = $user->ID; update_post_meta($id, '_lpdj_notified_users', $sent);
        } else $failed = true;
    }
    if (!$failed) update_post_meta($id, '_lpdj_notified', 1);
    else {
        $retries = (int) get_post_meta($id, '_lpdj_notification_retries', true);
        if ($retries < 3) { update_post_meta($id, '_lpdj_notification_retries', $retries + 1); wp_schedule_single_event(time() + 10 * MINUTE_IN_SECONDS, 'lpdj_notify_published', [$id]); }
    }
});
