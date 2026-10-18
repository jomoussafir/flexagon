#!/bin/zsh
# sftp prepends ControlMaster=no. This transport wrapper puts the required
# connection-sharing option first, as OpenSSH uses the first supplied value.
set -eu
exec /usr/bin/ssh -o ControlMaster=auto "$@"
