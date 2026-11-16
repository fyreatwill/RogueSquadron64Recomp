#!/bin/zsh
# s7453 class DI: fake-binary controls for the two live launchers that used to pass a dead game.
# tools/boot_freeze_hunt.sh: (1) fatal-text death -> exit 1, EXITED exitrc=1 crash=1; (2) silent exit 0 -> exit 1, EXITED crash=0;
#   (3) live game -> exit 0, OK (negative control). tools/g1e_owner_quiet_arms.zsh: (4) fatal death -> exit 1, done alive=0 fatal=1;
#   (5) silent death -> exit 1 alive=0 fatal=0; (6) live -> exit 0 alive=1 fatal=0. Then tools/s7243_resume_test.zsh must still pass.
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$(mktemp -d /tmp/s7453dt.XXXX); mkdir -p $T/g $T/r; echo 999 > $T/idle
printf '#!/bin/zsh\necho "[vi] fs=1"; echo "cursorMask)=0x00000010"; /bin/sleep 3; echo "Exiting with exit status '"'"'1'"'"'. Function f, at file x:1"; exit 1\n' > $T/g/die
printf '#!/bin/zsh\necho "[vi] fs=1"; echo "cursorMask)=0x00000010"; /bin/sleep 3; exit 0\n' > $T/g/silent
printf '#!/bin/zsh\necho "cursorMask)=0x00000010"; for i in $(seq 1 60); do echo "[vi] fs=$((i*20))"; /bin/sleep 1; done\n' > $T/g/live
chmod +x $T/g/*; fail=0
chk(){ if [[ $2 == $3 ]]; then echo "ok   $1 ($2)"; else echo "FAIL $1 got '$2' want '$3'"; fail=$((fail+1)); fi; }
bfh(){ env GAMEDIR=$T/g GAME=./$1 zsh tools/boot_freeze_hunt.sh $T/b_$1 1 20 12 > $T/b_$1.out 2>&1; echo $?; }
chk "bfh fatal death exit" $(bfh die) 1;     chk "bfh fatal line" "$(grep -o 'crash=[0-9]* EXITED exitrc=[0-9]*' $T/b_die.out)" "crash=1 EXITED exitrc=1"
chk "bfh silent death exit" $(bfh silent) 1; chk "bfh silent line" "$(grep -o 'crash=[0-9]* EXITED exitrc=[0-9]*' $T/b_silent.out)" "crash=0 EXITED exitrc=0"
chk "bfh live exit (neg ctl)" $(bfh live) 0; chk "bfh live line" "$(grep -o 'crash=[0-9]* [A-Z]*' $T/b_live.out)" "crash=0 OK"
qa(){ rm -f $T/r/arms.log $T/r/ok_*(N); env R=$T/r HOLD=6 ARM_GAP=0 DHZ=/usr/bin/true IDLE_FEED=$T/idle GAMEDIR=$T/g GAME=./$1 \
  ARMS="4:a:ROGUESQ_FORCE_SAVE_MISSION=4" zsh tools/g1e_owner_quiet_arms.zsh > $T/q_$1.out 2>&1; echo $?; }
chk "quiet fatal death exit" $(qa die) 1;     chk "quiet fatal line" "$(grep -o 'alive=[01] log= *[0-9]* fatal=[0-9]*' $T/r/arms.log | sed -E 's/log= *[0-9]+ //')" "alive=0 fatal=1"
chk "quiet silent death exit" $(qa silent) 1; chk "quiet silent line" "$(grep -o 'alive=[01] log= *[0-9]* fatal=[0-9]*' $T/r/arms.log | sed -E 's/log= *[0-9]+ //')" "alive=0 fatal=0"
chk "quiet live exit (neg ctl)" $(qa live) 0; chk "quiet live line" "$(grep -o 'alive=[01] log= *[0-9]* fatal=[0-9]*' $T/r/arms.log | sed -E 's/log= *[0-9]+ //')" "alive=1 fatal=0"
# s7457 class DM: each launcher's stdout (= the soak log) carries a tag= line, and the loop verdict scores it per arm.
V(){ zsh tools/agent/soak_verdict_fields.sh $1 | grep -oE 'arms=[0-9]+ alive=[0-9/]+ crash_arms=[0-9]+ stall_arms=[0-9]+' ; }
VN(){ zsh tools/agent/soak_verdict_fields.sh $1 | grep -oE 'stall_na=[0-9]+'; }
chk "verdict bfh die"    "$(V $T/b_die.out)"    "arms=1 alive=0/1 crash_arms=1 stall_arms=0"
chk "verdict bfh silent" "$(V $T/b_silent.out)" "arms=1 alive=0/1 crash_arms=0 stall_arms=0"
chk "verdict bfh live"   "$(V $T/b_live.out)"   "arms=1 alive=1/1 crash_arms=0 stall_arms=0"
chk "bfh live has a stall measure" "$(VN $T/b_live.out)" "stall_na=0"
chk "verdict quiet die"    "$(V $T/q_die.out)"    "arms=1 alive=0/1 crash_arms=1 stall_arms=0"
chk "verdict quiet silent" "$(V $T/q_silent.out)" "arms=1 alive=0/1 crash_arms=0 stall_arms=0"
chk "verdict quiet live"   "$(V $T/q_live.out)"   "arms=1 alive=1/1 crash_arms=0 stall_arms=0"
chk "quiet live: no VI stream -> stall_na=1" "$(VN $T/q_live.out)" "stall_na=1"
chk "quiet live level_ok=1" "$(grep -o 'level_ok=[0-9a-z]*' $T/q_live.out)" "level_ok=1"
# frozen boot: the game stops advancing fs -> FROZEN -> frozen=1 -> stall_arms=1
printf '#!/bin/zsh\necho "cursorMask)=0x00000010"; echo "[vi] fs=300"; exec /bin/sleep 60\n' > $T/g/frozen; chmod +x $T/g/frozen
bfh frozen >/dev/null; chk "verdict bfh frozen" "$(V $T/b_frozen.out)" "arms=1 alive=1/1 crash_arms=0 stall_arms=1"
# mutation control: the same launcher with its tag line removed must read arms=0 (the check above would then fail)
sed 's/^  al=1; \[\[ $st == EXITED/  : al=1; [[ $st == EXITED/; s/echo "tag=boot/: "tag=boot/' tools/boot_freeze_hunt.sh > $T/bfh_mut.sh
env GAMEDIR=$T/g GAME=./live zsh $T/bfh_mut.sh $T/b_mut 1 20 12 > $T/b_mut.out 2>&1
chk "mutation: bfh without tag line -> arms=0" "$(V $T/b_mut.out)" "arms=0 alive=0/0 crash_arms=0 stall_arms=0"
sed 's/tagline \$arm "\$dl" \$lok;/:;/' tools/g1e_owner_quiet_arms.zsh > $T/qa_mut.zsh
rm -f $T/r/arms.log $T/r/ok_*(N); env R=$T/r HOLD=6 ARM_GAP=0 DHZ=/usr/bin/true IDLE_FEED=$T/idle GAMEDIR=$T/g GAME=./live \
  ARMS="4:a:ROGUESQ_FORCE_SAVE_MISSION=4" TOOLS_OVERRIDE=1 zsh $T/qa_mut.zsh > $T/q_mut.out 2>&1
chk "mutation: quiet without tagline -> arms=0" "$(V $T/q_mut.out)" "arms=0 alive=0/0 crash_arms=0 stall_arms=0"
zsh tools/s7243_resume_test.zsh > $T/rt.out 2>&1; chk "s7243 resume test still passes" $? 0
rm -rf $T; echo "failures: $fail"; exit $((fail > 0))
