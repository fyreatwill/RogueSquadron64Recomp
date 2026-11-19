#!/bin/zsh
# s7643 class TS-2 runtime (copy of s7641 runner): $1 = arm tag, $2 = binary, extra env after. Boot ~45 s (title presents), SIGKILL. TSan reports -> tsan_$1.*
D=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s7643; mkdir -p $D
T=$1; BIN=$2; shift 2
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build || exit 2
rm -f $D/tsan_$T.* 2>/dev/null; setopt nonomatch
env TSAN_OPTIONS="log_path=$D/tsan_$T halt_on_error=0 report_signal_unsafe=0 history_size=4" ROGUESQ_NO_SAVE_WRITE=1 "$@" \
  ./$BIN rogue_squadron.z64 > $D/log_$T.txt 2>&1 &
PID=$!
for i in {1..${DUR:-45}}; do sleep 1; kill -0 $PID 2>/dev/null || break; done
kill -9 $PID 2>/dev/null; wait $PID 2>/dev/null
echo "arm $T alive_s=$i presents_log=$(grep -c . $D/log_$T.txt) tsan_files=$(ls $D/tsan_$T.* 2>/dev/null | wc -l) races=$(cat $D/tsan_$T.* 2>/dev/null | grep -c 'WARNING: ThreadSanitizer: data race') idx_races=$(cat $D/tsan_$T.* 2>/dev/null | grep -B2 -A40 'WARNING: ThreadSanitizer: data race' | grep -c 'acquireTexture')"
