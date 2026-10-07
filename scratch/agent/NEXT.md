# Next work unit: A12 second spin (0x8014974C) — same treatment as the countdown wait

HYPOTHESIS-ID: m5-a12-wait-hatches

s4192 de-stubbed the 0x8014998A countdown wait: default is now a yielding spin;
the old pump measured 16->16 (no-op). Template: tools/apply_s4192_m5_wait_spin_yield.py
(+ _default) and scratch/agent/s4192_wait_spin_default.sh (3 concurrent arms).

Work unit: instrument the separate one-byte gate spin at RAM 0x8014974C
(G_BASE-0x68B4) in waitForMusyXAudioTaskDone (see fixup_game_funcs.py ~line 8240
comment, s330-332). Hypotheses: H-never-entered (gate already satisfied at target
phases; nothing to de-stub), H-yield-clears (a yielding spin lets the real writer
clear it), H-needs-other-writer (still stuck after yield cap -> name the writer).
Discriminator: enter/exit rows with initial gate byte, blind vs yield arm, in one
run (blind arm = positive control: enter row without exit). If H-never-entered,
close it and move to Step 7 (status-03 reaping, A14).
Also worth one line: the pre-wait width-320 segfault si_addr=0x400128d47 (2/6 runs)
is an M3-family item; do not chase reactively.
