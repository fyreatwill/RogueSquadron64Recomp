# NEXT work unit (s1148)

HYPOTHESIS-ID: vi-post640-state-path

Audit the generated/runtime callers of the VI mode selector after the final
640 producer call. Do not add a runtime guard or repeat the NPC boundary test.

Competing hypotheses and discriminator before the work unit:

- H1/selector condition: the post-640 caller runs but its selector/state
  inputs prevent a 1024 mode request.
- H2/caller absent: the active loop continues in slot/host/audio work without
  reaching any post-640 mode-selector caller.
- H3/boundary relevance: the corrected boundary reaches the target phase;
  this requires both a positive task-control E9 row and a VI-1024 marker.

Discriminating measurement: statically enumerate every generated call to the
VI selector/mode-setting path and correlate it with one phase-scoped runtime
state marker after the final 640 producer call. A post-640 selector marker
with unchanged selector inputs selects H1; continued positive activity with
no selector marker selects H2; VI-1024 plus task-control E9 selects H3.

```sh
rg -n 'osViSetMode|setViMode|VI_.*1024|vi-selector' src lib tools docs | head -160
rg -n 'func_.*setVi|func_.*Vi|osViSetMode_recomp|ROGUESQ_LOG_VI_SELECTOR' RecompiledFuncs src tools | head -160
```

Expected outcomes:

- SELECTOR ACTIVE/H1: a post-640 selector call is present; compare its state
  inputs with the expected 1024 descriptor selection.
- SELECTOR ABSENT/H2: static callers are known but runtime state markers stop
  while host/audio/slot controls continue; isolate the missing state-path edge.
- TARGET REACHED/H3: VI-1024 and a positive task-control E9 row both appear;
  then run the corrected-boundary crash comparison.
