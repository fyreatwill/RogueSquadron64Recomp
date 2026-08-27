# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable project
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is
authoritative for exact commands and probe rows.

Current maintenance marker: Session 2517 (2026-08-26).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- Qualified route: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation needs a named writer, a
  legitimacy judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub. The image arm performs DMEM work, returns
  `Broke`, emits generated DMA, and can publish PCM. Stock `aspMain` is not
  this game's contract; MORT is a separate CPU speech asset.
- The retail oracle is the independent witness for game-side memory claims.
  Whole-RDRAM, phase, task/status, and named-PC controls must pass before a
  retail null is interpreted. It reaches attract, title, and hangar, not a
  mission.

## Latest evidence

- **s2514 — stage-2/DMA attribution is an observer-contract limitation.**
  Static audit shows `rs64_audio_image_stage` runs before the shared `L_13B0`
  `DO_DMA_WRITE`; the generic DMA observer later reconstructs identity from
  the current route and destination without retaining the stage marker. In
  s2513 ordinal 606, the nonzero pre-write stage row at `0x168B50` had no
  matching DMA event; the only joined event was stage 3 at `0x178D80` with
  zero payload. This does not distinguish missing stage-2 observation from a
  later overwrite. Image-stage and PCM controls were positive; no writer or
  mitigation claim is authorized. Artifact:
  `scratch/agent/s2514_m5_dma_attribution/audit.md`.
- **s2513 — the qualified image capture selects the RSP/image payload writer
  at the observable consumer boundary.** Image ordinal 606 produced stage-2
  output at `0x168B50` with 621 nonzero bytes and FNV `2B9E9631`; an
  independent PCM source/consumer pair used the same address and fingerprint.
  Image, DMA, AI-table, task-join, and PCM controls were positive, with no
  guest CPU writer rows. Exact DMA-event attribution remains open because of
  the observer limitation above. Artifact:
  `scratch/agent/s2513_m5_payload_writer/audit.md`.
- **s2511 — staggered startup separated paired-route failure from the later
  image-arm crash.** Both staggered image arms passed 1024 and reached hangar;
  the paired image arm later crashed in `updateHangarBayScene+76424`, the
  baseline in `do_rom_read+572`, and the silent peer reached its target and
  was killed without a crash marker. This supports startup-order as the
  explanation for the earlier pre-target symptom and refutes concurrent
  resource pressure as sufficient. The later crash writer and exact payload
  writer remain open. Artifact:
  `scratch/agent/s2511_m5_staggered_image_concurrency/audit.md`.
- **s2516 — no Step 3 edge was proven in the title-phase A/B.** The retail
  whole-RDRAM positive control reached 10,000 callbacks. Stub and image arms
  both reached `1024 @ 0x790400`; the image had 1,597-byte DMEM changes,
  `break_pc=0x1328`, and generated DMA, but all observed stage/PCM payloads
  were zero and no output consumer join or legitimate writer was selected.
  This selects no-edge at this route scope; route-only variation remains
  possible against s2513. No behavior change is authorized. Artifact:
  `scratch/agent/s2516_m5_contract_edge/audit.md`.
- **s2517 — a new independent retail task/data boundary still did not name a
  Step 3 edge.** The oracle whole-RDRAM control recorded 359,402 writes and
  reached title and hangar. It retained 1,227 phase-gated type-2 task rows:
  title used `data_ptr=0x80171CE0` / `+0x100=0x171DE0`, hangar used
  `data_ptr=0x80171E70` / `+0x100=0x171F70`, and every row had zero
  output/yield fields. The watched task-data, `+0x100`, and image spans had
  positive writer tables and nonzero snapshots, but no writer was shown to be
  the missing image payload or output consumer. Together with s2516 this
  selects `H-no-edge` at the current route scope; no behavior change is
  authorized. Artifact:
  `scratch/agent/s2517_m5_contract_boundary/audit.md`.

## Active backlog

This is one monotonic sequence; #1 is the next campaign priority.

1. **M5 Step 3 contract edge — closed at the current route scope.** The direct load boundary,
   SP completion/consumption, image DMEM work, generated DMA, and PCM
   consumer are live under qualified controls. Runtime joins show image
   stage-2 destinations equal generated AI-table entries, but the legitimate
   nonzero payload writer is only selected at the observable consumer
  boundary and exact DMA attribution is still open. Do not map through
  `gspTask`, infer identity from timing or hashes, or change task/output
  fields without a named writer and independent retail evidence. s2516 and
  s2517 found no new legitimate edge; do not add a writeback/remap or repeat
  the unresolved observer. M5 image execution remains opt-in, and later M5
  steps remain conditional on a new named retail writer/value boundary.
  Next work unit: begin the bounded generated-symbol renaming sweep.
2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence breadcrumbs belong in the
   soak queue.
3. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
4. **Generated-symbol renaming — active after M5 Step 3 closure.** Resume with
  one bounded address-region census and only names supported by the companion
  decomp or clear local semantics; leave unresolved placeholders unchanged.
5. **M4 accumulator-origin work — parked** pending a new boundary idea.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route is `LLE_UNGATED=1, LLE_SOLO=1`; it reaches title and
hangar. Menu spin yield is a diagnostic route aid, not a default behavior
change. Factor 5 mappings and independent controls are in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md).

### M5 audio and image output

Direct service entry/exit, service gate/loop, task/AI boundary, image DMEM
work, generated DMA, reporter association, target-route SP queue consumption,
and PCM consumption are live on the port. The image arm's downstream identity
is not yet a complete legitimate slot, voice, PCM, or output mapping. Retail
proves related ranges and task-field writers, including the second-range
helper/caller relation, but does not prove a port equivalent. Zero-valued rows
are diagnostically ambiguous; no output remap or mitigation is permitted
without a named legitimate writer and an `ORIGIN:` line.

### VI, M3, and generated symbols

Retail/port VI selector and current-line publication remain unresolved outside
the qualified route. M3 is parked pending a complete idiom audit. Generated
symbol renaming remains parked at the useful boundary.

## Superseded conclusions

These conclusions were believable before qualified routes or independent
controls, but are superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing input or
  wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- The s2190–s2197 and s2283/s2284 second-origin/A1 matrices, s2228,
  s2242–s2259 image/pair crash splits, and s2288 stub-first route conclusion.
- s2304's route-wide PCM gap, s2307's fixed addresses, s2308's zero-fill
  interpretation, s2325's destination-role split, and s2335–s2342's
  inactive-parent/gate labels.
- s2346's output-metadata-writer-absent label and the successive s2347–s2360
  candidate, overflow, value, task-field, and source/payload labels.
- s2376's input-dependent A1 label, s2379's unresolved flag split, s2383's
  missing-completion label, and s2399's identity-cleared label.
- s2445's `H-PortAlternatePath` label and s2446's assumption that
  `0x800078EC` was a callable function target; later boundary inspection and
  live indirect controls superseded them.
- s2493's descriptor-to-load mismatch, s2495's temporal image/load join,
  s2497's image-handoff-absent shorthand, and s2505's static destination
  non-join; later direct port-load and runtime table joins superseded those
  labels at their inspected boundaries.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument; arm its
  whole-RDRAM positive control first.
- A null requires a same-run positive control. Batch counters and A/B arms in
  one build/run, scope budgets to the phase, and use VI gates rather than
  time. A diagnostic field must be part of a complete discriminating table.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Keep the active hypothesis slug while pursuing one thread. After three
  stalled iterations, pivot or block; after six advanced iterations with no
  engineering change, pivot to bounded work.
