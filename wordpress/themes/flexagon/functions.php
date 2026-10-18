<?php
defined('ABSPATH') || exit;
add_action('after_setup_theme', function () { add_theme_support('title-tag'); add_theme_support('html5', ['style', 'script']); });
add_action('wp_enqueue_scripts', function () {
    $path = get_template_directory_uri();
    wp_enqueue_style('lpdj-katex', $path . '/assets/katex/katex.min.css', [], '0.16');
    wp_enqueue_style('lpdj-web', $path . '/assets/app.css', [], filemtime(get_template_directory() . '/assets/app.css'));
    wp_enqueue_script('lpdj-web', $path . '/assets/app.js', [], filemtime(get_template_directory() . '/assets/app.js'), true);
    wp_add_inline_script('lpdj-web', 'window.LPDJ=' . wp_json_encode([
        'api' => rest_url('lpdj/v1/'), 'logo' => $path . '/assets/logo.png',
        'pdfAssets' => $path . '/assets/pdfjs/',
        'session' => function_exists('lpdj_session') ? lpdj_session() : null,
    ]) . ';', 'before');
});
add_action('template_redirect', function () {
    nocache_headers();
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: same-origin');
    header('X-Frame-Options: SAMEORIGIN');
});
