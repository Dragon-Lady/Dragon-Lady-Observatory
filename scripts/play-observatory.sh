#!/usr/bin/env bash
# Desktop-friendly name for the Observatory telescope launcher.
# Same as ./scripts/observatory (Chuck's Astro viewer on :4331).
exec "$(cd "$(dirname "$0")" && pwd)/observatory" "$@"
