# NEXT: M5 audio de-stub (docs/M5-AUDIO-PLAN.md)
HYPOTHESIS-ID: m5-audio-destub
s4552 closed the hangar-reach line: late route 420 s sits at VI 1024 (never 512), early route dies at musyxSynthFrame+5436. Do not re-run either.
Work unit: open docs/M5-AUDIO-PLAN.md, take the next un-executed de-stub step, implement it, validate with one soak (title phase, odd=0 control retained), record outcome.
Discriminator: does the de-stub dissolve the +5436 list-walk crash on the early route (s4551 recipe)? crash gone => audio-stub artifact; crash persists => genuine pool-link writer.
