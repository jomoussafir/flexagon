<?php
defined('ABSPATH') || exit;

function lpdj_public_form($request) {
    $origin = $request->get_header('origin');
    $expected = wp_parse_url(home_url('/'));
    $actual = wp_parse_url($origin ?: '');
    if (!$origin || ($actual['scheme'] ?? '') !== $expected['scheme'] || ($actual['host'] ?? '') !== $expected['host'] || ($actual['port'] ?? null) !== ($expected['port'] ?? null)) {
        return lpdj_error('Rechargez la page avant de réessayer.', 403);
    }
    return wp_verify_nonce($request->get_header('x-lpdj-form'), 'lpdj_form') ? true : lpdj_error('Rechargez la page avant de réessayer.', 403);
}
function lpdj_throttle($action, $limit = 10) {
    $key = 'lpdj_rate_' . hash('sha256', $action . '|' . ($_SERVER['REMOTE_ADDR'] ?? 'local'));
    $n = (int) get_transient($key);
    if ($n >= $limit) return lpdj_error('Trop de tentatives. Réessayez dans quinze minutes.', 429);
    set_transient($key, $n + 1, 15 * MINUTE_IN_SECONDS);
    return true;
}
function lpdj_profile($user) {
    return ['id' => $user->ID, 'pseudo' => $user->display_name, 'email' => $user->user_email,
        'admin' => user_can($user, 'manage_options'), 'notifications' => (bool) get_user_meta($user->ID, '_lpdj_notifications', true),
        'avatar' => ($id = get_user_meta($user->ID, '_lpdj_avatar', true)) ? lpdj_asset_url($id) : null];
}
function lpdj_session() {
    return ['user' => lpdj_member() === true ? lpdj_profile(wp_get_current_user()) : null,
        'nonce' => wp_create_nonce('wp_rest'), 'formNonce' => wp_create_nonce('lpdj_form'), 'local' => lpdj_local(),
        'categories' => ['Algebra','Geometry','Number Theory','Combinatorics','Logic'],
        'sources' => ['Moscow Puzzles','Colossal Book','Animath','Challenging Problems in Geometry and Algebra','Yaglom','Stanford','IMO']];
}
add_filter('wp_authenticate_user', function ($user) {
    if (!is_wp_error($user) && get_user_meta($user->ID, '_lpdj_verification', true) === 'pending') return lpdj_error('Confirmez votre adresse e-mail avant de vous connecter.', 403);
    return $user;
}, 20);
function lpdj_send_verification($user) {
    $token = bin2hex(random_bytes(32));
    update_user_meta($user->ID, '_lpdj_verify_token', ['hash' => hash('sha256', $token), 'expires' => time() + DAY_IN_SECONDS]);
    $url = home_url('/#/confirmer?user=' . $user->ID . '&token=' . $token);
    return wp_mail($user->user_email, 'Confirmez votre compte — Le Problème du Jour', "Bonjour {$user->display_name},\n\nConfirmez votre adresse en ouvrant ce lien (valable 24 heures) :\n$url\n\nSi vous n’avez pas demandé ce compte, ignorez ce message.");
}
function lpdj_auth_register($r) {
    if (($t = lpdj_throttle('register', 6)) !== true) return $t;
    $email = sanitize_email($r['email']); $pseudo = sanitize_text_field($r['pseudo']); $password = (string) $r['password'];
    if (!is_email($email) || mb_strlen($pseudo) < 2 || mb_strlen($pseudo) > 40 || strlen($password) < 12 || strlen($password) > 200) return lpdj_error('Indiquez un pseudo de 2 à 40 caractères, un e-mail valide et un mot de passe d’au moins 12 caractères.');
    if (!$r['accept']) return lpdj_error('Veuillez accepter les conditions de contribution.');
    $message = ['message' => 'Consultez votre e-mail pour confirmer votre compte. Si vous avez déjà un compte, connectez-vous ou réinitialisez votre mot de passe.'];
    if (email_exists($email)) return $message;
    $id = wp_insert_user(['user_login' => 'member_' . bin2hex(random_bytes(12)), 'user_email' => $email, 'user_pass' => $password,
        'display_name' => $pseudo, 'role' => 'lpdj_member']);
    if (is_wp_error($id)) return lpdj_error('Impossible de créer le compte. Réessayez.');
    update_user_meta($id, '_lpdj_verification', 'pending');
    update_user_meta($id, '_lpdj_notifications', !empty($r['notifications']));
    update_user_meta($id, '_lpdj_consent', ['version' => 1, 'date' => gmdate('c')]);
    if (!lpdj_send_verification(get_user_by('id', $id))) return lpdj_error('Compte créé, mais l’e-mail n’a pas pu être envoyé. Utilisez « Renvoyer la confirmation ».', 503);
    return $message;
}
function lpdj_auth_login($r) {
    if (($t = lpdj_throttle('login', 15)) !== true) return $t;
    // Nonces in this response must use the newly issued session token, not the
    // anonymous cookie state from the beginning of the login request.
    $remember_cookie = function ($cookie) { $_COOKIE[LOGGED_IN_COOKIE] = $cookie; };
    add_action('set_logged_in_cookie', $remember_cookie);
    $user = wp_signon(['user_login' => sanitize_email($r['email']), 'user_password' => (string) $r['password'], 'remember' => !empty($r['remember'])], is_ssl());
    remove_action('set_logged_in_cookie', $remember_cookie);
    if (is_wp_error($user)) return lpdj_error('Connexion impossible. Vérifiez votre e-mail, votre mot de passe et la confirmation de votre compte.', 401);
    wp_set_current_user($user->ID);
    return lpdj_session();
}
function lpdj_auth_verify($r) {
    if (($t = lpdj_throttle('verify', 20)) !== true) return $t;
    $id = absint($r['user']); $record = get_user_meta($id, '_lpdj_verify_token', true);
    if (!$record || $record['expires'] < time() || !hash_equals($record['hash'], hash('sha256', (string) $r['token']))) return lpdj_error('Ce lien est invalide ou a expiré. Demandez un nouveau lien.');
    update_user_meta($id, '_lpdj_verification', 'verified'); delete_user_meta($id, '_lpdj_verify_token');
    return ['message' => 'Adresse confirmée. Vous pouvez vous connecter.'];
}
function lpdj_auth_resend($r) {
    if (($t = lpdj_throttle('resend', 5)) !== true) return $t;
    $user = get_user_by('email', sanitize_email($r['email']));
    if ($user && get_user_meta($user->ID, '_lpdj_verification', true) === 'pending') lpdj_send_verification($user);
    return ['message' => 'Si une confirmation est nécessaire, un nouveau lien a été envoyé.'];
}
function lpdj_auth_forgot($r) {
    if (($t = lpdj_throttle('forgot', 5)) !== true) return $t;
    $user = get_user_by('email', sanitize_email($r['email']));
    if ($user) {
        $key = get_password_reset_key($user);
        if (!is_wp_error($key)) wp_mail($user->user_email, 'Réinitialiser votre mot de passe — Le Problème du Jour', "Ouvrez ce lien pour choisir un nouveau mot de passe :\n" . home_url('/#/reinitialiser?login=' . rawurlencode($user->user_login) . '&key=' . rawurlencode($key)) . "\n\nSi vous n’êtes pas à l’origine de cette demande, ignorez ce message.");
    }
    return ['message' => 'Si ce compte existe, un lien de réinitialisation a été envoyé.'];
}
function lpdj_auth_reset($r) {
    if (($t = lpdj_throttle('reset', 10)) !== true) return $t;
    if (strlen((string) $r['password']) < 12 || strlen((string) $r['password']) > 200) return lpdj_error('Le mot de passe doit contenir entre 12 et 200 caractères.');
    $user = check_password_reset_key((string) $r['key'], (string) $r['login']);
    if (is_wp_error($user)) return lpdj_error('Ce lien est invalide ou a expiré.');
    reset_password($user, (string) $r['password']);
    WP_Session_Tokens::get_instance($user->ID)->destroy_all();
    return ['message' => 'Mot de passe modifié. Connectez-vous.'];
}
function lpdj_profile_save($r) {
    $pseudo = sanitize_text_field($r['pseudo']);
    if (mb_strlen($pseudo) < 2 || mb_strlen($pseudo) > 40) return lpdj_error('Le pseudo doit contenir de 2 à 40 caractères.');
    $id = get_current_user_id();
    if ($r->has_param('avatar')) {
        $avatar = absint($r['avatar']); $post = get_post($avatar);
        if ($avatar && (!$post || $post->post_type !== 'lpdj_asset' || (int) $post->post_author !== $id || (int) $post->post_parent !== 0)) return lpdj_error('Image de profil invalide.');
    }
    wp_update_user(['ID' => $id, 'display_name' => $pseudo]);
    update_user_meta($id, '_lpdj_notifications', !empty($r['notifications']));
    if ($r->has_param('avatar')) update_user_meta($id, '_lpdj_avatar', $avatar);
    return lpdj_profile(get_user_by('id', $id));
}
function lpdj_account_delete($r) {
    $user = wp_get_current_user();
    if (lpdj_admin()) return lpdj_error('Un administrateur doit transférer son rôle avant de supprimer son compte.');
    if (!wp_check_password((string) $r['password'], $user->user_pass, $user->ID)) return lpdj_error('Mot de passe incorrect.', 403);
    $posts = get_posts(['post_type' => 'lpdj_problem', 'author' => $user->ID, 'posts_per_page' => -1, 'post_status' => 'any']);
    foreach ($posts as $post) {
        $pub = get_post_meta($post->ID, '_lpdj_published', true);
        if ($pub) {
            $pub['author'] = 'Compte supprimé'; lpdj_json_meta($post->ID, '_lpdj_published', $pub);
            $draft = $pub;
            foreach (['fr','en'] as $lang) if (!isset($draft['versions'][$lang])) $draft['versions'][$lang] = ['title' => '', 'latex' => '', 'approved' => false];
            $draft['reviewNote'] = ''; $draft['revision'] = (int) get_post_meta($post->ID, '_lpdj_draft', true)['revision'] + 1;
            lpdj_json_meta($post->ID, '_lpdj_draft', $draft); wp_update_post(['ID' => $post->ID, 'post_author' => 0]);
            foreach (get_posts(['post_type' => 'lpdj_history', 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => -1]) as $history) {
                $snapshot = json_decode($history->post_content, true); $snapshot['author'] = 'Compte supprimé';
                wp_update_post(wp_slash(['ID' => $history->ID, 'post_content' => wp_json_encode($snapshot)]));
            }
        } else {
            foreach (get_posts(['post_type' => ['lpdj_asset','lpdj_history'], 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => -1]) as $child) wp_delete_post($child->ID, true);
            wp_delete_post($post->ID, true);
        }
    }
    // Remove historical personal attribution. Published figures remain attached to the problem.
    foreach (get_posts(['post_type' => ['lpdj_asset', 'lpdj_history'], 'author' => $user->ID, 'posts_per_page' => -1, 'post_status' => 'any']) as $post) {
        if ($post->post_type === 'lpdj_history' || !$post->post_parent || !get_post_meta($post->post_parent, '_lpdj_published', true)) wp_delete_post($post->ID, true);
        else wp_update_post(['ID' => $post->ID, 'post_author' => 0]);
    }
    require_once ABSPATH . 'wp-admin/includes/user.php';
    wp_logout(); wp_delete_user($user->ID, 0);
    return ['ok' => true];
}
// Only the local launcher sets this constant. OVH uses normal WordPress mail delivery.
add_filter('pre_wp_mail', function ($return, $args) {
    if (!lpdj_local()) return $return;
    $messages = get_option('_lpdj_local_mail', []);
    $messages[] = ['to' => $args['to'], 'subject' => $args['subject'], 'message' => $args['message'], 'date' => gmdate('c')];
    update_option('_lpdj_local_mail', array_slice($messages, -100), false);
    return true;
}, 10, 2);
