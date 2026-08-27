# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact
commands, counts, and probe rows remain in the ledger and scratch artifacts.

Current maintenance marker: Session 2680 (2026-08-27).

## Live result

The qualified port route is `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`; `ROGUESQ_SPIN_YIELD=1`
is diagnostic. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.

M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
MORT is a separate CPU speech boundary.

The latest qualified M5 evidence is:

- s2671 separated image work from the silent control in the same qualified
  driver: image DMEM/DMA/completion rows were live, while the silent arm had
  no image rows. Both arms retained zero task output fields and zero PCM
  source/consumer payloads in that capture (`H-contract-separated`).
- s2672–s2673 found image-stage and ring destinations but no complete writer,
  legitimate payload, and ordering edge. Retail attribution did not close
  the edge (`H-ring-unmapped`, `H-unmapped-edge`).
- s2675–s2676 audited the live CPU MORT boundary. `0x8009D740` executes from
  `0x8009D73C`; its source-derived 40-byte output at physical
  `0x11C7B0:0x11C7D8` is shared stack storage, with unrelated stack writers
  also present. This strengthens `H-MORT-unmapped` and forbids writeback or
  remap from that overlap. `H-image-edge` remains unproven.
- s2678's corrected retail oracle established the next CPU edge: retail
  `applyVoiceDelayFilter` writes persistent voice object `0x80153420+0x166`
  (physical `0x153586`) from `0x8009D8E4`, and `renderVoiceAudioBlock`
  (`0x8009DB44`, caller `0x8009C4C0`) consumes the same object in both hangar
  origins. The whole-RDRAM control fired 17,295 times; the phase-gated counts
  were 792 filter, 792 delay, and 198 render executions. This resolves the
  CPU-side consumer edge but not renderer-to-PCM/AI publication; no writeback
  or remap follows from it.
- s2679's batched retail capture reached title and both driven hangar origins
  with the whole-RDRAM control (`29,161` writes). `renderVoiceAudioBlock`
  executed 496 times, `audioMixStereoBlock8` 1,984 times, and
  `osAiSetNextBuffer`/`__osAiDeviceBusy` 6,180 times. The candidate port ring
  `0x166450:0x169450` was written 12,288 times, but every sampled writer was
  `rs_memset` at `0x800078EC`, including boot initialization; the capture did
  not join renderer/mixer output to that ring or another AI source. This
  strengthens `H-MORT-unmapped` at the CPU publication boundary and does not
  select `H-image-edge`.
- s2680's same-build AUTOPILOT re-baseline reached title and hangar in both
  port arms. The image arm alone produced 4,764 DMA-range rows and 14,328
  image-stage rows, with task `break_pc=0x1328`; the silent arm produced none.
  Both arms nevertheless had matching task dispatch/return, audio/SP route,
  PCM source/consumer counts (`98/98`) and zero-nonzero PCM payloads
  (`fnv=F59C39C5`, `nz=0`). This selects `H-ContractGap` at the measured
  downstream boundary, rejects `H-RouteOnly` and `H-AudioDegeneracy` there,
  and does not identify a legitimate writer or authorize writeback/remap.
- s2681's positive-controlled retail join reached both hangar origins and kept
  the named renderer/mixer/AI PCs live. The candidate AI-source span
  `0x166450:0x169450` had 3,072 reads but only the known initialization writer
  `0x800078EC`; the adjacent span `0x1B4A00:0x1B5000` had phase-live nonzero
  renderer writes at `0x8009DB2C`. The renderer was not joined to the AI
  source, selecting `H-AI-source-gap` for these candidate ranges (single-source
  retail evidence) and rejecting `H-MORT-PCM` there. The complete publication
  edge remains open; no writeback or remap is authorized.

Retail is the independent witness for game-side memory claims. A narrow null
is unevaluable unless the whole-RDRAM positive control fires first and the
target phase is reached. The current corrected oracle reaches attract, title
(`1024 @ 0x00790400`), and hangar (`512 @ 0x006AB400`), not a mission.

## Next steps

This is one monotonic sequence; #1 is the next campaign priority.

1. **M5 CPU-side MORT PCM publication.** The renderer-to-AI candidate join
   separates the live renderer span from the AI-source span but does not name
   the missing copy/publication edge. Audit the exact address arithmetic and
   caller contracts of `0x8009DB2C` and `0x8002A0B8` before another runtime
   probe; do not repeat the filter, persistent-object, task-field, ring,
   shared-stack, or Step 1 arm census.
2. **M5 image task contract edge.** Implement only after a named legitimate
   image writer and destination/order relation is independently established;
   s2680 authorizes no writeback or remap.
3. **Generated-symbol renaming sweep — parked fallback.** Resume only when
   M5 is closed or blocked by a new discriminator. Use exact companion
   address/name agreement; preserve ambiguous placeholders and overlay
   collisions. The five remaining true `func_` placeholders have no semantic
   companion identity; intentional `fake_func_` fragments remain generic.
4. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.
5. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
6. **M4 accumulator origin — parked.** One phase-6 producer/consumer join is
   established; broader slot coverage is lower priority than M5.

## Durable boundaries

### Route, rendering, and Factor 5

Factor 5 uses custom GBI mappings documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md). Do not infer stream
semantics from standard F3DEX. Keep the qualified LLE route and existing
defensive runtime guards until a named writer explains any bad value.

### M5 audio and image output

The Factor 5 image task and CPU MORT speech path are separate contracts. A
`Broke` return proves task completion only, not PCM correctness. A valid
publication edge needs a named writer, destination, legitimate payload
polarity, and ordering through service/slot/MORT, PCM source, PCM consumer,
and image completion where applicable. No writeback, gate bypass, forced
slot state, output remap, or mitigation is authorized without an `ORIGIN:`
line naming the writer and stating whether its value is legitimate.

### Safety and evidence

- Ask the retail oracle for ground truth before adding port instrumentation.
- Batch every discriminator in one build and one phase-gated run; include a
  positive control in the same run.
- Regenerate in order: `make_elf.py`, N64Recomp, fixup scripts, then CMake.
  Never hand-edit generated game functions for behavior changes.
- Kill runs with SIGKILL and run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export its patches in the same
  iteration.

## Superseded conclusions

The old overlay/menu explanation, intrinsic 640 flakiness, missing-input and
wait-return claims, global-zero image-DMA explanation, route-wide PCM gap,
and force-zero default policy are superseded at their measured scopes. They
were believable before qualified routes, same-build controls, or independent
retail attribution existed. Detailed failed experiments remain in
`PORTING-STATE.md` and the archive below.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not supply a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived durable progression

The detailed s2621–s2676 results were compacted into
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) during Session 2677. The ledger
retains every exact session entry and scratch artifact. The current decision
chain is: task-field census unresolved; image/silent separation qualified;
image ring/stage destinations not a publication edge; named retail utility
writers not a MORT edge; and the live MORT filter output is shared temporary
stack storage. The next legitimate discriminator is the next downstream
named voice consumer.
