# NEXT work unit (s2211) — identify the port VI field source

HYPOTHESIS-ID: m5-a1-port-vi-field-source

## Work unit

Make one bounded diagnostic change in
`lib/N64ModernRuntime/ultramodern/src/events.cpp`: extend the existing
`ROGUESQ_LOG_VI_CONTEXT_PORT` table with the port's
`VI_V_CURRENT_LINE_REG & 1` value for every width-640 row, and add its
per-origin/current-bit counts to the existing summary. Preserve the current
row fields, 512-row cap, positive prefix, field knob, VI-state update, and
target counters. Do not change the default field, audio dispatch, task data,
or any mitigation. Because this edits `lib/`, export the submodule patch in
the same iteration.

Before building, use these competing hypotheses and the one table below to
split them:

- H-PortCurrentRegAlternates: the port current-line bit follows the retail
  selector (`0` for `0x0066A500`/`0x005D4500`, `1` for the
  `0x0066AA00` context), but the port's selected field remains 0. This proves
  the host current-field source exists but is not wired into `ViState::field`.
- H-PortCurrentRegFixed: the current-line bit remains 0 with selected field 0
  across the early and target rows. This proves the host VI state does not
  publish a field-1 source at this route scope; the missing producer is below
  the guest context table.
- H-PortCurrentRegDecoupled: the current-line bit is nonzero or alternates in
  a pattern that does not match the observed origins, while mode/framebuffer
  candidates remain valid. This identifies a VI timing/state cadence mismatch
  rather than a simple missing propagation from the current-line bit.
- H-PortCurrentRegCoverage: the positive prefix fires but no bounded 640 table
  rows arrive or the 512-row table overflows. This proves only that the source
  collection is insufficient and does not classify field behavior.

The discriminator is one table keyed by observed 640 framebuffer/mode and
committed origin, counting selected `field`, `VI_V_CURRENT_LINE_REG & 1`,
field origins, candidates, and committed origin, alongside prefix, row, and
overflow counts. Require at least one prefix row, one width-640 row, and zero
overflow before classifying. Compare the port rows with s2209's independent
retail context table: field 0 at `0x0066A500`/`0x005D4500`, field 1 at
`0x0066AA00`, field 0 at `0x00696100`, and field 1 at `0x00696600`.

## Exact commands

After the bounded edit:

```sh
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_VI_CONTEXT_PORT=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2211_port_vi_field_source.log 2>&1 &
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
and context summaries. If the controls pass and the table is non-overflowing,
classify exactly one of the first three hypotheses. If not, record
H-PortCurrentRegCoverage and design a narrower phase-gated collection next.
Keep the field knob diagnostic-only.
