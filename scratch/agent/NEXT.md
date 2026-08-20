# NEXT work unit (s2017) — join port-side gate/status writers

HYPOTHESIS-ID: m5-port-writer-thread-census

## Work unit

Run one batched, phase-gated port-side census using the current external
45-file generated tree. The s2016 capture established that this tree reaches
the required phases, so do not wait for the exact s2007 snapshot and do not
reconcile the four companion symbol files. Keep status, audio, spin, PI,
guard, and mitigation behavior unchanged.

The join must contain all seven fields in the same run: every direct status
writer PC and slot/index, old/new byte, host thread, shutdown call, service
entry/exit, callback dispatch/return, and the expected `0x8009B7EC` zeroing
edge. The existing s2006/s2007/s2008 generated instrumentation is already in
the current build.

## Competing hypotheses and discriminator

- H1: The port reaches the legitimate slot-0 `0x03` write and the service
  worker clears it transiently; the join shows the same slot, writer, and
  callback edge before shutdown returns.
- H2: The port's `0x03` belongs to another slot or writer path; slot/index and
  thread correlation separates it from the watched slot-0 shutdown record.
- H3: The port never writes slot 0 to `0x03`; shutdown spins with live controls
  but no slot-0 `0x03` writer.

The discriminating result is one phase-gated table, not a field-by-field
probe. H1 requires same-slot `0x03` then zero with the worker edge; H2
requires another slot/index or writer; H3 requires shutdown with no live
slot-0 `0x03` writer and a live positive control.

## Exact commands

Verify the tree without changing it:

```sh
test -f ../N64Recomp/RecompiledFuncs/funcs.h
test -f ../N64Recomp/RecompiledFuncs/recomp_overlays.inl
test -f ../N64Recomp/RecompiledFuncs/lookup.cpp
test "$(find ../N64Recomp/RecompiledFuncs -maxdepth 1 -name 'funcs_*.c' | wc -l)" -eq 45
```

Run one capture from the build directory. VI 1024 and hangar VI 512 are the
phase controls; the first 24 service rows are the service positive control,
and `0x8009B7EC` is the named worker-store control:

```sh
OUT="$PWD/../scratch/agent/s2017_port_writer_join"
mkdir -p "$OUT"
env ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_S2008_STATUS_WRITERS=1 \
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
  zsh ../tools/probe.sh "$OUT" 180 2 >"$OUT/driver.log" 2>&1
```

Treat a crash before the phase or before the worker positive control as
unevaluable and fix the recipe in this iteration; do not infer H2/H3 from a
dead run. Do not use stopwatch-based comparison against an animating scene.
