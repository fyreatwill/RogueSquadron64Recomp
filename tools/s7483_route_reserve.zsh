#!/bin/zsh
# s7483 item 1a gap 2: the s7482 retarget-pool reservation (ROGUESQ_RETARGET_RESERVE, default on) over the owner hangar
# abort/re-entry route (s7326/s7469 schedule: 4 mission loads, 3 PAUSE/ABORT -> SELECT YOUR CRAFT re-entries) at the owner
# recipe FPS60 dd8 21:9 WIDEWIN, on the normal build. Two arms in one invocation, same build, same schedule, run one after
# the other (one game at a time): on (default) and off (ROGUESQ_RETARGET_RESERVE=0). ROGUESQ_S7482_CTL=1 in both arms
# (pool-collide detector CONTROL line). The owner save in build/saves is used read-only (g3_port_capture forces
# ROGUESQ_NO_SAVE_WRITE=1; no SAVE_FROM, so nothing is swapped).
# Per arm: hangar entries, initMission calls, reserve applied/skipped, collide CONTROL/hits, "[spill] arena full", spill reuse,
# crash lines, last VI. Hypotheses: H-route-clean (on arm: alive, 0 collide, 0 arena full, same leg counts as off) vs
# H-route-shrink (on arm only: arena full / rs_malloc NULL / crash at a re-entry carve).
# usage: tools/s7483_route_reserve.zsh [outname] ; exit 0 = H-route-clean, 1 = on-arm regression, 3 = control blind / route
# unreached (no reserve line in the on arm, or legs < 4 in either arm), 4 = screen locked.
cd "$(git rev-parse --show-toplevel)" || exit 1
N=${1:-r}; R=$PWD/scratch/s7483/$N; rm -rf $R; mkdir -p $R
AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,70:start,76:start,82:start,180:start,184:down,188:a,192:left,195:a,210:a,218:start,224:start,232:a,238:start,244:start,250:start,330:start,334:down,338:a,342:left,345:a,360:a,368:start,374:start,382:a,388:start,394:start,400:start,480:start,484:down,488:a,492:left,495:a,510:a,518:start,524:start,532:a,538:start,544:start,550:start
BASE="ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=8 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_WIDEWIN=1 ROGUESQ_ASPECT=21:9 ROGUESQ_S7326_CTL=1 ROGUESQ_S7482_CTL=1"
for a in on off; do
  X=$BASE; [ $a = off ] && X="$X ROGUESQ_RETARGET_RESERVE=0"
  env SECS=${SECS:-620} CAP0=99999 AP=$AP XE="$X" zsh tools/g3_port_capture.sh $R/$a > $R/cap_$a.txt 2>&1
  grep -q LOCKED $R/cap_$a.txt && { echo "s7483 arm=$a LOCKED"; exit 4; }
done
rc=0
for a in on off; do
  L=$R/$a/run.log
  he=$(grep -a -c 'hangarmenu-a0-entry' $L); im=$(grep -a -c 'initMission\] call' $L)
  ap=$(grep -a -c '\[s7482\] reserve applied' $L); sk=$(grep -a -c '\[s7482\] reserve skipped' $L)
  ct=$(grep -a -c '\[s7482\] pool-collide CONTROL' $L); co=$(grep -a '\[s7482\] pool-collide' $L | grep -a -v -c CONTROL)
  af=$(grep -a -c 'arena full' $L); ru=$(grep -a -c '\[spill\] reuse' $L)
  cr=$(grep -a -c 'CRASH\|SIGSEGV\|SIGBUS\|Assertion\|abort()' $L)
  vi=$(grep -a -o 'VI #[0-9]*' $L | tail -1)
  echo "tag=s7483_$a hangar_entries=$he initMission=$im reserve_applied=$ap reserve_skipped=$sk collide_ctl=$ct collide=$co arena_full=$af spill_reuse=$ru crashlines=$cr last=${vi:-none}"
  eval "IM_$a=$im AP_$a=$ap CO_$a=$co AF_$a=$af CR_$a=$cr"
done
grep -a '\[s7482\] reserve' $R/on/run.log | head -8
(( CO_on > 0 || CR_on > CR_off || AF_on > AF_off )) && rc=1
(( rc == 0 && ( AP_on == 0 || IM_on < 4 || IM_off < 4 ) )) && rc=3
echo "s7483 score=$rc"; exit $rc
