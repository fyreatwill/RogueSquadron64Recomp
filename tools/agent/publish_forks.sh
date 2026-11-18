#!/bin/bash
# publish_forks.sh - re-publish the three public GitHub forks the clean build uses.
# Run by loop.sh between iterations (in the background); safe to run by hand.
#
#   RogueSquadron64Recomp  autonomy  -> fork remote, fast-forward only, after guards
#   N64Recomp              rs64      -> fyreatwill/N64Recomp, tool source only (path whitelist)
#   rogue_squadron64       rs64      -> fyreatwill/rogue_squadron64, tracked files' working-tree state
#
# Never publishes generated game code: the N64Recomp live history has RecompiledFuncs
# committed, so that repo is published by copying whitelisted paths into a separate
# mirror clone, never by pushing its history. A guard failure writes
# scratch/agent/PUBLISH-BLOCKED.md and publishes nothing for that repo.
#
# usage: tools/agent/publish_forks.sh [--dry-run]
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 2
RS=$PWD; TOOLS=$(cd .. && pwd)
N64=${RS64_PUBLISH_N64:-$TOOLS/N64Recomp}; DEC=${RS64_PUBLISH_DEC:-$TOOLS/rogue_squadron64}
MIR=${RS64_PUBLISH_MIRRORS:-$TOOLS/.rs64-publish}
AG=$RS/scratch/agent; LOG=$AG/publish.log; BLOCK=$AG/PUBLISH-BLOCKED.md
GH=https://github.com/fyreatwill
NOREPLY=228090490+fyreatwill@users.noreply.github.com
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
mkdir -p "$AG" "$MIR"

# one run at a time
LOCK=$MIR/.lock
if ! mkdir "$LOCK" 2>/dev/null; then
  # stale after 30 min
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then rmdir "$LOCK"; mkdir "$LOCK" || exit 0; else exit 0; fi
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

log() { echo "[publish $(date '+%F %T')] $*" >> "$LOG"; [ -t 1 ] && echo "[publish] $*"; return 0; }
blocked=0
block() { blocked=1; log "BLOCKED: $*"; { echo "# Fork publishing blocked, $(date)"; echo; echo "$*"; echo; echo "Fix the cause, then delete this file. Details in scratch/agent/publish.log."; } > "$BLOCK"; }
push() { if [ $DRY = 1 ]; then log "dry-run: would push $*"; else git push -q "$@" >> "$LOG" 2>&1; fi; }

# ---------- 1. main repo: fast-forward push of autonomy ----------
publish_main() {
  git fetch -q fork autonomy 2>>"$LOG" || { log "main: fetch fork failed"; return; }
  local base=fork/autonomy tip; tip=$(git rev-parse autonomy)
  [ "$(git rev-parse $base)" = "$tip" ] && { log "main: up to date"; return; }
  git merge-base --is-ancestor $base "$tip" || { block "main: autonomy is not a fast-forward of fork/autonomy (history rewritten?). Not force-pushing."; return; }
  local bad
  bad=$(git log --format='%ae%n%ce' $base.."$tip" | sort -u | grep -vx "$NOREPLY")
  [ -n "$bad" ] && { block "main: commits with non-noreply emails: $(echo $bad)"; return; }
  bad=$(git diff --name-only --diff-filter=AM $base "$tip" | grep -i -E '\.(z64|n64|v64|rom)$|(^|/)ucode_[0-9A-Fa-f]+\.bin$|(^|/)RecompiledFuncs/|\.(sav|eep|ppm|raw)$')
  [ -n "$bad" ] && { block "main: ROM-derived or generated files in new commits: $(echo $bad | head -c 600)"; return; }
  bad=$(git rev-list --objects $base.."$tip" | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | awk '$1=="blob" && $2>50000000 {print $3" ("int($2/1e6)" MB)"}')
  [ -n "$bad" ] && { block "main: files over 50 MB in new commits: $(echo $bad)"; return; }
  local n; n=$(git rev-list --count $base.."$tip")
  push fork autonomy:autonomy && log "main: $([ $DRY = 1 ] && echo would push || echo pushed) $n commits -> ${tip:0:9}" || log "main: push failed"
}

# ---------- 2/3. mirror publishing for the two dependency forks ----------
# sync_mirror <name> <live repo> <file list cmd...>: copies the listed files' working-tree
# content from the live repo into mirror clone $MIR/<name>, commits if changed, pushes rs64.
sync_mirror() {
  local name=$1 live=$2; shift 2
  local m=$MIR/$name
  if [ ! -d "$m/.git" ]; then
    git clone -q --branch rs64 "$GH/$name.git" "$m" 2>>"$LOG" || { log "$name: clone failed"; return; }
  fi
  git -C "$m" fetch -q origin rs64 2>>"$LOG" && git -C "$m" reset -q --hard origin/rs64 || { log "$name: fetch failed"; return; }
  local list; list=$(cd "$live" && "$@") || { log "$name: listing failed"; return; }
  # deletions: whitelisted paths that exist in the mirror but no longer live
  (cd "$m" && "$@") | while read -r f; do [ -e "$live/$f" ] || git -C "$m" rm -q --cached -- "$f" 2>/dev/null; done
  echo "$list" | while read -r f; do
    [ -f "$live/$f" ] || continue
    mkdir -p "$m/$(dirname "$f")"; cp -p "$live/$f" "$m/$f"; git -C "$m" add -- "$f"
  done
  git -C "$m" diff --cached --quiet && { log "$name: up to date"; return; }
  local big; big=$(git -C "$m" diff --cached --name-only | while read -r f; do [ -f "$m/$f" ] && [ $(stat -f %z "$m/$f") -gt 5000000 ] && echo "$f"; done)
  [ -n "$big" ] && { block "$name: refusing files over 5 MB: $big"; git -C "$m" reset -q --hard; return; }
  local n; n=$(git -C "$m" diff --cached --name-only | wc -l | tr -d ' ')
  local src; src=$(git -C "$live" log -1 --format='%h %s' | cut -c1-72)
  git -C "$m" -c user.name="William Buckley" -c user.email="$NOREPLY" commit -q \
    -m "Sync from local working tree ($n files)" -m "Local HEAD at sync: $src" -m "Published automatically by RogueSquadron64Recomp/tools/agent/publish_forks.sh." \
    || { log "$name: commit failed"; return; }
  if [ $DRY = 1 ]; then log "$name: dry-run: would push $n changed files"; git -C "$m" reset -q --hard origin/rs64; return; fi
  git -C "$m" push -q origin rs64 >> "$LOG" 2>&1 && log "$name: pushed $n changed files" || log "$name: push failed"
}

# Recompiler: tool source and the RS64 config only. Never RecompiledFuncs, scratch, logs.
n64_list() { git ls-files -- src include RSPRecomp/src LiveRecomp CMakeLists.txt rogue_squadron.toml rogue_squadron_relocatable.txt | grep -v -E '(^|/)(RecompiledFuncs|scratch)'; }
# Decomp: files tracked there (asm/, assets/, the ROM are gitignored by that repo).
dec_list() { git ls-files | grep -v -i -E '\.(z64|n64|v64|bin|elf)$'; }

publish_main
sync_mirror N64Recomp "$N64" n64_list
sync_mirror rogue_squadron64 "$DEC" dec_list
[ $blocked = 0 ] && [ -f "$BLOCK" ] && [ $DRY = 0 ] && { rm -f "$BLOCK"; log "guards clear again - removed PUBLISH-BLOCKED.md"; }
exit 0
