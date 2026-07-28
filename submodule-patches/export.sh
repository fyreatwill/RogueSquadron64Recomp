#!/bin/bash
# Re-export the current submodule working-tree diffs into submodule-patches/.
# Run this after ANY edit inside lib/ so the patches never go stale, then commit.
set -e
cd "$(dirname "$0")/.."
# --ignore-submodules=dirty: N64Recomp is a nested submodule with its own
# patch file below; without this, a dirty N64Recomp shows up here too as a
# "Subproject commit ...-dirty" pointer line that `git apply` can't consume.
git -C lib/N64ModernRuntime        diff --ignore-submodules=dirty > submodule-patches/N64ModernRuntime.patch
git -C lib/N64ModernRuntime/N64Recomp diff > submodule-patches/N64Recomp-nested.patch
git -C lib/rt64                    diff > submodule-patches/rt64.patch
git -C lib/rt64/src/contrib/hlslpp diff > submodule-patches/rt64-hlslpp.patch
git -C lib/rt64/src/contrib/plume  diff > submodule-patches/rt64-plume.patch
wc -l submodule-patches/*.patch
