# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records
remain in the ledger. This file was compacted in the s1004 maintenance pass
from 60,345 bytes / 642 lines. It is intentionally a current-state document,
not a second ledger.

Reviewed through s1009 (2026-08-14). The active investigation is M4 zero-shade:
the emitted shade is a constant sentinel, and the retail Factor 5 instruction
stream omits a color-word read in the shaded-triangle emitter. The remaining
question is the intended semantic source of that emitter's shade record. M5 audio de-stubbing
is closed. M3 work is limited to complete idiom-class audits. The retail-oracle
callback thread is no longer directory-blocked (`.claude/settings.json`
currently lists `rs64-oracle`); see backlog.

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
- Retail oracle work: the s983 directory block is stale — `.claude/settings.json`
  currently lists `rs64-oracle` in `additionalDirectories` and `Read`. s982
  localized the corrected-core failure to dereferencing `r4300_pc(r4300)` in
  `read_with_bp_checks` before callback entry. No retail phase conclusion or
  recomp mitigation follows; resume only when the loop is not actively running
  a capture.

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

## Ranked backlog

1. Trace the retail Factor 5 shaded-triangle record semantics against the
   GLideN64 reference and the generated `TriGen`/triangle consumers. Identify
   whether the fixed `-0.5/+0.5` shade sentinel is an intentional no-lighting
   value or an incorrect vector/register source. Name the original producer,
   record offset, and consumer before proposing any mitigation.
2. The `slotDispatcherIter+872` guest-`$sp` corruption now has a landed
   diagnostic: `ROGUESQ_LOG_SLOT_SP_GUARD=1` dumps the register file when the
   stack pointer is out of RDRAM at `slotDispatcherIter` entry. Queue the soak
   and classify the captured caller; do not do another static sweep.
3. Directory access to `rs64-oracle` is restored; resume the archived s983
   oracle callback audit when the loop is not actively running a capture. Do
   not self-grant access or infer a retail phase result.
4. Preserve regeneration delete-before-regen ordering and audit fixup counts
   if a reproducible omission appears.

## Next work unit (s1009)

HYPOTHESIS-ID: m4-zero-shade-emission-constant

Trace the color-bearing vertex record from the Factor 5 ELF/disassembly through
`tools/fixup_factor5_ucode.py` and RSPRecomp generation. Determine whether the
missing shaded-triangle read of vertex `+0x10` is present in the original
microcode or was lost by the generated/fixup pipeline. Do not edit generated
output; static audit only — no build/run required.

Competing hypotheses and the discriminating measurement:

- `H-original-omits-color`: the retail microcode itself never consumes the
  color word for the shaded-triangle emission path.
- `H-generation-drops-color`: the original microcode has a color read, but
  disassembly conversion, RSPRecomp, or the fixup pipeline omitted it.
- `H-layout-misread`: the color read exists and feeds the generated vectors,
  but the RT64-side shade interpretation points at the wrong record offsets.

Discriminator: locate the original ELF instruction sequence and the generated
sequence around the vertex-record color store and the shaded-triangle entry.
An absent color read in the ELF selects `H-original-omits-color`; a color read
present only in ELF selects `H-generation-drops-color`; a generated color read
feeding the shade vectors with a consumer-offset discrepancy selects
`H-layout-misread`.

The `slotDispatcherIter` sp-guard soak is a separate queued recipe
(`scratch/agent/soak_queue/slot_sp_guard.sh`), not this work unit.

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
