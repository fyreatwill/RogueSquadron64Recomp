# Next work unit: catch the phase 0->3 write on 0x8010CA20 and its caller (early arm)
Hypotheses: H1 requestMissionTransitionMode(a0=3) via objective table (success); H2 another writer (FB2C8/FB454/FB558/FB634 sites in funcs_32); H3 death path (lives==0).
Discriminator: env TRAPSWAP=2500 zsh scratch/agent/m6_bp_trans.sh s5471a 480; first fix capture of ctx->r4 (try p ctx->r4). Control: rand_recomp stops. First phase-watch stop with value 3 -> bt frame #1 caller, and whether requestMissionTransitionMode bp fired just before.
HYPOTHESIS-ID: m6-mission-end-trigger
