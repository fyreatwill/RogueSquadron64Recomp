# NEXT work unit (attribute the predecessor of each active L_1DB0 reset)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

The consumed s734 soak ruled out mixed retained reset state but left its source
unresolved: all 61 section-2 cap rows retained `ra=0x1088`, resident 0,
pending L_12A0 source 0, and inactive inline state. Build one regeneration-safe,
phase-scoped predecessor latch: on every `do_indirect_jump` whose normalized
target is `0x1DB0`, retain `jump_target`, `debug_line`, `r31`, resident, `r17`,
and whether it followed `L_1298`; have `rs64_e9prov_l1db0_reset` consume and
print that latch with the existing bounded first/last active-reset records.
Do not change depth handling or add a mitigation.

## Competing hypotheses

- **H-direct-bootstrap-entry:** the predecessor latch shows a direct
  `do_indirect_jump→0x1DB0` entry with the bootstrap return (`ra=0x1088`), not
  the TriGen relay; repeatedly taking this path during an active `0x06` child
  is the concrete wrong-route candidate.
- **H-trigen-relay-entry:** the predecessor is `L_1298`/the known `0x05`
  selector-0x0C relay, so the reset belongs to the opaque TriGen continuation;
  its semantics, not overlay dispatch, must explain the depth model.
- **H-predecessor-latch-broken:** cap rows retain active resets but no matching
  preceding `0x1DB0` jump, while a same-run unconditional target-`0x1DB0`
  marker fires. The host correlation, rather than either route theory, is
  invalid.

## Discriminating measurement

Score the new `[e9-prov-reset-predecessor]` rows. A cap-row predecessor that
is direct/bootstrap selects H-direct-bootstrap-entry; an `L_1298` relay selects
H-trigen-relay-entry; a reset without a preceding marker while the unconditional
target marker fires selects H-predecessor-latch-broken. Positive controls: the
same run must retain balanced direct-only boot rows, reproduce a section-2 cap
row with reset-active count equal to depth-0 reuse and zero unpaired reuse, and
show at least one target-`0x1DB0` predecessor marker.

## Commands

    python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    cd build && cmake --build . -j8
    env ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 zsh ../tools/probe.sh ../scratch/agent/s735_reset_predecessor 300 '3:start 7:start 11:start'
    rg -n '\[e9-prov-reset-predecessor\]|\[e9-prov-reset\]|\[e9-prov-depth-summary\]|\[e9-prov\]' scratch/agent/s735_reset_predecessor/run.log | tail -180
