# NEXT (s7539)
HYPOTHESIS-ID: class-gb-device-done-before-read

s7538 class GB census (tools/s7538_gb_census.py, 29 sites / 31 rows, --controls 7/7) found ONE open sibling of GA: under the
owner opt-in ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1, rs64_rdpq_task_exit only flush_pend()s (src/main/rt64_render_context.cpp
~1716), so send_dl returns and dp_complete (events.cpp ~1750) is posted while the RT64 worker still holds the task's tail jobs
(s6709 pend_jobs 2.0, fullSync ~3.3 ms). Those jobs read texture sources from core.RDRAM (RDP::loadTile/loadBlock/loadTLUT,
lib/rt64/src/hle/rt64_rdp.cpp 1507/1636/1813; only command words are copied) and fullSync writes fb copies to RDRAM.
Read PORTING-STATE s7538 first. Fold first if SOAK-RESULTS has a non-VOID s7536_splate_cost line (recipe in CURRENT-TRUTH item 17).

Work unit: same-run A/B of the open row, ONE instrument, ONE build (separate build dir, e.g. build_gb; lib/rt64 edits -> export.sh).
- Arm: ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=2 (alternates per async window: as=2 drained vs as=3 not drained; [g1e-aq] as= tags it).
- Instrument ROGUESQ_S7539_GB_CHK=1: Gfx thread, right before dp_complete, snapshot guest RAM [0, osmem) (+spill 16-24 MB) and stamp
  dp_seq; tag every queued Job with its task's dp_seq. In loadTile/loadBlock/loadTLUT (worker thread only), when the job's dp_seq is
  already posted, compare the RDRAM source bytes with the snapshot -> diff bytes/loads per arm (as=2 must be 0 by construction:
  drained before the post = built-in negative arm). Also count fullSync RDRAM writes after the post, and guest loads... (skip: the
  s7391 fb-cpu-reader census says the guest never loads a live colour image).
- Positive control: every 64th post-signal load compared against a snapshot with one byte flipped (caught == planted).
- Activity witness: every 32nd post, count all bytes changed in RAM between post and the tail job's end (guest IS running).
- Runs: tools/g1e_owner_quiet_arms.zsh HOLD 120, owner recipe FPS60 16:9 fullscreen dd4, L4 + L12 (+ L1 dd8 21:9), NO_SAVE_WRITE.
Hypotheses / outcomes:
- H-quiet: post-signal loads exist (count > 0, witness > 0, ctl caught) but diff 0 in as=3 -> row H-canon(measured), census exits 0.
- H-torn: as=3 diff > 0 (as=2 0) -> name the writer (address histogram as in s7535: terrain texture stream? dynamic textures?),
  then fix: keep the fullSync tail async but run the job's texture loads before the post, or copy load sources at submit; or demote
  the OWNER-OPT-INS row. Measure visible consequence with the s7536-style per-state counters.
- H-no-window: 0 post-signal loads in as=3 (the tail is pure fullSync encode/GPU, all loads already processed) -> reads row
  H-ordered for reads; then only the fb-copy writes remain (check the guest never reads them before the next drain).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
