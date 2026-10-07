# Next work unit: discriminate the loop-exit successor after 0x8008F91C

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4187 qualified the canonical paired oracle/port route with a
regeneration-safe witness at `0x8008F91C`. The positive control, both retail
phases, both port phases, and 130 port branch rows fired. Port and retail
matched `v0=1` through `a2=0x47` and `v0=0` at `a2=s0=0x48`; the open
boundary is the loop-exit successor after the delay-slot increment.

Competing hypotheses:

- H-successor-parity: the post-delay-slot `v1` and first loop-exit state match,
  moving the boundary into the first post-loop load.
- H-successor-mismatch: the exit-side `v1` or post-loop state diverges,
  selecting the first divergent control value.
- H-target-route-invalid: any positive control or target phase fails; no
  branch comparison is valid.

Discriminator: add a regeneration-safe port witness at `0x8008F924` and the
first post-loop load, plus an oracle `--watch-pc`/field capture for the same
successor. Run one paired phase-gated measurement with:

`zsh scratch/agent/run_s4188_m5_object_successor.sh`

Preserve the whole-RDRAM positive control, both title origins
(`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), the existing entry/body/loop rows, and the
canonical autopilot with `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Matching
successor tuples select parity; a mismatch selects the first divergent
control input; missing controls or target phases selects route-invalid. Do
not change audio, gate, writer, payload, or mitigation behavior.
