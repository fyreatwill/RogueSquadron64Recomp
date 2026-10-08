# Next work unit: name the ~50 tracked framebuffers behind the RT64 stall (s4270)

HYPOTHESIS-ID: m5-audio-destub-sequence

Context (s4268): the send_dl / audio-gap stall is RT64 State::checkRDRAM XXH3-hashing a tracked framebuffer set that grows 3 -> 56 (1.8 -> 13 MB per fullSync). Not audio. s4269 was a maintenance compaction of CURRENT-TRUTH (no experiment run); this unit is unchanged from s4268's plan.

Hypotheses:
- A: bogus color-image sets from the LLE stream at wild addresses/widths create entries (cf. 0x1F0D74 width 1161).
- B: legitimate per-effect framebuffers that retail also tracks but RT64 never prunes.
- C: entries are depth/aux buffers duplicated per address alias.

Discriminating measurement (ONE build, ONE run): extend ROGUESQ_S4268 at the framebuffer creation site (lib/rt64 framebuffer_manager.cpp:~95) to log each creation (t, address, width, height, format/size, creating DL ordinal), plus a one-shot dump of the whole map (address, width, height, RAMBytes, lastWriteFmt) at ~28 s. Run from build/ with the ROM, SIGKILL after ~35 s, single instance, env-prefixed with `env`.
Positive control: the creation log must show the initial 3 entries at t~3 s and the dump must total 56 entries (matching the s4268 counter).

Outcomes:
- Many entries with odd widths/addresses outside the retail colour/depth set -> A: name the writer of those color-image sets in the LLE path (ORIGIN line required).
- Regular widths (320/640/etc.) at distinct addresses that retail also uses -> B: add a prune in lib/rt64, then `./submodule-patches/export.sh` and commit in the same session.
- Same sizes at address aliases (differing only in high bits) -> C: canonicalise the key.

After that: re-rank M5 steps in docs/M5-AUDIO-PLAN.md (Step 9/10) and measure the default-arm audio task rate t=18-28 with an `=0` control.
