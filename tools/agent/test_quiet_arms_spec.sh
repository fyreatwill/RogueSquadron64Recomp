#!/bin/sh
# s7464 class DU: tools/g1e_owner_quiet_arms.zsh must reject malformed ARMS specs (exit 3) before launching anything.
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$(mktemp -d); pass=0; fail=0
chk(){ rc=$(env R=$T SPEC_CHECK_ONLY=1 ARMS="$2" zsh tools/g1e_owner_quiet_arms.zsh >/dev/null 2>&1; echo $?)
  if [ "$rc" = "$3" ]; then pass=$((pass+1)); echo "ok   $1 rc=$rc"; else fail=$((fail+1)); echo "FAIL $1 rc=$rc want $3"; fi; }
chk "default arms ok" "" 0
chk "plus-joined env ok" "4:cnt:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_S7463_PADCOUNT=1 1:ctl:ROGUESQ_FORCE_SAVE_MISSION=1+ROGUESQ_S7463_PADCOUNT=ctl" 0
chk "empty extra ok" "4:q4: 2:q2:" 0
chk "s7463 space-split spec (the real defect)" "4:cnt:ROGUESQ_FORCE_SAVE_MISSION=4 ROGUESQ_S7463_PADCOUNT=1 1:ctl:ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_S7463_PADCOUNT=ctl" 3
chk "duplicate arm name" "4:a: 2:a:" 3
chk "case-only duplicate arm name (s7952)" "4:q4: 2:Q4:" 3
chk "case-distinct names ok" "4:q4: 2:q4b:" 0
mkdir -p $T/sub/S7952R; chkR(){ rc=$(env R=$2 SPEC_CHECK_ONLY=1 ARMS="4:a:" zsh tools/g1e_owner_quiet_arms.zsh >/dev/null 2>&1; echo $?)
  if [ "$rc" = "$3" ]; then pass=$((pass+1)); echo "ok   $1 rc=$rc"; else fail=$((fail+1)); echo "FAIL $1 rc=$rc want $3"; fi; }
chkR "R case-only sibling refused (s7952)" $T/sub/s7952r 3
chkR "R exact re-run ok" $T/sub/S7952R 0
chkR "R fresh ok" $T/sub/new 0
chk "non-numeric dd" "x:a:" 3
chk "empty arm name" "4::FOO=1" 3
chk "one colon" "4:a" 3
rm -rf $T; echo "test_quiet_arms_spec: $pass pass, $fail fail"; [ $fail = 0 ]
