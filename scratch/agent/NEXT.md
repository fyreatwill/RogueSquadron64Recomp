# NEXT work unit (s2212) — identify the guest mode VI field source

HYPOTHESIS-ID: m5-a1-port-mode-vcurrent-source

## Work unit

Make one bounded diagnostic change in
`lib/N64ModernRuntime/ultramodern/src/events.cpp`: extend the existing
`ROGUESQ_LOG_VI_CONTEXT_PORT` table with `mode->comRegs.vCurrent & 1` for
every width-640 row, and add its per-origin/bit counts to the existing
summary. Preserve the current row fields, 512-row cap, positive prefix,
current-line field, field knob, VI-state update, and target counters. Do not
change the default field, audio dispatch, task data, or any mitigation.
Because this edits `lib/`, export the submodule patch in the same iteration.

Before building, run the retail oracle preflight below with its whole-RDRAM
positive control. Then use these competing hypotheses and the one table below
to split them:

- H-PortModeVCurrentCarriesField: `comRegs.vCurrent & 1` is 1 on the
  field-1/`0x0066AA00` context while the current-line bit remains 0. This
  identifies the guest mode descriptor as the omitted field-one source.
- H-PortModeVCurrentFixed: `comRegs.vCurrent & 1` remains 0 across the early
  and target rows. This rules out the mode descriptor as the field selector.
- H-PortModeVCurrentDecoupled: the mode bit is nonzero or alternates without
  matching the observed origin/field relation. This identifies a mode/state
  cadence mismatch rather than a direct omitted source.
- H-PortModeVCurrentCoverage: the positive prefix fires but no bounded 640
  table rows arrive or the 512-row table overflows. This proves only that the
  source collection is insufficient.

The discriminator is one table keyed by observed 640 framebuffer/mode and
committed origin, counting selected `field`, `comRegs.vCurrent & 1`,
`VI_V_CURRENT_LINE_REG & 1`, field origins, candidates, and committed origin,
alongside prefix, row, and overflow counts. Require at least one prefix row,
one width-640 row, and zero overflow before classifying. Compare the port rows
with s2209's independent retail context table: field 0 at
`0x0066A500`/`0x005D4500`, field 1 at `0x0066AA00`, field 0 at
`0x00696100`, and field 1 at `0x00696600`.

## Exact commands

Retail preflight, before the port edit/build:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --input /opt/homebrew/lib/mupen64plus/mupen64plus-input-sdl.dylib \
  --secs 30 --hit-cap 10000 --watch-write 0:0x800000 \
  --watch-pc 0x80034D90 \
  --pc-phase-log 0x0066A500 --pc-phase-log 0x005D4500 \
  --pc-phase-log 0x0066AA00 --pc-phase-log 0x00696100 \
  --pc-phase-log 0x00696600 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start \
  --hold-ms 150 > scratch/agent/s2212_retail_mode_source.log 2>&1
```

Then edit, export, build, and run the same qualified port recipe:

```sh
./submodule-patches/export.sh
cmake --build build -j8
cd build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_VI_CONTEXT_PORT=1 ./RogueSquadron64Recomp \
  > ../scratch/agent/s2212_port_mode_source.log 2>&1 &
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
and summaries. If the controls pass and the table is non-overflowing,
classify exactly one of the first three hypotheses. Keep both field knobs
diagnostic-only.
