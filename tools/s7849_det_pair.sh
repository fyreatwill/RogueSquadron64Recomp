#!/bin/zsh
# s7849: one-shot G3 retail-flight det pair for one mission (the s7844-s7847 recipe as a driver).
# usage: zsh tools/s7849_det_pair.sh <0x31 value> OUTDIR   [env BASE_EEP=scratch/s7832/lvl.eep SECS=305]
# s7852: song handle 0x8010C0E0 + AI-buffer rows on both sides; score adds every fork window (s7852_fork_windows.py)
# and the song windows (g3_song_windows.py): a fork at a song-handle switch with VI/buffer parity = audio-clocked split (s6806).
# s7854: REC=1 (default; REC= turns it off) adds a tick-keyed 460-w player-record dump at 0x800FA730 on both sides (8 XTRACE_MEM specs) and scores it
# with tools/s7854_tick_rec_cmp.py (for levels where the 0x80043918 terrain-grid dump PC does not run per tick, e.g. 0x31=10).
# s7860: PP_OVR / AP_OVR override the retail (s7828 PP, port time) and port (AP) Start schedules; unset = the hangar-mission
# defaults, byte-identical. The self-starting bonus race needs no Start after the level pick (s6771): PP_OVR/AP_OVR end at 43.5.
# s7868: RBIN=1 keeps the RDP streams: retail OUTDIR/r1/retail.bin, port OUTDIR/p1.bin + p2.bin (6000 MB caps) for the
# matched-prefix render oracle tools/s7868_det_frame_cmp.py; unset = RDPBIN=/dev/null and no port bin, byte-identical.
# s7864: P1E / P2E append extra env to the p1 / p2 port arm only (e.g. P1E=ROGUESQ_AI_VI_CLOCK=1); unset = byte-identical.
# Steps: patch save 0x31=<v>; retail r1 (oracle, seed+dt watches); derive pins (tools/s7849_det_pins.py); port p1 pinned
# (tick-0 seed poke + DT_AT) and p2 unpinned control, sequentially (one game run at a time); score both with
# tools/s7845_rng_tick_cmp.py and tools/s7849_rec_align.py into OUTDIR/score.txt. Positive control: p2 must fork.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
REC=${REC-1}; RM=; if [[ -n $REC ]]; then for k in 0 1 2 3 4 5 6; do RM="$RM,800FA730:0:$(printf %X $((0x80137DB0+256*k))):64"; done; RM="$RM,800FA730:0:801384B0:12"; fi
V=${1:?usage: s7849_det_pair.sh <0x31 value> OUTDIR}; O=${2:?OUTDIR}; mkdir -p $O; SECS=${SECS:-305}
python3 tools/g3_eep_patch.py ${BASE_EEP:-scratch/s7832/lvl.eep} $O/lvl.eep --set 0x31=$V || exit 3
RB=/dev/null; [[ -n $RBIN ]] && RB=$PWD/$O/r1/retail.bin
if [[ ! -s $O/r1/oracle.log ]]; then
env CPO=1 RSECS=$SECS EEP=$O/lvl.eep PP=${PP_OVR:-19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start} RDPBIN=$RB \
  RS64_ORACLE_FPR=0,4,6,14,20 RS64_XTRACE_MEM=800FA730:0:80137E7C:1,800FA730:0:80003470:1,800FA730:0:8010C0E0:1$RM \
  XO="--watch-pc 0x80043918 --pc-ram-dump 0x80043918:0x80137DB0:0x801384E0 --exec-trace 0x80003430:8000000:0x80003470 --exec-trace-also 0x800FA730 --exec-trace-also 0x8008EE08 --exec-trace-also 0x8008EE84 --watch-write 0x137E7C:0x137E80 --watch-pc 0x800FA738 --watch-pc 0x800FA7D0" \
  zsh tools/s7828_retail_cpo.sh $O/r1 > $O/r1.out 2>&1
