#!/bin/zsh
# s7358 class AI runtime arms: ROGUESQ_DRAW_DISTANCE values on the s7326 hangar->mission route (dd8 21:9 bundle, owner save
# read-only, no SAVE_FROM). The last ROGUESQ_DRAW_DISTANCE on the env line wins.
#   ctl  8    -> "[dd] multiplier 8", tile pool k=128 (the qualified ceiling)
#   d12  12   -> pre-fix: tile pool k=288 (ceil(dd)^2*2 unclamped; terrain itself is clamped to 8) ; post-fix: k=128 + [s7358-env]
#   nan  nan  -> pre-fix: terrain multiplier nan ; post-fix: [s7358-env] unparseable -> retail (dd1)
#   typo x4   -> pre-fix: atof 0 -> terrain multiplier 0.25 silently ; post-fix: [s7358-env] unparseable -> retail
# usage: zsh tools/s7358_arms.zsh <tag> [arm ...]
R=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp; cd $R; T=$1; shift
typeset -A V; V=(ctl 8 d12 12 nan nan typo x4)
arms=($@); (( $#arms )) || arms=(ctl d12 nan typo)
for a in $arms; do
  env SECS=${SECS:-130} zsh scratch/s7326/run.zsh s7358_${T}_$a "ROGUESQ_DRAW_DISTANCE=${V[$a]}" >/dev/null 2>&1
  L=scratch/s7326/s7358_${T}_$a/run.log
  echo "$T $a dd=${V[$a]} mult=[$(grep -a -m1 '\[dd\] ROGUESQ_DRAW_DISTANCE multiplier' $L | awk '{print $NF}')] tilek=[$(grep -a '\[s6893\] tile pool entries' $L | sed 's/.*k=//;s/)//' | sort -u | tr '\n' ' ')] bundle=[$(grep -a -m1 '\[ddbundle\] dd=' $L | cut -c1-40)] s7358=$(grep -a -c '\[s7358-env\]' $L) arenafull=$(grep -a -c 'arena full' $L) nullmalloc=$(grep -a -c 'rs_malloc.*NULL\|returned NULL' $L) crash=$(grep -a -c 'CRASH\|SIGSEGV\|SIGBUS\|caught signal' $L) lines=$(wc -l < $L)"
  grep -a -m2 '\[s7358-env\]' $L
done
