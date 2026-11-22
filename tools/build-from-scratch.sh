#!/bin/bash
# build-from-scratch.sh - build the Rogue Squadron 64 recomp (macOS, Apple Silicon) from the three public repos + your ROM.
#
# usage:  ./build-from-scratch.sh /path/to/rogue_squadron.z64      (run it in an empty directory, or one it already used)
#
# Result: ./RogueSquadron64Recomp/build/RogueSquadron64Recomp with rogue_squadron.z64 beside it. Run it from that folder:
#         cd RogueSquadron64Recomp/build && ./RogueSquadron64Recomp
#
# Prerequisites (none are installed by this script):
#   - macOS on Apple Silicon, full Xcode (not just the Command Line Tools) with the Metal Toolchain component
#     (Xcode > Settings > Components, or: xcodebuild -downloadComponent MetalToolchain). The shader build calls
#     `xcrun metal`; if the active developer dir is the CLT, this script points DEVELOPER_DIR at /Applications/Xcode.app.
#   - Homebrew: cmake (>= 3.20), ninja, sdl2-compat (SDL2 cmake package), python3 (stdlib only; 3.14 tested)
#   - git, make, patch, zsh (stock macOS)
#   - mips64-elf-gcc + mips64-elf-ld on PATH (or MIPS_TOOLCHAIN_DIR=<root with bin/>). Not in Homebrew core; build
#     binutils 2.40 + gcc 14.2.0 with tools/build-mips64-toolchain.sh in the RogueSquadron64Recomp repo (needs brew gmp mpfr libmpc gnu-sed).
#     Without it the build still links, but the patches/ overrides (heap guards, RNG patch) are left out.
#   - ~15 GB free disk, network access to github.com.
#   - ROM: Star Wars: Rogue Squadron (USA) v1.0, .z64 byte order, sha1 ed42eed1ee2db646ff7ef94ba8c5421d164a4f0d
#
# Steps: clone 3 repos (or reuse) -> submodules -> submodule-patches/apply.sh -> build N64Recomp + RSPRecomp ->
#        tools/regen_front.sh + tools/regen_replay.sh -> N64Recomp/RecompiledFuncs -> RSP ucode (composites +
#        tools/ucode_regen.sh restore) -> cmake configure, build N64RecompCLI, reconfigure (enables patches/) -> build.
set -euo pipefail

