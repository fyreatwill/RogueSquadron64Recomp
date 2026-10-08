# Next work unit: M5 Step 10b - what is the fresh-save 640 phase (2.8-49 s) and post-title 640@0x696100 screen?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4226: stale save -> title 14.7 s, hangar 24.0 s (control OK). Fresh save -> title 49.3 s, then 640@0x696100 at 75.9 s, no hangar, crash last-guest-pc 0x80001b08. NOPUMP=0 no effect (A12 refuted).
Hypotheses: (a) fresh save triggers a first-run/intro flow needing different input; (b) nonzero audio lengthens an intro wait (audio-timing); (c) crash at 0x80001b08 truncates the run.
Discriminator: fresh-save arm with frame dumps at ~20 s, 49 s, 76 s, plus a fresh-save arm with volume forced to 0 after load. Title still at ~49 s with zero volume -> flow (a); 14.7 s -> audio timing (b).
