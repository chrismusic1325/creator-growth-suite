#!/usr/bin/env bash

ROOT="$HOME/creator-growth-suite"
cd "$ROOT" || exit 1

[ -f "$ROOT/launchers/free-only-env.sh" ] && \
    source "$ROOT/launchers/free-only-env.sh"

[ -f "$ROOT/.creator-local.env" ] && \
    source "$ROOT/.creator-local.env"

python dashboard/server.py
