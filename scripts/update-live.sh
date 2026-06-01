#!/bin/bash
# Dragon Eye Stars Edition — Live Update (Unix/macOS)

set -e

echo "=== Dragon Eye Stars Edition — Live Update ==="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo ""
echo "[1/2] Running engine poll..."
python -m engine.poll

echo ""
echo "[2/2] Rebuilding viewer..."
cd viewer
npm run build

echo ""
echo "✅ Done. Run 'cd viewer && npm run preview' to check the updated globe."