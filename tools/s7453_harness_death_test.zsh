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
  ARMS="4:a:ROGUESQ_FORCE_SAVE_MISSION=4" zsh tools/g1e_owner_quiet_arms.zsh >/dev/null 2>&1; echo $?; }
chk "quiet fatal death exit" $(qa die) 1;     chk "quiet fatal line" "$(grep -o 'alive=[01] log= *[0-9]* fatal=[0-9]*' $T/r/arms.log | sed -E 's/log= *[0-9]+ //')" "alive=0 fatal=1"
chk "quiet silent death exit" $(qa silent) 1; chk "quiet silent line" "$(grep -o 'alive=[01] log= *[0-9]* fatal=[0-9]*' $T/r/arms.log | sed -E 's/log= *[0-9]+ //')" "alive=0 fatal=0"
chk "quiet live exit (neg ctl)" $(qa live) 0; chk "quiet live line" "$(grep -o 'alive=[01] log= *[0-9]* fatal=[0-9]*' $T/r/arms.log | sed -E 's/log= *[0-9]+ //')" "alive=1 fatal=0"
zsh tools/s7243_resume_test.zsh > $T/rt.out 2>&1; chk "s7243 resume test still passes" $? 0
rm -rf $T; echo "failures: $fail"; exit $((fail > 0))
