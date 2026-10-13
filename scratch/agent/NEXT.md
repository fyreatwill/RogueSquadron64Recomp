# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4737: runaway tasks (240-242) re-seed 0x30(r18) at L_1DB0 (site 3) after an end-DL (prevop 0xB8) at call depth 0; normal tasks 41/42 hit site 3 only at entry and terminate another way.

Hypotheses:
- H-1DB0-is-restart: do_indirect_jump `case 0x1DB0` is the legit "DL ended -> re-run root" edge and normal tasks end earlier via a different edge (e.g. a 0xB8/0xB9 with a terminating flag/word we mis-evaluate in runaway).
- H-wrong-ra: r31 at the end-DL is a stale/wrong value (0x1DB0) in runaway only.
- H-overlay-byte: DMEM 0x153 overlay byte makes the dispatcher pick L_1DB0 vs a completion path.

Discriminator (one build, one run): at the indirect-jump dispatcher log (task, fetch n, jump_target, r31, DMEM[0x153], call depth, last DL word w0/w1) for the last 8 jumps before every task end (normal) and before each site-3 hit (runaway). Positive control: task 41 must log its terminating jump. Outcome: differing target/ra => H-wrong-ra; same target but differing 0x153 or depth => H-overlay-byte; identical => H-1DB0-is-restart (then inspect what the DL word at the end says).
Run: add to fixup 18, strip dlwalk lines from build/factor5_ucode/factor5_ucode_recompiled.c, rerun tools/fixup_factor5_ucode.py <file>, DEVELOPER_DIR=... cmake --build build -j8, zsh scratch/agent/s4737_run.sh.
