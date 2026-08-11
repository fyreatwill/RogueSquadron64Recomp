#!/usr/bin/env bash
# Build rs64_oracle against a DEBUGGER=1 mupen64plus core.
#
# The core must be built from source: Homebrew's bottle is compiled without
# DEBUGGER=1 and exports no Debug* symbols, so the oracle cannot set watches
# against it. build_core.sh does that build; this script only needs its
# headers to compile and finds the dylib at run time.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_SRC="${CORE_SRC:-$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core}"

if [ ! -d "$CORE_SRC/src/api" ]; then
  echo "core source not found at $CORE_SRC" >&2
  echo "run tools/oracle/build_core.sh first, or set CORE_SRC" >&2
  exit 1
fi

mkdir -p "$here/build"
cc -O2 -Wall -Wextra -std=c11 \
   -I"$CORE_SRC/src/api" \
   -o "$here/build/rs64_oracle" \
   "$here/rs64_oracle.c"

echo "built $here/build/rs64_oracle"
