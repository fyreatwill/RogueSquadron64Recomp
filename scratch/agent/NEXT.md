# NEXT: G3 -- lvl3 trajectories with dt pinned to 2 VI in both arms (H-sim residual)
HYPOTHESIS-ID: g3-lvl3-dt-pinned

s6752: runInMissionFrame (0x800FA728) feeds the sim timeSnapshotFiller's measured frame time (struct at sp+0x10,
+0x20 = seconds, read back at 0x800FA730 `lwc1 $f20, 0x30($sp)`). Retail (mupen) steps 2.04 VI with 3.08-VI drops
in 34% of frames; port is a flat 2.00. Early NPC gate flips line up in cumulative sim time, so the s6751 "one frame
late" lag is dt, not arithmetic. Open: does the sim match frame by frame when dt is equal (H-sim residual)?
Hypotheses:
- H-dt-only: with dt pinned to 1/30 s (0x3D088889) in both arms, every NPC point / gate result / rand caller matches
  through and past the first player hit (s6750's ~6 s desync point).
- H-sim: with dt pinned, some field still diverges -> first diverging tick + field names the arithmetic to bisect.
- H-input: divergence starts at a tick where the scripted input lands on different ticks (autopilot is wall-clock):
  check the controller word per tick in both arms (add a dump of the pad buffer to the tick spec).
Work:
1. Oracle: RS64_XTRACE_POKE="PC:REG:OFF:VALUE" -> at an --exec-trace-also PC, pDebugMemWrite32(gpr[REG]+OFF, VALUE)
   after the row (tools/oracle/rs64_oracle.c next to xtrace_mem). Arm 800FA730:29:30:3d088889.
2. Port: ROGUESQ_PIN_DT=<hex float> in rs64_xtrace_mark's 0x800FA730 path (write sp+0x30 before the lwc1), same value.
   Note rs64_xtrace_mark only runs once the rand trace is open (after the poke) -- fine, both arms pin from the poke.
3. Same recipe as s6752 (scratch/s6752/retail.sh with D=retail3 + RS64_XTRACE_POKE; port command in the s6752
   PORTING-STATE entry plus ROGUESQ_PIN_DT=3d088889), add the pad state to the tick dump (find the controller buffer
   the game reads: osContGetReadData destination).
4. python3 tools/g3_frame_snap.py retail3/oracle.log port_rand.txt 400 | grep -n '!=\|diff \[[0-9]' | head
Positive control: tick dt words read 3d088889 in every row of both arms (pin fired); unpinned s6752 logs as the
contrast (divergence at tick 2).
Outcomes: no diff through the hit -> H-dt-only, close lvl3 desync as pacing; first diff at tick k with equal pad ->
H-sim, bisect that field's writer; first diff coincides with a pad change on different ticks -> H-input (drive input
by game tick, not wall clock).
