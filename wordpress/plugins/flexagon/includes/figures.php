<?php
defined('ABSPATH') || exit;

// Vector figures of the scanned reference books: traced by tools/extract-figures.py,
// then redrawn cleanly by tools/redraw-figures.py. Only figures with a redrawing are
// offered. Like the books, the library is private and administrator-only: it is
// listed and previewed in the editor, and attaching a figure copies its PDF and SVG
// into a protected problem asset, so readers never touch the library itself.
function lpdj_figure_dir() {
    if (defined('LPDJ_FIGURE_DIR')) return LPDJ_FIGURE_DIR;
    return defined('LPDJ_REFERENCE_DIR') ? dirname(LPDJ_REFERENCE_DIR) . '/figures' : '';
}
function lpdj_figure_library() {
    static $library = null;
    if ($library !== null) return $library;
    $library = [];
    $dir = lpdj_figure_dir();
    if (!$dir) return $library;
    $manifest = lpdj_private_read($dir, 'manifest.json');
    if ($manifest === false) return $library;
    foreach ((json_decode($manifest, true)['figures'] ?? []) as $figure) {
        $files = $figure['redrawn'] ?? null;
        if (!is_array($figure) || !is_array($files) || !preg_match('/^[a-z0-9-]{1,80}$/D', $figure['id'] ?? '') || !preg_match('/^[a-z0-9-]{1,40}$/D', $files['dir'] ?? '')) continue;
        if (!preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]*\.pdf$/D', $files['pdf'] ?? '') || !preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]*\.svg$/D', $files['svg'] ?? '')) continue;
        if (!preg_match('/^[a-z0-9-]{1,40}$/D', $figure['source'] ?? '') || !is_int($figure['page'] ?? null) || !is_int($figure['index'] ?? null)) continue;
        $library[$figure['id']] = $figure;
    }
    return $library;
}
function lpdj_figure_read($figure, $format) {
    return lpdj_private_read(lpdj_figure_dir() . '/' . $figure['redrawn']['dir'], $figure['redrawn'][$format]);
}
function lpdj_figure_url($id, $format) {
    return add_query_arg(['action' => 'lpdj_figure', 'id' => $id, 'format' => $format], admin_url('admin-ajax.php'));
}
function lpdj_figure_item($figure) {
    return ['id' => $figure['id'], 'source' => $figure['source'], 'sourceId' => (string) ($figure['sourceId'] ?? ''),
        'sourceTitle' => (string) ($figure['sourceTitle'] ?? $figure['source']), 'page' => $figure['page'], 'index' => $figure['index'],
        'name' => $figure['id'] . '.pdf', 'width' => (float) ($figure['redrawn']['width'] ?? 0), 'height' => (float) ($figure['redrawn']['height'] ?? 0),
        'warnings' => array_values(array_filter((array) ($figure['warnings'] ?? []), 'is_string')),
        'url' => lpdj_figure_url($figure['id'], 'svg'), 'pdf' => lpdj_figure_url($figure['id'], 'pdf')];
}
// The first book page of the problem's source occurrences that has figures, if any.
function lpdj_figure_default_page($post) {
    $library = lpdj_figure_library();
    foreach (lpdj_problem_references(get_post_meta($post->ID, '_lpdj_legacy', true)) as $ref) {
        foreach ($library as $figure) {
            if (($figure['sourceId'] ?? '') === $ref['sourceId'] && $figure['page'] === $ref['page']) return [$figure['source'], $ref['page']];
        }
    }
    return null;
}
function lpdj_figures_list($r) {
    $library = lpdj_figure_library();
    $sources = [];
    foreach ($library as $figure) {
        $sources[$figure['source']] ??= ['slug' => $figure['source'], 'title' => (string) ($figure['sourceTitle'] ?? $figure['source']), 'pages' => []];
        $sources[$figure['source']]['pages'][$figure['page']] = true;
    }
    foreach ($sources as &$source) { $source['pages'] = array_keys($source['pages']); sort($source['pages']); }
    unset($source);
    $slug = sanitize_key((string) ($r['source'] ?? ''));
    $page = filter_var($r['page'] ?? null, FILTER_VALIDATE_INT) ?: 0;
    // On opening the gallery (default=1) start on the problem's own source page.
    $post = lpdj_problem_post($r['problem'] ?? 0);
    if ($post && !empty($r['default']) && !$slug && !$page && ($start = lpdj_figure_default_page($post))) [$slug, $page] = $start;
    $items = [];
    foreach ($library as $figure) {
        if ($slug && $figure['source'] !== $slug) continue;
        if ($page && $figure['page'] !== $page) continue;
        $items[] = lpdj_figure_item($figure);
    }
    return ['available' => (bool) $library, 'sources' => array_values($sources), 'source' => $slug, 'page' => $page ?: null,
        'figures' => array_slice($items, 0, 200), 'total' => count($items)];
}
function lpdj_figure_attach($r) {
    $post = lpdj_problem_post($r['id']);
    if (!$post) return lpdj_error('Problem not found.', 404);
    $figure = lpdj_figure_library()[(string) ($r['figure'] ?? '')] ?? null;
    if (!$figure) return lpdj_error('Unknown source figure.', 404);
    $pdf = lpdj_figure_read($figure, 'pdf');
    $svg = lpdj_figure_read($figure, 'svg');
    if ($pdf === false || $svg === false) return lpdj_error('This figure is missing from the private library.', 404);
    if (strlen($pdf) > LPDJ_ASSET_LIMIT || strlen($svg) > LPDJ_ASSET_LIMIT) return lpdj_error('This figure exceeds the 2 MB limit. Simplify it with the extraction tool first.');
    $check = lpdj_check_pdf($pdf); if (is_wp_error($check)) return $check;
    $svg = lpdj_clean_svg($svg); if (is_wp_error($svg)) return $svg;
    $record = ['mime' => 'application/pdf', 'data' => base64_encode($pdf), 'preview' => ['mime' => 'image/svg+xml', 'data' => base64_encode($svg)], 'library' => $figure['id']];
    return lpdj_asset_store($post, (int) $r['revision'], $figure['id'] . '.pdf', $record, true);
}
function lpdj_figure_serve() {
    if (lpdj_admin_permission() !== true) { status_header(is_user_logged_in() ? 403 : 401); nocache_headers(); exit; }
    $id = $_GET['id'] ?? ''; $format = $_GET['format'] ?? 'svg';
    $figure = is_string($id) ? (lpdj_figure_library()[$id] ?? null) : null;
    if (!$figure || !in_array($format, ['svg', 'pdf'], true)) { status_header(404); exit; }
    $content = lpdj_figure_read($figure, $format);
    if ($content === false) { status_header(404); exit; }
    if ($format === 'svg') { $content = lpdj_clean_svg($content); if (is_wp_error($content)) { status_header(415); exit; } }
    header('Content-Type: ' . ($format === 'pdf' ? 'application/pdf' : 'image/svg+xml'));
    header('Content-Disposition: inline; filename="' . $figure['id'] . '.' . $format . '"');
    header('Cache-Control: private, no-store'); header('X-Content-Type-Options: nosniff');
    header("Content-Security-Policy: default-src 'none'; style-src 'none'; sandbox");
    echo $content; exit;
}
add_action('wp_ajax_lpdj_figure', 'lpdj_figure_serve');
add_action('wp_ajax_nopriv_lpdj_figure', 'lpdj_figure_serve');
