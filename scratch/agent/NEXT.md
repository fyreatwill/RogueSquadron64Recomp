# NEXT work unit (s2015) — join port-side gate/status writers

HYPOTHESIS-ID: m5-port-writer-thread-census

## Work unit

Obtain from the project owner either the phase-valid s2007 generated snapshot
(`funcs_*.c`, `funcs.h`, `recomp_overlays.inl`, and `lookup.cpp`) or explicit
authorization to reconcile the four pending companion symbol files. Then run
one batched port-side census joining the gate writer PC, slot/index, old/new
byte, host thread, shutdown call, and service/callback edge. Do not change
status, audio, spin, PI, guard, or mitigation behavior.

This unit cannot start until that artifact or authorization is supplied. The
s2014 retail oracle capture is complete and does not substitute for the
port-side generated provenance.

## Competing hypotheses and discriminator

- H1: The port reaches the legitimate slot-0 `0x03` write and the service
  worker clears it transiently; the join shows the same slot, writer, and
  callback edge before shutdown returns.
- H2: The port's `0x03` belongs to another slot or writer path; slot/index and
  thread correlation separates it from the watched slot-0 shutdown record.
- H3: The port never writes slot 0 to `0x03`; the shutdown spin observes a
  stale or mismatched status, so the missing writer—not the reaper—is the
  discriminator.

The one discriminating measurement is the seven-site join in one phase-gated
run: writer PC, slot/index, old/new status byte, host thread, shutdown call,
service entry, and callback/zeroing edge. H1 requires a same-slot `0x03` then
zero with the worker edge; H2 requires another slot/index or writer; H3
requires shutdown with no live slot-0 `0x03` writer.

## Exact commands after the dependency is resolved

Verify the supplied tree before any build:

```sh
test -f <phase-valid-tree>/funcs.h
test -f <phase-valid-tree>/recomp_overlays.inl
test -f <phase-valid-tree>/lookup.cpp
find <phase-valid-tree> -maxdepth 1 -name 'funcs_*.c' | wc -l
```

If the owner authorizes reconciliation, record the authorization in the
ledger, reconcile only the four named companion files, then regenerate in the
required order (`make_elf.py`, N64Recomp, `fixup_game_funcs.py`, CMake). Build
all census fields in one build and run the existing phase-gated hangar recipe
with `ROGUESQ_LOG_ALL=1`; do not spend a build/run per field. The outcome table
above selects the next audio step.
