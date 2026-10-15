# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Context: s4956 — keys from title reach the hangar 3/3 (58-66 s) but (36,6) x8 never launches a mission (0 hits on 0x690400/0x620400). 512/0x690400 on the hangar-less route is the attract demo (s4954/s4955).
Work unit: find the hangar->mission input. Hypotheses: H-wrong-keys (other keycodes needed) vs H-menu-needs-navigation (selection must move before confirm) vs H-input-not-delivered (port ignores injected keys in the hangar). Discriminator: in ONE run at hangar, send a sweep of keycodes (36 return, 49 space, 125/126 arrows, 6 z, 7 x, then 36) with 5 s gaps and log which one changes the origin/phase or an input-poll counter. First grep src/ for the key->N64 button map. Positive control: a key that visibly advances a phase (e.g. at title). Start from scratch/agent/s4956_keyed_title.sh (no `timeout` on macOS).
Then record a mission-phase row in docs/M5-AUDIO-PLAN.md.
