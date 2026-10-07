# Next work unit: discriminate the loop branch after 0x8008F918

HYPOTHESIS-ID: m5-step4-object-entry-body

Session 4186 qualified the canonical paired oracle/port route with a
regeneration-safe witness at `0x8008F914` and `0x8008F918`. The positive
control, both retail phases, both port phases, and 130 port body rows fired;
port emitted 260 loop rows. At hangar, port progressed `a2=0x47` to `0x48`
against `s0=0x48`, changing the compare from 1 to 0. Retail independently
recorded 71 hits at both PCs with matching `s0=0x48`, `s1=0x1B000`, and
predecessor linkage. The open boundary is the branch at `0x8008F91C`.

Competing hypotheses:

- H-branch-parity: the `bne $v0,$zero,0x8008F8FC` decision and delay-slot
  successor match, moving the boundary into the branch target/exit.
- H-branch-mismatch: the branch input or taken/not-taken outcome diverges,
  selecting the first divergent control value.
- H-target-route-invalid: any positive control or target phase fails; no
  branch comparison is valid.

Discriminator: add a regeneration-safe port witness at `0x8008F91C` and
`0x8008F920`, and an oracle `--watch-pc`/field capture for the same PCs. Run
one paired phase-gated measurement with:

`zsh scratch/agent/run_s4182_m5_object_body.sh`

Preserve the whole-RDRAM positive control, both title origins
(`0x00790400`/`0x00790800`), both hangar origins
(`0x006AB400`/`0x006AB800`), the existing entry/body/loop rows, and the
canonical autopilot with `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`. Matching branch
tuples select parity; a mismatch selects the first divergent control input;
missing controls or target phases selects route-invalid. Do not change audio,
gate, writer, payload, or mitigation behavior.
