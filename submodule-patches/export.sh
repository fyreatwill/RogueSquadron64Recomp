#!/bin/bash
# Re-export the current submodule working-tree diffs into submodule-patches/.
# Run this after ANY edit inside lib/ so the patches never go stale, then commit.
set -e
cd "$(dirname "$0")/.."
git -C lib/N64ModernRuntime        diff > submodule-patches/N64ModernRuntime.patch
git -C lib/rt64                    diff > submodule-patches/rt64.patch
git -C lib/rt64/src/contrib/hlslpp diff > submodule-patches/rt64-hlslpp.patch
git -C lib/rt64/src/contrib/plume  diff > submodule-patches/rt64-plume.patch
wc -l submodule-patches/*.patch
