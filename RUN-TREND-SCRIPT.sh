#!/usr/bin/env bash
cd "$HOME/creator-growth-suite/engines/agenttube" || exit 1

npm run agent:strategy
npm run agent:script
npm run agent:seo
