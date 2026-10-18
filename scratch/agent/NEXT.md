# Next work unit: confirm terrain relief renders in free flight (not briefing shot)
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5428): across pitch the horizon moves and flat sand ground renders; no terrain relief seen, but frames are briefing/opening. Tools: `FBD_EVERY=50 zsh scratch/agent/m6_keyed_hold.sh <tag> <hold>`.
Hypotheses: (A) relief exists only later in flight; (B) relief meshes dropped post-parse; (C) never submitted.
Discriminator: hold >=600 s so autopilot is in free flight, dump every 50 VIs, montage the last 10 frames; compare LOG_RDP_TRICOUNT vs LOG_RT64_DRAWN. Relief seen -> A; flat only with high tricounts -> B; low tricounts -> C.
