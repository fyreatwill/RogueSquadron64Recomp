# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact commands
and probe rows remain in the ledger.

Current maintenance marker: Session 2618 (2026-08-27).

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

1. **M5 title PCM publication boundary.** Explain the missing title positive
   control before revisiting the hangar `0x80094648` relation. Keep C88=`0`
   and `ROGUESQ_AUDIO_UCODE=0` as rollbacks/controls; do not infer a writer
   from the hangar-only image output.
2. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.
3. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
4. **Generated-symbol renaming — bounded fallback.** If M5 is inapplicable,
   continue one companion-supported batch under
   `HYPOTHESIS-ID: generated-symbol-renaming-sweep`; unresolved boundary
   fragments stay placeholders. Session 2615 added the supported duplicate
   prefix at `0x800E8A34`.
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
