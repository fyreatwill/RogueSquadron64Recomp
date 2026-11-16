#!/bin/zsh
# s7470 class EA: write one self-contained ASan+UBSan per-level soak recipe for build_asan (UCODE=1) at the owner recipe.
# usage: zsh tools/s7470_gen_asan_lv.zsh <name> <hold> <lv:dd> [lv:dd ...]   (dd4 -> 16:9, dd8 -> 21:9)
#   writes scratch/agent/soak_queue/<name>.sh (OUT=<path> overrides); first arm carries both plants (main TU + ucode TU).
# Recipe exit: 0 = controls PASS + 0 NEW groups, 1 = NEW group (review $R/san_*), 3 = control FAIL, harness rc wins over score.
set -e; n=$1; hold=$2; shift 2; (( $# >= 1 )) || { echo "usage: $0 name hold lv:dd ..."; exit 2; }
arms=""; names=""; plant=""
for s in "$@"; do lv=${s%%:*}; dd=${s#*:}; [[ $lv == <-> && $dd == <-> ]] || { echo "bad arm $s"; exit 2; }
  a=l$lv; x="ROGUESQ_FORCE_SAVE_MISSION=$lv"; [[ $dd == 8 ]] && x="$x+ROGUESQ_ASPECT=21:9"
  [[ -z $plant ]] && { x="$x+ROGUESQ_S7467_ASAN_PLANT=1+ROGUESQ_S7468_UCODE_PLANT=1"; plant=$a; }
  arms="$arms $dd:$a:$x+\$(so $a)"; names="$names $a"; done
f=${OUT:-scratch/agent/soak_queue/$n.sh}
to=$(( ($hold+100)*$# )); (( to < 900 )) && to=900
cat > $f <<EOF
#!/bin/zsh
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=$to
# $n (tools/s7470_gen_asan_lv.zsh): class EA ASan+UBSan per-level sweep on build_asan, owner recipe, HOLD=$hold. Arms:${names}
# (dd4 = 16:9, dd8 = 21:9); first arm $plant carries both plants. Score: tools/s7467_san_report.py --known tools/s7467_san_reviewed.tsv.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
[ -x build_asan/RogueSquadron64Recomp ] || { echo "no build_asan: run tools/build_asan.sh"; exit 3; }
R=\$PWD/scratch/$n; mkdir -p \$R; rm -f \$R/quiet.done \$R/void_*(N) \$R/ok_*(N) \$R/ring_*.txt(N) \$R/san_*(N)
so(){ echo "ASAN_OPTIONS=halt_on_error=0:detect_leaks=0:log_path=\$R/san_\$1+UBSAN_OPTIONS=halt_on_error=0:print_stacktrace=1:log_path=\$R/san_\$1"; }
env R=\$R HOLD=$hold DONE=quiet.done GAMEDIR=build_asan ARMS="${arms# }" zsh tools/g1e_owner_quiet_arms.zsh | tee \$R/out.txt; rc=\${pipestatus[1]}
(( rc == 2 )) && exit 2
for a in${names}; do echo "$n arm=\$a initMission=\$(grep -a -c 'initMission\] call' \$R/log_\$a.txt 2>/dev/null)"; done
python3 tools/s7467_san_report.py \$R${names} --plant $plant --uplant $plant --known tools/s7467_san_reviewed.tsv | tee \$R/san_report.txt; sr=\${pipestatus[1]}
(( rc != 0 )) && exit \$rc
exit \$sr
EOF
zsh -n $f && echo "wrote $f arms:$names plant=$plant timeout=$to"
