#!/bin/zsh
# s7454 class DJ: m6_god_common.sh restarts() must count same-process mission re-inits ([initMission] call#>=2) and
# nothing else. Cases: synthetic, plus the real s7449 L4 (call#1 + call#2 after endMissionCleanup -> 1) and L10 (-> 0)
# logs when present. Mutation control: a call#>=1 variant must FAIL the same cases, so the test can see a wrong counter.
ROOT=$(git -C ${0:A:h} rev-parse --show-toplevel); T=$(mktemp -d); pass=0; failn=0
eval "$(grep '^restarts() ' $ROOT/scratch/agent/m6_god_common.sh)"
eval "$(grep '^restarts() ' $ROOT/scratch/agent/m6_god_common.sh | sed 's/^restarts()/mut()/; s/>= 2/>= 1/')"
printf '[initMission] call#1 a\n[initMission] call#2 b\n' > $T/one; printf '[initMission] call#1 a\n' > $T/zero
printf 'x [initMission] call#2 not-at-bol\n[initMission] call#1 a\n[initMission] call#10 c\n' > $T/edge; : > $T/empty
cases=($T/one:1 $T/zero:0 $T/edge:1 $T/empty:0)
L4=$ROOT/scratch/agent/m6/g1_lvl4s7449argck/run.log; L10=$ROOT/scratch/agent/m6/g1_lvl10s7449argck/run.log
# s7802: the real logs are retained as *.zst; a missing raw file used to drop these cases silently
for v in L4 L10; do f=${(P)v}; [ ! -f $f ] && [ -f $f.zst ] && { zstd -dcq $f.zst > $T/real_$v.log; typeset $v=$T/real_$v.log; }; done
[ -f $L4 ] && cases+=($L4:1) || echo "WARN real L4 log absent"; [ -f $L10 ] && cases+=($L10:0) || echo "WARN real L10 log absent"
mutfail=0
for c in $cases; do f=${c%:*}; want=${c##*:}; got=$(restarts $f)
  if [ "$got" = "$want" ]; then pass=$((pass+1)); else failn=$((failn+1)); echo "FAIL ${f:t} want=$want got=$got"; fi
  [ "$(mut $f)" = "$want" ] || mutfail=$((mutfail+1)); done
echo "restarts: $pass/${#cases} pass; mutation control caught on $mutfail/${#cases} cases"
rm -rf $T; [ $failn = 0 ] && [ $mutfail -gt 0 ]
