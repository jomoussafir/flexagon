<?php
/**
 * Plugin Name: Flexagon
 * Description: Member accounts, LaTeX submissions and reviewed publication.
 * Version: 0.2.4
 * Requires at least: 6.8
 * Requires PHP: 8.2
 * License: GPL-2.0-or-later
 */
defined('ABSPATH') || exit;
define('LPDJ_VERSION', '0.2.4');
$private_config = WP_CONTENT_DIR . '/lpdj-private-storage.php';
if (is_readable($private_config)) require_once $private_config;
// The predecessor's independently hosted review/PDF viewer, now retired: the default
// is '' so no external link is emitted. Set it in the private configuration only if
// that service is ever revived.
defined('LPDJ_LEGACY_REVIEW_URL') || define('LPDJ_LEGACY_REVIEW_URL', '');
require_once __DIR__ . '/includes/private-files.php';
require_once __DIR__ . '/includes/accounts.php';
require_once __DIR__ . '/includes/problems.php';
require_once __DIR__ . '/includes/admin-alerts.php';
require_once __DIR__ . '/includes/assets.php';
require_once __DIR__ . '/includes/import.php';
require_once __DIR__ . '/includes/references.php';
require_once __DIR__ . '/includes/figures.php';

function lpdj_activate() {
    add_role('lpdj_member', 'Member', ['read' => true]);
    update_option('users_can_register', 0); // Registration goes through email verification below.
}
register_activation_hook(__FILE__, 'lpdj_activate');
add_action('init', function () {
    foreach (['lpdj_problem', 'lpdj_asset', 'lpdj_history'] as $type) {
        register_post_type($type, ['public' => false, 'show_ui' => false, 'show_in_rest' => false,
            'exclude_from_search' => true, 'supports' => []]);
    }
});
function lpdj_error($message, $status = 400) { return new WP_Error('lpdj_error', $message, ['status' => $status]); }
function lpdj_admin() { return current_user_can('manage_options'); }
function lpdj_member() {
    return is_user_logged_in() && get_user_meta(get_current_user_id(), '_lpdj_verification', true) !== 'pending'
        ? true : lpdj_error('Sign in with a confirmed email address.', 401);
}
function lpdj_admin_permission() { return lpdj_member() === true && lpdj_admin() ? true : lpdj_error('Administrator access required.', 403); }
function lpdj_local() { return defined('LPDJ_LOCAL_PREVIEW') && LPDJ_LOCAL_PREVIEW && wp_get_environment_type() === 'local'; }
function lpdj_route($path, $methods, $callback, $permission = 'lpdj_member') {
    register_rest_route('lpdj/v1', $path, ['methods' => $methods, 'callback' => $callback, 'permission_callback' => $permission]);
}
add_action('profile_update', 'lpdj_catalogue_changed');
add_action('deleted_user', 'lpdj_catalogue_changed');
add_action('rest_api_init', function () {
    lpdj_route('/session', 'GET', 'lpdj_session', '__return_true');
    foreach (['register','login','verify','resend','forgot','reset'] as $action) {
        lpdj_route('/auth/' . $action, 'POST', 'lpdj_auth_' . $action, 'lpdj_public_form');
    }
    lpdj_route('/auth/logout', 'POST', function () { wp_logout(); return ['ok' => true]; });
    lpdj_route('/profile', 'POST', 'lpdj_profile_save');
    lpdj_route('/account', 'DELETE', 'lpdj_account_delete');
    lpdj_route('/problems', 'GET', 'lpdj_problems_list');
    lpdj_route('/problems', 'POST', 'lpdj_problem_create');
    lpdj_route('/problems/(?P<id>\d+)', 'GET', 'lpdj_problem_get');
    lpdj_route('/problems/(?P<id>\d+)', 'POST', 'lpdj_problem_save');
    lpdj_route('/problems/(?P<id>\d+)', 'DELETE', 'lpdj_problem_delete');
    lpdj_route('/problems/(?P<id>\d+)/history', 'GET', 'lpdj_problem_history');
    lpdj_route('/problems/(?P<id>\d+)/progress', 'POST', 'lpdj_progress_save');
    lpdj_route('/problems/(?P<id>\d+)/triage', 'POST', 'lpdj_triage_save', 'lpdj_admin_permission');
    lpdj_route('/problems/(?P<id>\d+)/reference', 'GET', 'lpdj_problem_reference', 'lpdj_admin_permission');
    lpdj_route('/assets', 'POST', 'lpdj_asset_upload');
    lpdj_route('/problems/(?P<id>\d+)/assets/(?P<name>[A-Za-z0-9][A-Za-z0-9_.-]{0,104})', 'DELETE', 'lpdj_asset_detach');
    lpdj_route('/figures', 'GET', 'lpdj_figures_list', 'lpdj_admin_permission');
    lpdj_route('/problems/(?P<id>\d+)/figures', 'POST', 'lpdj_figure_attach', 'lpdj_admin_permission');
    lpdj_route('/mailbox', 'GET', function () { return array_reverse(get_option('_lpdj_local_mail', [])); }, function () {
        return lpdj_local() && lpdj_admin_permission() === true ? true : lpdj_error('Unavailable.', 404);
    });
});
// Member responses and email links must never be stored in a shared cache.
add_filter('rest_post_dispatch', function ($response, $server, $request) {
    if (str_starts_with($request->get_route(), '/lpdj/')) {
        $response->header('Cache-Control', 'private, no-store, max-age=0');
        $response->header('X-Content-Type-Options', 'nosniff');
    }
    return $response;
}, 10, 3);
add_action('admin_init', function () {
    if (!wp_doing_ajax() && !lpdj_admin()) { wp_safe_redirect(home_url('/')); exit; }
});
add_filter('show_admin_bar', '__return_false');
add_action('admin_menu', function () {
    add_menu_page('Flexagon', 'Problems', 'manage_options', 'lpdj', function () {
        echo '<div class="wrap"><h1>Flexagon</h1><p><a class="button button-primary" href="' . esc_url(home_url('/#/administration')) . '">Open admin review</a></p></div>';
    }, 'dashicons-welcome-learn-more');
});
