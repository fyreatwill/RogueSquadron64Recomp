# Next: idiom-class audit follow-ups after the unsigned-base class closure
HYPOTHESIS-ID: hangar-flake-fault-class

State (s5095): the hangar flake (updateHangarBayScene+76424) is confirmed fixed (s5094 soak: 3/3 hangar
arrivals, 0 CRASH). The remaining 11 unsigned-base MEM_x sites in the live tree (all env-gated
diagnostics) were stale forms of text whose fixup sources already emit S32(); tools/repair_unsigned_base_live.py
synced them, `scratch/agent/audit_unsigned_base.sh` is now empty for tools/ and generated code
(positive control = 1). s5095 soak (all gating env vars ON) verdict is in SOAK-RESULTS.md.

1. Fold the s5095 soak verdict into CURRENT-TRUTH if not yet done. Crash with a gated diagnostic ON =>
   a new fault class (read the faulting symbol; do not guess).
2. DONE s5096 (shape 2 audited, 0 live sites). Original text: Extend the audit to the other zero-extension shapes the regex does not match: `MEM_x(off, (uint32_t)X)`,
   `MEM_x(off, U32(X))`, `(uint32_t)` / `u`-suffixed *variables* used as the base in diagnostics.
   Command: grep -nE 'MEM_[A-Z]+\([^,]+,[[:space:]]*(U32|\(uint32_t\))\(' tools/*.py build/factor5_ucode/*.c
   Classify each as base (bug) vs value (fine).
3. Regen-safety (still open): confirm the fixup repair branch ("AC8C0 port log unsigned base repaired")
   triggers on a copy with the stale form — needs a pristine-regen copy, see s5090/s5091 notes.
