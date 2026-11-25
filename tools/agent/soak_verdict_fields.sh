#!/bin/zsh
# s7456 class DL: per-arm evidence for loop.sh's SOAK-RESULTS verdict line, so a fold never has to open the log
# to learn alive_at_end / crashlines (s7449 rc=1 was a benign mission re-init; s7450 rc=137 the cap; s7452 rc=0
# carried a deliberately dead planted arm). Reads the m6 "tag=..." summary lines the recipe cat'ed into its log.
# usage: soak_verdict_fields.sh <soak log>
#   -> "arms=<k> alive=<a>/<k> crash_arms=<c> stall_arms=<s> fatal=<n> first=<line> stall_na=<m> alive_na=<x> freeze_arms=<z> freeze_na=<y>"   (arms=0: recipe printed no summary)
# s7457: a stall arm is vi_stalls30s>0 OR frozen=1 (boot_freeze_hunt) OR fs_holds>0 (s7459, m6 log fs= held >=1800 VIs) OR void_holds>0 (s7462, held frame in a retried void attempt); stall_na counts arms that carry neither measure.
# s7697 class DN: alive=/crash= (s7695/s7696/s7678 recipes) are read as aliases of alive_at_end=/crashlines=; before this the
# s7696_cut_L1/L4 verdicts read alive=0/1 for arms whose tag line said alive=1. alive_na counts arms with neither alive key.
# s7924 class DO: freeze_arms = arms whose max_vihold_ms (frozen VI holds only, s7923 ring_stalls.py) or max_gap_ms (present
# gap) is >= FREEZE_MS (default 1000): the owner's 1-5 s "buffering" freeze (G5c), which vi_stalls30s (>= 30 s) never sees.
# freeze_na = arms carrying neither key. Pre-s7923 tag lines counted the animating 17 s title as a hold: re-score their rings.
# fatal counts fatal_patterns.txt lines lines in the log itself, excluding the recipe's own "tag=" and "== " echo lines.
L=${1:?log}; H=${0:A:h}
[ -f "$L" ] || { print "arms=? (no log)"; exit 0; }
grep -aE '^[[:space:]]*tag=' "$L" | awk -v FMS="${FREEZE_MS:-1000}" '
  function v(k,  i,a){ for(i=1;i<=NF;i++){ split($i,a,"="); if(a[1]==k) return a[2] } return "" }
  { n++; a=v("alive_at_end"); if (a=="") a=v("alive"); if (a=="1") al++; else if (a=="") an++
    c=v("crashlines"); if (c=="") c=v("crash"); if (c!="" && c!="0") cr++; s=v("vi_stalls30s"); f=v("frozen"); h=v("fs_holds"); w=v("void_holds")
    if ((s!="" && s!="0" && s!="na") || (f!="" && f!="0") || (h!="" && h!="0" && h!="na") || (w!="" && w!="0")) st++; else if ((s=="" || s=="na") && f=="" && (h=="" || h=="na")) na++
    mh=v("max_vihold_ms"); mg=v("max_gap_ms"); if (mh=="" && mg=="") fna++; else if (mh+0 >= FMS+0 || mg+0 >= FMS+0) fz++ }
  END { printf "arms=%d alive=%d/%d crash_arms=%d stall_arms=%d", n, al, n, cr, st; printf "%d %d %d %d\n", na, an, fz, fna > "/dev/stderr" }' 2> "${TMPDIR:-/tmp}/svfna.$$"
grep -avE '^[[:space:]]*(tag=|== )' "$L" > "${TMPDIR:-/tmp}/svf.$$"; print -n " "; print -rn -- "$(zsh "$H/fatal_scan.sh" "${TMPDIR:-/tmp}/svf.$$")"
# s7457 class DM: stall_na = arms with no stall measure (vi_stalls30s missing or "na", no frozen=): their stall_arms=0 is not a zero.
NA=($(head -1 "${TMPDIR:-/tmp}/svfna.$$" 2>/dev/null)); print " stall_na=${NA[1]:-0} alive_na=${NA[2]:-0} freeze_arms=${NA[3]:-0} freeze_na=${NA[4]:-0}"
rm -f "${TMPDIR:-/tmp}/svfna.$$"
rm -f "${TMPDIR:-/tmp}/svf.$$"
