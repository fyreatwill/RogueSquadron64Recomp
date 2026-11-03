#!/bin/zsh
# s6810 G1e: owner-settings game fps WITHOUT recipe logging. Diagnostic recipes (G3_CENSUS, G3E_TRACE, FB_HASH, TRICOUNT,
# DRAWN, FB dumps) cost ~10 fps at dd4 (s6810: 48.8 vs 59.3), so never quote fps from them; use this.
# usage: zsh tools/g1e_clean_fps.zsh LEVEL "DD..." [HOLD_S]   e.g. zsh tools/g1e_clean_fps.zsh 1 "4 1" 150
# Runs scratch/agent/s6716_bridge.zsh (FPS60 + ASYNC/NODRAIN, [g1e-split] + [g1b] only) per dd, sequentially, then prints
# tools/g1e_dd_table.py plus the [g1b] tasks/vi mean+min over the last 140 s. Takes a 10 s `sample` 60 s into each flight.
cd "$(git rev-parse --show-toplevel)" || exit 1
lvl=${1:-1}; dds=(${=2:-4 1}); hold=${3:-150}; O=scratch/agent/m6
for dd in $dds; do
  T=g1_lvl${lvl}s6716_cleandd$dd
  ( for i in $(seq 1 400); do [ -f $O/$T/run.log ] && grep -a -q '\[g1e-split\] phase=6' $O/$T/run.log && break; sleep 1; done
    sleep 60; p=$(pgrep -x RogueSquadron64Recomp | head -1); [ -n "$p" ] && sample $p 10 -file $O/$T/sample.txt >/dev/null 2>&1 ) &
  env HOLD_S=$hold zsh scratch/agent/s6716_bridge.zsh $lvl $dd cleandd$dd
  wait
done
python3 tools/g1e_dd_table.py $(for dd in $dds; do echo $O/g1_lvl${lvl}s6716_cleandd$dd; done)
for dd in $dds; do
  printf 'dd%s [g1b] ' $dd
  grep -a '^\[g1b\]' $O/g1_lvl${lvl}s6716_cleandd$dd/run.log | tail -140 | python3 -c "
import sys,re,statistics as s
rows=[dict(re.findall(r'(\w+)=([-\d.]+)',l)) for l in sys.stdin]
print(len(rows), *('%s mean %.2f min %g' % (k, s.mean(float(r[k]) for r in rows), min(float(r[k]) for r in rows)) for k in ('tasks','vi')) if rows else 'no rows')"
done