ROM_SHA1=ed42eed1ee2db646ff7ef94ba8c5421d164a4f0d
GH=https://github.com/fyreatwill
ROM_IN=${1:-}
[ -n "$ROM_IN" ] && [ -f "$ROM_IN" ] || { echo "usage: $0 /path/to/rogue_squadron.z64"; exit 2; }
ROM_IN=$(cd "$(dirname "$ROM_IN")" && pwd)/$(basename "$ROM_IN")
TOP=$PWD
LOGS=$TOP/build-logs; mkdir -p "$LOGS"
T0=$(date +%s)
step() { echo; echo "=== [$(( $(date +%s) - T0 ))s] $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }

# ---- prerequisites ----
step "checking prerequisites"
for t in git cmake ninja python3 make patch zsh clang shasum; do command -v $t >/dev/null || die "missing tool: $t"; done
if ! xcrun -sdk macosx -f metal >/dev/null 2>&1; then
  [ -d /Applications/Xcode.app ] && export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
  xcrun -sdk macosx -f metal >/dev/null 2>&1 || die "no Metal compiler: install Xcode and its Metal Toolchain (xcodebuild -downloadComponent MetalToolchain)"
fi
echo "metal: $(xcrun -sdk macosx -f metal)"
MIPS_ARGS=()
if [ -n "${MIPS_TOOLCHAIN_DIR:-}" ]; then MIPS_ARGS=(-DMIPS_TOOLCHAIN_DIR="$MIPS_TOOLCHAIN_DIR")
elif ! command -v mips64-elf-gcc >/dev/null || ! command -v mips64-elf-ld >/dev/null; then
  echo "WARNING: mips64-elf-gcc/ld not found: patches/ will NOT be built into the game"
fi
sha=$(shasum -a 1 "$ROM_IN" | cut -d' ' -f1)
[ "$sha" = "$ROM_SHA1" ] || [ "${ALLOW_ANY_ROM:-0}" = 1 ] || die "ROM sha1 $sha != $ROM_SHA1 (USA v1.0 .z64); ALLOW_ANY_ROM=1 to skip"

# ---- 1. clone (or reuse) ----
clone() { # dir branch
  if [ -d "$1/.git" ]; then echo "reusing $1 ($(git -C "$1" rev-parse --short HEAD))"
  else git clone -b "$2" "$GH/$1.git" "$1"; fi
}
step "cloning repos"
clone RogueSquadron64Recomp autonomy
clone N64Recomp rs64
clone rogue_squadron64 rs64

step "submodules + submodule patches"
git -C N64Recomp submodule update --init --recursive
git -C RogueSquadron64Recomp submodule update --init --recursive
./RogueSquadron64Recomp/submodule-patches/apply.sh

# ROM copies the tools read (regen_front: rogue_squadron64/; ucode + composites: RogueSquadron64Recomp/)
cp "$ROM_IN" rogue_squadron64/rogue_squadron.z64
cp "$ROM_IN" RogueSquadron64Recomp/rogue_squadron.z64

# ---- 2. recompiler ----
step "building N64Recomp + RSPRecomp"
cmake -S N64Recomp -B N64Recomp/build -G Ninja -DCMAKE_BUILD_TYPE=Release > "$LOGS/n64recomp-cfg.log" 2>&1
cmake --build N64Recomp/build --target N64Recomp RSPRecomp > "$LOGS/n64recomp-build.log" 2>&1 || die "N64Recomp build failed ($LOGS/n64recomp-build.log)"

# ---- 3. RecompiledFuncs: regen_front + regen_replay ----
RF=$TOP/N64Recomp/RecompiledFuncs
if [ -f "$TOP/N64Recomp/.rs64_regen_ok" ] && [ -f "$RF/funcs_0.c" ]; then
  step "RecompiledFuncs already generated (delete N64Recomp/.rs64_regen_ok to redo)"
else
  step "regen_front (make_elf + N64Recomp)"
  # straight into N64Recomp/RecompiledFuncs: CMake's default RECOMP_FUNCS_DIR, and the s7420 census reads that path
  rm -rf "$RF" "$RF.work" "$TOP/N64Recomp/.rs64_regen_ok"
  ./RogueSquadron64Recomp/tools/regen_front.sh "$RF"
  step "regen_replay (post-processing, ~6 min)"
  set +e; out=$(./RogueSquadron64Recomp/tools/regen_replay.sh "$RF" "$LOGS/regen_replay.log"); rc=$?; set -e
  echo "$out"
  if [ $rc -ne 0 ]; then
    # Every step that edits the tree (fixers, weaken, cut tails, rename) runs before the s73xx/s74xx censuses. Those
    # censuses only read the tree and host sources; a failure there is a lint verdict, not a broken tree.
    echo "$out" | grep -qE '^regen_replay: s7[0-9]+ ' || die "regen_replay failed in a tree-editing step (see $LOGS/regen_replay.log)"
    echo "WARNING: regen_replay trailing census check failed (read-only; tree is complete). See $LOGS/regen_replay.log"
  fi
  rm -rf "$RF.work"
  touch "$TOP/N64Recomp/.rs64_regen_ok"
fi

# ---- 4. RSP ucode -> RogueSquadron64Recomp/build/factor5_ucode ----
step "RSP ucode (overlay composites + tools/ucode_regen.sh restore)"
cd "$TOP/RogueSquadron64Recomp"
for ov in 4 10 12 14 18 0x1C 0x20 0x2C 24; do python3 tools/make_clip_composite.py $ov > /dev/null; done
mkdir -p build/factor5_ucode
# restore exits 1 when build/factor5_ucode was empty before (its byte-compare finds nothing to match); "restored" = done.
set +e; out=$(RSPRECOMP="$TOP/N64Recomp/build/RSPRecomp" FORCE=1 zsh tools/ucode_regen.sh restore 2>&1); set -e
echo "$out" | grep -E '^census|^restored'
echo "$out" | grep -q '^restored' || { echo "$out"; die "ucode_regen.sh restore failed"; }

# ---- 5. game ----
step "configuring game (pass 1)"
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug ${MIPS_ARGS[@]+"${MIPS_ARGS[@]}"} > "$LOGS/game-cfg1.log" 2>&1 || die "configure failed ($LOGS/game-cfg1.log)"
# The patches/ build is enabled only if build/N64Recomp exists at configure time, and that binary is a target of this
# same build dir (N64RecompCLI) -> build it, then configure again.
step "building N64RecompCLI, configuring game (pass 2)"
cmake --build build --target N64RecompCLI > "$LOGS/game-n64recompcli.log" 2>&1 || die "N64RecompCLI failed"
cmake -S . -B build > "$LOGS/game-cfg2.log" 2>&1 || die "configure failed ($LOGS/game-cfg2.log)"
grep -q "Patches build skipped" "$LOGS/game-cfg2.log" && echo "WARNING: patches/ build skipped (see $LOGS/game-cfg2.log)" || echo "patches/ build enabled"
step "building game (long)"
cmake --build build > "$LOGS/game-build.log" 2>&1 || { tail -30 "$LOGS/game-build.log"; die "game build failed ($LOGS/game-build.log)"; }
cp "$ROM_IN" build/rogue_squadron.z64

# s7806: regen_replay ran the s7420 census before CMake made RecompiledPatches/patches.c, so its patches-tree row could only
# DEFER. Now the tree exists: the census must vouch for it (read-only lint, so a failure warns rather than stops).
step "s7420 census on the generated patches tree"
if [ -f RecompiledPatches/patches.c ]; then
  python3 tools/s7420_parser_census.py --controls --require-tree > "$LOGS/s7420_post.log" 2>&1 \
    && echo "s7420: $(grep '^VERDICT' "$LOGS/s7420_post.log")" \
    || echo "WARNING: s7420 post-build census failed: $(grep '^VERDICT' "$LOGS/s7420_post.log") (see $LOGS/s7420_post.log)"
else echo "s7420: no RecompiledPatches/patches.c (patches/ build skipped), nothing to check"; fi

step "done in $(( $(date +%s) - T0 ))s"
ls -la build/RogueSquadron64Recomp build/rogue_squadron.z64
echo "run: cd $TOP/RogueSquadron64Recomp/build && ./RogueSquadron64Recomp"
