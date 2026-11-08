# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — why late presents commit at the wrong vsync phase (s6986).
HYPOTHESIS-ID: g1e-vi-phase-slip
State (s6986): with PRESENT_QOS=1, residual lates are committed 0-4 ms after the last on-glass vsync where normal frames
commit 6-12 ms after it, so they miss the latch and wait one extra vsync. Present hop and GPU tail refuted. s6984: VI->Q is
not longer on lates. So either the guest VI itself fired at the wrong phase vs the display vsync, or VI was on phase and
something before Q (not counted in VI->Q) varies.
Hypotheses:
- H-vi-slip: VI timestamps (tl event code 1, mapped to ring time via the G-row offset in g1e_late_leg.py) drift against the
  presentedTime grid; on lates VI phase vs display vsync is ~6-8 ms later than on normals. Points at ROGUESQ_VI_LOCK
  (events.cpp rs64_vi_lock_note_vsync) correcting too slowly or a VI timer wake late under the burst.
- H-vsync-jitter: the display vsync grid itself (P at intervals) jumps (WindowServer frame drop / ProMotion), VI steady.
- H-pre-Q: VI on phase, VI->Q equal, but the reference I compared is wrong (Q vs commit offset qc is ~0, so check VI->commit).
Measure OFFLINE first, no new build: extend tools/g1e_commit_phase.py to load the tl file (as g1e_late_leg.py does: ev,
offset o from G rows) and report per late/normal the phase of the VI that produced the frame vs the on-glass vsync grid,
plus P-interval regularity around lates. Data: scratch/s6986q/{tl_E*.bin.*,gring_E*.txt,ring_E*.txt}.
If H-vi-slip: inspect the VI_LOCK controller (events.cpp) and the VI timer thread wake (QoS?), fix, ABBA under the s6982
burst with scratch/s6986/drive.sh pattern.
Positive control: the normal-frame VI phase must be tightly clustered (VI_LOCK target 10 ms predicts a fixed offset).
