<?php
defined('ABSPATH') || exit;

// Source PDFs live outside the document root, never in public uploads or the theme.
function lpdj_reference_library() {
    static $library = null;
    if ($library !== null) return $library;
    $library = [];
    if (!defined('LPDJ_REFERENCE_DIR')) return $library;
    $file = rtrim(LPDJ_REFERENCE_DIR, '/\\') . '/manifest.json';
    if (!is_readable($file)) return $library;
    foreach (json_decode(file_get_contents($file), true) ?: [] as $source) {
        if (is_array($source) && preg_match('/^[a-z0-9-]{1,100}$/D', $source['id'] ?? '')) $library[$source['id']] = $source;
    }
    return $library;
}
function lpdj_problem_references($legacy) {
    $references = [];
    foreach (($legacy['occurrences'] ?? []) as $index => $occurrence) {
        $page = filter_var($occurrence['pdf_page'] ?? null, FILTER_VALIDATE_INT);
        $source = $occurrence['source_id'] ?? '';
        if (!$page || $page < 1 || !preg_match('/^[a-z0-9-]{1,100}$/D', $source)) continue;
        $description = $legacy['sources'][$index] ?? [];
        $references[] = ['index'=>$index, 'sourceId'=>$source, 'title'=>$description['title'] ?? $source,
            'number'=>(string) ($occurrence['number'] ?? $description['number'] ?? ''), 'page'=>$page,
            'printedPage'=>(string) ($occurrence['printed_page'] ?? '')];
    }
    return $references;
}
function lpdj_reference_part($source_id, $page) {
    $source = lpdj_reference_library()[$source_id] ?? null;
    if (!$source) return lpdj_error('This reference PDF is not installed in the private library.', 404);
    if ($page < 1 || $page > ($source['pages'] ?? 0)) return lpdj_error('Reference page not found.', 404);
    foreach ($source['parts'] ?? [] as $part) {
        if ($page < $part['start'] || $page > $part['end']) continue;
        $name = $part['file'] ?? '';
        if (!preg_match('/^[a-zA-Z0-9][a-zA-Z0-9_.-]*\.pdf$/D', $name)) break;
        $root = realpath(LPDJ_REFERENCE_DIR);
        $file = $root ? realpath($root . '/' . $name) : false;
        if (!$file || !str_starts_with($file, $root . DIRECTORY_SEPARATOR) || !is_file($file) || !is_readable($file)) break;
        return ['source'=>$source, 'file'=>$file, 'name'=>$name, 'pageInFile'=>$page - $part['start'] + 1,
            'start'=>$part['start'], 'end'=>$part['end']];
    }
    return lpdj_error('Reference PDF file not found.', 404);
}
function lpdj_reference_url($source_id, $page) {
    return add_query_arg(['action'=>'lpdj_reference', 'source'=>$source_id, 'page'=>$page], admin_url('admin-ajax.php'));
}
function lpdj_problem_reference($r) {
    $post = lpdj_problem_post($r['id']);
    if (!$post) return lpdj_error('Problem not found.', 404);
    $refs = lpdj_problem_references(get_post_meta($post->ID, '_lpdj_legacy', true));
    $index = filter_var($r['index'] ?? 0, FILTER_VALIDATE_INT);
    $ref = null;
    if ($index !== false && $index >= 0) foreach ($refs as $item) if ($item['index'] === $index) $ref = $item;
    if (!$ref) return lpdj_error('This problem has no matching reference PDF.', 404);
    $page = filter_var($r['page'] ?? $ref['page'], FILTER_VALIDATE_INT);
    if ($page === false || $page < 1) return lpdj_error('Choose a valid PDF page.');
    $part = lpdj_reference_part($ref['sourceId'], $page);
    if (is_wp_error($part)) return $part;
    return array_merge($ref, ['page'=>$page, 'originalPage'=>$ref['page'], 'totalPages'=>$part['source']['pages'],
        'pageInFile'=>$part['pageInFile'], 'partStart'=>$part['start'], 'partEnd'=>$part['end'],
        'url'=>lpdj_reference_url($ref['sourceId'], $part['start'])]);
}
function lpdj_reference_serve() {
    if (lpdj_admin_permission() !== true) { status_header(is_user_logged_in() ? 403 : 401); nocache_headers(); exit; }
    $source = $_GET['source'] ?? '';
    $page = filter_var($_GET['page'] ?? 1, FILTER_VALIDATE_INT);
    if (!is_string($source) || !preg_match('/^[a-z0-9-]{1,100}$/D', $source) || $page === false || $page < 1) { status_header(400); exit; }
    $part = lpdj_reference_part($source, $page);
    if (is_wp_error($part)) { status_header(404); exit; }
    header('Content-Type: application/pdf');
    header('Content-Disposition: inline; filename="' . $part['name'] . '"');
    header('Content-Length: ' . filesize($part['file']));
    header('Cache-Control: private, no-store, max-age=0');
    header('X-Content-Type-Options: nosniff');
    header("Content-Security-Policy: default-src 'none'; sandbox");
    readfile($part['file']); exit;
}
add_action('wp_ajax_lpdj_reference', 'lpdj_reference_serve');
add_action('wp_ajax_nopriv_lpdj_reference', 'lpdj_reference_serve');
