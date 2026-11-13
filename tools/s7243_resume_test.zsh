#!/bin/zsh
# s7243: test RESUME=1 in tools/g1e_owner_quiet_arms.zsh with a fake game (no window, no real binary).
# Cases: (1) fresh run launches all 3 arms; (2) RESUME=1 rerun launches none; (3) arm b voided (ok_b removed) -> only b relaunched;
# (4) negative control: binary changed (mtime) -> all 3 relaunch; (5) RESUME unset -> all 3 relaunch; (6) spec changed for c -> only c.
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$(mktemp -d /tmp/s7243rt.XXXX); mkdir -p $T/g $T/r; echo 999 > $T/idle
cat > $T/g/fake <<'G'
#!/bin/zsh
echo launch >> $LAUNCHES; echo 'cursorMask)=0x00000010'; exec /bin/sleep 30
G
chmod +x $T/g/fake; : > $T/launches
run(){ : > $T/launches; rm -f $T/r/arms.log; env LAUNCHES=$T/launches R=$T/r HOLD=2 ARM_GAP=0 DHZ=/usr/bin/true IDLE_FEED=$T/idle GAMEDIR=$T/g GAME=./fake \
  ARMS="4:a:ROGUESQ_FORCE_SAVE_MISSION=4 4:b:ROGUESQ_FORCE_SAVE_MISSION=4 4:c:ROGUESQ_FORCE_SAVE_MISSION=4$1" "${@:2}" zsh tools/g1e_owner_quiet_arms.zsh >/dev/null 2>&1; wc -l < $T/launches | tr -d ' '; }
fail=0; chk(){ if [[ $2 == $3 ]]; then echo "ok   $1 ($2)"; else echo "FAIL $1 got $2 want $3"; fail=$((fail+1)); fi; }
chk "fresh run launches 3" $(run "") 3
chk "resume, all ok, launches 0" $(run "" RESUME=1) 0
grep -c 'done alive=1' $T/r/arms.log | read n; chk "resume keeps one done line per arm" $n 3
rm -f $T/r/ok_b; chk "b voided -> 1 relaunch" $(run "" RESUME=1) 1
touch -t 202001010000 $T/g/fake; chk "neg control: binary changed -> 3" $(run "" RESUME=1) 3
chk "RESUME unset -> 3" $(run "") 3
chk "spec of c changed -> 1" $(run "+X=1" RESUME=1) 1
# s7256 VOID_OK_AFTER: idle falls at ~5 s during arm a (HOLD=20). (7) VOID_OK_AFTER=2 -> ok_a kept, exit 2, RESUME rerun launches only b; (8) void before VOID_OK_AFTER / unset -> not kept.
latevoid(){ rm -f $T/r/ok_*(N); echo 999 > $T/idle; ( /bin/sleep 5; echo 0 >> $T/idle ) & : > $T/launches; rm -f $T/r/arms.log
  env LAUNCHES=$T/launches R=$T/r HOLD=20 ARM_GAP=0 DHZ=/usr/bin/true IDLE_FEED=$T/idle GAMEDIR=$T/g GAME=./fake VOID_OK_AFTER=$1 \
    ARMS="4:a:ROGUESQ_FORCE_SAVE_MISSION=4 4:b:ROGUESQ_FORCE_SAVE_MISSION=4" zsh tools/g1e_owner_quiet_arms.zsh >/dev/null 2>&1; echo $?; wait; echo 999 > $T/idle; }
chk "late void exits 2" $(latevoid 2) 2
[ -e $T/r/ok_a ] && r=kept || r=none; chk "late void (t>=2) keeps ok_a" $r kept
grep -c 'latevoid=t' $T/r/arms.log | read n; chk "latevoid done line" $n 1
chk "resume after late void launches only b" $(: > $T/launches; env LAUNCHES=$T/launches R=$T/r HOLD=20 ARM_GAP=0 DHZ=/usr/bin/true IDLE_FEED=$T/idle GAMEDIR=$T/g GAME=./fake RESUME=1 VOID_OK_AFTER=2 ARMS="4:a:ROGUESQ_FORCE_SAVE_MISSION=4 4:b:ROGUESQ_FORCE_SAVE_MISSION=4" zsh tools/g1e_owner_quiet_arms.zsh >/dev/null 2>&1; wc -l < $T/launches | tr -d ' ') 1
latevoid 100 >/dev/null; [ -e $T/r/ok_a ] && r=kept || r=none; chk "neg control: early void (t<100) not kept" $r none
latevoid "" >/dev/null; [ -e $T/r/ok_a ] && r=kept || r=none; chk "VOID_OK_AFTER unset: not kept" $r none
rm -rf $T; echo "failures: $fail"; exit $((fail > 0))