fi
python3 tools/s7849_det_pins.py $O/r1/oracle.log > $O/pins.txt || { cat $O/pins.txt; echo "pins failed" >&2; exit 4; }
source $O/pins.txt; cat $O/pins.txt
# s7880: APM=1 = the retail-matched port schedule for the default PP: the oracle's fixed 16 s boot press lands on level
# select (VI +232 after 640->1024) and the PP presses land +287 VI later than the default AP, so the default AP is one press
# short in the 640 pre-flight scene (mission 1 then sits its 115 s intro out). APM=1 puts every port press within 4 VI of
# retail's (tools/s7880_press_scene.py). Unset = the old default, byte-identical. AP_OVR still wins over both.
APD=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start
[[ -n $APM ]] && APD=6:start,11:start,11.5:w1024,15.05:start,24.3:start,36.3:start,48.3:start,72.3:start,84.3:start,96.3:start
AP=${AP_OVR:-$APD}
B="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7834_RAMDUMP=1 ROGUESQ_G3C_CAMLOG=1 ROGUESQ_S7835_DT=1 ROGUESQ_VI_STAMP=1 ROGUESQ_RETAIL_SNAP=1 ROGUESQ_RAND_TRACE_BOOT=1 ROGUESQ_RAND_TRACE_MAX=8000000 ROGUESQ_XTRACE_MEM=800FA730:0:80137E7C:1,800FA730:0:80003470:1,800FA730:0:8010C0E0:1$RM"
P1X="ROGUESQ_XTRACE_POKE=800FA730:0:80003470:$SEED:1"; [[ -n $DT_AT ]] && P1X="$P1X ROGUESQ_S7844_DT_AT=$DT_AT"
A=$PWD/$O
B1=; B2=; [[ -n $RBIN ]] && { B1="RS64_RDP_BIN_PORT=$A/p1.bin RS64_RDP_BIN_PORT_MAX_MB=6000"; B2="RS64_RDP_BIN_PORT=$A/p2.bin RS64_RDP_BIN_PORT_MAX_MB=6000"; }
env SAVE_FROM=$O/lvl.eep SECS=$SECS CAP0=$((SECS-3)) AP=$AP XE="$B ROGUESQ_RAND_TRACE=$A/p1_rand.txt $P1X $P1E $B1" zsh tools/g3_port_capture.sh $O/p1 > $O/p1.out 2>&1
env SAVE_FROM=$O/lvl.eep SECS=$SECS CAP0=$((SECS-3)) AP=$AP XE="$B ROGUESQ_RAND_TRACE=$A/p2_rand.txt $P2E $B2" zsh tools/g3_port_capture.sh $O/p2 > $O/p2.out 2>&1
{ for a in p1 p2; do echo "=== $a"; echo "crashlines $(grep -c 'CRASH\|SIGSEGV\|SIGBUS\|abort' $O/$a/run.log)"
  grep -m3 'dt7844\|pin=' $O/$a/run.log | cut -c1-160
  python3 tools/s7845_rng_tick_cmp.py $O/r1/oracle.log $O/${a}_rand.txt | head -30
  python3 tools/s7852_fork_windows.py $O/r1/oracle.log $O/${a}_rand.txt | head -6
  python3 tools/g3_song_windows.py $O/r1/oracle.log $O/${a}_rand.txt
  python3 tools/s7849_rec_align.py $O/r1/oracle.log $O/$a/run.log | tail -12
  [[ -n $REC ]] && python3 tools/s7854_tick_rec_cmp.py $O/r1/oracle.log $O/${a}_rand.txt; done;
  [[ -n $REC ]] && { echo "=== control (p1 word 50 flipped at tick 100)"; python3 tools/s7854_tick_rec_cmp.py $O/r1/oracle.log $O/p1_rand.txt --control 100; }; } > $O/score.txt 2>&1
echo done; grep -n 'first\|crashlines' $O/score.txt
