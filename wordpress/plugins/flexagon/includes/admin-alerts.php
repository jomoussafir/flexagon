<?php
defined('ABSPATH') || exit;

function lpdj_admin_alert_preferences() {
    return wp_parse_args((array) get_option('lpdj_admin_email_alerts', []), ['user' => 1, 'submission' => 1]);
}
function lpdj_sanitize_admin_alert_preferences($value) {
    $value = is_array($value) ? $value : [];
    return ['user' => empty($value['user']) ? 0 : 1, 'submission' => empty($value['submission']) ? 0 : 1];
}
add_action('admin_init', function () {
    register_setting('general', 'lpdj_admin_email_alerts', [
        'type' => 'array', 'sanitize_callback' => 'lpdj_sanitize_admin_alert_preferences',
        'default' => ['user' => 1, 'submission' => 1],
    ]);
    add_settings_section('lpdj_admin_email_alerts', 'Flexagon — email alerts', function () {
        echo '<p>Send alerts to the administration email address configured above. Only future confirmations and submissions trigger an email.</p>';
    }, 'general');
    foreach (['user' => 'New users', 'submission' => 'Problems submitted for review'] as $kind => $label) {
        add_settings_field('lpdj_admin_alert_' . $kind, $label, function () use ($kind) {
            $preferences = lpdj_admin_alert_preferences();
            $label = $kind === 'user' ? 'Email me when a new user confirms their account.' : 'Email me when a problem is submitted or resubmitted for review.';
            echo '<input type="hidden" name="lpdj_admin_email_alerts[' . esc_attr($kind) . ']" value="0">';
            echo '<label><input type="checkbox" name="lpdj_admin_email_alerts[' . esc_attr($kind) . ']" value="1" ' . checked(!empty($preferences[$kind]), true, false) . '> ' . esc_html($label) . '</label>';
        }, 'general', 'lpdj_admin_email_alerts');
    }
});

// One record per user/problem bounds storage. A revision identifies each submission;
// a retry for an older revision must never replace or resend the latest alert.
function lpdj_admin_alert($kind, $id, $event = 0, $retry = false) {
    if (!in_array($kind, ['user', 'submission'], true)) return;
    $id = absint($id); $event = absint($event);
    $lock = '_lpdj_admin_alert_lock_' . $kind . '_' . $id;
    $existing_lock = (int) get_option($lock, 0);
    if ($existing_lock && $existing_lock < time() - 120) delete_option($lock);
    if (!add_option($lock, time(), '', false)) return;
    $meta_type = $kind === 'user' ? 'user' : 'post';
    $key = '_lpdj_admin_email_alert';
    try {
        $record = get_metadata($meta_type, $id, $key, true);
        if ($retry && (!$record || (int) $record['event'] !== $event || $record['status'] !== 'pending')) return;
        if (!$retry && $record && (int) $record['event'] >= $event) return;
        $record = $retry ? $record : ['event' => $event, 'attempts' => 0, 'status' => 'pending'];
        $preferences = lpdj_admin_alert_preferences();
        $recipient = sanitize_email(get_option('admin_email'));
        $subject = ''; $message = '';
        if ($kind === 'user') {
            $user = get_user_by('id', $id);
            if ($user && get_user_meta($id, '_lpdj_verification', true) === 'verified') {
                $subject = 'New confirmed user — Flexagon';
                $message = "A new user has confirmed their email address.\n\nDisplay name: {$user->display_name}\nEmail: {$user->user_email}\n\nView account (administrator sign-in required):\n" . admin_url('user-edit.php?user_id=' . $id);
            }
        } else {
            $post = lpdj_problem_post($id);
            $draft = $post ? get_post_meta($id, '_lpdj_draft', true) : null;
            if ($draft && $draft['state'] === 'submitted') {
                $subject = 'Problem submitted for review — ' . sanitize_text_field($post->post_title);
                $author = get_the_author_meta('display_name', $post->post_author) ?: 'Deleted account';
                $message = "A problem is ready for review.\n\nTitle: {$post->post_title}\nSubmitted by: $author\nCategory: {$draft['category']}\nDifficulty: {$draft['difficulty']}/5\nSource: {$draft['source']}\n\nReview the problem (administrator sign-in required):\n" . home_url('/#/editer/' . $id);
            }
        }
        if (empty($preferences[$kind]) || !$message) {
            $record['status'] = 'skipped';
            update_metadata($meta_type, $id, $key, $record);
            return;
        }
        $record['attempts']++;
        $sent = is_email($recipient) && wp_mail($recipient, $subject, $message);
        $record['status'] = $sent ? 'sent' : ($record['attempts'] >= 4 ? 'failed' : 'pending');
        update_metadata($meta_type, $id, $key, $record);
        $args = [$kind, $id, $event];
        if ($record['status'] === 'pending' && !wp_next_scheduled('lpdj_retry_admin_alert', $args)) {
            wp_schedule_single_event(time() + 10 * MINUTE_IN_SECONDS, 'lpdj_retry_admin_alert', $args);
        }
    } finally { delete_option($lock); }
}
add_action('lpdj_retry_admin_alert', function ($kind, $id, $event) {
    lpdj_admin_alert($kind, $id, $event, true);
}, 10, 3);
