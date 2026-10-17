#!/bin/zsh
# Build an old commit in a git worktree WITHOUT cp/ditto (permission-denied headless).
# usage: tools/bisect_worktree.sh <commit> [build]   (second arg = also configure+build)
# Untracked inputs (lib/ submodules, RecompiledPatches, ROMs) are SYMLINKED from the
# main tree, so the arm tests "old src/ + CURRENT lib patches". Current-lib-vs-old-lib
# is already separated: the TO_PTR mask (the only lib behaviour change) was A/B'd in s5242.
set -eu
ROOT=$(git -C "${0:A:h}" rev-parse --show-toplevel)
C=${1:?commit}; WT="$ROOT/scratch/wt_${C:0:8}"
[ -d "$WT" ] || git -C "$ROOT" worktree add "$WT" "$C"
for d in lib/N64ModernRuntime lib/rt64; do
  rmdir "$WT/$d" 2>/dev/null || true
  [ -e "$WT/$d" ] || ln -s "$ROOT/$d" "$WT/$d"
done
for f in RecompiledPatches rogue_squadron.z64 rs64.n64.us.1.0.z64; do
  if [ -e "$ROOT/$f" ] && [ ! -e "$WT/$f" ]; then ln -s "$ROOT/$f" "$WT/$f"; fi
done
echo "worktree ready: $WT"
if [ "${2:-}" = build ]; then
  cd "$WT"
  export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
  cmake --build build -j8
fi
