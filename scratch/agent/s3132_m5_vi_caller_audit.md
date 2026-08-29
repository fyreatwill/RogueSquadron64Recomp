# Session 3132 — `freeRenderSubsystemResources` caller audit

## Competing hypotheses

- H-AlreadyEnumerated: the wrapper has no transition-capable caller absent from
  the already audited video paths.
- H-NewStaticCaller: an unenumerated caller reaches the wrapper during the
  retail 640-to-1024 transition and supplies a new oracle PC.
- H-StaticInsufficient: the available generated/decomp artifacts do not expose
  enough callsite identity to classify the wrapper.

## Discriminating measurement

The complete text census covered the companion repository, project sources,
generated-function snapshot, symbol table, and registration artifacts for
`freeRenderSubsystemResources`, `selectAndApplyViMode`, and both addresses.
The generated bodies were inspected for the actual call edge and surrounding
control flow. A transition-capable caller would select H-NewStaticCaller and
an exact guest instruction for a later retail watch; a complete absence of
callers beyond the known wrapper edge selects H-AlreadyEnumerated; contradictory
or incomplete identity selects H-StaticInsufficient.

## Census

| Artifact | Result |
|---|---|
| Companion `symbol_files/main_overlay.txt` | Names `freeRenderSubsystemResources` at `0x80018650` and `selectAndApplyViMode` at `0x8001BB6C`; no callsite listing or alternate alias |
| Companion source/decomp tree | No body or textual call reference for either symbol; only symbol-file definitions are present |
| Current project sources and symbols | One definition entry for each function in `syms/rogue_squadron.syms.toml`; no source-side caller |
| Generated snapshot `scratch/agent/s390_verify/before_current_applied` | `freeRenderSubsystemResources` is defined once in `funcs_4.c`; its only relevant edge is `0x800186C0: jal 0x8001BB6C` |
| Generated registration/headers and available scans | Both functions are registered under their human names; no second generated caller or overlay alias |

The complete generated wrapper body frees the texture LUT and four resource
pointers, then calls `selectAndApplyViMode` at `0x800186C0`, and returns 1.
The selector copies one of three 0x50-byte mode descriptors based on feature
bytes at `0x8012A865`, `0x8012A864`, and `0x8012A862`, then calls `osViSetMode`
at `0x8001BC28` and waits on the video queue. Neither body contains a
target-phase marker, pending-word store, or alternate dispatch.

## Decision

H-AlreadyEnumerated selected. No new transition-capable instruction can be
selected from this chain. The represented `0x800186C0` edge was rejected by
the independent retail capture in Session 3131. This static result rules out
another hidden caller in the wrapper chain, but it does not identify the
upstream 640-to-1024 handoff. No build, oracle run, port probe, audio change,
or mitigation was performed.

Evidence: the bounded `rg` census, generated body excerpts, project symbol
table, and companion symbol file inspected in this iteration.
