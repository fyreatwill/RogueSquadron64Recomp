#!/bin/zsh
# s7065: back-to-back 1 s host samples (all threads, blocked stacks included) of the game from +60 s until it exits.
O=${1:?usage: s7065_sample_loop.zsh <outdir> [start_delay_s]}; D=${2:-60}
for i in {1..600}; do p=$(. ${0:A:h}/rs64_game_pid.zsh; rs64_game_pid 2>/dev/null) && break; /bin/sleep 1; done
echo "pid=$p" > $O/smp_log.txt; /bin/sleep $D; i=0
while kill -0 $p 2>/dev/null; do i=$((i+1)); python3 -c 'import time;print(time.time(),time.monotonic())' >> $O/smp_log.txt
  /usr/bin/sample $p 1 1 -file $O/smp_$i.txt >/dev/null 2>&1; echo "end $i $(python3 -c 'import time;print(time.time())')" >> $O/smp_log.txt; done
echo SMPDONE >> $O/smp_log.txt
