# Next work unit: M5 A11 — yield inside waitForAnyAudioSlot spin so ticks can finish the voice

HYPOTHESIS-ID: m5-a11-pretitle-slot-stall

s4196: slot-0 byte stall pre-title is NOT a missing producer; musyxRenderVoiceSamples clears 02->00 only after the cap fires
(cap5m.log:110398 vs fire 110202). The spin is non-yielding so audio ticks are starved. Hypotheses: H-no-yield (adding a yield in
the spin lets render finish, fires 1->0), H-tick-gated-elsewhere (yield added but ticks still don't come; fires stay 1), H-retail-same.
Discriminator: one run, two concurrent arms: (a) unchanged, (b) yield-per-N-iterations in the waitForAnyAudioSlot loop
(fixup_game_funcs.py, same pattern as the A12 countdown yield, s4192). Positive control: arm (a) still prints
[waitforslot-guard-fire] fires=1. Template: scratch/agent/s4196_slot0_cap_ab.sh. Regen order applies (fixup script, then cmake).
