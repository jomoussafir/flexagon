<?php
defined('ABSPATH') || exit;

const LPDJ_ASSET_LIMIT = 2 * 1024 * 1024;
function lpdj_asset_url($id, $format = '') {
    $args = ['action' => 'lpdj_asset', 'id' => absint($id)];
    if ($format) $args['format'] = $format;
    return add_query_arg($args, admin_url('admin-ajax.php'));
}
// A PDF figure keeps its vector master and is displayed through a preview image
// (the traced SVG of a library figure, or a browser-rendered PNG for an upload).
function lpdj_asset_present($asset) {
    $asset['url'] = lpdj_asset_url($asset['id']);
    if (($asset['mime'] ?? '') === 'application/pdf') $asset['pdf'] = lpdj_asset_url($asset['id'], 'pdf');
    return $asset;
}
function lpdj_clean_svg($content) {
    if (preg_match('/<!DOCTYPE|<!ENTITY|<\?/i', $content)) return lpdj_error('SVG: remove XML declarations, entities and DOCTYPE.');
    $doc = new DOMDocument();
    $previous = libxml_use_internal_errors(true);
    $loaded = $doc->loadXML($content, LIBXML_NONET | LIBXML_NOBLANKS);
    libxml_clear_errors(); libxml_use_internal_errors($previous);
    if (!$loaded || $doc->documentElement->localName !== 'svg') return lpdj_error('Invalid SVG file.');
    $tags = ['svg','g','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','defs','clipPath','mask','linearGradient','radialGradient','stop','title','desc','use'];
    $attrs = ['role','aria-label','aria-labelledby','aria-describedby','xmlns','xmlns:xlink','width','height','viewBox','version','id','d','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','points','transform','fill','fill-rule','fill-opacity','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-miterlimit','stroke-dasharray','stroke-dashoffset','stroke-opacity','opacity','clip-path','clip-rule','mask','font-family','font-size','font-weight','font-style','text-anchor','dominant-baseline','dx','dy','offset','stop-color','stop-opacity','gradientUnits','gradientTransform','spreadMethod','href','xlink:href','preserveAspectRatio'];
    foreach ($doc->getElementsByTagName('*') as $node) {
        if (!in_array($node->tagName, $tags, true)) return lpdj_error('Unsupported SVG element: ' . $node->tagName . '. Export as plain SVG (shapes and paths).');
        if ($node->namespaceURI && $node->namespaceURI !== 'http://www.w3.org/2000/svg') return lpdj_error('Unsupported SVG namespace.');
        foreach ($node->attributes as $attribute) {
            $name = $attribute->nodeName; $value = $attribute->nodeValue;
            if (!in_array($name, $attrs, true)) return lpdj_error('Unsupported SVG attribute: ' . $name . '. Export as plain SVG without CSS styles.');
            if (in_array($name, ['href','xlink:href'], true) && !preg_match('/^#[A-Za-z_][\w.-]*$/D', $value)) return lpdj_error('External links are not allowed in SVGs.');
            if (stripos($value, 'url') !== false && !preg_match('/^url\(#[A-Za-z_][\w.-]*\)$/D', trim($value))) return lpdj_error('External resources are not allowed in SVGs.');
            if (preg_match('/javascript:|data:|expression\s*\(|[<>]/i', $value)) return lpdj_error('Unsupported SVG content.');
        }
    }
    return $doc->saveXML($doc->documentElement);
}
// Figures are static drawings: a PDF with actions, scripts or attachments is refused.
// Only object dictionaries are scanned; compressed stream bytes may contain anything.
// The PDF is still served under a sandboxing CSP, only to authenticated members.
function lpdj_check_pdf($content) {
    if (!str_starts_with($content, '%PDF-')) return lpdj_error('Invalid PDF file.');
    $objects = preg_replace('~stream\r?\n.*?endstream~s', '', $content);
    if (preg_match('~/(JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|RichMedia|URI)\b~', $objects)) return lpdj_error('PDF figures must not contain scripts, actions, links or embedded files.');
    return true;
}
function lpdj_check_raster($content) {
    $info = @getimagesizefromstring($content);
    $mime = $info['mime'] ?? '';
    if (!in_array($mime, ['image/png','image/jpeg'], true) || !$info || $info[0] > 8000 || $info[1] > 8000) return lpdj_error('Invalid PNG/JPEG image or dimensions exceed 8,000 pixels.');
    return $mime;
}
function lpdj_asset_upload($r) {
    if (($t = lpdj_throttle('upload', 40)) !== true) return $t;
    $id = absint($r['problem']); $post = $id ? lpdj_problem_post($id) : null;
    if ($id && !lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    $file = $r->get_file_params()['file'] ?? null;
    if (!$file || $file['error'] !== UPLOAD_ERR_OK || !is_uploaded_file($file['tmp_name'])) return lpdj_error('Upload failed.');
    if ($file['size'] > LPDJ_ASSET_LIMIT) return lpdj_error('Each figure must be no larger than 2 MB.');
    $name = sanitize_file_name($file['name']); $extension = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    if (!preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.(svg|png|jpe?g|pdf)$/iD', $name)) return lpdj_error('Use a short filename without spaces: figure-1.svg, .png, .jpg or .pdf.');
    $content = file_get_contents($file['tmp_name']);
    if ($extension === 'svg') {
        $content = lpdj_clean_svg($content); if (is_wp_error($content)) return $content;
        $record = ['mime' => 'image/svg+xml', 'data' => base64_encode($content)];
    } elseif ($extension === 'pdf') {
        if (!$id) return lpdj_error('Profile images must be SVG, PNG or JPEG.');
        $check = lpdj_check_pdf($content); if (is_wp_error($check)) return $check;
        $preview = $r->get_file_params()['preview'] ?? null;
        if (!$preview || $preview['error'] !== UPLOAD_ERR_OK || !is_uploaded_file($preview['tmp_name']) || $preview['size'] > LPDJ_ASSET_LIMIT) return lpdj_error('A PDF figure needs its rendered preview image.');
        $view = file_get_contents($preview['tmp_name']);
        if (str_starts_with(ltrim($view), '<')) {
            $view = lpdj_clean_svg($view); if (is_wp_error($view)) return $view;
            $view_mime = 'image/svg+xml';
        } else {
            $view_mime = lpdj_check_raster($view); if (is_wp_error($view_mime)) return $view_mime;
        }
        $record = ['mime' => 'application/pdf', 'data' => base64_encode($content), 'preview' => ['mime' => $view_mime, 'data' => base64_encode($view)]];
    } else {
        $mime = lpdj_check_raster($content); if (is_wp_error($mime)) return $mime;
        if (($mime === 'image/png') !== ($extension === 'png')) return lpdj_error('The file extension does not match the image type.');
        $record = ['mime' => $mime, 'data' => base64_encode($content)];
    }
    return lpdj_asset_store($post, (int) $r['revision'], $name, $record);
}
// Shared by uploads and library figures: one protected record per figure, attached
// to the draft under its filename and bumping the revision like any other edit.
// With $replace, an existing figure of that name is refreshed from the new record
// (a library figure redrawn since it was attached). A copy still shown by the
// published snapshot is left untouched; the draft then points to a new record.
function lpdj_asset_store($post, $revision, $name, $record, $replace = false) {
    $id = $post ? $post->ID : 0;
    if (count(get_posts(['post_type' => 'lpdj_asset', 'post_status' => 'private', 'author' => get_current_user_id(), 'posts_per_page' => 201, 'fields' => 'ids'])) >= 200) return lpdj_error('The limit of 200 images per account has been reached. Contact an administrator.');
    if ($id && !lpdj_lock($id)) return lpdj_error('A save is in progress. Please try again.', 409);
    try {
        $draft = $id ? lpdj_draft($post) : null;
        if ($id && $revision !== (int) $draft['revision']) return lpdj_error('This problem was changed elsewhere. Reload before adding a figure.', 409);
        $existing = $id ? ($draft['assets'][$name]['id'] ?? 0) : 0;
        if ($existing && $replace) {
            $published = get_post_meta($id, '_lpdj_published', true);
            $kept = false;
            foreach (($published['assets'] ?? []) as $entry) if ((int) $entry['id'] === (int) $existing) $kept = true;
            if (!$kept) {
                $updated = wp_update_post(wp_slash(['ID' => $existing, 'post_content' => wp_json_encode($record)]), true);
                if (is_wp_error($updated)) return lpdj_error('Could not refresh the figure.', 500);
                $draft['assets'][$name] = ['id' => (int) $existing, 'mime' => $record['mime']]; $draft['revision']++;
                lpdj_json_meta($id, '_lpdj_draft', $draft); lpdj_catalogue_changed();
                return ['name' => $name, 'asset' => lpdj_asset_present($draft['assets'][$name]), 'revision' => $draft['revision'], 'replaced' => true];
            }
            unset($draft['assets'][$name]);
        }
        if ($id && (count($draft['assets']) >= 20 || isset($draft['assets'][$name]))) return lpdj_error('Use a new filename; maximum 20 figures per problem.');
        $asset_id = wp_insert_post(wp_slash(['post_type' => 'lpdj_asset', 'post_status' => 'private', 'post_author' => get_current_user_id(), 'post_parent' => $id,
            'post_title' => $name, 'post_content' => wp_json_encode($record)]), true);
        if (is_wp_error($asset_id)) return lpdj_error('Could not save the figure.', 500);
        $asset = ['id' => $asset_id, 'mime' => $record['mime']];
        if ($id) { $draft['assets'][$name] = $asset; $draft['revision']++; lpdj_json_meta($id, '_lpdj_draft', $draft); lpdj_catalogue_changed(); }
        return ['name' => $name, 'asset' => lpdj_asset_present($asset), 'revision' => $id ? $draft['revision'] : null];
    } finally { if ($id) delete_option('_lpdj_lock_' . $id); }
}
// Detach a figure from a draft. The record is deleted unless the published snapshot
// still shows it; the statement keeps any \includegraphics line for the author to edit.
function lpdj_asset_detach($r) {
    $post = lpdj_problem_post($r['id']);
    if (!lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    $name = (string) $r['name'];
    if (!lpdj_lock($post->ID)) return lpdj_error('A save is in progress. Please try again.', 409);
    try {
        $draft = lpdj_draft($post);
        if ((int) $r['revision'] !== (int) $draft['revision']) return lpdj_error('This problem was changed elsewhere. Reload before removing a figure.', 409);
        if (!isset($draft['assets'][$name])) return lpdj_error('This figure is not attached.', 404);
        $asset_id = (int) $draft['assets'][$name]['id'];
        unset($draft['assets'][$name]); $draft['revision']++;
        lpdj_json_meta($post->ID, '_lpdj_draft', $draft);
        $kept = false;
        foreach ((get_post_meta($post->ID, '_lpdj_published', true)['assets'] ?? []) as $entry) if ((int) $entry['id'] === $asset_id) $kept = true;
        if (!$kept) wp_delete_post($asset_id, true);
        lpdj_catalogue_changed();
        return ['name' => $name, 'revision' => $draft['revision']];
    } finally { delete_option('_lpdj_lock_' . $post->ID); }
}
function lpdj_asset_serve() {
    $asset = get_post(absint($_GET['id'] ?? 0));
    if (!$asset || $asset->post_type !== 'lpdj_asset') { status_header(404); exit; }
    // A figure is served to its owner and administrators; otherwise only if it belongs to a
    // published problem, which makes published figures readable by anonymous visitors too.
    $allowed = lpdj_admin() || (is_user_logged_in() && (int) $asset->post_author === get_current_user_id());
    if (!$allowed && $asset->post_parent) {
        $pub = get_post_meta($asset->post_parent, '_lpdj_published', true);
        foreach (($pub['assets'] ?? []) as $entry) if ((int) $entry['id'] === $asset->ID) $allowed = true;
    }
    if (!$allowed) { status_header(403); exit; }
    $data = json_decode($asset->post_content, true);
    if (($_GET['format'] ?? '') === 'pdf') {
        if (($data['mime'] ?? '') !== 'application/pdf') { status_header(404); exit; }
        $view = $data;
    } else $view = $data['preview'] ?? $data;
    header('Content-Type: ' . $view['mime']); header('Content-Disposition: inline; filename="' . sanitize_file_name($asset->post_title) . '"');
    header('Cache-Control: private, no-store'); header('X-Content-Type-Options: nosniff');
    header("Content-Security-Policy: default-src 'none'; style-src 'none'; sandbox");
    echo base64_decode($view['data']); exit;
}
add_action('wp_ajax_lpdj_asset', 'lpdj_asset_serve');
add_action('wp_ajax_nopriv_lpdj_asset', 'lpdj_asset_serve');
