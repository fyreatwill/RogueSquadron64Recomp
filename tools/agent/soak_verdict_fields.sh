#!/bin/zsh
# s7456 class DL: per-arm evidence for loop.sh's SOAK-RESULTS verdict line, so a fold never has to open the log
# to learn alive_at_end / crashlines (s7449 rc=1 was a benign mission re-init; s7450 rc=137 the cap; s7452 rc=0
# carried a deliberately dead planted arm). Reads the m6 "tag=..." summary lines the recipe cat'ed into its log.
# usage: soak_verdict_fields.sh <soak log>
#   -> "arms=<k> alive=<a>/<k> crash_arms=<c> stall_arms=<s> fatal=<n> first=<line> stall_na=<m>"   (arms=0: recipe printed no summary)
# s7457: a stall arm is vi_stalls30s>0 OR frozen=1 (boot_freeze_hunt); stall_na counts arms that carry neither measure.
# fatal counts fatal_patterns.txt lines in the log itself, excluding the recipe's own "tag=" and "== " echo lines.
L=${1:?log}; H=${0:A:h}
[ -f "$L" ] || { print "arms=? (no log)"; exit 0; }
grep -aE '^[[:space:]]*tag=' "$L" | awk '
  function v(k,  i,a){ for(i=1;i<=NF;i++){ split($i,a,"="); if(a[1]==k) return a[2] } return "" }
  { n++; if (v("alive_at_end")=="1") al++; c=v("crashlines"); if (c!="" && c!="0") cr++; s=v("vi_stalls30s"); f=v("frozen")
    if ((s!="" && s!="0" && s!="na") || (f!="" && f!="0")) st++; else if ((s=="" || s=="na") && f=="") na++ }
  END { printf "arms=%d alive=%d/%d crash_arms=%d stall_arms=%d", n, al, n, cr, st; printf "%d\n", na > "/dev/stderr" }' 2> "${TMPDIR:-/tmp}/svfna.$$"
grep -avE '^[[:space:]]*(tag=|== )' "$L" > "${TMPDIR:-/tmp}/svf.$$"; print -n " "; print -rn -- "$(zsh "$H/fatal_scan.sh" "${TMPDIR:-/tmp}/svf.$$")"
# s7457 class DM: stall_na = arms with no stall measure (vi_stalls30s missing or "na", no frozen=): their stall_arms=0 is not a zero.
print " stall_na=$(head -1 "${TMPDIR:-/tmp}/svfna.$$" 2>/dev/null || echo 0)"
rm -f "${TMPDIR:-/tmp}/svfna.$$"
rm -f "${TMPDIR:-/tmp}/svf.$$"
