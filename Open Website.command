#!/bin/zsh
cd -- "${0:A:h}"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
if ! test -d node_modules; then
    npm ci || exit 1
fi
npm start
