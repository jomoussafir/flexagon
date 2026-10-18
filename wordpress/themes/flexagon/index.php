<!doctype html>
<html lang="en">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#233e68">
    <meta name="description" content="Read, submit and review mathematical problems.">
    <link rel="icon" href="<?php echo esc_url(get_template_directory_uri() . '/assets/favicon.png'); ?>">
    <link rel="apple-touch-icon" href="<?php echo esc_url(get_template_directory_uri() . '/assets/logo.png'); ?>">
    <?php wp_head(); ?>
</head>
<body>
<?php if (!function_exists('lpdj_session')) : ?>
<main class="container"><h1>Flexagon</h1><p>Activate the Flexagon plugin in WordPress administration.</p></main>
<?php else : ?>
<a class="skip-link" href="#main">Skip to content</a>
<div id="app"><main class="container"><p>Loading problems…</p></main></div>
<noscript>Enable JavaScript to read problems and use the forms.</noscript>
<div id="toast" role="status" aria-live="polite"></div>
<?php endif; wp_footer(); ?>
</body>
</html>
