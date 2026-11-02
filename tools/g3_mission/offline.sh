#!/bin/zsh
# G3 per-mission offline analysis over SDIR/{retail/oracle.log,port.rand.txt,port/}. Writes SDIR/*.txt, prints a summary.
# usage: zsh tools/g3_mission/offline.sh SDIR [SNAP_TICKS]   (SNAP_TICKS default: first rand split + 6, else 3000)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
export G3_MIN_TICK=${G3_MIN_TICK:--1}
S=$1; R=$S/retail/oracle.log; P=$S/port.rand.txt
python3 tools/g3_rand_ticks.py $R $P > $S/rand_ticks.txt 2>&1
python3 tools/g3_song_windows.py $R $P > $S/songs.txt 2>&1
N=${2:-$(python3 - $S/rand_ticks.txt <<'PY'
import re, sys
for l in open(sys.argv[1]):
    m = re.match(r'!=\s+\d+\s+R t(\d+)', l)
    if m: print(int(m.group(1)) + 6); break
else: print(3000)
PY
)}
python3 tools/g3_frame_snap.py $R $P $N > $S/snap.txt 2>&1
python3 tools/g3_mission/snap_parse.py $S/snap.txt > $S/snap_summary.txt 2>&1
env G3_IGN=04,0c,18 python3 tools/g3_tick_mem.py $R $P 8010c9e0 8010c0e0 > $S/tick_mem.txt 2>&1
# s6771: retail fb bases = logged origin0 & ~0xFFF (missions 1-16 690000,620000; the mission-17 race 6AB000,656000)
B=${G3_BASES:-$(grep -o 'origin0=0x[0-9a-f]*' $R | python3 -c "import sys; print(','.join(sorted({'%X' % (int(l.split('=')[1], 16) & ~0xFFF) for l in sys.stdin})) or '690000,620000')")}
python3 tools/g3_oracle_match.py $R $S/port $S/match --w 512 --bases $B --h 446 --win 60,1024 \
  --winx 85,1191 --dec shift --worst 6 > $S/match.txt 2>&1
python3 tools/g3_hud_presence.py $S > $S/hud.txt 2>&1
# positive control: one flipped rand value must be flagged
python3 tools/g3_mission/flip_ctl.py $P $S/ctl.rand.txt 30000 > $S/ctl.txt 2>&1
python3 tools/g3_rand_ticks.py $R $S/ctl.rand.txt > $S/ctl_ticks.txt 2>&1
G=$S/port_run.txt; [ -f $S/port/run.log ] && G=$S/port/run.log
for f in rand_ticks songs snap_summary tick_mem hud ctl ctl_ticks; do echo "== $f"; head -${HEAD:-12} $S/$f.txt; done
echo "== match"; tail -${HEAD:-12} $S/match.txt
echo "== port log: cap fires $(grep -c 'ucode-cap\] fired' $G 2>/dev/null), crash lines $(grep -ci 'CRASH\|SIGSEGV\|SIGBUS\|abort' $G 2>/dev/null)"
