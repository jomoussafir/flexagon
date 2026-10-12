<?php
defined('ABSPATH') || exit;

function lpdj_asset_url($id) { return add_query_arg(['action' => 'lpdj_asset', 'id' => absint($id)], admin_url('admin-ajax.php')); }
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
function lpdj_asset_upload($r) {
    if (($t = lpdj_throttle('upload', 40)) !== true) return $t;
    $id = absint($r['problem']); $post = $id ? lpdj_problem_post($id) : null;
    if ($id && !lpdj_can_edit($post)) return lpdj_error('Access denied.', 403);
    $file = $r->get_file_params()['file'] ?? null;
    if (!$file || $file['error'] !== UPLOAD_ERR_OK || !is_uploaded_file($file['tmp_name'])) return lpdj_error('Upload failed.');
    if ($file['size'] > 2 * 1024 * 1024) return lpdj_error('Each image must be no larger than 2 MB.');
    $name = sanitize_file_name($file['name']); $extension = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    if (!preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.(svg|png|jpe?g)$/iD', $name)) return lpdj_error('Use a short filename without spaces: figure-1.svg, .png or .jpg.');
    $content = file_get_contents($file['tmp_name']);
    if ($extension === 'svg') {
        $content = lpdj_clean_svg($content); if (is_wp_error($content)) return $content;
        $mime = 'image/svg+xml';
    } else {
        $info = @getimagesizefromstring($content);
        $mime = $info['mime'] ?? '';
        if (!in_array($mime, ['image/png','image/jpeg'], true) || !$info || $info[0] > 8000 || $info[1] > 8000 || ($mime === 'image/png') !== ($extension === 'png')) return lpdj_error('Invalid PNG/JPEG image or dimensions exceed 8,000 pixels.');
    }
    if (count(get_posts(['post_type' => 'lpdj_asset', 'post_status' => 'private', 'author' => get_current_user_id(), 'posts_per_page' => 201, 'fields' => 'ids'])) >= 200) return lpdj_error('The limit of 200 images per account has been reached. Contact an administrator.');
    if ($id && !lpdj_lock($id)) return lpdj_error('A save is in progress. Please try again.', 409);
    try {
        $draft = $id ? lpdj_draft($post) : null;
        if ($id && (int) $r['revision'] !== (int) $draft['revision']) return lpdj_error('This problem was changed elsewhere. Reload before adding a figure.', 409);
        if ($id && (count($draft['assets']) >= 20 || isset($draft['assets'][$name]))) return lpdj_error('Use a new filename; maximum 20 figures per problem.');
        $asset_id = wp_insert_post(wp_slash(['post_type' => 'lpdj_asset', 'post_status' => 'private', 'post_author' => get_current_user_id(), 'post_parent' => $id,
            'post_title' => $name, 'post_content' => wp_json_encode(['mime' => $mime, 'data' => base64_encode($content)])]), true);
        if (is_wp_error($asset_id)) return lpdj_error('Could not save the figure.', 500);
        $asset = ['id' => $asset_id, 'mime' => $mime];
        if ($id) { $draft['assets'][$name] = $asset; $draft['revision']++; lpdj_json_meta($id, '_lpdj_draft', $draft); }
        return ['name' => $name, 'asset' => $asset + ['url' => lpdj_asset_url($asset_id)], 'revision' => $id ? $draft['revision'] : null];
    } finally { if ($id) delete_option('_lpdj_lock_' . $id); }
}
function lpdj_asset_serve() {
    if (lpdj_member() !== true) { status_header(401); exit; }
    $asset = get_post(absint($_GET['id'] ?? 0));
    if (!$asset || $asset->post_type !== 'lpdj_asset') { status_header(404); exit; }
    $allowed = lpdj_admin() || (int) $asset->post_author === get_current_user_id();
    if (!$allowed && $asset->post_parent) {
        $pub = get_post_meta($asset->post_parent, '_lpdj_published', true);
        foreach (($pub['assets'] ?? []) as $entry) if ((int) $entry['id'] === $asset->ID) $allowed = true;
    }
    if (!$allowed) { status_header(403); exit; }
    $data = json_decode($asset->post_content, true);
    header('Content-Type: ' . $data['mime']); header('Content-Disposition: inline');
    header('Cache-Control: private, no-store'); header('X-Content-Type-Options: nosniff');
    header("Content-Security-Policy: default-src 'none'; style-src 'none'; sandbox");
    echo base64_decode($data['data']); exit;
}
add_action('wp_ajax_lpdj_asset', 'lpdj_asset_serve');
add_action('wp_ajax_nopriv_lpdj_asset', 'lpdj_asset_serve');
