# NEXT work unit (independently test command-boundary E9 overcount)

HYPOTHESIS-ID: m3-e9-command-boundary

Build one phase-gated, telemetry-only probe recording, for the same late submit
ranges, every bridge-tested E9 slot, every RT64 command-start fetch (address,
raw opcode, command length), and direct versus pending completion. Keep runtime
behavior and mitigation code unchanged. Require existing positive controls in
the same run.

Competing hypotheses and discriminator:

- H-command-boundary: late bridge-only E9s are interior words skipped by the
  command-length walk.
- H-pending-path: late bridge-only E9s are split commands not counted at
  pending completion.
- H-other-filter: late E9 command starts reach a remaining parser/callback
  gate that prevents the count.

Discriminator: an E9 slot covered by the preceding parser command span selects
H-command-boundary; an E9 command start with pending metadata and no completion
selects H-pending-path; a command-start record that reaches the handler but
lacks the increment selects H-other-filter. Missing pairings remain unproven.

Expected commands: add all records in one build, run the existing phase-gated
VI-1024 recipe from `build/`, capture one log, and inspect bounded windows. No
mitigation is authorized.
