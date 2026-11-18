#!/bin/zsh
# s7597 class XC runtime witness: boot-only, one game at a time, each arm in scratch/s7597/w/<tag>/<arm> (symlinked binary,
# import ROM + stored ROM symlinked, NO owner save: saves/ empty). ROGUESQ_NO_SAVE_WRITE=1 always.
# Arms plant malformed boot-read inputs: mods.json (config_path/mods.json, parse_mods_config at every boot) and mods/ entries
# (scan_mod_folder: directory_entry::is_regular_file/is_directory throwing forms, mod.json manifest parse, .nrm open).
cd "$(git rev-parse --show-toplevel)" || exit 1
S=$PWD/scratch/s7597; TAG=$1; shift; OUT=$S/results_$TAG.txt; : > $OUT; BOOT_S=${BOOT_S:-30}; X=${XENV:-ROGUESQ_S7597_NONE=1}
BIN=$PWD/build/RogueSquadron64Recomp; ROM=$PWD/build/rs64.n64.us.1.0.z64
ARMS=($@); (( $#ARMS )) || ARMS=(ctl mj_garbage mj_array mj_types mj_dir mj_bin mod_loop mod_dangle mod_dir_garbage mod_dir_types mod_dir_empty mod_nrm_garbage mod_nrm_dir)
for arm in $ARMS; do
  /usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo "arm=$arm VOID locked" >> $OUT; continue; }
  W=$S/w/$TAG/$arm; [[ -e $W/locked ]] && chmod 755 $W/locked; [[ -e $W ]] && rm -rf $W; mkdir -p $W/saves $W/mods $W/mod_config
  ln -s $BIN $W/RogueSquadron64Recomp; ln -s $ROM $W/rogue_squadron.z64; ln -s $ROM $W/rs64.n64.us.1.0.z64
  case $arm in
    mj_garbage) print -n '{{{ not json' > $W/mods.json ;;
    mj_array) print -n '[1,2,3]' > $W/mods.json ;;
    mj_types) print -n '{"enabled_mods":5,"mod_order":[1,{},null],"x":[[[[]]]]}' > $W/mods.json ;;
    mj_dir) mkdir $W/mods.json ;;
    mj_bin) head -c 4096 $ROM > $W/mods.json ;;
    mod_loop) ln -s loop $W/mods/loop ;;
    mod_dangle) ln -s /nonexistent/x $W/mods/dangle.nrm ;;
    mod_dir_garbage) mkdir $W/mods/foo; print -n '{{{' > $W/mods/foo/mod.json ;;
    mod_dir_types) mkdir $W/mods/foo; print -n '{"id":5,"version":[],"authors":"x","game_id":{},"minimum_recomp_version":7,"dependencies":"y","native_libraries":3,"config_schema":[1]}' > $W/mods/foo/mod.json ;;
    mod_dir_empty) mkdir $W/mods/foo ;;
    mod_nrm_garbage) head -c 4096 $ROM > $W/mods/x.nrm ;;
    mod_nrm_dir) mkdir $W/mods/x.nrm ;;
    mod_eacces) mkdir $W/locked; ln -s ../locked/x $W/mods/acc; chmod 000 $W/locked ;;
  esac
  log=$S/w/$TAG/$arm.log
  ( cd $W && exec env ROGUESQ_NO_SAVE_WRITE=1 $X ./RogueSquadron64Recomp ) > $log 2>&1 &
  gp=$!; t=0; rc=alive
  while (( t < BOOT_S * 10 )); do kill -0 $gp 2>/dev/null || { wait $gp; rc=$?; break; }; /bin/sleep 0.1; t=$((t+1)); done
  [[ $rc == alive ]] && { kill -KILL $gp; wait $gp 2>/dev/null; }
  io=$(grep -E '^\[s7(595|596|597)-|^Error opening mod|^Opening mod|^Skipping' $log | head -3 | cut -c1-140 | tr '\n' ';')
  term=$(grep -m1 -E 'terminat|filesystem error|libc\+\+abi|exception' $log | cut -c1-170)
  printf 'arm=%s rc=%s at_s=%.1f io=[%s] term=[%s] crash=%s loglines=%s\n' $arm $rc $((t/10.0)) "$io" "$term" \
    $(grep -cE '\[CRASH\]' $log) $(wc -l < $log) >> $OUT
  tail -1 $OUT; /bin/sleep 2
done
