<?php
defined('ABSPATH') || exit;

function lpdj_asset_url($id) { return add_query_arg(['action' => 'lpdj_asset', 'id' => absint($id)], admin_url('admin-ajax.php')); }
function lpdj_clean_svg($content) {
    if (preg_match('/<!DOCTYPE|<!ENTITY|<\?/i', $content)) return lpdj_error('SVG : retirez les déclarations XML, entités et DOCTYPE.');
    $doc = new DOMDocument();
    $previous = libxml_use_internal_errors(true);
    $loaded = $doc->loadXML($content, LIBXML_NONET | LIBXML_NOBLANKS);
    libxml_clear_errors(); libxml_use_internal_errors($previous);
    if (!$loaded || $doc->documentElement->localName !== 'svg') return lpdj_error('Fichier SVG invalide.');
    $tags = ['svg','g','path','rect','circle','ellipse','line','polyline','polygon','text','tspan','defs','clipPath','mask','linearGradient','radialGradient','stop','title','desc','use'];
    $attrs = ['xmlns','xmlns:xlink','width','height','viewBox','version','id','d','x','y','x1','y1','x2','y2','cx','cy','r','rx','ry','points','transform','fill','fill-rule','fill-opacity','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-miterlimit','stroke-dasharray','stroke-dashoffset','stroke-opacity','opacity','clip-path','clip-rule','mask','font-family','font-size','font-weight','font-style','text-anchor','dominant-baseline','dx','dy','offset','stop-color','stop-opacity','gradientUnits','gradientTransform','spreadMethod','href','xlink:href','preserveAspectRatio'];
    foreach ($doc->getElementsByTagName('*') as $node) {
        if (!in_array($node->tagName, $tags, true)) return lpdj_error('SVG non pris en charge : ' . $node->tagName . '. Exportez en SVG simple (formes et tracés).');
        if ($node->namespaceURI && $node->namespaceURI !== 'http://www.w3.org/2000/svg') return lpdj_error('Espace de noms SVG interdit.');
        foreach ($node->attributes as $attribute) {
            $name = $attribute->nodeName; $value = $attribute->nodeValue;
            if (!in_array($name, $attrs, true)) return lpdj_error('Attribut SVG non pris en charge : ' . $name . '. Exportez en SVG simple sans styles CSS.');
            if (in_array($name, ['href','xlink:href'], true) && !preg_match('/^#[A-Za-z_][\w.-]*$/D', $value)) return lpdj_error('Les liens externes dans les SVG ne sont pas autorisés.');
            if (stripos($value, 'url') !== false && !preg_match('/^url\(#[A-Za-z_][\w.-]*\)$/D', trim($value))) return lpdj_error('Les ressources externes dans les SVG ne sont pas autorisées.');
            if (preg_match('/javascript:|data:|expression\s*\(|[<>]/i', $value)) return lpdj_error('Contenu SVG non autorisé.');
        }
    }
    return $doc->saveXML($doc->documentElement);
}
function lpdj_asset_upload($r) {
    if (($t = lpdj_throttle('upload', 40)) !== true) return $t;
    $id = absint($r['problem']); $post = $id ? lpdj_problem_post($id) : null;
    if ($id && !lpdj_can_edit($post)) return lpdj_error('Accès refusé.', 403);
    $file = $r->get_file_params()['file'] ?? null;
    if (!$file || $file['error'] !== UPLOAD_ERR_OK || !is_uploaded_file($file['tmp_name'])) return lpdj_error('Téléversement impossible.');
    if ($file['size'] > 2 * 1024 * 1024) return lpdj_error('Chaque image doit peser au maximum 2 Mo.');
    $name = sanitize_file_name($file['name']); $extension = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    if (!preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.(svg|png|jpe?g)$/iD', $name)) return lpdj_error('Utilisez un nom court sans espaces : figure-1.svg, .png ou .jpg.');
    $content = file_get_contents($file['tmp_name']);
    if ($extension === 'svg') {
        $content = lpdj_clean_svg($content); if (is_wp_error($content)) return $content;
        $mime = 'image/svg+xml';
    } else {
        $info = @getimagesizefromstring($content);
        $mime = $info['mime'] ?? '';
        if (!in_array($mime, ['image/png','image/jpeg'], true) || !$info || $info[0] > 8000 || $info[1] > 8000 || ($mime === 'image/png') !== ($extension === 'png')) return lpdj_error('Image PNG/JPEG invalide ou trop grande (8 000 px maximum).');
    }
    if (count(get_posts(['post_type' => 'lpdj_asset', 'post_status' => 'private', 'author' => get_current_user_id(), 'posts_per_page' => 201, 'fields' => 'ids'])) >= 200) return lpdj_error('Limite de 200 images par compte atteinte. Contactez un administrateur.');
    if ($id && !lpdj_lock($id)) return lpdj_error('Une sauvegarde est en cours. Réessayez.', 409);
    try {
        $draft = $id ? lpdj_draft($post) : null;
        if ($id && (int) $r['revision'] !== (int) $draft['revision']) return lpdj_error('Ce problème a été modifié ailleurs. Rechargez la page avant d’ajouter une figure.', 409);
        if ($id && (count($draft['assets']) >= 20 || isset($draft['assets'][$name]))) return lpdj_error('Utilisez un nouveau nom de fichier ; maximum 20 figures par problème.');
        $asset_id = wp_insert_post(wp_slash(['post_type' => 'lpdj_asset', 'post_status' => 'private', 'post_author' => get_current_user_id(), 'post_parent' => $id,
            'post_title' => $name, 'post_content' => wp_json_encode(['mime' => $mime, 'data' => base64_encode($content)])]), true);
        if (is_wp_error($asset_id)) return lpdj_error('Enregistrement de la figure impossible.', 500);
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
