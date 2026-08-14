# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records
remain in the ledger. This file was compacted in the s1004 maintenance pass
from 60,345 bytes / 642 lines. It is intentionally a current-state document,
not a second ledger.

Reviewed through s1046 (2026-08-14). M3 slot-SP corruption is parked after two
phase-positive no-event recipes; the retail oracle phase audit found live
whole-RDRAM and pad controls but no transition beyond the early width-320
phase. M4 zero-shade is parked after its third consecutive controlled null:
the emitted shade is a constant sentinel, and the retail Factor 5 instruction
stream omits a color-word read in the shaded-triangle emitter. VGE cannot create
the sentinel; the remaining question is the preceding accumulator/high-half
numeric source of the shade record. The corrected s1022 capture proved the
probe path live with 19 independent VMADH controls and 77 M4 stage rows, but
the sampled rows contained no 0x8000 endpoint before the recurring crash. s1023
paired the valid rows offline: 19 stage-1 controls passed, 25 complete M4
stage-10/11/12 triplets were available, and one stage-10/11 pair was trailing;
none of the M4 fields contained 0x8000. Stage-12 v6 matched stage-11 v6 in
all 25 triplets, with the zero lanes also matching v29, but no endpoint was
present to discriminate arithmetic from VGE selection. The M4 numeric origin
therefore remains unevaluable from this capture. s1017
identified that the 512-gated recipe starts its
phase-relative key worker only after 512, so it cannot drive the transition that
may be needed to reach 512. s1018 corrected the gate to 1024 and delivered the
scheduled keys, but the run stayed at 1024 and emitted neither the M4 target nor
its VMADH positive control. This is a valid phase-control result but an invalid
M4 capture. s1019 found the concrete artifact defect: the probe-bearing ovl20
source was generated after the last CMake build, and ovl20 is not a standalone
CMake source. s1020 reconfigured and rebuilt: the composite source and
executable now contain the probe, but the build graph still links only
base/boot/B ucode, with no ovl20 object or executable ovl20 marker. This
remains a link-path result, not an M4 numeric result. s1021 completed the
source-to-dispatch audit: standalone ovl20 is a fixup-6q splice input, and its
region is already present in the linked composite. The executable contains 68
ovl20 route markers and the M4 helper, but correctly has no standalone ovl20
object or symbol. The missing-standalone-link interpretation is refuted. s1022
then reached VI-1024 with the independent VMADH control and M4 stages live;
the sampled M4 tuples had no 0x8000 endpoint before the recurring
slotDispatcherIter+8592 crash, so the three numeric hypotheses remain open.
s1024 raised the phase-scoped M4 row cap to 512 and built successfully, but
three capture attempts produced no stage-1 positive control: the first stopped
on a VI-phase change, the second used an abbreviated key schedule, and the
final full schedule reached VI-1024 and logged input edges but still emitted
no M4 rows. These are valid reachability/input observations but invalid
numeric captures; no M4 hypothesis changed.
s1025 first repeated the no-LLE configuration and again produced no M4 rows.
The corrected same-build LLE arm reached VI-1024, logged 14 input edges and
138 stage-1 controls, and filled the 512-row budget with 124 complete M4
triplets. Every stage-12 v6 matched stage-11 v6; the only two 0x8000 values
were unrelated stage-1 accl fields, and no shade v6 endpoint was created.
The numeric hypotheses remain unevaluable.
s1026 raised the same phase-scoped cap to 2048 and repeated the corrected LLE
recipe. VI-1024, 14 input edges, 598 stage-1 controls, and 161 complete M4
triplets all passed. No M4 `v6`, `v29`, `acch`, or `accm` field contained
0x8000; 44 rows contained it only in `accl`, outside the tested endpoint.
The larger budget therefore remains a controlled null, not a numeric
classification. The next capture must budget the stage-1 control separately
so later M4 tasks are sampled.
s1027 split the budget to 64 stage-1 controls and 2048 target rows. VI-1024,
input, all 64 controls, and all 2048 target rows passed; no M4 `v6`, `v29`,
`acch`, or `accm` field contained 0x8000 (22 unrelated `accl` fields did).
This is the third controlled M4 null, so no numeric hypothesis is selected and
the next iteration pivots to the landed slot-SP diagnostic. s1028 verified
against ground truth (not just the backlog's word) that the guard is genuinely
landed: the fixup patch is `N64Recomp/fixup_game_funcs.py:25156-25185` (s1005),
present in the generated `funcs_8.c` and in the compiled binary's strings. The
guard already ran once pre-M4-detour (`SOAK-RESULTS.md` s1009): a forced-LLE
recipe reached 57 frames and crashed at `slotDispatcherIter+8592` (not `+872`)
with zero guard hits — a valid but unevaluable null, since that run never
reached the `+872` fault site. The changed non-forced-LLE recipe then reached
VI-1024 but exited after 65 frames at sticky guest PC `0x8000834c`, before the
slot-dispatch family or guard fired. A follow-up recipe postpones the late
`a` input.
M5 audio de-stubbing is closed. M3 work is limited to complete idiom-class audits. The
retail-oracle callback thread is no longer directory-blocked
(`.claude/settings.json` currently lists `rs64-oracle`); see backlog.

## Current truth

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation; the original boot/menu hypothesis is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing legitimacy.
- Phase-gated port captures reach VI width 1024 with independent
  `emit/raw/dispatch/match` controls. Pre-chain crashes are disjoint families
  and do not classify parser loss.
- Ordinary late E9 producer/consumer identity is established; synthetic
  FULL_SYNC was absent in the decisive capture. Remaining accounting deltas
  are boundary/span-shaped and the residual extended condition is unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. All 144 direct callers have
  balanced frame shapes; statically addressed indirect targets are balanced;
  `0x8010B350` is compiled data with no generated writer. The general runtime
  caller-frame corruption mechanism remains open, but a
  `ROGUESQ_LOG_SLOT_SP_GUARD=1` register-dump diagnostic is now landed (see
  backlog).
- M5 audio de-stubbing is closed. Do not reopen it without a genuinely new
  lead. The legacy audio idiom audits and their structural limitations are in
  PROJECT-OVERVIEW §§9–12 and §30.
- Retail oracle work: s1036 audited the startup/attachment order and ran the
  fresh-config 60-second schedule. CoreStartup initializes core config before
  the input plugin is attached; the plugin then creates/repairs its four
  Input-SDL sections, so the first-run missing/incompatible warnings are
  expected initialization rather than a local ordering defect. The generated
  file records `Start = "key(13)"`, while the verified scancode-40 presses
  still produced Start pad words (`0x10000000`). The whole-RDRAM positive
  control reached 10,000 callbacks and was removed; 3,599 VI stayed at width
 320/origin `0x006dd280`. This closes the local config-order explanation and
  leaves the retail phase-path question open; no freelist watch was armed.
  s1039 tested the same eleven Start events as 150 ms pulses and as 2000 ms
  holds; both arms stayed at width 320/origin `0x006dd280` after passing the
  whole-RDRAM control. s1040 tested documented five-second versus rapid
  one-second cadence with the same result. s1041 tested an early first pulse
  at 1 second versus the documented first pulse at 6 seconds; both arms
  delivered all eleven Start edges, passed the 10,000-callback control, and
  stayed at width 320/origin `0x006dd280` for 3,599 VI. These results select
  `H-retail-path-independent` for the tested input shapes and 60-second
  horizon; the hangar phase remains unevaluable. s1042 extended both arms to
  120 seconds: each passed the 10,000 whole-RDRAM control and all 11 Start
  edges, but both stayed at width 320/origin `0x006dd280` for 7,199 VI. This
  closes duration as the explanation for the tested attract path; the 512
  hangar phase remains unevaluable.

## M4 zero-shade evidence

The independent F5 command-reference audit and same-combiner/white-shade A/B
evidence agree that RT64's shade decode lane order is not the cause. Phase-6
VTXCOLOR payloads are nonzero while decoded shade is exact ZERO. The observed
source population is mixed: some payload addresses have exact generated CPU
writes, including later phase-6 sources, while other nonzero sources have no
generated-store overlap. The instrumented DMEM-to-RDRAM DMA path had no overlap
with sampled target ranges. Page-fault census and static PC classification do
not identify a single target-byte writer. No mitigation is authorized from
these facts.

The provenance campaign now establishes:

- F5 payload rows carry task serial, root DL, command address, and task-global
  VTXCOLOR ordinal.
- RT64 shade and zero-shade rows carry task/DL-local ordinals and DL starts.
- F5 root DL is not the RT64 consumer DL. Zero-shade rows repeat on child DLs
  within one task, so the observed association is child-DL-shaped.
- s1003 added accepted DPC first/last ranges and aggregate physical bounds.
  In a valid capture, zero-shade task 193 had root `0x73E7C8`, bounds
  `[0x4B7800,0x4C9318)`, and consumer DLs `0x4B7930`, `0x4B7BE8`, and
  `0x4B8B28`, all inside those bounds. This selects only
  `H-dpc-range-contains-consumer`; it does not identify the F5 update feeding
  an individual replacement.

- s1005 added accepted submit serial/range fields directly to RT64 shade rows.
  The valid VI-1024 capture produced positive and zero rows with nonzero
  serials and ranges. Zero-shade task 194 used serial 49346 and consumer range
  `[0x4B7990,0x4B7C88)`, while its accepted F5 task bounds were
  `[0x4B7800,0x4B7EA0)`. The consumer range begins at the child DL and is
  contained by the task bounds; it does not identify an individual F5 VTXCOLOR
  source update. This selects `H-child-range-only`. No mitigation follows.

- s1006 added a diagnostic join at RT64's actual triangle parse site. The
  valid VI-1024 capture produced 25 join rows, including positive and
  zero-shade rows, with task, child DL, shade ordinal, submit serial/range,
  and F5 state. Zero-shade task 193 rows on child DLs `0x4B7930` and
  `0x4B7BE8` repeatedly carried the same last F5 state (`ord=30`, source
  `0x7403A8`). The rows are live and stable but still task/child-DL-shaped;
  they do not identify the individual update feeding a replacement. This
  selects `H-child-range-only`. No mitigation follows.

- Offline re-analysis of the saved s1000 capture shows every zero-shade row
  carries the fixed decoded shade base (-32768,-32768,-32768,+32768) =
  `0xFFFF8000` RGB / `0x00008000` alpha — a constant -0.5/+0.5 sentinel — while
  the same task's op=0x02 vertex-color payload is nonzero and correct. This
  closes the source-to-consumer join (the data exists and is not used) and
  moves the question to the ucode shade-emission path. Non-zero-shade rows
  additionally show sign-extended color-shaped fields (0x8A -> -118), but the
  s1008 audit shows the lone signed load in the generated emission region feeds
  flags rather than shade; the runtime field's exact producer remains open.
  See PORTING-STATE s1007–s1008.

All runtime claims above had positive controls in their relevant captures.
Static single-source claims are explicitly described as such in the ledger.

The s1008 static audit closes the current emission split. In the generated
Factor 5 path, the four unsigned color bytes are loaded from the per-vertex
color table and copied as a word to each transformed vertex at offset `0x10`
(lines 829–883 of `build/factor5_ucode/factor5_ucode_recompiled.c`). The shaded
triangle path later loads vertex data at `0x18` and emits shade halfwords from
geometry/vector registers; an exhaustive search of that path finds no read of
the color word at `0x10` before the shade stores at `0x8..0x1E`. The lone `lb`
at `0x37($18)` feeds packed flag bytes at output offsets 0/1, not the shade
vectors. GLideN64's independent F5Rogue reference instead copies `colorData`
directly into `vtx.r/g/b/a` before triangle submission. This selects
`H-shade-source-mismatch`; `H-signed-color-load` and `H-emission-layout` are
refuted by the two source inspections. No mitigation is authorized.

The s1009 retail-stream audit resolves the generation question. The game ELF
made by `tools/make_elf.py` contains game code and overlay sections, not the
runtime-loaded Factor 5 IMEM image; the authoritative original is the ROM
text segment at `0x025610`. Its instruction sequence has the color-bearing
record stores at PC `0x1424`, `0x1428`, and delay-slot `0x1468`, all targeting
record `+0x10`. The shaded-triangle emitter at PC `0x1740` stores shade from
`v6` at `+0x18` and related geometry vectors at `+0x1E..+0x22`; the preceding
consumer block has no load from `+0x10`. The generated C preserves this exact
sequence, and `tools/fixup_factor5_ucode.py` has no transformation that could
remove a color load. This selects `H-original-omits-color`; generation-loss
and layout-misread are refuted for this specific missing read. The prior
`H-shade-source-mismatch` wording was believable because the independent
GLideN64 semantic implementation copies colorData into RGBA, but it is now
refined: the mismatch is present in the retail ucode path, not introduced by
RSPRecomp. No mitigation is authorized.

The s1010 semantic audit separates the missing color read from the downstream
consumer. GLideN64's independent `TriGen0000`/`TriGen0001` paths load the
colour array and `F3DSWRS_PrepareVertices` copies its four bytes into each
vertex's RGBA fields before submitting triangles. In the retail/generated
emitter, record `+0x18` is instead written by `sdv v6` at `L_1740`; `v6` is
produced by the transformed-vector and clip/lighting-like path beginning at
`L_162C`/`L_16B8`, not by a color-table load. Both `L_16B8` arms reach the
same `v6` store. RT64 decodes the following shade coefficient words after
the eight position words (`curData[0..7]` in `rt64_gbi_rdp.cpp`), so no
record-offset discrepancy was found. This selects
`H-missing-lighting-source` over `H-intentional-sentinel` and
`H-record-consumer-mismatch`: the fixed sentinel is an output of the
vector-source path, not an explicit no-lighting fallback, while the intended
RGBA source is the separate VTXCOLOR array. No mitigation is authorized.

The s1011 `v6` producer audit finds `r3 = DMEM[0x134] & 1`; both arms of the
`L_16B8` branch reach the same final `vge v6,v6,v29[1q]` and `L_1740` shade
stores. `v6` is overwritten by `vmadh v6,v4,v0`, then compared against the
DMEM-`0x60` table vector `0577 638F 1756 FF96 04D1 62CB 18CB FF8A` (from the
captured ucode-data image). The source is transformed-vector arithmetic plus a
table threshold, not VTXCOLOR or a lighting load. This refutes mode-semantic
misread and the lighting-result interpretation; it selects the narrow
`H-v6-clip-predicate` description for the final compare, while leaving the
sentinel's numeric origin open. Full audit: [M4-V6-PRODUCER-AUDIT.md](M4-V6-PRODUCER-AUDIT.md).

The s1012 compare-semantics audit closes the encoding question. The independent
[SGI RSP Programmer's Guide](https://ultra64.ca/files/documentation/silicon-graphics/SGI_Nintendo_64_RSP_Programmers_Guide.pdf)
describes VGE as a signed greater-or-equal compare that selects an operand; it
does not synthesize predicate values. The runtime implementation independently
agrees: each lane writes `vs` when the compare passes (with the VCO tie rule),
otherwise the selected `vt` lane. For the final `VGE<3>(v6,v6,v29)`, element-3
lane routing supplies alternating lanes from `v29`, while the other choice is
the already-computed `v6`; the DMEM-0x60 table does not contain the observed
`0x8000` RGB / `0x8000` alpha pattern. VGE therefore preserves a value already
present in `v6` or selects a table lane; it cannot create the fixed
`-0.5/+0.5` sentinel. The final compare is not a fixed `v4/v0` source either:
those registers feed the preceding `vmadh v6,v4,v0`. This refutes
`H-vge-sentinel-encoding`, the fixed-operand form of `H-v4-v0-source`, and
`H-shade-store-interpretation`; the numeric-origin lead is the accumulator/high-
half arithmetic before VGE. No mitigation is authorized.

The s1013 accumulator audit corrects the dataflow detail: the shared
accumulator entering `vmadh v6,v4,v0` was most recently updated by
`vmadn v7,v5,v0`, not by the preceding `vmadm v4,v4,v19[0]`. The local VMADH
model shows that `0x8000` can be produced by negative saturation or can be an
in-range sign-extending middle word. The DMEM-0x60 table has no `0x8000` lane,
so `H-v29-selection` is refuted, but the saturation-vs-ordinary arithmetic
split remains unresolved without a complete pre/post accumulator tuple.

The s1014 runtime probe is landed in the regeneration fixup and DPC bridge. It
records all eight `v4`, `v0`, `v6`, `v29`, and `ACCH:ACCM:ACCL` lanes before and
after the final `vmadh`, with a post-VGE record and an independent VMADH
positive control. The first build/run reached VI-1024 but fired neither
control nor target because the main generated file was not the executing shade
overlay. The corrected overlay-20 build likewise reached VI-1024 with zero
control records; the log shows title/menu work. A prescribed Start-driven
512-width attempt never reached 512 (last width 1024), so the discriminator
remains unevaluable. This is a phase-selection result, not evidence for any M4
hypothesis.

The s1038 corrected LLE capture passed the phase gate and the stage-1 positive
control (64/64). It filled the target budget with 683 stage-10, 683 stage-11,
and 682 stage-12 rows, but no `v6`, `v29`, `acch`, or `accm` lane contained
`0x8000`; no crash marker appeared. This is a controlled null after the M4
probe was resumed, not evidence for any numeric-origin hypothesis. The M4
capture recipe is closed pending a genuinely new discriminator; the next work
unit is the retail attract-path discriminator.

## Recent evidence ledger

Details are in `PORTING-STATE.md`; durable summaries are in
`PROJECT-OVERVIEW.md` §31.

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes were classified or parked; no legitimacy conclusion. |
| s881–s951 | Complete M3 idiom inventories closed the audio channel-field thread; no mitigation. |
| s952–s983 | Dispatcher stack-spill family was localized; oracle callback work became blocked after s982. |
| s984 | F5/RT64 shade decode layout audit refuted lane/order defect; upstream shade-state or lighting remains. |
| s985–s990 | Payload/source census, DMA census, page-fault census, and host-PC mapping ruled out the instrumented DMA path and a universal direct-writer explanation. |
| s991–s995 | Regeneration-owned generated-store instrumentation established generated ownership for some rows and bounded values, not a universal writer. |
| s996–s999 | Source ownership is mixed; task-scoped provenance showed the zero-shade source-to-replacement join was still missing. |
| s1000–s1001 | F5 ordinals reset at RT64 DL boundaries; root-DL identity does not join to child consumer DLs. |
| s1002 | Root-DL validation retries were invalid before VI-1024; no conclusion changed. |
| s1003 | Accepted DPC bounds contained all observed repeated RT64 consumer DLs in a valid capture; individual source mapping remains open. |
| s1005 | RT64 shade rows carried accepted serial/range fields; consumer ranges were child-DL-shaped and did not identify an individual F5 source update. |
| s1006 | RT64 triangle-parse join rows carried the live last F5 state, but repeated zero-shade child DLs shared one task-level state; individual source mapping remains open. |
| s1007 | Offline re-analysis: zero-shade rows are a fixed -0.5/+0.5 shade sentinel while the VTXCOLOR array is nonzero; source-join closed, question moves to ucode shade emission. |
| s1008 | Static generated-vs-GLideN64 audit: color is copied to vertex `+0x10` but the shaded-triangle path consumes `+0x18`/geometry vectors and never reads it; the `lb` is flag-only. Selected `H-shade-source-mismatch`; no mitigation. |
| s1009 | Retail ROM instruction audit: color stores are present at `0x1424/0x1428/0x1468`, but the shaded emitter at `0x1740` has no `+0x10` read; generated output preserves it and fixup does not remove it. Selected `H-original-omits-color`; no mitigation. |
| s1010 | GLideN64 TriGen semantics vs retail/generated emitter: reference copies colorData into RGBA, while retail `L_1740` writes `+0x18` from vector `v6`; RT64 shade decoding uses the subsequent RDP coefficient block. Selected `H-missing-lighting-source`; no mitigation. |
| s1011 | `v6` producer audit: `r3=DMEM[0x134]&1`; both mode arms share the final compare/store, and DMEM `0x60` is a signed table vector. Selected narrow `H-v6-clip-predicate`; sentinel origin remains open. |
| s1012 | Independent RSP semantics and the local VGE implementation agree that `vge` selects `v6` or a `v29` lane; it cannot synthesize the observed sentinel. The numeric-origin lead moves to the preceding `vmadh v6,v4,v0` accumulator/high-half path; no mitigation. |
| s1013 | Static accumulator audit: the final VMADH consumes shared state last updated by `vmadn v7,v5,v0`; `v29` cannot supply `0x8000`. Saturation versus an in-range sign-extending middle word remains open because no complete lane tuple is captured. |
| s1014 | Landed regeneration-owned M4 accumulator/VGE probe with a VMADH positive control. Two VI-1024 captures fired neither control; a Start-driven 512 gate timed out at 1024. No numeric conclusion. |
| s1015 | Closed the s1014 null-result question: root cause is phase-gate failure (positive control never armed), not an M4 result. Refutes treating either s1014 capture as evidence for/against any M4 hypothesis; next step is isolating the phase/input control before re-running the probe. |
| s1016 | Start control was positive in both the isolated and accumulator runs, but VI remained at 640 and never reached the required 512 phase; M4 and VMADH-control counts were zero. The null is phase-selection evidence only and does not classify accumulator hypotheses. |
| s1017 | Static audit: `PROBE_PHASE_WIDTH` is an exact latest-width equality gate, and `PROBE_KEYS_FROM_PHASE=1` launches keys only after the gate. A 512-gated run therefore cannot send the Start needed to cause a 512 transition; selected `H-key-schedule-phase`, no runtime M4 conclusion. |
| s1018 | Corrected 1024-gated capture reached VI-1024 at 78.3s and delivered all scheduled keys, but remained at 1024 for 85 frames with zero M4 and VMADH-control rows. Phase control passed; probe control failed, so no M4 hypothesis was classified. |
| s1019 | Artifact audit found ovl20 probe source newer than the build; CMake compiles only base/boot/B ucode, and the linked executable has neither `rs64_m4_accum_probe` nor `factor5_ucode_ovl20`. Selected `H-stale-build-link`; no M4 hypothesis classified. |
| s1020 | Reconfigure/build linked `rs64_m4_accum_probe` in the executable and regenerated the composite source, but CMake still omitted `factor5_ucode_ovl20_recompiled.c`; no executable ovl20 marker exists. Capture withheld; M4 remains unevaluated. |
| s1021 | Source/build-graph audit showed standalone ovl20 is a fixup-6q splice input, not a runtime TU: the linked composite contains 68 ovl20 route markers and `_rs64_m4_accum_probe`, while no standalone ovl20 object/symbol is expected. The missing-link interpretation is refuted; M4 remains unevaluated. |
| s1022 | The first capture omitted `ROGUESQ_LOG_M4_ACCUM` and was invalid despite VI-1024. The corrected capture reached VI-1024, fired 19 VMADH controls and 77 M4 stage rows, then hit `slotDispatcherIter+8592`; sampled endpoints lacked the 0x8000 sentinel, so no numeric hypothesis was selected. |
| s1023 | Offline pairing of the valid capture found 19 stage-1 controls, 25 complete M4 triplets, and one trailing stage-10/11 pair. Stage-12 `v6` equaled stage-11 `v6` in all complete triplets; zero lanes also equaled stage-11 `v29`, but no M4 field contained `0x8000`. The live control's two `0x8000` values were unrelated `accl` fields, so saturation, ordinary arithmetic, and VGE selection remain unevaluable. |
| s1024 | Raised the M4 row cap from 96 to 512 and rebuilt. The first two recipes were invalid (phase-stop and abbreviated schedule); the final full schedule reached VI-1024 and logged input edges but produced no stage-1 or M4 rows. Numeric hypotheses remain unevaluable; no mitigation. |
| s1025 | The no-LLE recipe reproduced the zero-row configuration failure. The corrected LLE arm passed VI-1024, input, and stage-1 controls and produced 124 complete M4 triplets. All stage-12 v6 values matched stage-11 v6; no shade field reached 0x8000, so the numeric hypotheses remain unevaluable. |
| s1026 | A 2048-row corrected LLE capture passed VI/input/stage-1 controls and produced 161 complete M4 triplets. No tested shade/accumulator endpoint reached 0x8000; only low `accl` fields did. Numeric hypotheses remain unevaluable. |
| s1027 | Split the caps to 64 stage-1 controls and 2048 target rows. VI-1024, input, all controls, and all target rows passed; no `v6`, `v29`, `acch`, or `accm` endpoint reached 0x8000 (22 `accl` hits only). Third controlled M4 null; pivot to slot-SP diagnostic. |
| s1029 | The changed ordinary-dispatch slot-SP recipe reached VI-1024, but exited after 65 frames at sticky guest PC `0x8000834c` before `slotDispatcherIter` or `[slot-sp-guard]`; classify as `H-no-sp-event` and adjust the key schedule rather than selecting a corruption model. |
| s1030 | The postponed-`a` ordinary-dispatch recipe reached VI-1024, delivered all scheduled inputs, and captured 108 frames but still produced no slot-dispatch or guard marker; `H-no-sp-event` recurred, so the recipe family is closed without classifying `$sp` corruption. |
| s1031 | The corrected retail oracle armed both watches and its whole-RDRAM positive control visibly fired 200 callbacks, confirming callback liveness. The all-RDRAM watch slowed the run to VI 62 / 1.2 emulated seconds before SIGKILL; the freelist watch had no hit or usable PC attribution, so the retail question remains unevaluable. |
| s1032 | Added thresholded removal of only watch index 0 after 10,000 positive-control callbacks. The marker reported removal `rc=0` and index 1 remained armed; the 180-second run completed 10,799 VI but stayed at width 320, with zero freelist hits. Callback instrumentation is validated, but the retail target phase remains unevaluable. |
| s1033 | Re-ran the threshold-removal oracle with the documented 11-Start schedule. The positive-control marker fired, PIF RAM showed the Start bit on every injected edge, and 10,799 VI completed, but VI stayed at width 320/origin `0x006dd280`; the freelist watch had zero hits. This ruled out callback failure and any retail freelist conclusion. |
| s1034 | Ran the verified Start-only versus Start+A discriminator. The config was confirmed as `Start = key(40)`; the whole-RDRAM positive control reached 10,000 callbacks and was removed, pad words showed Start and A edges, and 5,398 VI completed with no transition beyond width 320/origin `0x006dd280`. This refuted input-not-consumed and A-confirmation explanations; the freelist watch remained unevaluable. |
| s1035 | Ran the bounded retail-oracle environment/phase audit. The core identity and pure-interpreter mode matched the prescribed paths; the whole-RDRAM control/removal and Start/A pad controls passed, but 2,694 VI stayed at width 320/origin `0x006dd280`. Startup logged missing/incompatible input sections before config materialization. This refutes the controller-protocol hypothesis and leaves config/phase-path explanations open; the freelist watch was not evaluated. |
| s1036 | Audited the oracle source order and ran a fresh-config 60-second schedule. CoreStartup precedes input-plugin attachment, whose first startup creates the missing sections; generated `Start = key(13)` nevertheless accepted verified scancode-40 Start presses. The whole-RDRAM control/removal passed and 3,599 VI stayed at width 320/origin `0x006dd280`; no freelist watch was armed. This closes local config ordering and leaves the phase-path explanation open. |
| s1037 | Added an independent VI-register poll audit and repeated the verified 11-Start schedule. Whole-RDRAM callbacks reached 10,000 and were removed; all 11 presses produced Start pad words, and callback/poll traces stayed at width 320/origin `0x006dd280` for 3,599 VI. Selected `H-retail-attract`; the 512 hangar phase and freelist watch remain unevaluable. |
| s1038 | Corrected LLE M4 capture reached VI-1024, passed 64/64 stage-1 controls, and produced 683/683/682 stage-10/11/12 rows. No `v6`, `v29`, `acch`, or `accm` endpoint reached `0x8000`; no crash marker appeared. Controlled null; M4 recipe closed pending a new discriminator. |
| s1039 | Retail oracle pulse-vs-hold discriminator: both eleven-Start arms passed 10,000 whole-RDRAM callbacks with removal `rc=0`, delivered all Start pad edges, and completed 3,600 VI at width 320/origin `0x006dd280`. Selected `H-retail-path-independent` for these input shapes; freelist watch remains unevaluable. |
| s1040 | Retail oracle cadence discriminator: documented five-second and rapid one-second eleven-Start schedules both passed the 10,000 whole-RDRAM control/removal, delivered all 11 Start pad edges, and completed 3,599 VI at width 320/origin `0x006dd280`. Neither cadence reached 512; timing cadence is not sufficient in this 60-second window, and the freelist watch remains unevaluable. |
| s1041 | Retail oracle first-input discriminator: eleven 150 ms Start pulses beginning at 1 second versus the documented 6-second start both passed the 10,000 whole-RDRAM control/removal, delivered all 11 Start pad edges, and completed 3,599 VI at width 320/origin `0x006dd280`. Neither first-input timing reached 512; the tested timing window is not sufficient to explain the attract path, and the freelist watch remains unevaluable. |
| s1042 | Extended the same early-versus-documented Start arms to 120 seconds. Both passed the 10,000 whole-RDRAM control/removal and delivered all 11 Start pad edges; both completed 7,199 VI with no transition beyond width 320/origin `0x006dd280`. This closes duration as an explanation for the tested attract path, while the 512 hangar phase and freelist writer remain unevaluable. |
| s1045 | Concurrent retail-oracle Start-only versus Start+Z schedules both passed 10,000 whole-RDRAM callbacks, delivered 11 Start edges, and completed 120 seconds with VI callback/poll fixed at width 320/origin `0x006dd280`; the enriched arm also delivered 11 Z words. Selects `H-retail-path-independent` for this tested input variant; hangar phase remains unevaluable. |
| s1046 | Source/config audit found the documented eleven `start` events map to scancode 40 and verified Start pad words; the generated `Start = key(13)` is an SDL1-era config label, not the named-button injection. The 150 ms hold and absolute schedule match, and the VI origin distinction is compatible. Selects `H-retail-state`; the state transition remains open. |
| s1044 | Offline reconstruction of 682 complete M4 stage triplets matched all 5,456 observed post-VMADH lanes. Synthetic saturation and in-range `0x8000` controls passed; real rows had no `0x8000` pre-saturation, post-saturation, or post-VGE. The accumulator model is validated, but the real numeric origin remains open. |

## Ranked backlog

1. The retail oracle remains in the width-320 attract path despite verified
   Start edges, long Start holds, rapid cadence, early first input, 120 seconds,
   simultaneous A, and Start+Z. s1045's callback/poll agreement and PIF Z
   control are live. s1046 closes the documented recipe/input contract as
   `H-retail-state`. Do not arm the freelist watch until a 512 hangar-origin
   phase is reached; the next probe must identify a genuinely different
   state/control sequence.
2. The M4 accumulator/VGE numeric-origin question remains open, but the
   existing capture recipe is closed after a fourth controlled null. Resume
   only with a new discriminator or independent ground truth.
3. The `slotDispatcherIter+872` guest-`$sp` corruption has a landed and
   binary-verified diagnostic (`N64Recomp/fixup_game_funcs.py:25156-25185`,
   s1005): `ROGUESQ_LOG_SLOT_SP_GUARD=1` dumps the register file when the
   stack pointer is out of RDRAM at `slotDispatcherIter` entry. The queued
   `s1029_slot_sp_guard_late_a.sh` is closed after two phase-positive no-event
   results; do not do another static sweep.
4. Directory access to `rs64-oracle` is restored; the callback ABI repair is
   confirmed by runtime positive control, but target attribution still needs
   the bounded-watch change in item 1. Do not self-grant access or infer a
   retail phase result.
5. Preserve regeneration delete-before-regen ordering and audit fixup counts
   if a reproducible omission appears.

## Phase-gate audit (s1017)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

The phase-gate audit found a harness sequencing defect, not an M4 result.
`PROBE_PHASE_WIDTH` is an exact comparison against the latest `[phase]
vi_width=N` line. With `PROBE_KEYS_FROM_PHASE=1`, `tools/probe.sh` starts the
key worker only after that exact width is observed. Therefore a
`PROBE_PHASE_WIDTH=512` run cannot send the Start event that may be required
to leave the title/attract path and enter 512; s1016's positive Start records
came from a separate ungated control and do not refute this ordering defect.
The s1018 capture did gate on reachable 1024 and send the documented schedule,
but it stayed at 1024 and produced no probe-control rows. The next step is an
artifact/runtime-path audit before another capture; exact commands are in
`scratch/agent/NEXT.md`.

The source-level truth table selected `H-key-schedule-phase`:

| Condition | Implementation | s1016 512-gated run |
|---|---|---|
| Gate predicate | `cur_width() == PROBE_PHASE_WIDTH` | waits for exact 512 |
| Key worker start | after gate when `PROBE_KEYS_FROM_PHASE=1` | never starts |
| Start can cause transition | requires an event before/while leaving 640 | impossible in this recipe |
| Non-gated control | keys start immediately when phase mode is off | Start positive, but no 512 transition observed |

`H-gate-exact-width` is not selected: the gate is behaving as implemented,
and 512 is only a target width, not a phase ordinal. `H-probe-contract-mismatch`
is refuted by the source/default parsing matching the documented variables.

The next artifact discriminator is whether the active ovl20 implementation is
present in the linked dispatch path, not merely whether the shared probe helper
is linked. The runtime discriminator remains whether the corrected
1024-relative schedule fires the independent VMADH control.

Competing M4 hypotheses remain unevaluated:

- `H-accumulator-saturation`: `vmadh v6,v4,v0` produces the signed endpoint
  pattern through the RSP accumulator high-half and saturation behavior.
- `H-v4-v0-arithmetic`: the endpoint pattern is an ordinary bounded result of
  the `v4`/`v0` arithmetic, without saturation being decisive.
- `H-v29-selection`: VGE selects a DMEM-0x60 threshold lane that coincidentally
  matches the sentinel.

Discriminator: reconstruct the four shade lanes immediately before and after
`vmadh v6,v4,v0`, applying the independent accumulator rules. Endpoint lanes
appearing before saturation select `H-v4-v0-arithmetic`; endpoint lanes created
only by saturation select `H-accumulator-saturation`; a matching `v29` lane
selects `H-v29-selection`.

The `slotDispatcherIter` sp-guard soak is a separate queued recipe
(`scratch/agent/soak_queue/s1029_slot_sp_guard_late_a.sh`), not this work unit.

## Method and safety rules

- Before runtime instrumentation, consult `tools/oracle/README.md` and
  `docs/F5-UCODE-REFERENCE.md`; arm a whole-RDRAM positive control.
- Gate animated comparisons on VI transitions; scope counters and log budgets
  to the phase; batch all instrumentation into one build/run.
- Use SIGKILL, launch from `build/`, and use capture paths whose final
  component does not begin with `.`. Queue repeat soaks rather than babysit.
- Diagnostics in generated code belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require patch export.

## Closed and parked

M5 audio, overlay boot/menu, old ucode/DMA experiments, rendering dead ends,
earlier idiom campaigns, duplicate-symbol work, and the M3 audio class are
closed or archived in PROJECT-OVERVIEW. Parked items include intermittent
regeneration omission, isolated animation/frameStart SIGBUS reports, the M3
DoD gate, and M4 band-row coverage.
