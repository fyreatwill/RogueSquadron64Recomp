# NEXT work unit (s2032)

HYPOTHESIS-ID: m5-guest-gate-writer-order

## Work unit

Trace the retail caller/order for `reapplyDisplayMode` and its
`0x8008EC88` gate write before changing the existing port force-zero. This is
one ground-truth experiment, not a store reversal or a new runtime counter.
Use the already-valid s2031 port table as the port-side line: its phase-valid
row is `reapplyDisplayMode:reapply-success`, `0 -> 0`, followed by raw-gate
zero/skip rows. The new discriminator is retail execution at the reapply
entry and store PC, with the `exec-prev` caller histogram, in the same run as
the whole-RDRAM and physical gate-write controls.

## Competing hypotheses and discriminator

- **A — ordinary reapply order:** retail enters `reapplyDisplayMode` through
  the expected display-mode caller, reaches `0x8008EC88`, and the write is
  part of the normal title/hangar transition. This supports testing the
  original guest value later, but does not authorize it now.
- **B — late or alternate writer order:** retail reaches the store from a
  different caller/re-entry or with a transition order absent from the port.
  This keeps the force-zero arm closed and selects caller/order tracing.
- **C — watch/control failure:** the whole-RDRAM watch does not reach its cap,
  retail misses VI 1024 or hangar VI 512, or the PC watch has no hit despite
  the target write. Treat the result as unevaluable and repair only the
  oracle control.

The discriminator is one retail table keyed by phase and PC: reapply-entry
execution count, `exec-prev` caller PCs, `0x8008EC88` execution/write count,
and the target-write PC cluster. A/B split on the caller/order; C is accepted
only when its positive-control failure is visible. Do not compare a new
animating port run by wall-clock timing.

## Ground truth command

~~~sh
tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F51 --watch-pc 0x8008EB7C,0x8008EC88 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace > scratch/agent/s2032-groundtruth.log 2>&1
~~~

Accept the run only if the whole-RDRAM watch reaches its cap, the target
write watch fires, and retail reaches VI 1024 plus the hangar VI 512 origin.
Do not edit `fixup_game_funcs.py`, reverse `0x8008EC88`, or rebuild until
this command supplies its caller/order result. If the result is A or B, the
following unit can make one env-gated C88 store arm with every other gate
writer unchanged; it must be built and compared phase-gated against its
unset control in one iteration.
