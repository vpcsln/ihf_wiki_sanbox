#!/usr/bin/env bash

set -Eeuo pipefail

SANDBOX_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec python3 "$SANDBOX_DIR/serve.py" "$@"
