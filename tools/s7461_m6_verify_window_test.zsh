#!/bin/zsh
# s7461 class DQ: m6_god_common.sh's live stall poller started only after the 130 s mission-verify sleep, so the s7460 planted
# hold (120-160 s, mission gate at 72 s) read vi_stalls30s=0 while offline fs_holds=1. This runs the harness's own verify-window
# block (extracted verbatim) on fake logs with simulated time (sleep shim advances SECONDS):
#   held fs log -> stalls>=1; advancing fs log -> 0 (neg ctl); M6_VERIFY_BLIND=1 (old sleep 130) on the held log -> 0 (mutation).
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$(mktemp -d /tmp/s7461.XXXX); fail=0
chk(){ if [[ $2 == $3 ]]; then echo "ok   $1 ($2)"; else echo "FAIL $1 got '$2' want '$3'"; fail=$((fail+1)); fi; }
H=scratch/agent/m6_god_common.sh
B=$(awk '/^  # s7459 class DO: \[vi\] update_screen rows/{on=1} on{print} on&&/^  else for n in .*vtick; done; fi$/{exit}' $H)
[[ $B == *vtick* && $B == *M6_VERIFY_BLIND* ]] || { echo "FAIL verify-window block not found in $H"; exit 1; }
run(){ # $1=advance(0/1) $2=M6_VERIFY_BLIND
  zsh -c '
    L=$1; K=$2/k; p=$$; t0=0; ADV=$3; M6_VERIFY_BLIND=$4; i=0
    sleep(){ SECONDS=$((SECONDS+$1)); i=$((i+1)); echo "[vi] update_screen #$((i*64)) origin=0x0098B038 fs=$((ADV ? 100+i : 273))" >> $L; }
    eval "$5"; echo $stalls' _ $T/log.$1$2 $T $1 $2 "$B"
}
for a in 0 1; do for m in 0 1; do echo "[vi] update_screen #0 origin=0x0098B038 fs=273" > $T/log.$a$m; done; done
s=$(run 0 0); chk "held fs in verify window -> stall" "$([ "$s" -ge 1 ] 2>/dev/null && echo stall || echo "none($s)")" stall
s=$(run 1 0); chk "advancing fs in verify window -> 0 (neg ctl)" "$s" 0
s=$(run 0 1); chk "mutation M6_VERIFY_BLIND=1: held log unscored" "$s" 0
rm -rf $T; echo "result fail=$fail"; [ $fail = 0 ]
