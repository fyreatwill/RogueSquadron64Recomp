#!/bin/zsh
# SOAK_TIMEOUT=1700
# s5728 re-aimed: bool 7 never fires (fired ids 0x61,0x62,0x5,0x3C,0x1A). Control: [objbool-sup] lines present.
# s5721 CLEAN save (aside copy) + ROGUESQ_NO_SAVE_WRITE; control: [lvsel] B2F != 9 (s5720 saw 9 from forced-run pollution). real-input (unforced) level-select route: control = [lvsel] init with B2F default, cursor ticks vary with sl/sr keys
# s5706 force unlock N=3 with masks recomputed (s5705 hook left a1/a2 stale). Control: [lvsel] init a1==1<<N
cd "$(git rev-parse --show-toplevel)" || exit 1
mkdir -p build/saves; cp build/saves_s4224_aside/rs64.n64.us.1.0.bin build/saves/rs64.n64.us.1.0.bin; rm -f build/saves/*.bak
EARLY=""; e=10; for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95; for i in $(seq 1 40); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 175 )) && break; done; for i in $(seq 1 100); do for k in a sl a su a sr a sd; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 900 )) && break; done; FL=${FL%,}
export AP_OVERRIDE="${EARLY}${FL}"
export TAG=s5728_supc STOP=0 HOLD=540 WAITN=170 MISSION_RE=62BD00
export XENV="ROGUESQ_SUPPRESS_BOOL=0x1A ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_LOG_OBJBOOL=1 ROGUESQ_LOG_HUDBIT=1"
exec zsh scratch/agent/m6_god_common.sh
