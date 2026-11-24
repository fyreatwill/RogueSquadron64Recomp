# NEXT (s7873)
HYPOTHESIS-ID: g3-cinematic-half-frame-phase
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7872): island A (opening cinematic, 64 PRIM-FF tris, port ~half a frame AHEAD of retail, offset 0.510 x speed) is not
dt (identical dt both sides from the cinematic's first frame) and not stall parity. timeSnapshotFiller el (0x8000BE28) moves
the element: VI-window el=0 (ROGUESQ_S7872_SNAP_WIN=5560:6300:0) changed it on 164/168 frames but threw it far off (-489..244),
so el=0 takes a special path; the RETAIL_SNAP pin 811160 gives the half-frame lead.
Unit (ONE pair, both arms windowed, no extra build): read timeSnapshotFiller 0x8000BE28..L_8000BF38 first (what el=0 does to
f0 / a0+0x20: divide, clamp, branch), then
  W=scratch/s7873/w10; mkdir -p $W/r1; ln scratch/s7872/v10/r1/oracle.log $W/r1/; ln scratch/s7872/v10/r1/retail.bin $W/r1/
  env RBIN=1 P1E=ROGUESQ_S7872_SNAP_WIN=5560:6300:1 P2E=ROGUESQ_S7872_SNAP_WIN=5560:6300:405580 zsh tools/s7849_det_pair.sh 10 $W
Score: `python3 tools/s7868_det_frame_cmp.py $W/r1/retail.bin $W/p1.bin --plant --neg $W/p2.bin`, then island probe
(tools/s7869_island_probe.py ... OFF OFF2 J0 J1 at each arm's offset over retail[2864:3032]) and the phase_a regression
(scratch/s7872/phase_a_p1.py pattern; edit O/off/range). Controls: s7872 w10 p2 (pin 811160) = 0.510 x speed is the
reference; the window must log `[snap7872] hits` in both arms; frames outside the window must stay exact (retail[3600:5200]).
Outcomes: el=1 exact on island A -> H-snap with "retail el ~ 0 but not the 0 special case" (then check how retail reaches the
el=0 branch differently: v0 at BE28 vs the BE08 prev==-1 path); el=0.5 VI gives offset ~0.25 x speed -> offset linear in el,
solve for the retail el; neither moves toward 0 -> el is a proxy, look at vd (0x8000BE80) / gt (0x8000BC70) in the same
function (trace both on retail via --exec-trace-also).
Delete p1/p2 bins after scoring; keep scratch/s7872/v10/r1 until the thread closes.
