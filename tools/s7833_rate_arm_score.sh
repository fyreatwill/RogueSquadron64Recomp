#!/bin/zsh
# s7833: score one retail oracle arm (e.g. a CountPerOp arm from tools/s7828_retail_cpo.sh) against the s7832 lvl2 references:
# world-tri pose fit (s7827 --controls --pose) on two static-sky bands and big/small reticle path (s7826), each vs R1 (--p-retail)
# and vs the port capture. Bands are given in the arm's frame numbers; R1/port bands default to the s7832 ones.
# usage: zsh tools/s7833_rate_arm_score.sh ARM_retail.bin OUTDIR A0:A1 B0:B1 W0:W1
#   A/B = arm frames of s7832 band a (R1 3408:3475, tri~880; port 4304:4383) and band b (R1 3539:3594, tri~789; port 4453:4516)
#   W   = arm flight window for the reticle (R1 3290:4140, port 4150:5160)
# env R1= P= RA= RB= RW= PA= PB= PW= override the reference captures/bands. Runs two scoring streams at once (CPU rule: <=2).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
C=${1:?arm bin}; O=${2:?outdir}; A=${3:?band a}; B=${4:?band b}; W=${5:?window}; mkdir -p $O
R1=${R1:-scratch/s7832/ret/retail.bin.zst}; P=${P:-scratch/s7832/port.bin.zst}
RA=${RA:-3408:3475}; RB=${RB:-3539:3594}; RW=${RW:-3290:4140}; PA=${PA:-4304:4383}; PB=${PB:-4453:4516}; PW=${PW:-4150:5160}
T=tools/s7827_tri_yshift_census.py; K=tools/s7826_rect_path_offset.py
( python3 $T $R1 $C --win $RA,$A --controls --pose $RA,$A --p-retail > $O/pose_a_r1.txt 2>&1
  python3 $T $R1 $C --win $RB,$B --controls --pose $RB,$B --p-retail > $O/pose_b_r1.txt 2>&1
  python3 $K $R1 $C --win $RW,$W --p-retail > $O/rect_r1.txt 2>&1 ) &
( python3 $T $C $P --win $A,$PA --controls --pose $A,$PA > $O/pose_a_port.txt 2>&1
  python3 $T $C $P --win $B,$PB --controls --pose $B,$PB > $O/pose_b_port.txt 2>&1
  python3 $K $C $P --win $W,$PW > $O/rect_port.txt 2>&1 ) &
wait
for f in $O/pose_{a,b}_{r1,port}.txt; do
  printf '%-14s %s | %s\n' ${f:t:r} "$(grep -m1 'H-pitch  rms' $f | sed 's/^ *//')" "$(grep -m1 'pose controls' $f)"; done
for f in $O/rect_{r1,port}.txt; do
  printf '%-14s %s\n' ${f:t:r} "$(grep -m1 '^elem 51' $f | sed -E 's/.*median ([0-9.]+) p90.*\((PASS|FAIL)\).*classes (.*)/med \1 plant \2 big \3/' | cut -c1-220)"; done
