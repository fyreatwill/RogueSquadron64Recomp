#!/bin/zsh
# s7253: test the harness clock gate. Extracts clk() and the refusal line from tools/g1e_owner_quiet_arms.zsh (so it tests the real
# text), then checks: real base -> ratio 0.9-1.1 and no refusal; CLK_MAX=0.5 -> refusal; a half-speed fake base -> ratio ~2 and refusal;
# missing base -> NA and no refusal; ALLOW_SLOW=1 -> no refusal. Exit 0 = all pass.
cd ${0:A:h}/..; H=tools/g1e_owner_quiet_arms.zsh; T=$(mktemp -d); fail=0
eval "$(grep -A1 '^clk(){' $H)"; gate=$(grep 'host clock capped' $H | sed 's/{ echo.*/{ print REFUSE; }/; s/^ *//')
ok(){ print "PASS $1"; }; bad(){ print "FAIL $1"; fail=1; }
TOOLS=$PWD/tools; [ -x $TOOLS/s7253_clkprobe ] || cc -O2 -o $TOOLS/s7253_clkprobe $TOOLS/s7253_clkprobe.c
run(){ ck=$(clk); out=$(eval "$gate"); print "  clk=$ck CLK_MAX=${CLK_MAX:-1.15} ALLOW_SLOW=${ALLOW_SLOW:-0} -> ${out:-run}"; }
run; [[ $ck != NA ]] && (( ck > 0.9 && ck < 1.1 )) && [[ -z $out ]] && ok "real base ~1.0, runs" || bad "real base"
CLK_MAX=0.5 run; [[ $out == REFUSE ]] && ok "CLK_MAX=0.5 refuses (positive control)" || bad "CLK_MAX=0.5"
ALLOW_SLOW=1 CLK_MAX=0.5 run; [[ -z $out ]] && ok "ALLOW_SLOW=1 overrides" || bad "ALLOW_SLOW"
mkdir -p $T/tools; cp tools/s7253_clkprobe $T/tools/; b=$(awk 'NR==1{print $1/2}' tools/s7253_clkprobe.base); echo $b > $T/tools/s7253_clkprobe.base
TOOLS=$T/tools run; (( ck > 1.8 && ck < 2.2 )) && [[ $out == REFUSE ]] && ok "half-speed base reads ~2 and refuses" || bad "half base"
rm $T/tools/s7253_clkprobe.base; TOOLS=$T/tools run; [[ $ck == NA && -z $out ]] && ok "missing base -> NA, runs" || bad "missing base"
rm -rf $T; exit $fail
