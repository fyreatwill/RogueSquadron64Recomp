#!/bin/zsh
# s7937: F6 controls panel driven end to end with REAL OS events (CGEvent keys + mouse clicks via build/winctl), not the
# ROGUESQ_BIND_PANEL_TEST / PANEL_TEST_WINDOW hooks. Checks, in one run:
#   N1 panel closed: a click on the (future) Bind-A spot and a P press arm nothing
#   K1 F6 key opens the panel                     ([controls-panel] open)
#   N2 click on a non-button cell arms nothing    (negative control for the click path)
#   C1 click Bind on row A arms capture           ([controls] capture armed target=<A>)
#   C2 P key is captured                          ([controls] captured ... src=key:P)
#   S1 click Save writes the file, A = ["key:P"]  (explicit ROGUESQ_CONTROLS path under scratch/, owner files untouched)
#   R1 click Reset, Save again: A back to defaults
#   K2 Esc closes the panel                       ([controls-panel] closed)
# Usage: zsh tools/s7937_panel_e2e.zsh [outdir]   env CLICK_MODE=hid|pid (default hid; moves the real cursor)
# Needs: unlocked screen, Accessibility trust for this shell (build/winctl trusted), no other game instance.
cd "$(git rev-parse --show-toplevel)" || exit 2
O=${1:-$PWD/scratch/s7937/run}; rm -rf $O; mkdir -p $O
MODE=${CLICK_MODE:-hid}  # pid-posted clicks never reach SDL (s7937: C1 FAIL 1/1), keys do
W=$PWD/build/winctl
$W trusted >/dev/null || { echo "VOID: winctl not trusted"; exit 2; }
pgrep -x RogueSquadron64Recomp >/dev/null && { echo "VOID: game already running"; exit 2; }
LOG=$O/game.log; J=$O/controls.json
cd build || exit 2
env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_SETTINGS=0 ROGUESQ_FULLSCREEN=0 \
    ROGUESQ_PANEL_RECTS=1 ROGUESQ_CONTROLS=$J ./RogueSquadron64Recomp rogue_squadron.z64 > $LOG 2>&1 &
PID=$!
cd ..
trap 'kill -9 $PID 2>/dev/null' EXIT
typeset -A R
res() { R[$1]=$2; echo "$1 $2 ${3:-}"; }
cnt() { grep -c -- "$1" $LOG 2>/dev/null || true; }
waitfor() {  # pattern, min count, timeout s
  local i=0; while (( i < $3 * 10 )); do (( $(cnt "$1") >= $2 )) && return 0; sleep 0.1; ((i++)); done; return 1; }
sleep 20
kill -0 $PID 2>/dev/null || { echo "VOID: game died at boot"; exit 1; }
read WID BX BY BW BH <<< "$($W find $PID)"
# winctl activate is a no-op on macOS 14+ (activateWithOptions ignoringOtherApps), and pid-posted keys only reach SDL
# while the game is the active app (s7937 probe: Chrome front -> F6 0/1; game front -> 1/1), so raise it via System Events.
osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $PID) to true" >/dev/null; sleep 1
FRONT=$(osascript -e 'tell application "System Events" to get unix id of first process whose frontmost is true')
[[ $FRONT == $PID ]] || { echo "VOID: game not frontmost (front=$FRONT)"; exit 2; }
echo "window id=$WID bounds=$BX,$BY ${BW}x$BH mode=$MODE"
# panel rects arrive in window points; content origin = bottom-aligned inside the CG bounds (title bar on top)
pt() {  # name -> "gx gy" (centre of the logged rect, global screen points)
  local line=$(grep '^\[panel-rect\]' $LOG | tail -1)
  local disp=${${line#*disp=}%% *}; local dh=${disp#*x}
  local r=${${line#* $1=}%% *}; local a=(${(s:,:)r})
  python3 -c "print($BX+($a[1]+$a[3])/2, $BY+$BH-$dh+($a[2]+$a[4])/2)"; }
arm0=$(cnt 'capture armed'); cap0=$(cnt 'captured target')
# N1: panel closed. Click roughly where Bind-A will be (centre-left of window) and press P.
$W click $PID $((BX+BW/2)) $((BY+BH/2)) $MODE; $W key $PID 35 200; sleep 1.5
(( $(cnt 'capture armed') == arm0 && $(cnt 'captured target') == cap0 && $(cnt '\[controls-panel\] open') == 0 )) && res N1 PASS || res N1 FAIL
# K1: F6 opens
$W key $PID 97 200
waitfor '\[controls-panel\] open' 1 5 && waitfor '^\[panel-rect\]' 1 5 && res K1 PASS || res K1 FAIL
sleep 1; grep '^\[panel-rect\]' $LOG | tail -1
read AX AY <<< "$(pt bindA)"
# N2: click in the Inputs cell of row A (left of the Bind button), must arm nothing
read LX LY <<< "$(python3 -c "print($BX+($AX-$BX)*0.6, $AY)")"
$W click $PID $LX $LY $MODE; sleep 1.5
(( $(cnt 'capture armed') == arm0 )) && res N2 PASS || res N2 FAIL
# C1: click Bind (row A)
$W click $PID $AX $AY $MODE
waitfor 'capture armed target=' $((arm0+1)) 4 && res C1 PASS "$(grep 'capture armed' $LOG | tail -1)" || res C1 FAIL
# C2: press P
sleep 0.5; $W key $PID 35 250
waitfor 'captured target=.*src=key:P' 1 4 && res C2 PASS "$(grep 'captured target' $LOG | tail -1)" || res C2 FAIL
# S1: Save
sleep 0.5; read SX SY <<< "$(pt save)"; $W click $PID $SX $SY $MODE
waitfor "\[controls\] Saved to $J" 1 4 && cp $J $O/after_bind.json && \
  python3 -c "import json,sys;d=json.load(open('$O/after_bind.json'));sys.exit(0 if d['buttons'].get('A')==['key:P'] else 1)" \
  && res S1 PASS "$(python3 -c "import json;print('A=',json.load(open('$O/after_bind.json'))['buttons'].get('A'))")" || res S1 FAIL
# R1: Reset then Save
sleep 0.5; read RX RY <<< "$(pt reset)"; $W click $PID $RX $RY $MODE
waitfor 'table set (panel reset)' 1 4; sleep 0.5; read SX SY <<< "$(pt save)"; $W click $PID $SX $SY $MODE
waitfor "\[controls\] Saved to $J" 2 4 && cp $J $O/after_reset.json && \
  python3 -c "import json,sys;d=json.load(open('$O/after_reset.json'));a=d['buttons'].get('A');sys.exit(0 if a and 'key:P' not in a else 1)" \
  && res R1 PASS "$(python3 -c "import json;print('A=',json.load(open('$O/after_reset.json'))['buttons'].get('A'))")" || res R1 FAIL
# K2: Esc closes
sleep 0.5; $W key $PID 53 200
waitfor '\[controls-panel\] closed' 1 4 && res K2 PASS || res K2 FAIL
sleep 1; kill -0 $PID 2>/dev/null && alive=1 || alive=0
kill -9 $PID 2>/dev/null
bad=0; for k in N1 K1 N2 C1 C2 S1 R1 K2; do [[ ${R[$k]} == PASS ]] || bad=$((bad+1)); done
echo "tag=s7937_panel_e2e mode=$MODE alive=$alive checks=8 fail=$bad"
(( bad == 0 && alive == 1 ))
