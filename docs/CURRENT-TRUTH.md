# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact commands
and probe rows remain in the ledger.

Current maintenance marker: Session 2631 (2026-08-27).

## Decision-relevant evidence

- **s2616 — same-build Step 1 rebaseline selects the image output contract
  gap.** The retail oracle passed the whole-RDRAM control at 10,000 writes and
  reached title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. Both port
  arms reached title and hangar. The silent arm produced no image-stage or DMA
  rows; the image arm produced 1,014 task/DMA rows, 2,189 DMA-range rows, and
  4,496 image-stage rows, with `break_pc=0x1328` and `exit=1` (`Broke`). Image
  DMA payloads and PCM source/consumer spans were still zero. The silent arm
  ended with `rc=139` in hangar; the image arm had no crash, abort, or missing
  function marker. The independent oracle route controls and the same-build
  silent/image separation select `H-ContractGap` over `H-AudioDegeneracy`;
  the crash is recorded as a failure signal, not its cause. Artifact:
  `scratch/agent/s2616_m5_step1_contract_pair/`.

- **s2614 — retail names the PCM-span writers; the port does not.** The
  debugger-enabled retail oracle passed the whole-RDRAM control with 23,413
  writes, reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and
  recorded 12,288 writes in `0x166450:0x169450`, dominated by PC `0x800078EC`.
  The secondary `0x1798B0:0x179A48` span had 1,125 writes from
  `0x800078EC`, `0x8001E2C0`, `0x80007670`, and `0x8001FAxx–0x8001FD2C`.
  The same-build port reached both phases with image completion, audio
  returns, and task joins live, but its host writer witness saw only 893
  zero-valued `kind=2, pc=0` rows. This selects `H-PortPublicationGap` over an
  absent retail writer; it does not map a legitimate port store or authorize
  writeback. Artifact: `scratch/agent/s2614_m5_pcm_writer/`.

- **s2613–s2611 — the image task contract is live but output remains open.**
  Qualified same-build runs reached title and hangar with no crash, abort, or
  missing-function markers. The image arm produced DMEM changes, generated
  DMA, image completion at `break_pc=0x1328`, and SP/task returns; the silent
  arm produced none of that work. Image payload samples and port PCM samples
  were nevertheless zero in the evaluated reruns. This selects
  `H-ContractGap` at the output edge and refutes `H-SilentPathNotIndependent`.

- **s2608–s2609 — the C88 gate promotion is shipped and the indexed writer is
  legitimate.** Unset `0x8008EC88` now stores guest `$v0`; setting
  `ROGUESQ_M5_C88_VALUE=0` is the rollback. C88=`1` opens the gate and reaches
  `startSongSequence` in title and hangar. The indexed store at `0x80094648`
  writes `0x7F` to `0x80141AD8..0x80141B08`, with matching post-store reads.
  Title PCM was positive in the promotion run; hangar PCM remains zero.
  ORIGIN: these are guest writers, and the observed values are legitimate;
  no output remap or mitigation is authorized without a named publication
  edge.

- **s2605 — the known 640 abort was a broken host return.** The continuation
  `0x800155EC` was incorrectly passed to `get_function` by the lowered
  `jr-$t9` path. The regeneration-safe fixup restores the writer-parity line
  and rejects that lookup. The qualified run then reached title and hangar.

- **s2617 — the port-side PCM publication census found no complete candidate.**
  The generated tree contains no direct static references to either retail
  destination span. The named retail-PC matches are unrelated: port
  `0x8001E2C0` clears 0x24-byte texture-table records, and
  `0x8001FAxx–0x8001FD2C` parses image/texture metadata and calls the image
  parser. Existing `rs64_m5_pcm_writer_store` coverage is a generic dynamic
  destination witness, not a source/destination edge. This selects
  `H-PortPublicationGap`; no build or runtime arm was warranted.

