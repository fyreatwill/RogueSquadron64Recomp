# Identify the rs_strncpy caller that supplies the late name span
HYPOTHESIS-ID: m5-audio-destub

The s4601 widened census passed the entry and adjacent controls and captured
`late` at physical offsets `0x1724F4..0x1724F7`, all from `rs_strncpy`
(`0x80007670`) in phase 3. Eight static callers remain.

Competing hypotheses and the discriminator:

- H-call-voice-name: the bad caller supplies the destination and source from
  the live voice/name table; its caller PC and `(a0,a1,a2)` row identify the
  legitimate name-construction path.
- H-call-other-name: another caller writes the same destination; its call-site
  PC identifies the unexpected path.
- H-call-port-only: no call-site row targets `0x801724C0`/`0x801724F4` in the
  qualified phase; the remaining boundary is host/translation or an
  uninstrumented call setup.

Discriminating measurement: one build and one qualified run. Add a
regeneration-preserved hook at every generated `jal rs_strncpy` call site,
logging caller PC, phase, `ctx->r4`, `ctx->r5`, and `ctx->r6`, bounded by the
phase and caller PC. Keep the existing entry and adjacent controls. A call
with destination `0x801724C0` selects its caller; a source in the name table
with length covering offset `0x34` identifies the input; no destination row
with controls live selects the unresolved boundary.

Before building, add the call-site hook to the existing generated fixup
workflow, then run:

```sh
python3 tools/apply_s4601_strncpy_callers.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from the repo root with the qualified environment used for s4601:
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1
ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_S4299=1 ROGUESQ_LOG_S4597=1`, using
`PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=300 PROBE_KEYS_FROM_PHASE=1
PROBE_LEAVE_OK=1 PROBE_KEYS="3:start 7:start 11:start 15:a 100:start"` and a
SIGKILL watchdog. Capture under `scratch/agent/s4602_callers/`.
