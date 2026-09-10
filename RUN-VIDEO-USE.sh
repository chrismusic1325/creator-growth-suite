#!/usr/bin/env bash

ROOT="$HOME/creator-growth-suite"

if [ -d "$ROOT/engines/video-use" ]; then
    cd "$ROOT/engines/video-use" || exit 1

    if [ -f package.json ]; then
        npm start
    else
        echo "Video Use engine exists but has no npm start command here."
    fi
else
    echo "Video Use engine not found."
fi
