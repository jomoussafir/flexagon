<?php
/**
 * Plugin Name: Flexagon — Catalogue Transfer
 * Description: Temporary administrator-only transfer of the current local catalogue.
 * Version: 1.0.0
 * Requires PHP: 8.2
 */
defined('ABSPATH') || exit;

function lpdj_transfer_guard() {
    if (!current_user_can('manage_options')) throw new RuntimeException('Administrator access required.');
    if (!function_exists('lpdj_json_meta')) throw new RuntimeException('Activate Flexagon first.');
}
function lpdj_transfer_scalar_tree($value) {
    if (is_object($value) || is_resource($value)) throw new RuntimeException('Unsupported serialized object.');
    if (is_array($value)) foreach ($value as $child) lpdj_transfer_scalar_tree($child);
    return $value;
}
function lpdj_transfer_decode($raw) {
    if (!is_string($raw)) throw new RuntimeException('Invalid metadata encoding.');
    if (!is_serialized($raw)) return $raw;
    $value = @unserialize($raw, ['allowed_classes' => false, 'max_depth' => 64]);
    if ($value === false && $raw !== 'b:0;') throw new RuntimeException('Invalid serialized metadata.');
    return lpdj_transfer_scalar_tree($value);
}
function lpdj_transfer_bundle() {
    lpdj_transfer_guard();
    if (!defined('LPDJ_TRANSFER_DIR')) throw new RuntimeException('Configure the private transfer directory first.');
    $root = realpath(LPDJ_TRANSFER_DIR);
    if (!$root || !is_dir($root)) throw new RuntimeException('Private transfer directory is missing.');
    foreach ([ABSPATH, $_SERVER['DOCUMENT_ROOT'] ?? ''] as $public) {
        $public = $public ? realpath($public) : false;
        if (!lpdj_private_encrypted() && $public && ($root === $public || str_starts_with($root, rtrim($public, '/\\') . DIRECTORY_SEPARATOR))) {
            throw new RuntimeException('The transfer directory must be outside every public web directory.');
        }
    }
    $file = lpdj_private_path($root, 'catalogue.json');
    if (!$file || dirname($file) !== $root || !is_readable($file) || filesize($file) > 32 * 1024 * 1024) throw new RuntimeException('Private catalogue.json is missing or too large.');
    $plain = lpdj_private_read($root, 'catalogue.json');
    if ($plain === false) throw new RuntimeException('Catalogue could not be authenticated or decrypted.');
    $bundle = json_decode($plain, true, 128, JSON_THROW_ON_ERROR);
    if (($bundle['format'] ?? '') !== 'lpdj-wordpress-catalogue-v1' || empty($bundle['records'])) throw new RuntimeException('Unsupported catalogue format.');
    if (count($bundle['authors'] ?? []) !== 1) throw new RuntimeException('This transfer requires one explicitly mapped source administrator.');
    $author = (int) $bundle['authors'][0]['ID'];
    $keys = ['_lpdj_draft', '_lpdj_published', '_lpdj_legacy', '_lpdj_legacy_history', '_lpdj_legacy_id'];
    $counts = []; $records = []; $published = [];
    foreach ($bundle['records'] as $record) {
        $id = (int) ($record['ID'] ?? 0); $type = $record['post_type'] ?? '';
        if (!$id || isset($records[$id]) || !in_array($type, ['lpdj_problem','lpdj_asset','lpdj_history'], true) || $record['post_status'] !== 'private' || (int) $record['post_author'] !== $author) throw new RuntimeException('Invalid content record.');
        $record['decoded'] = [];
        foreach ($record['meta'] as $key => $raw) {
            if (!in_array($key, $keys, true)) throw new RuntimeException('Unexpected metadata key.');
            $record['decoded'][$key] = lpdj_transfer_decode($raw);
        }
        if ($type === 'lpdj_problem') {
            if (!is_array($record['decoded']['_lpdj_draft'] ?? null) || (int) $record['decoded']['_lpdj_draft']['id'] !== $id) throw new RuntimeException('Problem draft is missing or has the wrong ID.');
            if (isset($record['decoded']['_lpdj_published'])) {
                $snapshot = $record['decoded']['_lpdj_published'];
                if (!is_array($snapshot) || empty($snapshot['versions'])) throw new RuntimeException('Invalid publication snapshot.');
                foreach ($snapshot['versions'] as $version) if (empty($version['approved'])) throw new RuntimeException('A published language is unapproved.');
                $published[] = $id;
            }
        }
        $counts[$type] = ($counts[$type] ?? 0) + 1; $records[$id] = $record;
    }
    $declared = $bundle['counts']; ksort($declared); ksort($counts);
    $expected_published = array_map('intval', array_column($bundle['published'], 'id')); sort($expected_published); sort($published);
    if ($counts !== $declared || $expected_published !== $published) throw new RuntimeException('Catalogue counts do not match.');
    foreach ($records as $id => $record) {
        $parent = (int) $record['post_parent'];
        if ($parent && ($records[$parent]['post_type'] ?? '') !== 'lpdj_problem') throw new RuntimeException('Invalid parent reference.');
        $snapshots = [];
        foreach (['_lpdj_draft','_lpdj_published'] as $key) if (isset($record['decoded'][$key])) $snapshots[] = $record['decoded'][$key];
        if ($record['post_type'] === 'lpdj_history') $snapshots[] = json_decode($record['post_content'], true, 128, JSON_THROW_ON_ERROR);
        foreach ($snapshots as $snapshot) {
            if (($records[(int) $snapshot['id']]['post_type'] ?? '') !== 'lpdj_problem') throw new RuntimeException('Invalid snapshot problem ID.');
            foreach (($snapshot['assets'] ?? []) as $asset) if (($records[(int) $asset['id']]['post_type'] ?? '') !== 'lpdj_asset') throw new RuntimeException('Missing snapshot figure.');
        }
    }
    // Install figures before problems, so publication can never reference an unfinished figure.
    $order = ['lpdj_asset'=>0, 'lpdj_problem'=>1, 'lpdj_history'=>2];
    uasort($records, fn($a,$b) => [$order[$a['post_type']],$a['ID']] <=> [$order[$b['post_type']],$b['ID']]);
    $bundle['records'] = $records; $bundle['hash'] = hash('sha256', $plain);
    return $bundle;
}
function lpdj_transfer_snapshot($snapshot, $ids) {
    $snapshot['id'] = $ids[(string) $snapshot['id']];
    foreach (($snapshot['assets'] ?? []) as $name => $asset) {
        $snapshot['assets'][$name]['id'] = $ids[(string) $asset['id']];
        unset($snapshot['assets'][$name]['url']);
    }
    return $snapshot;
}
function lpdj_transfer_expected($record, $ids) {
    $meta = $record['decoded'];
    foreach (['_lpdj_draft','_lpdj_published'] as $key) if (isset($meta[$key])) $meta[$key] = lpdj_transfer_snapshot($meta[$key], $ids);
    $content = $record['post_content'];
    if ($record['post_type'] === 'lpdj_history') $content = wp_json_encode(lpdj_transfer_snapshot(json_decode($content, true, 128, JSON_THROW_ON_ERROR), $ids), JSON_UNESCAPED_UNICODE);
    return ['meta'=>$meta, 'content'=>$content];
}
function lpdj_transfer_step($expected_hash, $batch = 100) {
    lpdj_transfer_guard();
    if (!add_option('_lpdj_catalogue_transfer_lock', time(), '', false)) throw new RuntimeException('Another transfer batch is running.');
    try { return lpdj_transfer_step_locked($expected_hash, $batch); }
    finally { delete_option('_lpdj_catalogue_transfer_lock'); if (function_exists('lpdj_catalogue_changed')) lpdj_catalogue_changed(); }
}
function lpdj_transfer_step_locked($expected_hash, $batch = 100) {
    global $wpdb;
    $bundle = lpdj_transfer_bundle();
    if (!hash_equals($bundle['hash'], $expected_hash)) throw new RuntimeException('The transfer file changed. Stop and review the new export.');
    $state = get_option('_lpdj_catalogue_transfer_v1');
    if (!$state) {
        $existing = get_posts(['post_type'=>['lpdj_problem','lpdj_asset','lpdj_history','lpdj_transfer'], 'post_status'=>'any','posts_per_page'=>1,'fields'=>'ids']);
        if ($existing) throw new RuntimeException('Import is allowed only into an empty community catalogue. Existing content is never overwritten.');
        $state = ['hash'=>$bundle['hash'], 'owner'=>get_current_user_id(), 'phase'=>'allocate', 'offset'=>0, 'ids'=>[], 'counts'=>$bundle['counts'], 'published'=>count($bundle['published'])];
    }
    if ($state['hash'] !== $bundle['hash'] || (int) $state['owner'] !== get_current_user_id()) throw new RuntimeException('Only the original importing administrator can resume this transfer.');
    if ($state['phase'] === 'done') return $state;
    $all = array_values($bundle['records']); $total = count($all); $touched = [];
    if ($wpdb->query('START TRANSACTION') === false) throw new RuntimeException('Database transactions are required.');
    try {
        $chunk = array_slice($all, $state['offset'], max(1, min(150, $batch)));
        if ($state['phase'] === 'publish') $chunk = $all;
        foreach ($chunk as $record) {
            $old_id = (string) $record['ID'];
            if ($state['phase'] === 'allocate') {
                $id = wp_insert_post(wp_slash(['post_type'=>'lpdj_transfer','post_status'=>'private', 'post_author'=>$state['owner'], 'post_title'=>'Catalogue transfer '.$old_id]), true);
                if (is_wp_error($id)) throw new RuntimeException($id->get_error_message());
                $state['ids'][$old_id] = $id; $touched[] = $id;
            } else {
                $id = $state['ids'][$old_id]; $touched[] = $id;
                $expected = lpdj_transfer_expected($record, $state['ids']);
                $parent = $record['post_parent'] ? $state['ids'][(string) $record['post_parent']] : 0;
                if ($state['phase'] === 'content') {
                    $updated = wp_update_post(wp_slash(['ID'=>$id,'post_type'=>$record['post_type'],'post_status'=>'private', 'post_parent'=>$parent, 'post_author'=>$state['owner'], 'post_title'=>$record['post_title'], 'post_content'=>$expected['content'], 'post_date'=>$record['post_date'], 'post_date_gmt'=>$record['post_date_gmt'], 'comment_status'=>'closed', 'ping_status'=>'closed']), true);
                    if (is_wp_error($updated)) throw new RuntimeException($updated->get_error_message());
                    foreach ($expected['meta'] as $key => $value) lpdj_json_meta($id, $key === '_lpdj_published' ? '_lpdj_transfer_published' : $key, $value);
                    if ($wpdb->update($wpdb->posts, ['post_modified'=>$record['post_modified'],'post_modified_gmt'=>$record['post_modified_gmt']], ['ID'=>$id]) === false) throw new RuntimeException('Could not preserve modification dates.');
                    clean_post_cache($id);
                } elseif ($state['phase'] === 'verify') {
                    $post = get_post($id);
                    foreach (['post_type','post_title','post_status','post_date','post_date_gmt','post_modified','post_modified_gmt'] as $field) if ($post->$field !== $record[$field]) throw new RuntimeException('Verification failed for '.$old_id.': '.$field);
                    if ((int)$post->post_parent !== (int)$parent || $post->post_content !== $expected['content']) throw new RuntimeException('Content verification failed for '.$old_id);
                    foreach ($expected['meta'] as $key => $value) if (get_post_meta($id, $key === '_lpdj_published' ? '_lpdj_transfer_published' : $key, true) !== $value) throw new RuntimeException('Metadata verification failed for '.$old_id.': '.$key);
                    if (get_post_meta($id, '_lpdj_published', true)) throw new RuntimeException('A problem was published before verification finished.');
                } elseif ($state['phase'] === 'publish' && isset($expected['meta']['_lpdj_published'])) {
                    lpdj_json_meta($id, '_lpdj_published', $expected['meta']['_lpdj_published']);
                    update_post_meta($id, '_lpdj_notified', 1); // This is a migration, not a new publication event.
                    delete_post_meta($id, '_lpdj_transfer_published');
                    if (get_post_meta($id, '_lpdj_published', true) !== $expected['meta']['_lpdj_published']) throw new RuntimeException('Publication verification failed.');
                }
            }
        }
        $state['offset'] += count($chunk);
        if ($state['offset'] >= $total) {
            $next = ['allocate'=>'content','content'=>'verify','verify'=>'publish','publish'=>'done'];
            $state['phase'] = $next[$state['phase']]; $state['offset'] = 0;
        }
        $state['total'] = $total;
        update_option('_lpdj_catalogue_transfer_v1', $state, false);
        if ($wpdb->query('COMMIT') === false) throw new RuntimeException('Could not commit the transfer batch.');
        return $state;
    } catch (Throwable $error) {
        $wpdb->query('ROLLBACK');
        foreach ($touched as $id) clean_post_cache($id);
        wp_cache_delete('_lpdj_catalogue_transfer_v1', 'options');
        throw $error;
    }
}
function lpdj_transfer_references($bundle) {
    if (!defined('LPDJ_REFERENCE_DIR')) throw new RuntimeException('Private reference directory is not configured.');
    $root = realpath(LPDJ_REFERENCE_DIR); $count = 0;
    foreach ($bundle['references'] as $expected) {
        $name = $expected['file'];
        if (!preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]*\.(pdf|json)$/D', $name)) throw new RuntimeException('Invalid reference filename.');
        $plain = $root ? lpdj_private_read($root, $name) : false;
        if ($plain === false || strlen($plain) !== $expected['bytes'] || !hash_equals($expected['sha256'], hash('sha256', $plain))) throw new RuntimeException('Reference integrity check failed: '.$name);
        $count++;
    }
    return $count;
}
add_action('admin_menu', function () {
    add_management_page('Catalogue transfer', 'Catalogue transfer', 'manage_options', 'lpdj-catalogue-transfer', function () {
        echo '<div class="wrap"><h1>Catalogue transfer</h1>';
        if (!defined('LPDJ_TRANSFER_DIR')) {
            $parent = dirname(rtrim(ABSPATH, '/\\'));
            echo '<h2>Private storage preflight</h2><dl>';
            foreach (['WordPress root'=>ABSPATH, 'Document root'=>($_SERVER['DOCUMENT_ROOT'] ?? ''), 'Parent directory'=>$parent, 'Parent writable'=>is_writable($parent)?'yes':'no', 'PHP open_basedir'=>ini_get('open_basedir') ?: '(unrestricted)', 'Upload directory'=>wp_upload_dir()['basedir']] as $label=>$value) echo '<dt>'.esc_html($label).'</dt><dd>'.esc_html($value).'</dd>';
            foreach (glob($parent.'/*', GLOB_ONLYDIR) ?: [] as $directory) echo '<dt>Sibling directory</dt><dd>'.esc_html($directory.'; writable='.(is_writable($directory)?'yes':'no').'; realpath='.realpath($directory)).'</dd>';
            echo '</dl>';
        }
        try {
            $bundle = lpdj_transfer_bundle(); $state = get_option('_lpdj_catalogue_transfer_v1');
            echo '<p>Private current-data export: <strong>'.esc_html($bundle['counts']['lpdj_problem']).' problems</strong>, '.esc_html(count($bundle['published'])).' published, '.esc_html($bundle['counts']['lpdj_asset'] ?? 0).' figures.</p>';
            echo '<p>All imported content will belong to this production administrator. Local user accounts and passwords are excluded.</p>';
            echo '<p id="transfer-status">Status: '.esc_html($state ? $state['phase'].' '.$state['offset'].' / '.count($bundle['records']) : 'Ready').'</p>';
            if (($state['phase'] ?? '') === 'done') {
                echo '<p><strong>Catalogue imported and verified. Publication states preserved; no notification emails sent.</strong></p><p><a href="'.esc_url(home_url('/#/administration')).'">Open admin review</a></p>';
            } else {
                echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'"><input type="hidden" name="action" value="lpdj_catalogue_transfer"><input type="hidden" name="hash" value="'.esc_attr($bundle['hash']).'">';
                wp_nonce_field('lpdj_catalogue_transfer');
                submit_button($state ? 'Continue transfer' : 'Start transfer'); echo '</form>';
            }
            echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'"><input type="hidden" name="action" value="lpdj_reference_check">'; wp_nonce_field('lpdj_reference_check'); submit_button('Verify private reference files', 'secondary'); echo '</form>';
            if (isset($_GET['references'])) echo '<p>'.esc_html(absint($_GET['references'])).' private reference files verified.</p>';
        } catch (Throwable $error) { echo '<p>'.esc_html($error->getMessage()).'</p>'; }
        echo '</div>';
    });
});
add_action('admin_post_lpdj_catalogue_transfer', function () {
    try { lpdj_transfer_guard(); check_admin_referer('lpdj_catalogue_transfer'); lpdj_transfer_step((string)($_POST['hash'] ?? '')); }
    catch (Throwable $error) { wp_die(esc_html($error->getMessage()), 'Catalogue transfer stopped', ['response'=>400]); }
    wp_safe_redirect(admin_url('tools.php?page=lpdj-catalogue-transfer')); exit;
});
add_action('admin_post_lpdj_reference_check', function () {
    try { lpdj_transfer_guard(); check_admin_referer('lpdj_reference_check'); $count = lpdj_transfer_references(lpdj_transfer_bundle()); }
    catch (Throwable $error) { wp_die(esc_html($error->getMessage()), 'Reference check stopped', ['response'=>400]); }
    wp_safe_redirect(admin_url('tools.php?page=lpdj-catalogue-transfer&references='.$count)); exit;
});
