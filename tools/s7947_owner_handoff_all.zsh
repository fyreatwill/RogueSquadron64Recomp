#!/bin/zsh
# s7947: whole owner-handoff regression in one command (s7762 docs, s7763 queue commands, s7765 controls dump,
# s7764 in-flight toggles). Each gate's own pass line is required; prints one row per gate + VERDICT.
#   SKIP_INFLIGHT=1   skip the ~12 min s7764 game run (fast pass: 3 gates)
#   S7947_PLANT=1     planted control: adds a gate that must FAIL (wrapper must then print VERDICT FAIL)
cd "$(git rev-parse --show-toplevel)" || exit 1
O=$PWD/scratch/s7947; mkdir -p $O
typeset -a names cmds pats
names+=(s7762_docs);    cmds+=("python3 tools/s7762_owner_doc_check.py --controls"); pats+=('CONTROL PASS')
names+=(s7765_dump);    cmds+=("python3 tools/s7765_controls_dump_check.py");        pats+=('^VERDICT PASS')
names+=(s7763_cmds);    cmds+=("python3 tools/s7763_owner_cmd_check.py --control");  pats+=('mismatch=0 noecho=0')
[[ -z $SKIP_INFLIGHT ]] && { names+=(s7764_toggles); cmds+=("zsh tools/s7764_inflight_toggles.zsh"); pats+=('controls_fail=none broken=none'); }
[[ -n $S7947_PLANT ]] && { names+=(plant_fail); cmds+=("echo 'mismatch=1 noecho=0'"); pats+=('mismatch=0 noecho=0'); }
fail=0
for i in {1..${#names}}; do
  log=$O/${names[i]}.log
  eval "${cmds[i]}" > $log 2>&1; rc=$?
  if grep -Eq "${pats[i]}" $log; then st=PASS; else st=FAIL; fail=$((fail+1)); fi
  # s7762 must also report 0 missing/stale on every doc
  if [[ ${names[i]} == s7762_docs ]] && grep -Eq 'paths_missing=[1-9]|names_stale=[1-9]' $log; then st=FAIL; fail=$((fail+1)); fi
  print "${names[i]} rc=$rc $st  ($(grep -E "${pats[i]}" $log | tail -1 | cut -c1-90))"
done
if (( fail )); then print "VERDICT FAIL fails=$fail"; exit 1; else print "VERDICT PASS gates=${#names}"; fi
