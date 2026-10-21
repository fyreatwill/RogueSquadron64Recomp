# NEXT: who sets orientation record byte0=1 for the player?

s5780 result: sb 0x800FFC60 copies record byte0 (=1, idx 0, flag sp+0x497=1) to the
caller's sp+0x175; every visible bit8call follows it. Do not re-log that store.

Work unit: static trace first (no build): in funcs_43.c find every store to the
record array at sp+0x198 (stride 0x2C, byte 0) in stepObjectOrientationTowardTarget
(s5775 found the ret2 store at 0x800FF6F0 writes sp+0x497; look for sb to 0($s?)/record
byte0 near 0x800FF*, 0x800FFA*). Name the test (geometry/terrain) that sets byte0=1.
Then one build+run on s5777_althold.sh logging that test's inputs for the player at the
store, paired to the next [bit8call].

- H-real-impact: byte0=1 comes from a true terrain/object hit test with plausible inputs (player really at ground y). Next: why the hit is lethal (float<=0 test).
- H-bad-input: test inputs wild/stale (e.g. uninitialised geometry). Next: writer of inputs.

Control: [bit8call] hw=0x0001 still prints; [sp175] lines still print src=1.

HYPOTHESIS-ID: g1-record-byte0
