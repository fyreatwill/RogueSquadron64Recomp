# NEXT: post-RSP-fix crash-family re-evaluation (passive soaks) then M3/M5 audit

HYPOTHESIS-ID: rsp-fix-dissolves-crash-families

s4521 parked hangar-artifact-triage (stubs/right-edge strip cosmetic; needs RT64 tri-index mask render to map pixels to tris, a renderer patch).
Hypotheses: (A) the s4518 LUV/LFV/LHV fix dissolved some RSP-fed corruption crash families (waitForAnyAudioSlot, voice-array, +5436 pool links); (B) no effect on crash rates.
Work unit: enqueue 2 soak recipes in scratch/agent/soak_queue/ from an existing recipe (e.g. s4467/s4468 hdr_nested style: self-contained, watchdog, SIGKILL, all passive breadcrumbs armed) on the current build, and compare crash/no-crash and phase reached against the pre-fix SOAK-RESULTS lines (s4450/s4452 rc=1 at 304s/217s). Need a positive control (a pre-fix-style crash signature check) before reading zeros.
Discriminator: >=2 of 2 soaks reach hangar VI 512 and survive 600s => supports A (weak, n=2); crash with the known +5436/+9632 signatures => B.


## s4522 update
Soak s4522_postfix_replay enqueued. Next iteration: read its SOAK-RESULTS.md line. 0 crashes in 4 arms => record A (n=4, single recipe) in CURRENT-TRUTH and re-audit which waitForAnyAudioSlot/voice-array guards are now dead; crashes => B, compare signature to s4452 and resume M5 plan.
HYPOTHESIS-ID: rsp-fix-dissolves-crash-families
