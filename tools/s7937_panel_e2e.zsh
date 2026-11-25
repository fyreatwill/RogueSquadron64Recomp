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
# s7939: env PANEL_ASPECT=<16:9|...> PANEL_FS=<0|1> run the same checks in the owner's high-DPI window / fullscreen
#   (ASPECT or FULLSCREEN set -> SDL_WINDOW_ALLOW_HIGHDPI, drawable = 2x window points on Retina). Adds check D1:
#   ImGui DisplaySize == CG window content size in points (H-scale would log drawable pixels instead).
# s7940: env PANEL_F1=1 presses F1 (RT64 developer inspector) BEFORE F6 and adds checks
#   I1 F1 reaches OUR PollEvent unconsumed and RT64's SDL filter never installed (no "[RT64] sdlEventFilter NOW installed"):
#      on macOS that filter (sdlWindow!=null) is the only route to the inspector, so it cannot open (s7940: the pixel-diff
#      version of this check passed on the animating intro alone with NO overlay drawn - never use pixel diffs here);
#   X1 40 HID clicks on inert panel cells with F1 pressed arm nothing and the game survives;
#   F2 a second F1 after the panel closed also reaches PollEvent (nothing grabbed the key in between).
# Needs: unlocked screen, Accessibility trust for this shell (build/winctl trusted), no other game instance.
cd "$(git rev-parse --show-toplevel)" || exit 2
O=${1:-$PWD/scratch/s7937/run}; [[ $O == /* ]] || O=$PWD/$O; rm -rf $O; mkdir -p $O
MODE=${CLICK_MODE:-hid}  # pid-posted clicks never reach SDL (s7937: C1 FAIL 1/1), keys do
W=$PWD/build/winctl
$W trusted >/dev/null || { echo "VOID: winctl not trusted"; exit 2; }
pgrep -x RogueSquadron64Recomp >/dev/null && { echo "VOID: game already running"; exit 2; }
LOG=$O/game.log; J=$O/controls.json
cd build || exit 2
env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_SETTINGS=0 ROGUESQ_FULLSCREEN=${PANEL_FS:-0} ${PANEL_ASPECT:+ROGUESQ_ASPECT=$PANEL_ASPECT} \
    ROGUESQ_PANEL_RECTS=1 ROGUESQ_CONTROLS=$J ./RogueSquadron64Recomp rogue_squadron.z64 > $LOG 2>&1 &
PID=$!
cd ..
trap 'kill -9 $PID 2>/dev/null' EXIT
typeset -A R
res() { R[$1]=$2; echo "$1 $2 ${3:-}"; }
cnt() { grep -c -- "$1" $LOG 2>/dev/null || true; }
waitfor() {  # pattern, min count, timeout s
  local i=0; while (( i < $3 * 10 )); do (( $(cnt "$1") >= $2 )) && return 0; sleep 0.1; ((i++)); done; return 1; }
sleep ${PANEL_BOOT_S:-20}
kill -0 $PID 2>/dev/null || { echo "VOID: game died at boot"; exit 1; }
read WID BX BY BW BH <<< "$($W find $PID)"
# winctl activate is a no-op on macOS 14+ (activateWithOptions ignoringOtherApps), and pid-posted keys only reach SDL
# while the game is the active app (s7937 probe: Chrome front -> F6 0/1; game front -> 1/1), so raise it via System Events.
osascript -e "tell application \"System Events\" to set frontmost of (first process whose unix id is $PID) to true" >/dev/null; sleep 1
FRONT=$(osascript -e 'tell application "System Events" to get unix id of first process whose frontmost is true')
[[ $FRONT == $PID ]] || { echo "VOID: game not frontmost (front=$FRONT)"; exit 2; }
echo "window id=$WID bounds=$BX,$BY ${BW}x$BH mode=$MODE f1=${PANEL_F1:-0}"
F1=${PANEL_F1:-0}
f1n() { cnt 'SDL_KEYDOWN sym=1073741882 (F1) reached PollEvent'; }
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
if (( F1 )); then  # I1: F1 reaches our poll, RT64 filter absent
  $W key $PID 122 200; waitfor 'F1) reached PollEvent' 1 4; sleep 1
  ins=$(cnt 'sdlEventFilter NOW installed'); (( $(f1n) == 1 && ins == 0 )) && res I1 PASS "f1_polled=$(f1n) rt64_filter=$ins" || res I1 FAIL "f1_polled=$(f1n) rt64_filter=$ins"
fi
# K1: F6 opens
$W key $PID 97 200
waitfor '\[controls-panel\] open' 1 5 && waitfor '^\[panel-rect\]' 1 5 && res K1 PASS || res K1 FAIL
sleep 1; grep '^\[panel-rect\]' $LOG | tail -1
read WID BX BY BW BH <<< "$($W find $PID)"   # re-read: fullscreen/resize may have settled since boot
disp=$(grep '^\[panel-rect\]' $LOG | tail -1 | sed 's/.*disp=\([0-9x]*\).*/\1/')
dw=${disp%x*}; dh=${disp#*x}
# content = full width, bottom-aligned (title bar, if any, on top): width must match, height within title-bar slack
(( dw == BW && dh <= BH && BH - dh <= 40 )) && res D1 PASS "disp=$disp bounds=${BW}x$BH" || res D1 FAIL "disp=$disp bounds=${BW}x$BH"
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
if (( F1 )); then  # X1: click storm on inert cells (N64 label column) with both overlays open
  a0=$(cnt 'capture armed'); read AX AY <<< "$(pt bindA)"
  for i in {1..40}; do read QX QY <<< "$(python3 -c "print($BX+($AX-$BX)*(0.15+0.25*(($i*7)%10)/10), $AY+($i%5)*3)")"; $W click $PID $QX $QY $MODE; done
  sleep 1; kill -0 $PID 2>/dev/null && (( $(cnt 'capture armed') == a0 )) && res X1 PASS "armed+$(( $(cnt 'capture armed') - a0 ))" || res X1 FAIL "alive=$(kill -0 $PID 2>/dev/null && echo 1 || echo 0) armed+$(( $(cnt 'capture armed') - a0 ))"
fi
# K2: Esc closes
sleep 0.5; $W key $PID 53 200
waitfor '\[controls-panel\] closed' 1 4 && res K2 PASS || res K2 FAIL
if (( F1 )); then  # F2: second F1 after F6 closed
  $W key $PID 122 200; waitfor 'F1) reached PollEvent' 2 4 && res F2 PASS "f1_polled=$(f1n)" || res F2 FAIL "f1_polled=$(f1n)"
fi
sleep 1; kill -0 $PID 2>/dev/null && alive=1 || alive=0
kill -9 $PID 2>/dev/null
KS=(D1 N1 K1 N2 C1 C2 S1 R1 K2); (( F1 )) && KS+=(I1 X1 F2)
bad=0; for k in $KS; do [[ ${R[$k]} == PASS ]] || bad=$((bad+1)); done
echo "tag=s7937_panel_e2e mode=$MODE aspect=${PANEL_ASPECT:-retail} fs=${PANEL_FS:-0} win=${BW}x$BH disp=$disp f1=$F1 alive=$alive checks=${#KS} fail=$bad"
(( bad == 0 && alive == 1 ))
