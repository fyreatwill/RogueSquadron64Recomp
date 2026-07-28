#!/bin/bash
# Re-apply the submodule working-tree patches after any submodule reset.
#
# lib/N64ModernRuntime and lib/rt64 (and rt64's own nested contrib submodules,
# plus N64ModernRuntime's own nested N64Recomp submodule) carry uncommitted
# working-tree changes that months of this port depend on: the shared-DMEM
# serialization, the overlay loader, the RT64 assert-guard chain, the
# Metal/plume additions. If a submodule ever gets reset, run this.
#
# Regenerate the patches after making new submodule edits:
#   ./submodule-patches/export.sh
set -e
cd "$(dirname "$0")/.."
root="$PWD"

apply_one() { # $1 = submodule path, $2 = patch file
  local sub="$1" patch="$root/submodule-patches/$2"
  [ -f "$patch" ] || { echo "missing $patch"; exit 1; }
  if git -C "$sub" apply --check "$patch" 2>/dev/null; then
    git -C "$sub" apply "$patch"
    echo "applied  $2 -> $sub"
  elif git -C "$sub" apply --reverse --check "$patch" 2>/dev/null; then
    echo "already applied: $2"
  else
    echo "FAILED to apply $2 to $sub (conflicts with current tree)"; exit 1
  fi
}

apply_one lib/N64ModernRuntime            N64ModernRuntime.patch
apply_one lib/N64ModernRuntime/N64Recomp  N64Recomp-nested.patch
apply_one lib/rt64                        rt64.patch
apply_one lib/rt64/src/contrib/hlslpp     rt64-hlslpp.patch
apply_one lib/rt64/src/contrib/plume      rt64-plume.patch
echo "patches applied"
