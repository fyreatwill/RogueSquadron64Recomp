# Session 3042 ProducerMark call-chain audit

Date: 2026-08-28

## Grounded question

The retail oracle executed ProducerMark at `0x8001BCE4` in title/hangar,
while the port stopped at VI 640 with 526 route-prepares and `accepted=0`.
This audit checks whether the port's generated call chain or host acceptance
edge is missing or misidentified.

## Complete static discriminator table

| Item | Generated evidence | Registration / probe | Result |
|---|---|---|---|
| `0x8001BCE4` | `bufferArbiterProducerMark`, `funcs_5.c`, body range `0x8001BCE4..0x8001BE7F`; waits on queue `0x80128D10`, scans the six-state table, and calls `osViSwapBuffer` on the presentation branch | `funcs.h`, `recomp_overlays.inl` offset `0x1B8A4`, size `0x19C`, and `syms/rogue_squadron.syms.toml` agree | Present and consistently registered |
| Caller `0x8000BFE8` | In `bufferArbiterProducerScanWait` (`funcs_3.c`, `0x8000BF60..0x8000C07B`), direct `jal 0x8001BCE4`; delay slot sets `s2=3` | Probe is immediately before the generated call and captures caller state | Correct handoff site; not missing |
| Caller `0x8000C628` | In `submitGfxFrame` (`funcs_3.c`, `0x8000C07C..0x8000C6EF`), stores computed frame value at `0x8011D24C`, then direct `jal 0x8001BCE4` | Probe is immediately before the generated call; `submitGfxFrame` is registered at `0xBC3C`, size `0x674` | Correct handoff site; not missing |
| Other `submitGfxFrame` calls | Same function has direct calls at `0x8000C440` and `0x8000C64C` | Both dispatch to the same registered ProducerMark function | Complete local call chain |
| Caller `0x80018258` | In `advanceVideoFrame` (`funcs_4.c`), direct `jal 0x8001BCE4` after buffer-ready work | Separate registered main-overlay function | Present |
| Caller `0x8001A300` | In `initVideoSubsystem` (`funcs_5.c`), direct `jal 0x8001BCE4` after allocation, memset, cache writeback, and mark-ready | Both functions are registered in the same overlay table | Present; boot-time path |
| Project identity | `bufferArbiterProducerMark = 0x8001BCE4`, size `0x19C`; companion map gives the same address and describes `2→3` / `X→4` transitions | No conflicting project identity found | Synchronized |
| Host route prepare | `rs64_audio_route_prepare` is called by the two audio dispatch arms and fallback return preparation; it clears the thread-local identity, snapshots committed VI width/origin, and accepts only `(1024,0x00790400)` or `(512,0x006AB400)` | `rs64_m5_route_prepare_inputs` reports `target` and `accepted` from this same predicate; ProducerMark does not set or gate it | `accepted=0` at VI 640 is intentional predicate behavior, not ProducerMark rejection |

## Hypothesis decision

- H-PortProbeWrongEdge is refuted for the audited addresses. The probes at
  `0x8000BFE8` and `0x8000C628` are real direct `jal` sites, and enumeration
  finds the other four direct sites.
- H-PortCallerMissing is refuted statically for this call chain. The
  generated body contains every discovered ProducerMark caller and the
  registrations resolve to the expected symbols.
- H-PortAcceptanceWrong is not selected. The host acceptance predicate is a
  phase classifier based solely on committed VI width/origin; it cannot
  reject a ProducerMark call, and VI 640 is outside its two target pairs.
- H-StaticInsufficient applies to the remaining route explanation: these
  sources identify the ProducerMark path but do not identify why the port
  never reaches a target VI commit. No generated or host behavior change is
  justified by this audit.

The next discriminator must move to a different signal edge: the host VI
commit writer and the ordering/identity handoff into the first route prepare,
with retail attribution retained as the ground-truth control.
