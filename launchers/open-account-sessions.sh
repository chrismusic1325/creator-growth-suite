#!/usr/bin/env bash

CHROME='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
ROOT="$HOME/creator-growth-suite/account-profiles"

openp() {
  PROFILE="$(cygpath -w "$1")"
  URL="$2"
  PROFILE_WIN_ENV="$PROFILE" URL_ENV="$URL" CHROME_ENV="$CHROME"   powershell.exe -NoProfile -Command '
    Start-Process -FilePath $env:CHROME_ENV -ArgumentList @(
      "--user-data-dir=$env:PROFILE_WIN_ENV",
      $env:URL_ENV
    )
  ' >/dev/null 2>&1
}

openp "$ROOT/rumble-browser" "https://rumble.com/account/"
openp "$ROOT/bandcamp-browser" "https://account.bandcamp.com/"
openp "$ROOT/amaze-spring-browser" "https://dashboard.teespring.com/"
