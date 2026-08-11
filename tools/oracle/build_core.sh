#!/usr/bin/env bash
# Build a mupen64plus core with the R4300 debugger compiled in.
#
# Homebrew's mupen64plus bottle is built WITHOUT DEBUGGER=1 and exports no
# Debug* symbols, so the oracle cannot set watches against it. We still use
# Homebrew for the RSP plugin and the data dir; only the core needs building.
set -euo pipefail

ROOT="${RS64_ORACLE_ROOT:-$HOME/Documents/Tools/rs64-oracle}"
SRC="$ROOT/src/mupen64plus-core"

command -v brew >/dev/null || { echo "needs Homebrew" >&2; exit 1; }

# DEBUGGER=1 links against libopcodes for its disassembler, which macOS does
# not ship. This is the whole reason a plain `make DEBUGGER=1` fails with
# "ld: library 'opcodes' not found".
brew list binutils >/dev/null 2>&1 || brew install binutils
brew list mupen64plus >/dev/null 2>&1 || brew install mupen64plus

mkdir -p "$ROOT/src"
[ -d "$SRC" ] || git clone --depth 1 https://github.com/mupen64plus/mupen64plus-core "$SRC"

cd "$SRC/projects/unix"
export LDFLAGS="-L$(brew --prefix binutils)/lib"
export CFLAGS="-I$(brew --prefix binutils)/include"
export CXXFLAGS="$CFLAGS"
make DEBUGGER=1 all -j"$(sysctl -n hw.ncpu)"

echo
echo "core: $SRC/projects/unix/libmupen64plus.dylib"
nm -gU "$SRC/projects/unix/libmupen64plus.dylib" | grep -q _DebugBreakpointCommand \
  && echo "debugger symbols present" \
  || { echo "NO debugger symbols - build did not honour DEBUGGER=1" >&2; exit 1; }
