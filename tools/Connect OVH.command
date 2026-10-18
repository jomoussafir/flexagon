#!/bin/zsh
# Open the Mac's built-in SFTP client. Passwords are read by OpenSSH, never saved
# in this project or exposed to the assistant. A private, temporary control socket
# lets subsequent catalogue-transfer commands reuse this authenticated connection.
set -eu
transfer_root="$(cd "$(dirname "$0")/.." && pwd)"
transfer_dir="$transfer_root/.local/ovh-sftp"
umask 077
mkdir -p "$transfer_dir"
chmod 700 "$transfer_dir"
printf '\nFlexagon — OVH file transfer\n\n'
printf 'Enter the SFTP password you created in OVH. Nothing appears while typing.\n'
printf 'Once you see sftp>, leave this window open and return to Codex.\n\n'
/usr/bin/sftp -S "$transfer_root/tools/ovh-sftp-ssh.sh" \
  -o ControlMaster=auto \
  -o ControlPersist=no \
  -o "ControlPath=$transfer_dir/control" \
  -o "UserKnownHostsFile=$transfer_dir/known_hosts" \
  -o StrictHostKeyChecking=ask \
  -o UpdateHostKeys=no \
  -o PreferredAuthentications=keyboard-interactive,password \
  -o PubkeyAuthentication=no \
  -o IdentityAgent=none \
  -o IdentityFile=none \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -o ConnectTimeout=20 \
  -P 2222 00950f03e7@00950f03e7-sftp.0ea.mcms.ovh.net
