<?php
defined('ABSPATH') || exit;

// Managed hosts may expose only the WordPress directory over SFTP. Their private
// library contains authenticated ciphertext, not publicly readable books/data.
// The dedicated key is in an ABSPATH-guarded PHP configuration outside the plugin
// package. Keep both the key and encrypted files in hosting backups.
function lpdj_private_encrypted() {
    return defined('LPDJ_PRIVATE_FILE_KEY') && LPDJ_PRIVATE_FILE_KEY !== '';
}
function lpdj_private_path($root, $name) {
    if (!is_string($name) || !preg_match('/^[A-Za-z0-9][A-Za-z0-9_.-]*$/D', $name)) return false;
    $root = realpath($root);
    if (!$root) return false;
    $file = realpath($root . DIRECTORY_SEPARATOR . $name . (lpdj_private_encrypted() ? '.lpdj' : ''));
    return $file && dirname($file) === $root && is_file($file) && is_readable($file) ? $file : false;
}
function lpdj_private_decrypt($payload, $name) {
    $key = base64_decode(LPDJ_PRIVATE_FILE_KEY, true);
    if (!$key || strlen($key) !== 32 || strlen($payload) < 36 || substr($payload, 0, 8) !== 'LPDJENC1' || !function_exists('openssl_decrypt')) return false;
    return openssl_decrypt(substr($payload, 36), 'aes-256-gcm', $key, OPENSSL_RAW_DATA,
        substr($payload, 8, 12), substr($payload, 20, 16), 'LPDJENC1:' . $name);
}
function lpdj_private_read($root, $name) {
    $file = lpdj_private_path($root, $name);
    if (!$file) return false;
    $data = file_get_contents($file);
    if ($data === false) return false;
    return lpdj_private_encrypted() ? lpdj_private_decrypt($data, $name) : $data;
}
