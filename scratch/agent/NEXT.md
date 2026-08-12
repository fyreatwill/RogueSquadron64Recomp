# NEXT work unit (consume the predecessor-latch soak)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

The v5 regeneration-safe latch is built and boot-positive-controlled: each of
tasks 1--4 reports `predecessor=1`. Consume the queued `s736_reset_predecessor`
verdict before changing code. It drives title-gated input to section 2 and must
produce `[e9-prov-reset-predecessor]` plus a depth cap row.

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

Score the queued `[e9-prov-reset-predecessor]` rows. A cap-row predecessor that
is direct/bootstrap selects H-direct-bootstrap-entry; an `L_1298` relay selects
H-trigen-relay-entry; a reset without a preceding marker while the unconditional
target marker fires selects H-predecessor-latch-broken. Positive controls: the
same run must retain balanced direct-only boot rows, reproduce a section-2 cap
row with reset-active count equal to depth-0 reuse and zero unpaired reuse, and
show at least one target-`0x1DB0` predecessor marker.

## Commands

    tail -20 scratch/agent/SOAK-RESULTS.md
    rg -n '\[e9-prov-reset-predecessor\]|\[e9-prov-reset\]|\[e9-prov-depth-summary\]|\[e9-prov\]' scratch/agent/soak_results/s736_reset_predecessor_*/run.log | tail -180
