<!doctype html>
<html lang="fr">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#f7f6f2">
    <meta name="description" content="Une communauté pour proposer, partager et résoudre des problèmes mathématiques.">
    <link rel="icon" href="<?php echo esc_url(get_template_directory_uri() . '/assets/favicon.png'); ?>">
    <link rel="apple-touch-icon" href="<?php echo esc_url(get_template_directory_uri() . '/assets/logo.png'); ?>">
    <?php wp_head(); ?>
</head>
<body>
<?php if (!function_exists('lpdj_session')) : ?>
<main class="container"><h1>Le Problème du Jour</h1><p>Activez le plugin « Le Problème du Jour » dans l’administration WordPress.</p></main>
<?php else : ?>
<a class="skip-link" href="#main">Aller au contenu</a>
<div id="app"><main class="container"><p>Chargement de la collection…</p></main></div>
<noscript>Activez JavaScript pour lire les problèmes et utiliser les formulaires.</noscript>
<div id="toast" role="status" aria-live="polite"></div>
<?php endif; wp_footer(); ?>
</body>
</html>
