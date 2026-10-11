<?php
defined('ABSPATH') || exit;

function lpdj_problem_post($id) {
    $post = get_post(absint($id));
    return $post && $post->post_type === 'lpdj_problem' ? $post : null;
}
function lpdj_can_edit($post) { return $post && (lpdj_admin() || (int) $post->post_author === get_current_user_id()); }
function lpdj_json_meta($id, $key, $value) { return update_post_meta($id, $key, wp_slash($value)); }
function lpdj_draft($post) {
    $data = get_post_meta($post->ID, '_lpdj_draft', true);
    $data['id'] = $post->ID;
    $data['author'] = get_the_author_meta('display_name', $post->post_author) ?: 'Compte supprimé';
    $data['hasPublished'] = (bool) get_post_meta($post->ID, '_lpdj_published', true);
    return $data;
}
function lpdj_present($data, $editor = false) {
    foreach (($data['assets'] ?? []) as $name => $asset) $data['assets'][$name]['url'] = lpdj_asset_url($asset['id']);
    $data['progress'] = get_user_meta(get_current_user_id(), '_lpdj_progress_' . $data['id'], true) ?: 'unseen';
    $data['editable'] = lpdj_can_edit(lpdj_problem_post($data['id']));
    if (!$editor) unset($data['reviewNote']);
    return $data;
}
function lpdj_problems_list($r) {
    $scope = $r['scope'] ?: 'published';
    if (!in_array($scope, ['published','mine','review'], true)) return lpdj_error('Liste inconnue.');
    if ($scope === 'review' && !lpdj_admin()) return lpdj_error('Accès réservé aux administrateurs.', 403);
    $args = ['post_type' => 'lpdj_problem', 'post_status' => 'private', 'posts_per_page' => -1, 'orderby' => 'ID', 'order' => 'DESC'];
    if ($scope === 'mine') $args['author'] = get_current_user_id();
    $items = []; $counts = []; $published = 0;
    foreach (get_posts($args) as $post) {
        $pub = get_post_meta($post->ID, '_lpdj_published', true);
        if ($pub) { $published++; $source = $pub['source'] ?: 'Communauté'; $counts[$source] = ($counts[$source] ?? 0) + 1; }
        $data = $scope === 'published' ? $pub : lpdj_draft($post);
        if (!$data) continue;
        $data = lpdj_present($data, $scope !== 'published');
        // Overview records do not include full statements or image data.
        foreach ($data['versions'] as &$version) unset($version['latex']);
        unset($version, $data['assets']);
        $items[] = $data;
    }
    return ['items' => $items, 'total' => count($items), 'published' => $published, 'sources' => $counts];
}
function lpdj_problem_get($r) {
    $post = lpdj_problem_post($r['id']);
    if (!$post) return lpdj_error('Problème introuvable.', 404);
    $edit = $r['context'] === 'edit';
    if ($edit && !lpdj_can_edit($post)) return lpdj_error('Accès refusé.', 403);
    $data = $edit ? lpdj_draft($post) : get_post_meta($post->ID, '_lpdj_published', true);
    return $data ? lpdj_present($data, $edit) : lpdj_error('Ce problème n’est pas publié.', 404);
}
function lpdj_problem_create() {
    if (($t = lpdj_throttle('create', 30)) !== true) return $t;
    $id = wp_insert_post(['post_type' => 'lpdj_problem', 'post_status' => 'private', 'post_title' => 'Nouveau problème', 'post_author' => get_current_user_id()], true);
    if (is_wp_error($id)) return lpdj_error('Création impossible.', 500);
    $data = ['id' => $id, 'revision' => 1, 'state' => 'draft', 'category' => 'Algebra', 'difficulty' => 1,
        'source' => 'Communauté', 'keywords' => [], 'reviewNote' => '', 'assets' => [],
        'updated' => gmdate('c'), 'versions' => ['fr' => ['title' => '', 'latex' => '', 'approved' => false], 'en' => ['title' => '', 'latex' => '', 'approved' => false]]];
    lpdj_json_meta($id, '_lpdj_draft', $data);
    return lpdj_present(lpdj_draft(get_post($id)), true);
}
function lpdj_validate_problem($r, $old) {
    $category = (string) $r['category']; $difficulty = filter_var($r['difficulty'], FILTER_VALIDATE_INT);
    if (!in_array($category, ['Algebra','Geometry','Number Theory','Combinatorics','Logic'], true) || $difficulty < 1 || $difficulty > 5) return lpdj_error('Choisissez une catégorie et une difficulté de 1 à 5.');
    $source = sanitize_text_field((string) $r['source']);
    if (mb_strlen($source) > 160) return lpdj_error('La source est trop longue.');
    $keywords = array_values(array_unique(array_filter(array_map('sanitize_text_field', (array) $r['keywords']))));
    if (count($keywords) > 15 || strlen(implode(',', $keywords)) > 400) return lpdj_error('Utilisez au maximum 15 mots-clés courts.');
    $data = $old;
    $data['category'] = $category; $data['difficulty'] = $difficulty; $data['source'] = $source ?: 'Communauté'; $data['keywords'] = $keywords;
    $versions = $r['versions'];
    if (!is_array($versions)) return lpdj_error('Versions manquantes.');
    $metadata_changed = $old['category'] !== $category || $old['difficulty'] !== $difficulty || $old['source'] !== $data['source'] || $old['keywords'] !== $keywords;
    foreach (['fr','en'] as $lang) {
        $version = $versions[$lang] ?? []; $title = sanitize_text_field((string) ($version['title'] ?? ''));
        $latex = str_replace("\0", '', (string) ($version['latex'] ?? ''));
        if (mb_strlen($title) > 200 || strlen($latex) > 60000) return lpdj_error('Limite : 200 caractères pour le titre et 60 Ko pour un énoncé.');
        $changed = $metadata_changed || $title !== $old['versions'][$lang]['title'] || $latex !== $old['versions'][$lang]['latex'];
        $approved = lpdj_admin() ? !empty($version['approved']) : (!$changed && !empty($old['versions'][$lang]['approved']));
        if ($approved && (!$title || !trim($latex))) return lpdj_error('Une version validée doit avoir un titre et un énoncé.');
        $data['versions'][$lang] = ['title' => $title, 'latex' => $latex, 'approved' => $approved];
    }
    if (lpdj_admin()) $data['reviewNote'] = sanitize_textarea_field((string) $r['reviewNote']);
    if (strlen($data['reviewNote']) > 5000) return lpdj_error('La note de révision est trop longue.');
    unset($data['hasPublished'], $data['editable'], $data['progress']);
    return $data;
}
function lpdj_check_figures($version, $assets) {
    preg_match_all('/\\\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}/', $version['latex'], $matches);
    foreach ($matches[1] as $name) if (!isset($assets[$name])) return lpdj_error('Figure manquante : ' . $name);
    preg_match_all('/\\\\label\{([^}]+)\}/', $version['latex'], $labels);
    if (count($labels[1]) !== count(array_unique($labels[1]))) return lpdj_error('Les noms de labels doivent être uniques dans chaque version.');
    preg_match_all('/\\\\ref\{([^}]+)\}/', $version['latex'], $refs);
    foreach ($refs[1] as $ref) if (!in_array($ref, $labels[1], true)) return lpdj_error('Référence inconnue : ' . $ref);
    return true;
}
function lpdj_lock($id) {
    $name = '_lpdj_lock_' . $id; $existing = (int) get_option($name, 0);
    if ($existing && $existing < time() - 120) delete_option($name);
    return add_option($name, time(), '', false);
}
function lpdj_problem_save($r) {
    $post = lpdj_problem_post($r['id']);
    if (!lpdj_can_edit($post)) return lpdj_error('Accès refusé.', 403);
    $id = $post->ID;
    if (!lpdj_lock($id)) return lpdj_error('Une sauvegarde est en cours. Réessayez.', 409);
    try {
        $old = lpdj_draft($post);
        if ((int) $r['revision'] !== (int) $old['revision']) return lpdj_error('Ce problème a été modifié ailleurs. Copiez vos changements puis rechargez la page.', 409);
        $action = (string) ($r['action'] ?: 'save');
        if (!in_array($action, ['save','submit','publish','return','unpublish'], true)) return lpdj_error('Action inconnue.');
        if (in_array($action, ['publish','return','unpublish'], true) && !lpdj_admin()) return lpdj_error('Seul un administrateur peut publier ou retourner un problème.', 403);
        $data = lpdj_validate_problem($r, $old); if (is_wp_error($data)) return $data;
        $complete = false;
        foreach ($data['versions'] as $version) {
            if ($version['title'] && trim($version['latex'])) $complete = true;
            if ($action === 'submit' || ($action === 'publish' && $version['approved'])) {
                $check = lpdj_check_figures($version, $data['assets']); if (is_wp_error($check)) return $check;
            }
        }
        if (in_array($action, ['submit','publish'], true) && !$complete) return lpdj_error('Complétez au moins un titre et son énoncé.');
        $data['revision']++; $data['updated'] = gmdate('c'); $data['author'] = $old['author'];
        $previous_pub = get_post_meta($id, '_lpdj_published', true);
        if ($action === 'publish') {
            $approved = array_filter($data['versions'], fn($v) => $v['approved']);
            if (!$approved) return lpdj_error('Cochez la validation d’au moins une version avant de publier.');
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
            if (!trim($data['reviewNote'])) return lpdj_error('Ajoutez une note pour expliquer les changements demandés.');
            $data['state'] = 'returned';
        } elseif ($action === 'submit') {
            $data['state'] = 'submitted';
        } else $data['state'] = 'draft';
        lpdj_json_meta($id, '_lpdj_draft', $data);
        wp_update_post(['ID' => $id, 'post_title' => wp_slash($data['versions']['fr']['title'] ?: $data['versions']['en']['title'] ?: 'Nouveau problème')]);
        wp_insert_post(wp_slash(['post_type' => 'lpdj_history', 'post_status' => 'private', 'post_parent' => $id, 'post_author' => get_current_user_id(),
            'post_title' => $action, 'post_content' => wp_json_encode($data, JSON_UNESCAPED_UNICODE)]));
        return lpdj_present(lpdj_draft(get_post($id)), true);
    } finally { delete_option('_lpdj_lock_' . $id); }
}
function lpdj_problem_history($r) {
    $post = lpdj_problem_post($r['id']); if (!lpdj_can_edit($post)) return lpdj_error('Accès refusé.', 403);
    return array_map(function ($entry) {
        return ['id' => $entry->ID, 'action' => $entry->post_title, 'date' => $entry->post_date_gmt . 'Z',
            'by' => get_the_author_meta('display_name', $entry->post_author) ?: 'Compte supprimé', 'snapshot' => json_decode($entry->post_content, true)];
    }, get_posts(['post_type' => 'lpdj_history', 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => 50, 'orderby' => 'ID', 'order' => 'DESC']));
}
function lpdj_problem_delete($r) {
    $post = lpdj_problem_post($r['id']);
    if (!lpdj_can_edit($post)) return lpdj_error('Accès refusé.', 403);
    if (!lpdj_lock($post->ID)) return lpdj_error('Une sauvegarde est en cours. Réessayez.', 409);
    try {
        if (get_post_meta($post->ID, '_lpdj_published', true)) return lpdj_error('Un administrateur doit d’abord retirer la publication.');
        foreach (get_posts(['post_type' => ['lpdj_asset','lpdj_history'], 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => -1]) as $child) wp_delete_post($child->ID, true);
        wp_delete_post($post->ID, true);
        return ['ok' => true];
    } finally { delete_option('_lpdj_lock_' . $post->ID); }
}
function lpdj_progress_save($r) {
    if (!get_post_meta(absint($r['id']), '_lpdj_published', true)) return lpdj_error('Problème introuvable.', 404);
    if (!in_array($r['progress'], ['unseen','bookmarked','attempted','solved'], true)) return lpdj_error('Progression inconnue.');
    update_user_meta(get_current_user_id(), '_lpdj_progress_' . absint($r['id']), $r['progress']);
    return ['progress' => $r['progress']];
}
add_action('lpdj_notify_published', function ($id) {
    $pub = get_post_meta($id, '_lpdj_published', true); if (!$pub || get_post_meta($id, '_lpdj_notified', true)) return;
    $version = $pub['versions']['fr'] ?? reset($pub['versions']);
    $users = get_users(['meta_key' => '_lpdj_notifications', 'meta_value' => '1']);
    $sent = get_post_meta($id, '_lpdj_notified_users', true) ?: []; $failed = false;
    foreach ($users as $user) {
        if (get_user_meta($user->ID, '_lpdj_verification', true) === 'pending') continue;
        if (in_array($user->ID, $sent, true)) continue;
        if (wp_mail($user->user_email, 'Nouveau problème : ' . $version['title'], $version['title'] . "\n\nUn nouveau problème est disponible :\n" . home_url('/#/probleme/' . $id) . "\n\nPour arrêter ces notifications, décochez l’option dans votre profil :\n" . home_url('/#/profil'))) {
            $sent[] = $user->ID; update_post_meta($id, '_lpdj_notified_users', $sent);
        } else $failed = true;
    }
    if (!$failed) update_post_meta($id, '_lpdj_notified', 1);
    else {
        $retries = (int) get_post_meta($id, '_lpdj_notification_retries', true);
        if ($retries < 3) { update_post_meta($id, '_lpdj_notification_retries', $retries + 1); wp_schedule_single_event(time() + 10 * MINUTE_IN_SECONDS, 'lpdj_notify_published', [$id]); }
    }
});
