# NEXT: G3 -- name the lvl4 scripted-event trigger that fires at tick 2302 retail vs 2317 port
HYPOTHESIS-ID: g3-lvl4-event-trigger

s6754: lvl4 with dt pinned is sim-identical for ticks 0-2301 (rand, NPCs, camera object). At tick 2302 retail fires a
scripted event (initActorMotionParams 0x800F2888 rand at 0x800F28F4 + dispatchDatSubtypeByRandomIndex burst at 0x8007132C,
camera object 0x80138D20 word0 -> 0x803623AC, NPC 803663D0 reactivated); the port fires the identical event at tick 2317.
Not tick count, not elapsed VI (retail 5166 / port 4633), not the measured snapshot words.
Hypotheses:
- H-audio: the script waits for a dialogue/stream voice to finish (MusyX voice state; retail audio = mupen dummy AI,
  port = real host audio timing).
- H-pi: waits for an asset/stream PI DMA or a load-queue completion (mupen PI timing vs port instant/threaded).
- H-clock: a script timer reads osGetTime/osGetCount (or snapshot word 9) directly, not the pinned dt.
Work (offline first, then ONE run per arm):
1. Static: find the caller of initActorMotionParams on this path. Add `--exec-trace-also 0x800F2888` to the retail
   recipe and log $ra (the oracle row prints ra? check rs64_oracle exec-trace columns; else xtrace-mem 800F2888:31:0:1)
   - or grep the syms/disassembly for jal 0x800F2888 callers and pick the mission-script one.
2. Walk up to the conditional branch that gates the event; xtrace-mem its operands per tick in both arms
   (oracle RS64_XTRACE_MEM, port ROGUESQ_XTRACE_MEM) with the s6754 recipes (scratch/s6754/retail.sh RD=retail3 SECS=200,
   scratch/s6754/port.sh PD=port2).
3. Whichever operand differs before tick 2302 names the timebase: voice/sound state -> H-audio, DMA/load flag -> H-pi,
   count/time -> H-clock.
Tools: tools/g3_rand_ticks.py (sim-tick keyed rand diff; positive control: s6753 pair -> no mismatch), g3_frame_snap.py.
If the timebase is host audio/PI and retail-equivalent in real play, close as pacing (not a port defect) and move G3 to
mission 5 with the pinned method.
