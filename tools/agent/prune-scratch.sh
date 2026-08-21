#!/bin/bash
# Scratch log retention. Called once per iteration from loop.sh.
#
# probe.sh and regress.sh redirect the whole emulator trace to <outdir>/run.log
# (probe.sh:53, regress.sh:167) and grep it during the run for [CRASH] and
# [phase] markers; regress_score.py parses it afterwards. Nothing ever removed
# them. By 2026-08-20 the tree held 202 GB across 2044 run.log files -- the
# largest a single 18 GB file from s73_post_a_scene/dequeuearg1 -- and the disk
# was at 97%. The traces are highly repetitive text, so gzip returns ~13x
# (a measured 0.54 GB -> 0.04 GB); a compressed log is still greppable with
# zgrep, so compressing beats deleting for anything inside the window.
#
# Env: GZIP_AFTER_DAYS (2), DELETE_AFTER_DAYS (21)

set -u
cd "$(dirname "$0")/../.."
[ -d scratch ] || exit 0

GZIP_AFTER_DAYS="${GZIP_AFTER_DAYS:-2}"
DELETE_AFTER_DAYS="${DELETE_AFTER_DAYS:-21}"

# Compress settled logs only. The +N day cutoff keeps the in-flight iteration's
# logs as plain files, which matters because the greps in probe.sh read run.log
# while the capture is still running. loop.log is skipped outright: it is
# appended to every iteration and is usually held open by a `tail -f`.
gz=0
while IFS= read -r -d '' f; do
  case "$f" in */agent/loop.log) continue ;; esac
  if gzip -q "$f" 2>/dev/null; then gz=$((gz+1)); fi
done < <(find scratch -name '*.log' -type f -mtime +"$GZIP_AFTER_DAYS" -print0 2>/dev/null)

# Past the retention window the raw trace has no audience: the durable findings
# were reconciled into PORTING-STATE.md, docs/ and SOAK-RESULTS.md when the
# session that produced them closed.
rm_n=0
while IFS= read -r -d '' f; do
  if rm -f "$f"; then rm_n=$((rm_n+1)); fi
done < <(find scratch -name '*.log.gz' -type f -mtime +"$DELETE_AFTER_DAYS" -print0 2>/dev/null)

# Outdirs the sweep above emptied. Bounded by the same age cutoff so a freshly
# created (still empty) outdir is never pulled out from under a running probe.
find scratch -mindepth 2 -type d -empty -mtime +"$DELETE_AFTER_DAYS" -delete 2>/dev/null

if [ "$gz" -gt 0 ] || [ "$rm_n" -gt 0 ]; then
  echo "[prune] gzipped=$gz removed=$rm_n"
fi
exit 0
