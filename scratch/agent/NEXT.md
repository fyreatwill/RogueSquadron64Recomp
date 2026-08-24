# NEXT work unit (s2210) — compare port early VI context to retail

HYPOTHESIS-ID: m5-a1-retail-early-context-parity

## Work unit

Make one bounded diagnostic change in
`lib/N64ModernRuntime/ultramodern/src/events.cpp`: in the existing
`ROGUESQ_LOG_VI_CONTEXT_PORT` path, admit every width-640 commit to the
existing context-row table instead of filtering to framebuffer
`0x00695C00`, and raise only that printed row cap from 256 to 512. Preserve
the existing row fields, positive prefix, field knob, VI state update, and
target counters. Do not change the default field, audio dispatch, task data,
or any mitigation. Because this edits `lib/`, export the submodule patch in
the same iteration.

Before building, record the following competing hypotheses and use the one
run below to split them:

- H-PortEarlyContextParity: port rows for `0x0066A500` and `0x005D4500`
  select field 0 and commit candidate 0, while `0x0066AA00` selects field 1
  and commits candidate 1, matching the retail context table. This moves the
  open boundary past the early selector.
- H-PortEarlyContextFixedField: the port's early rows select field 0 for both
  `0x0066A500` and `0x0066AA00`, or commit the same candidate for both. This
  identifies a port field-state mismatch before the target transition.
- H-PortEarlyContextOther: the port has valid rows but its early framebuffer,
  mode pointer, field origins, or candidate arithmetic differs from retail.
  This identifies a context-tuple mismatch rather than a selector mismatch.
- H-PortEarlyContextCoverage: the positive prefix fires, but no bounded
  width-640 table rows arrive or the 512-row table overflows. This proves only
  that the port collection is insufficient and does not classify parity.

The discriminator is one table keyed by committed origin: for each observed
640 origin, count rows by `field`, `framebuffer`, `mode`, `candidate0`,
`candidate1`, and `committed`, alongside prefix count, summary `rows`, and
`overflow`. Require at least one prefix row, one width-640 row, and zero
overflow before classifying. Compare the port rows with s2209's retail rows:
retail had A500 `field=0/candidate0` 17/17, AA00 `field=1/candidate1` 139/139,
5D4500 `field=0/candidate0` 121/121, target 696100 field 0 96/96, and target
696600 field 1 95/95.

## Exact commands

After the bounded edit:

```sh
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_VI_CONTEXT_PORT=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2210_port_early_context.log 2>&1 &
pid=$!
for i in {1..60}; do
  kill -0 "$pid" 2>/dev/null || break
  sleep 1
done
kill -9 "$pid" 2>/dev/null || true
wait "$pid" 2>/dev/null || true
cd ..
```

Inspect only the positive prefix, `[phase]` width-640 origins, context rows,
and context summary. Use SIGKILL as shown. If the control is positive and the
table is non-overflowing, classify exactly one of the first three hypotheses;
otherwise record H-PortEarlyContextCoverage and design a narrower phase-gated
collection next.
