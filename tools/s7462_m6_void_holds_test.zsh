#!/bin/zsh
# s7462 class DR: m6_god_common.sh retried void attempts (notitle/nohangar/nomission/died_in_verify) without scoring their stalls,
# so a pre-gate held frame (s6993 boot-freeze shape) was invisible once a later attempt passed. Runs the harness's own fail()
# (extracted verbatim) on fake and real logs:
#   planted held-fs void log -> void_holds=1 + keys line carries fs_holds=1; REAL held log (s61_death_repro run4) -> 1;
#   advancing fake log -> 0 (neg ctl); REAL void log (s7450 fxP fail_att1) -> 0 (real neg); two held voids sum to 2;
#   M6_VOID_BLIND=1 on the held log -> 0 and no fs_holds= on the keys line (mutation); verdict counts void_holds>0 as a stall arm.
cd "$(git rev-parse --show-toplevel)" || exit 1
ROOT=$PWD; T=$(mktemp -d /tmp/s7462.XXXX); fail=0
chk(){ if [[ $2 == $3 ]]; then echo "ok   $1 ($2)"; else echo "FAIL $1 got '$2' want '$3'"; fail=$((fail+1)); fi; }
H=scratch/agent/m6_god_common.sh
F=$(awk '/^  fail\(\) \{ local lv=1 vs=""/{on=1} on{print} on&&/cp \$L \$OUT\/fail_att\$att.log; \}$/{exit}' $H)
[[ $F == *vilog_stalls* && $F == *M6_VOID_BLIND* ]] || { echo "FAIL fail() block not found in $H"; exit 1; }
grep -q '^void_holds=0$' $H || { echo "FAIL void_holds init missing"; fail=$((fail+1)); }
[ "$(grep -c 'void_holds=\$void_holds' $H)" = 3 ] || { echo "FAIL not all 3 summaries carry void_holds"; fail=$((fail+1)); }
run(){ # $1=log list (space sep) $2=M6_VOID_BLIND -> prints "void_holds|last keys line"
  zsh -c '
    ROOT=$1; OUT=$2; K=$OUT/k; : > $K; M6_VOID_BLIND=$3; void_holds=0; att=0; sleep 1000 & p=$!
    eval "$4"
    for L in ${=5}; do att=$((att+1)); fail nomission; sleep 1000 & p=$!; done; kill -9 $p 2>/dev/null
    echo "$void_holds|$(tail -1 $K)"' _ $ROOT $T $2 "$F" "$1"
}
mk(){ local i; : > $1; for i in $(seq 0 40); do echo "[vi] update_screen #$((i*64)) origin=0x0098B038 fs=$(( $2 ? 100+i : 273 ))" >> $1; done; }
mk $T/held.log 0; mk $T/adv.log 1
R=scratch/s61_death_repro/run4/vilines.txt; RN=scratch/agent/m6/g1_lvl1s7450fxP/fail_att1.log
[ ! -f $RN ] && [ -f $RN.zst ] && { zstd -dcq $RN.zst > $T/real_rn.log; RN=$T/real_rn.log; }  # s7802: retained as *.zst
r=$(run $T/held.log 0); chk "planted held void -> void_holds=1" "${r%%|*}" 1; chk "keys line carries fs_holds=1" "$([[ ${r#*|} == *fs_holds=1* ]] && echo y)" y
[ -f $R ] && { r=$(run $R 0); chk "REAL held log (s61 run4) -> 1" "${r%%|*}" 1; } || { echo "FAIL missing $R"; fail=$((fail+1)); }
r=$(run $T/adv.log 0); chk "advancing void -> 0 (neg ctl)" "${r%%|*}" 0
[ -f $RN ] && { r=$(run $RN 0); chk "REAL void log s7450 fxP att1 -> 0" "${r%%|*}" 0; } || echo "WARN real void log $RN absent"
r=$(run "$T/held.log $T/adv.log $T/held.log" 0); chk "held+adv+held voids sum -> 2" "${r%%|*}" 2
r=$(run $T/held.log 1); chk "mutation M6_VOID_BLIND=1 -> 0" "${r%%|*}" 0; chk "mutation keys line has no fs_holds" "$([[ ${r#*|} == *fs_holds* ]] && echo y || echo n)" n
V(){ printf '%s\n' "$1" > $T/v.log; zsh tools/agent/soak_verdict_fields.sh $T/v.log | grep -oE 'stall_arms=[0-9]+' ; }
chk "verdict void_holds=1 on a clean held arm -> stall" "$(V 'tag=a alive_at_end=1 crashlines=0 vi_stalls30s=0 void_holds=1 fs_holds=0')" stall_arms=1
chk "verdict void_holds=0 -> clean" "$(V 'tag=a alive_at_end=1 crashlines=0 vi_stalls30s=0 void_holds=0 fs_holds=0')" stall_arms=0
chk "verdict allattempts-failed void_holds=2 -> stall" "$(V 'tag=a allattempts-failed void_holds=2 deaths=0 fatal_total=0')" stall_arms=1
rm -rf $T; echo "result fail=$fail"; [ $fail = 0 ]
