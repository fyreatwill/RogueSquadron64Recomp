# Next work unit: why do ~40% of private-DMEM arms never leave VI phase 640 (intro) — and when does the sample-block chain break? (s4254)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4253: crash = stuck at 640 x cache first recycle (12/12 vs 12/12 separation). Two open questions:
(a) stuck-intro cause. Hypotheses: h1 intro end gated on audio/stream completion that private-DMEM/hurried audio perturbs; h2 input/autopilot timing; h3 gfx stall (LLE lock) delaying VI. Discriminator (offline first, no run): diff the logs of a stuck arm vs a good arm (s4252e4253_ab_1 armB2 vs armB1) in the 10-14 s window: first line present in good, absent in stuck.
(b) chain break: add head->next + node count to the [s4234-ENTRY] probe (tools/apply_s4234_entryprobe.py) for every call n>=15000; one B-arm wave of 4, SECS=75, env ROGUESQ_LOG_S4222=1. Control: ringS rows fire.
Harness: env OUTN=f TAG=_1 ARMS="B1 B2 B3 B4" SECS=75 zsh scratch/agent/s4252_ab.sh ; classify arms by last [phase] line + CRASH.
