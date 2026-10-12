<?php
defined('ABSPATH') || exit;

function lpdj_public_form($request) {
    $origin = $request->get_header('origin');
    $expected = wp_parse_url(home_url('/'));
    $actual = wp_parse_url($origin ?: '');
    if (!$origin || ($actual['scheme'] ?? '') !== $expected['scheme'] || ($actual['host'] ?? '') !== $expected['host'] || ($actual['port'] ?? null) !== ($expected['port'] ?? null)) {
        return lpdj_error('Reload the page and try again.', 403);
    }
    return wp_verify_nonce($request->get_header('x-lpdj-form'), 'lpdj_form') ? true : lpdj_error('Reload the page and try again.', 403);
}
function lpdj_throttle($action, $limit = 10) {
    $key = 'lpdj_rate_' . hash('sha256', $action . '|' . ($_SERVER['REMOTE_ADDR'] ?? 'local'));
    $n = (int) get_transient($key);
    if ($n >= $limit) return lpdj_error('Too many attempts. Try again in fifteen minutes.', 429);
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
    if (!is_wp_error($user) && get_user_meta($user->ID, '_lpdj_verification', true) === 'pending') return lpdj_error('Confirm your email address before signing in.', 403);
    return $user;
}, 20);
function lpdj_send_verification($user) {
    $token = bin2hex(random_bytes(32));
    update_user_meta($user->ID, '_lpdj_verify_token', ['hash' => hash('sha256', $token), 'expires' => time() + DAY_IN_SECONDS]);
    $url = home_url('/#/confirmer?user=' . $user->ID . '&token=' . $token);
    return wp_mail($user->user_email, 'Confirm your account — Le Problème du Jour', "Hello {$user->display_name},\n\nConfirm your email using this link (valid for 24 hours):\n$url\n\nIf you did not request this account, ignore this message.");
}
function lpdj_auth_register($r) {
    if (($t = lpdj_throttle('register', 6)) !== true) return $t;
    $email = sanitize_email($r['email']); $pseudo = sanitize_text_field($r['pseudo']); $password = (string) $r['password'];
    if (!is_email($email) || mb_strlen($pseudo) < 2 || mb_strlen($pseudo) > 40 || strlen($password) < 12 || strlen($password) > 200) return lpdj_error('Enter a display name of 2–40 characters, a valid email and a password of at least 12 characters.');
    if (!$r['accept']) return lpdj_error('Please accept the contribution terms.');
    $message = ['message' => 'Check your email to confirm your account. If you already have an account, sign in or reset your password.'];
    if (email_exists($email)) return $message;
    $id = wp_insert_user(['user_login' => 'member_' . bin2hex(random_bytes(12)), 'user_email' => $email, 'user_pass' => $password,
        'display_name' => $pseudo, 'role' => 'lpdj_member']);
    if (is_wp_error($id)) return lpdj_error('Could not create the account. Please try again.');
    update_user_meta($id, '_lpdj_verification', 'pending');
    update_user_meta($id, '_lpdj_notifications', !empty($r['notifications']));
    update_user_meta($id, '_lpdj_consent', ['version' => 1, 'date' => gmdate('c')]);
    if (!lpdj_send_verification(get_user_by('id', $id))) return lpdj_error('Account created, but the email could not be sent. Use “Resend confirmation”.', 503);
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
    if (is_wp_error($user)) return lpdj_error('Sign-in failed. Check your email, password and account confirmation.', 401);
    wp_set_current_user($user->ID);
    return lpdj_session();
}
function lpdj_auth_verify($r) {
    if (($t = lpdj_throttle('verify', 20)) !== true) return $t;
    $id = absint($r['user']); $record = get_user_meta($id, '_lpdj_verify_token', true);
    if (!$record || $record['expires'] < time() || !hash_equals($record['hash'], hash('sha256', (string) $r['token']))) return lpdj_error('This link is invalid or expired. Request a new link.');
    update_user_meta($id, '_lpdj_verification', 'verified'); delete_user_meta($id, '_lpdj_verify_token');
    return ['message' => 'Email confirmed. You can now sign in.'];
}
function lpdj_auth_resend($r) {
    if (($t = lpdj_throttle('resend', 5)) !== true) return $t;
    $user = get_user_by('email', sanitize_email($r['email']));
    if ($user && get_user_meta($user->ID, '_lpdj_verification', true) === 'pending') lpdj_send_verification($user);
    return ['message' => 'If confirmation is needed, a new link has been sent.'];
}
function lpdj_auth_forgot($r) {
    if (($t = lpdj_throttle('forgot', 5)) !== true) return $t;
    $user = get_user_by('email', sanitize_email($r['email']));
    if ($user) {
        $key = get_password_reset_key($user);
        if (!is_wp_error($key)) wp_mail($user->user_email, 'Reset your password — Le Problème du Jour', "Open this link to choose a new password:\n" . home_url('/#/reinitialiser?login=' . rawurlencode($user->user_login) . '&key=' . rawurlencode($key)) . "\n\nIf you did not request this, ignore this message.");
    }
    return ['message' => 'If this account exists, a password-reset link has been sent.'];
}
function lpdj_auth_reset($r) {
    if (($t = lpdj_throttle('reset', 10)) !== true) return $t;
    if (strlen((string) $r['password']) < 12 || strlen((string) $r['password']) > 200) return lpdj_error('The password must be between 12 and 200 characters.');
    $user = check_password_reset_key((string) $r['key'], (string) $r['login']);
    if (is_wp_error($user)) return lpdj_error('This link is invalid or expired.');
    reset_password($user, (string) $r['password']);
    WP_Session_Tokens::get_instance($user->ID)->destroy_all();
    return ['message' => 'Password changed. Please sign in.'];
}
function lpdj_profile_save($r) {
    $pseudo = sanitize_text_field($r['pseudo']);
    if (mb_strlen($pseudo) < 2 || mb_strlen($pseudo) > 40) return lpdj_error('The display name must contain 2–40 characters.');
    $id = get_current_user_id();
    if ($r->has_param('avatar')) {
        $avatar = absint($r['avatar']); $post = get_post($avatar);
        if ($avatar && (!$post || $post->post_type !== 'lpdj_asset' || (int) $post->post_author !== $id || (int) $post->post_parent !== 0)) return lpdj_error('Invalid profile image.');
    }
    wp_update_user(['ID' => $id, 'display_name' => $pseudo]);
    update_user_meta($id, '_lpdj_notifications', !empty($r['notifications']));
    if ($r->has_param('avatar')) update_user_meta($id, '_lpdj_avatar', $avatar);
    return lpdj_profile(get_user_by('id', $id));
}
function lpdj_account_delete($r) {
    $user = wp_get_current_user();
    if (lpdj_admin()) return lpdj_error('Transfer your administrator role before deleting your account.');
    if (!wp_check_password((string) $r['password'], $user->user_pass, $user->ID)) return lpdj_error('Incorrect password.', 403);
    $posts = get_posts(['post_type' => 'lpdj_problem', 'author' => $user->ID, 'posts_per_page' => -1, 'post_status' => 'any']);
    foreach ($posts as $post) {
        $pub = get_post_meta($post->ID, '_lpdj_published', true);
        if ($pub) {
            $pub['author'] = 'Deleted account'; lpdj_json_meta($post->ID, '_lpdj_published', $pub);
            $draft = $pub;
            $draft['reviewNote'] = ''; $draft['revision'] = (int) get_post_meta($post->ID, '_lpdj_draft', true)['revision'] + 1;
            lpdj_json_meta($post->ID, '_lpdj_draft', $draft); wp_update_post(['ID' => $post->ID, 'post_author' => 0]);
            foreach (get_posts(['post_type' => 'lpdj_history', 'post_status' => 'private', 'post_parent' => $post->ID, 'posts_per_page' => -1]) as $history) {
                $snapshot = json_decode($history->post_content, true); $snapshot['author'] = 'Deleted account';
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
