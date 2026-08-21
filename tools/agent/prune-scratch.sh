#!/bin/bash
# Scratch retention. Called once per iteration from loop.sh.
#
# probe.sh and regress.sh leave two kinds of bulk artifact in <outdir>:
# the full emulator trace (run.log, probe.sh:53 / regress.sh:167) and the frame
# captures (f_*.png and the recipe-specific hold_/stable_/pre_/post_ series).
# Nothing ever removed either. By 2026-08-20 scratch held 202 GB of traces --
# 2044 run.log files, the largest a single 18 GB file -- plus 51.7 GB across
# 93,406 PNGs, and the disk was at 97%. Burn rate is ~8 GB/day while the loop
# runs.
#
# Traces gzip 13-18x (a measured 0.54 GB -> 0.04 GB) and stay greppable with
# zgrep, so logs are compressed rather than deleted. PNG is already compressed,
# so frames can only be aged out.
#
# Env: GZIP_AFTER_DAYS (2), DELETE_AFTER_DAYS (21), FRAMES_AFTER_DAYS (14)

set -u
cd "$(dirname "$0")/../.."
[ -d scratch ] || exit 0

GZIP_AFTER_DAYS="${GZIP_AFTER_DAYS:-2}"
DELETE_AFTER_DAYS="${DELETE_AFTER_DAYS:-21}"
FRAMES_AFTER_DAYS="${FRAMES_AFTER_DAYS:-14}"

TMP="$(mktemp -d -t prunescratch)"
trap 'rm -rf "$TMP"' EXIT
KEEP="$TMP/keep"; CAND="$TMP/cand"; TODO="$TMP/todo"

# PORTING-STATE.md and docs/ cite specific scratch artifacts as the evidence
# behind conclusions -- 302 .log and 50 .png paths as of 2026-08-20. A sweep
# that ignores them breaks the audit trail: the first cleanup on 2026-08-20
# deleted 101 cited logs before this guard existed. Anything named in the docs
# is exempt from every step below, at ANY age.
grep -rhoE 'scratch/[A-Za-z0-9_./-]+\.(log|png)' \
  docs/ PORTING-STATE.md AGENTS.md CLAUDE.md 2>/dev/null | sort -u > "$KEEP"

# comm needs both sides sorted; scratch paths are machine-generated and contain
# no spaces or newlines, so line-oriented set subtraction is safe here.
run_batch() {  # $1 = action word, reads NUL-safe list on stdin
  [ -s "$TODO" ] || return 0
  tr '\n' '\0' < "$TODO" | xargs -0 "$@" 2>/dev/null
}

# 1. Compress settled traces. The +N cutoff leaves the in-flight iteration's
#    logs as plain files: the greps in probe.sh read run.log while the capture
#    is still running. loop.log is skipped outright -- appended every iteration
#    and usually held open by a `tail -f`.
find scratch -name '*.log' -type f -mtime +"$GZIP_AFTER_DAYS" -print 2>/dev/null \
  | sort > "$CAND"
comm -23 "$CAND" "$KEEP" | grep -v '/agent/loop\.log$' > "$TODO"
gz=$(wc -l < "$TODO" | tr -d ' ')
run_batch gzip -q

# 2. Past the retention window the raw trace has no audience: the durable
#    findings were reconciled into PORTING-STATE.md, docs/ and SOAK-RESULTS.md
#    when the session that produced them closed.
find scratch -name '*.log.gz' -type f -mtime +"$DELETE_AFTER_DAYS" -print 2>/dev/null \
  | sort > "$TODO"
rmlog=$(wc -l < "$TODO" | tr -d ' ')
run_batch rm -f

# 3. Frames. Kept longer than the gzip window because a visual regression is
#    re-read by eye days later, but they are the single largest consumer once
#    the logs are compressed, so they cannot be kept forever.
find scratch \( -name '*.png' -o -name '*.jpg' \) -type f -mtime +"$FRAMES_AFTER_DAYS" \
  -print 2>/dev/null | sort > "$CAND"
comm -23 "$CAND" "$KEEP" > "$TODO"
rmpng=$(wc -l < "$TODO" | tr -d ' ')
run_batch rm -f

# Outdirs the sweeps above emptied. Bounded by the same age cutoff so a freshly
# created (still empty) outdir is never pulled out from under a running probe.
find scratch -mindepth 2 -type d -empty -mtime +"$DELETE_AFTER_DAYS" -delete 2>/dev/null

if [ "$gz" -gt 0 ] || [ "$rmlog" -gt 0 ] || [ "$rmpng" -gt 0 ]; then
  echo "[prune] gzipped=$gz removed_logs=$rmlog removed_frames=$rmpng kept_cited=$(wc -l < "$KEEP" | tr -d ' ')"
fi
exit 0