- **s2618 — hangar PCM is image-arm output, but the indexed-writer test was
  unevaluable.** The rebuilt same-build image/silent pair reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`; image produced 4,047
  image-stage rows and silent produced none, with 512 task handoffs in each
  arm and no crash/abort markers. Both arms had zero PCM rows in title. In
  hangar, image produced matched nonzero source/consumer rows at
  `0x80168850` and `0x80168B50` (621 and 639 nonzero bytes), while silent
  remained zero. The `0x80094648` channel-writer tag emitted no rows in
  either arm. This is a two-line result for image-arm output separation, but
  the required title positive control failed, so it does not select
  `H-HangarWriterLegitimate`, `H-HangarWriterNonPCM`, or
  `H-HangarPublicationGap`.

- **s2619 — title PCM remains absent after an oracle-grounded same-build
  recheck.** The retail oracle passed the whole-RDRAM control with 23,005
  writes, including all 12,288 writes to `0x166450:0x169450`; title was live
  for 635 VI callbacks and the dominant writer was again PC `0x800078EC`.
  The rebuilt port image/silent pair both reached title `1024 @ 0x00790400`.
  The image positive control emitted 6,627 image-stage rows and 1,027 title
  image-DMA joins; the silent arm emitted no image-stage or image-DMA rows.
  Despite that separation, title PCM joins were all zero: image had 110
  source/consumer rows and silent had 106, with `nz=0` in every row. This
  selects `H-TitlePublicationMissing` over a missing phase join and requires
  pivoting to the M5 de-stubbing sequence; it does not authorize writeback or
  identify a legitimate port writer. The image arm later hit a host bus-error
  during capture; that is a failure signal, not the title discriminator.
  Artifact: `scratch/agent/s2619_title_pcm_boundary/`.

- **s2620 — Step 3 contract-edge audit found no promotable edge.** The retail
  whole-RDRAM control and title/hangar transitions are present. Retail names
  PC `0x800078EC` as the dominant writer of `0x166450:0x169450`; the secondary
  `0x1798B0:0x179A48` span also has named retail writers. Port image rows show
  task ordering and DMA destinations, but every sampled image DMA payload is
  zero, and the host writer witness is `kind=2`, `pc=0`, with no guest
  publication PC. The generated tree has no direct static reference to the
  retail PCM spans. Thus `H-ImageOutputEdge` and `H-CPU-MORT-Edge` remain
  incomplete mappings; `H-Unproven` is selected. No writeback, remap, gate,
  or de-stub behavior change is authorized until an independent mapping names
  the port writer, destination, legitimate value, and ordering.

## s2621 unblock audit

The local oracle route passed the whole-RDRAM control with 9,107,853 writes,
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and its
phase-gated `--watch-pc 0x800078EC` rows confirmed the companion `rs_memset`
body and zero-fill arguments. The result did not identify a legitimate
port-side PCM publication destination or producer ordering. The companion
source also has no complete body for retail `0x8002BEEC` or CPU-MORT
publication boundary. The M5 mapping remains an open dependency; the next
action is the local generated-symbol sweep. Artifact:
`scratch/agent/unblock_s2621/oracle.log`.

## s2622 symbol-sweep result

The `0x800BF790` lead is already resolved: the companion symbol and generated
overlay table agree on `updateHudHealthIndicator` at `0x800BF790`, size
`0x634`, and `handleHUD` contains an in-tree caller. The neighboring
`0x800BF784` and `0x800BF498` entries are 12-byte and 8-byte generated
fragments; `0x800BF4A0` is the previously documented duplicate-symbol
boundary. No new defensible rename exists in this region. The next sweep lead
is `0x800C41AC/0x800C41B0`.

## s2623 symbol-sweep result

The `0x800C41B0` lead is resolved. The companion mission symbol file names it
`plotRadarBlipColumn`; the generated body spans `0x1AC` bytes from
`0x800C41B0` through `0x800C4358`, with `plotRadarBlipRow` beginning at the
exact next boundary `0x800C435C`. The generated radar path has three callers
at `0x800C4540`, `0x800C60C8`, and `0x800C60E8`, and the generated overlay
table carries the same name and `0x1AC` ROM size. The repository TOML had
remained address-coded, so it was synchronized to `plotRadarBlipColumn`; the
regenerated rename table contains `func_`, `D_`, and `fake_func_` mappings for
the address. This is an exact companion/span/caller result, not a boundary-only
rename. The next lead is `0x800C63C0`.

## s2624 symbol-sweep result

The bounded `0x800C63C0/0x800C64A4/0x800C64B0` census found one exact rename.
The mission companion file names `0x800C64B0` `initHangarDisplayItemTimers`;
the generated body spans `0x11C` bytes through `0x800C65CC`, and the generated
hangar caller at `0x800C69C4` invokes that name. The repository TOML still had
an address-coded `func_800C64B0` row, so it was synchronized to the companion
name and `build_redefs.py` emitted the `func_`, `D_`, and `fake_func_` mappings.
The `0x800C63C0` row remains an intentional overlay collision: mission
`getAvailableShipsForLevel` and menu `getAvailablePlayerCraftFlagsIgnoreUnlocks`
have distinct bodies and overlay-table entries at the same VRAM address. The
`0x800C64A4` fragment remains `fake_func_800C64A4`. No runtime behavior changed.

## s2625 symbol-sweep result

The bounded region immediately after `0x800C64B0` produced no new rename.
`0x800C64C8` is already emitted as `unlockLevelsAndCraftsBasedOnMedalsEarned`:
the menu companion names it exactly, the generated body has the matching
`0x198` span, and generated caller `0x800C09F0` invokes that name. The
mission-overlay body beginning at `0x800C64B0` overlaps this menu-overlay
address, so the two context-specific identities must not be collapsed.
`0x800C65CC` (`tickHangarDisplayItemAnimations`) and `0x800C68A0`
(`hangarVehicleDisplayNpcHandler`) are already named with matching companion
entries. `0x800C64A4` remains a 12-byte collision fragment with no defensible
semantic identity. No runtime behavior changed.

## s2626 symbol-sweep result

The bounded `0x800C68A0` census found no new rename because the region is
already exact in every required source. The mission companion names
`hangarVehicleDisplayNpcHandler`; its generated body starts at `0x800C68A0`
and spans `0x75C` bytes to the exact next boundary `0x800C6FFC`, while the
generated overlay table carries the same name and ROM size. Generated callers
use the resolved symbol. The menu-overlay `0x800C6900` entry is a distinct
overlay identity inside the mission body and must not be collapsed. The next
bounded lead is the adjacent `0x800C6FFC` boundary.

- **s2629 — the `0x800C722C` sweep lead was already exact.** The repository
  TOML maps `0x800C722C` to `getConfigFloatValue` with size `0x10`; the
  generated body is the matching 16-byte load-and-return fragment. Adjacent
  generated bodies and TOML entries match `findNamedEntryInCurrentObject`
  (`0x800C723C`, `0x2C`), `copyCurrentObjectMatrix` (`0x800C7268`, `0x48`),
  `initializeObjectiveTracking` (`0x800C72B0`, `0x38`),
  `dispatchObjectiveSlot1` (`0x800C72E8`, `0x38`),
  `calculateFriendliesSaved` (`0x800C7320`, `0x38`), and
  `checkComplexObjectives` (`0x800C7358`, `0x38`). Generated callers invoke
  the placeholder forms for `0x800C722C`, `0x800C723C`, and `0x800C7268`, while
  no unresolved symbol exists at the lead. No rename or runtime change was
  warranted; the next bounded lead is `0x800C7358`.

## Current state

- The qualified route is `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`; spin yield is diagnostic
  and default-off. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
  MORT is a separate CPU speech boundary.
- Image DMEM work, generated DMA, image completion, SP completion, service
  entry/exit, AI/PCM consumers, and target route controls are live. The
  missing edge is publication of nonzero PCM from the port-side equivalent of
  the retail writer family.
- Retail is the independent witness for game-side memory claims. Its
  whole-RDRAM control and target-phase transitions must precede interpretation
  of any narrow null. It reaches attract, title, and hangar, not a mission.

## Active backlog

This is one monotonic sequence; #1 is the next campaign priority.

1. **Generated-symbol renaming sweep — active fallback while M5 is blocked.**
   Audit `0x800C7718` next using companion symbols, exact spans, and callers;
   unresolved fragments stay placeholders under
   `HYPOTHESIS-ID: generated-symbol-renaming-sweep`.
2. **M5 de-stubbing sequence — open dependency, not a project stop.** Obtain an
   independent mapping from retail PC `0x800078EC` (and the secondary-span
   writers) to the port-side writer or CPU MORT publication boundary, including
   destination, legitimate payload polarity, and ordering relative to image
   completion and PCM consumption. Do not repeat the title-zero census or
   revisit the hangar `0x80094648` relation. Keep C88=`0` and
   `ROGUESQ_AUDIO_UCODE=0` as rollbacks/controls.
3. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.
4. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
5. **M4 accumulator origin — parked.** One phase-6 producer/consumer join is
   established; broader slot coverage is optional and lower priority than M5.

## Durable boundaries

### Route, rendering, and Factor 5

Factor 5 uses custom GBI mappings documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md). Do not infer stream
semantics from standard F3DEX. Keep the qualified LLE route and existing
defensive runtime guards until a named writer explains the bad value.

### M5 audio and image output

The Factor 5 image task and CPU MORT speech path must not be conflated. A
`Broke` return is only task completion; it is not proof of PCM correctness.
The image arm's task fields, DMEM, DMA, exit, and SP completion must be joined
to service, slot/voice, MORT, PCM source, and PCM consumer rows. The current
host writer rows are zero-valued and ambiguous. No writeback, gate bypass,
forced slot state, or output remap is allowed without an `ORIGIN:` line naming
the writer and stating whether its value is legitimate.

### Safety and evidence rules

- Ask the retail oracle for ground truth before adding an instrument; its
  whole-RDRAM watch is the positive control.
- Batch every discriminator in one build and one phase-gated run. A null is
  unevaluable without its positive control; a branch counter alone is not one.
- Regenerate in order: `make_elf.py`, N64Recomp, fixup scripts, then CMake.
  Never hand-edit generated game functions for behavior changes.
- Kill runs with SIGKILL and run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export its patches in the same
  iteration.

## Session 2627 result

The bounded sweep audited `0x800C6FFC` and its adjacent boundary. The mission
companion names `0x800C6FFC` `applyNpcPositionDrift`; the generated body starts
at that address and ends at the exact next boundary `0x800C7120`, spanning
`0x124` bytes. The generated overlay table and repository TOML carry the same
name and size, and generated caller `0x800B3DFC` invokes it. `0x800C7120` is
already an exact `getConfigFloatPair` entry, so no placeholder or collision was
available to rename. This selects `H-CompanionExact` as already resolved,
rules out a boundary-only interpretation for the lead, and changes no runtime
behavior. The next bounded lead is `0x800C7120`.

## Session 2628 result

The bounded sweep audited `0x800C7120` against the mission companion symbols,
generated body, overlay table, repository TOML, and callers. The companion
name is `getConfigFloatPair`; the generated body starts at `0x800C7120` and
spans the exact `0x1C` bytes to `0x800C713C`, and the overlay table carries the
matching ROM size. Generated caller `0x800530A4` invokes the target. The
adjacent `0x800C713C` row is already the exact
`accumulateVectorInObjectFrame` mapping. No placeholder or collision remained,
so no rename or runtime change was made. This selects `H-CompanionExact` as
already resolved and moves the next bounded lead to `0x800C722C`.

## Session 2630 result

The bounded sweep audited `0x800C7358` and its adjacent objective-dispatch
region. The mission companion names the target `checkComplexObjectives`; the
generated body starts at `0x800C7358` and spans the exact `0x38` bytes to
`0x800C7390`, while the overlay table and repository TOML carry the same name
and size. Generated caller `0x800FA940` invokes the resolved symbol. The
adjacent `calculateFriendliesSaved` entry at `0x800C7320` is also exact, and
`0x800C7390` is the distinct `dealDamagetoDatItem` boundary. No placeholder,
boundary-only ambiguity, or overlay collision remained, so no source-map or
runtime change was made. This selects `H-CompanionExact` as already resolved;
the next bounded lead is `0x800C7390`.

## Superseded conclusions

The old overlay/menu explanation, intrinsic 640 flakiness, missing-input and
wait-return claims, global-zero image-DMA explanation, route-wide PCM gap,
and force-zero default policy are superseded at their measured scopes. They
were believable before qualified routes, same-build controls, or independent
retail attribution existed. The detailed evidence and failed experiments are
preserved in `PORTING-STATE.md`; do not revive them without a new discriminator.

The prior symbol sweep contains many static boundary-only classifications.
Those fragments remain placeholders when the companion, source, m2c, caller,
and local-semantics searches do not supply a defensible name. Stable companion
duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Session 2631 result

The bounded generated-symbol sweep found five exact companion mappings whose
repository TOML entries were still address-coded: `computeTrackedObjectWorldAnchor`
(`0x800AD380`), `updateHangarBayScene` (`0x800AB658`),
`buildFormatMessageGlyphBuffer` (`0x800B2630`),
`buildLevelSelectTextTextures` (`0x800B3824`), and `menuOverlayInit`
(`0x800C58A0`). Each companion name matched the generated function definition;
the existing generated bodies therefore required no regeneration. The TOML
batch was synchronized to those names. The neighboring `0x800AD378` fragment
remains `fake_func_800AD378` because its companion entry is also a gap filler,
not a semantic identity. This selects `H-CompanionExact` for the five-row
batch and advances the next bounded lead to `0x800C7540`.

## Session 2632 result

The bounded `0x800C7540` census found no new rename. The companion mission
symbols, generated definitions, repository TOML, and mission overlay table
agree on exact names and spans for the objective helper family through
`setObjectiveTimer` at `0x800C76FC`; generated mission callers use the
resolved names. The generated JPEG entries `parseJfifDHTMarker` and
`paserJfifSOSMarker` overlap this VRAM range only as a separate overlay
identity, so they remain an overlay collision and must not be collapsed with
the mission helpers. No source-map or runtime change was warranted. This
selects `H-BoundaryOnly`/`H-OverlayCollision` for the remaining ambiguity and
advances the next bounded lead to `0x800C7718`.
