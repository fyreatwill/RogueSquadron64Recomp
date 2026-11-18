#!/bin/zsh
# s7598 class AZ-1 runtime witness: boot to attract/title, one game at a time, each arm in scratch/s7598/w/<arm> (symlinked
# binary + ROMs, NO owner save, ROGUESQ_NO_SAVE_WRITE=1). Plant = ROGUESQ_S7598_PLANT=N (SETTILE masks=maskt=15 + wrap for
# 4096 calls from the Nth), arms: ctl (no plant), old (plant + ROGUESQ_S7598_MASK=0), new (plant, clamp on).
cd "$(git rev-parse --show-toplevel)" || exit 1
S=$PWD/scratch/s7598; OUT=$S/results.txt; : > $OUT; BOOT_S=${BOOT_S:-45}; P=${PLANT:-200}
export ROGUESQ_S7598_PLANT_LEN=${PLEN:-1000000000}; BIN=$PWD/build/RogueSquadron64Recomp; ROM=$PWD/build/rs64.n64.us.1.0.z64
ARMS=($@); (( $#ARMS )) || ARMS=(ctl old new)
for arm in $ARMS; do
  /usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo "arm=$arm VOID locked" >> $OUT; continue; }
  W=$S/w/$arm; rm -rf $W; mkdir -p $W/saves $W/mods
  ln -s $BIN $W/RogueSquadron64Recomp; ln -s $ROM $W/rogue_squadron.z64; ln -s $ROM $W/rs64.n64.us.1.0.z64
  case $arm in ctl) X=(ROGUESQ_S7598_NONE=1) ;; old) X=(ROGUESQ_S7598_PLANT=$P ROGUESQ_S7598_MASK=0) ;; new) X=(ROGUESQ_S7598_PLANT=$P) ;; oldspan) X=(ROGUESQ_S7598_PLANT=$P ROGUESQ_S7598_MASK=0 ROGUESQ_LOG_UPSPAN=1) ;; esac
  log=$S/w/$arm.log
  ( cd $W && exec env ROGUESQ_NO_SAVE_WRITE=1 $X ./RogueSquadron64Recomp ) > $log 2>&1 &
  gp=$!; t=0; rc=alive
  while (( t < BOOT_S * 10 )); do kill -0 $gp 2>/dev/null || { wait $gp; rc=$?; break; }; /bin/sleep 0.1; t=$((t+1)); done
  [[ $rc == alive ]] && { kill -KILL $gp; wait $gp 2>/dev/null; }
  printf 'arm=%s rc=%s at_s=%.1f plant=%s clamp=%s bigtex=%s bigmax=[%s] crash=%s metal=%s vi=%s term=[%s]\n' $arm $rc $((t/10.0)) \
    $(grep -c '^\[s7598-plant\]' $log) $(grep -c '^\[s7598-mask\]' $log) $(grep -c '^\[s7598-bigtex\]' $log) \
    "$(grep -m1 '^\[s7598-bigtex\]' $log | cut -c1-60)" $(grep -cE '\[CRASH\]|SIGSEGV|SIGBUS' $log) \
    $(grep -ciE 'MTL|metal.*(error|fail)|newTexture' $log) $(grep -cE 'VI|vi_origin' $log) \
    "$(grep -m1 -E 'terminat|Assertion|abort|\[CRASH\]' $log | cut -c1-150)" >> $OUT
  tail -1 $OUT; /bin/sleep 2
done
