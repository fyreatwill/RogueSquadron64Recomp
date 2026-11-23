#!/bin/zsh
# s7849: one-shot G3 retail-flight det pair for one mission (the s7844-s7847 recipe as a driver).
# usage: zsh tools/s7849_det_pair.sh <0x31 value> OUTDIR   [env BASE_EEP=scratch/s7832/lvl.eep SECS=305]
# s7852: song handle 0x8010C0E0 + AI-buffer rows on both sides; score adds every fork window (s7852_fork_windows.py)
# and the song windows (g3_song_windows.py): a fork at a song-handle switch with VI/buffer parity = audio-clocked split (s6806).
# Steps: patch save 0x31=<v>; retail r1 (oracle, seed+dt watches); derive pins (tools/s7849_det_pins.py); port p1 pinned
# (tick-0 seed poke + DT_AT) and p2 unpinned control, sequentially (one game run at a time); score both with
# tools/s7845_rng_tick_cmp.py and tools/s7849_rec_align.py into OUTDIR/score.txt. Positive control: p2 must fork.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
V=${1:?usage: s7849_det_pair.sh <0x31 value> OUTDIR}; O=${2:?OUTDIR}; mkdir -p $O; SECS=${SECS:-305}
python3 tools/g3_eep_patch.py ${BASE_EEP:-scratch/s7832/lvl.eep} $O/lvl.eep --set 0x31=$V || exit 3
if [[ ! -s $O/r1/oracle.log ]]; then
env CPO=1 RSECS=$SECS EEP=$O/lvl.eep PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start RDPBIN=/dev/null \
  RS64_ORACLE_FPR=0,4,6,14,20 RS64_XTRACE_MEM=800FA730:0:80137E7C:1,800FA730:0:80003470:1,800FA730:0:8010C0E0:1 \
  XO="--watch-pc 0x80043918 --pc-ram-dump 0x80043918:0x80137DB0:0x801384E0 --exec-trace 0x80003430:8000000:0x80003470 --exec-trace-also 0x800FA730 --exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84 --watch-write 0x137E7C:0x137E80 --watch-pc 0x800FA738 --watch-pc 0x800FA7D0" \
  zsh tools/s7828_retail_cpo.sh $O/r1 > $O/r1.out 2>&1
fi
python3 tools/s7849_det_pins.py $O/r1/oracle.log > $O/pins.txt || { cat $O/pins.txt; echo "pins failed" >&2; exit 4; }
source $O/pins.txt; cat $O/pins.txt
AP=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start
B="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7834_RAMDUMP=1 ROGUESQ_G3C_CAMLOG=1 ROGUESQ_S7835_DT=1 ROGUESQ_VI_STAMP=1 ROGUESQ_RETAIL_SNAP=1 ROGUESQ_RAND_TRACE_BOOT=1 ROGUESQ_RAND_TRACE_MAX=8000000 ROGUESQ_XTRACE_MEM=800FA730:0:80137E7C:1,800FA730:0:80003470:1,800FA730:0:8010C0E0:1"
P1X="ROGUESQ_XTRACE_POKE=800FA730:0:80003470:$SEED:1"; [[ -n $DT_AT ]] && P1X="$P1X ROGUESQ_S7844_DT_AT=$DT_AT"
A=$PWD/$O
env SAVE_FROM=$O/lvl.eep SECS=$SECS CAP0=$((SECS-3)) AP=$AP XE="$B ROGUESQ_RAND_TRACE=$A/p1_rand.txt $P1X" zsh tools/g3_port_capture.sh $O/p1 > $O/p1.out 2>&1
env SAVE_FROM=$O/lvl.eep SECS=$SECS CAP0=$((SECS-3)) AP=$AP XE="$B ROGUESQ_RAND_TRACE=$A/p2_rand.txt" zsh tools/g3_port_capture.sh $O/p2 > $O/p2.out 2>&1
{ for a in p1 p2; do echo "=== $a"; echo "crashlines $(grep -c 'CRASH\|SIGSEGV\|SIGBUS\|abort' $O/$a/run.log)"
  grep -m3 'dt7844\|pin=' $O/$a/run.log | cut -c1-160
  python3 tools/s7845_rng_tick_cmp.py $O/r1/oracle.log $O/${a}_rand.txt | head -30
  python3 tools/s7852_fork_windows.py $O/r1/oracle.log $O/${a}_rand.txt | head -6
  python3 tools/g3_song_windows.py $O/r1/oracle.log $O/${a}_rand.txt
  python3 tools/s7849_rec_align.py $O/r1/oracle.log $O/$a/run.log | tail -12; done; } > $O/score.txt 2>&1
echo done; grep -n 'first\|crashlines' $O/score.txt
