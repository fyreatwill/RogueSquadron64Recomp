# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — do the QoS opt-ins (GFX/GUEST/PRESENT/WL/UPLOAD) help on a QUIET host at the owner recipe? (s6988)
HYPOTHESIS-ID: g1e-qos-bundle
State (s6988): under the synthetic 14-spinner burst, all five QoS opt-ins together bring lates from ~160/5.5 min (s6982 no QoS)
to 4-14; UPLOAD_QOS=1 alone cut 21/21 -> 14/4 ABBA. Residual = Gfx thread runnable-not-running even at USER_INTERACTIVE.
None of this has been measured on a quiet host (the owner's normal play), and the owner has to flip five knobs.
Hypotheses:
- H-quiet-null: on a quiet host lates are already ~0 both ways -> bundle is harmless insurance; offer as one knob.
- H-quiet-gain: quiet-host lates (background WindowServer/Chrome) also drop -> recommend default-on to the owner.
- H-harm: USER_INTERACTIVE on ~17 threads starves audio/VI/present (more lates, AI underruns) -> keep opt-in, split.
Unit: one build adds ROGUESQ_QOS_ALL=1 (sets GFX/GUEST/PRESENT/WL/UPLOAD_QOS defaults to 1 unless individually set =0);
ABBA quiet host (NO burst), scratch/s6988/drive.sh minus the burst line, owner recipe 16:9 and 21:9 dd4 FPS60 VI_LOCK,
arms A0 (all off) / A1 (QOS_ALL) / A1b / A0b; score lates + [ai] underruns + crash with scratch/s6988/score.sh.
Positive control: the same QOS_ALL arm under the burst for 60 s must show lates << no-QoS (re-use s6982 burst).
Then a one-line OWNER-OPT-INS row "ROGUESQ_QOS_ALL=1"; default stays the owner's call.
