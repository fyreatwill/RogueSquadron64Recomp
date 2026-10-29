# NEXT: name the store that zeros the depth-upload source
HYPOTHESIS-ID: g1d-levelselect-ram

s6628 selects H-between, single-source runtime evidence. Evidence:
scratch/agent/s6628_rdram/depth_verdict.json. One Debug binary, both widths,
54/55 good frames, all controls pass, 0 crash markers. On 21:9:
- copyToRAM n=3499 covers physical 0x00BB0020; native rawBe=0x9EC4.
- site A n=3500: native=swap=exit=0x9EC4, bytes CC9EC49E, fl=0.
- site B n=3501: bytes 00000000, left head 13 zeros.
- upload n=3502: guest/GPU MAE 0 on 142 samples.
A and B use the identical host address 0x300bb0020, runtime base 0x300000000.
The native value varies with animation; do not require the old 0x9F4C.
No shader patch, skip, restore, or default change is justified.

ONE unit: attribute the actual writer, not another join-field increment.
Build the whole discriminator in ONE binary, both widths. Before building,
check the boring possibilities: depth buffer allocation/clear ranges, existing
host zero/copy calls and the higher-memory masks. Read bounded source windows
before adding probes. Consult F5-UCODE-REFERENCE and oracle/README; retail
has no corresponding >8MB framebuffer allocation, so label this mapping
single-source until independent semantics or a writer instruction corroborates it.

Hypotheses:
- H-guest-store: a generated MIPS store/loop clears this physical address.
- H-host-write: a host memset/bzero/memcpy/DMA writes it (possibly a range
  intended for another allocation). Attribute caller, src/dst/length.
- H-uncovered: A/B transition recurs but no intersecting writer is captured;
  the instrumentation is incomplete, not proof of absent guest stores.

Discriminating measurement: actual before/after bytes for every intersecting
store or bulk operation, joined to A/B/upload on their existing sequence.
The winning record must contain PC/function or host call stack, exact byte
range, source/length, width and old/new bytes; distinguish a zero already
present from the operation that changes it. Trace the named writer's caller
and allocation/range arithmetic to decide whether that value is legitimate.
Do not land a guard in lieu of that explanation.

Use existing generated callbacks where coverage is proven:
rs64_m5_writer_parity in funcs_*.c calls rs64_m5_route_value_writer before
its enabled early return. The latter lives in src/main/upstream_compat.cpp.
Audit coverage for scalar, FP, double and unaligned stores; do not assume
all are covered. Log at the actual store (or correctly resolve a pending
pre-store record), not the next unrelated store. Hook existing host memory
begin/end paths too; some currently mask to 8MB, so compute this diagnostic's
physical range from the real destination/base, not their masked field.
rs64_g1d_blk_dma exists but filters to specific fill words and is insufficient
for a zero-write witness as-is. A poller backtrace is not writer attribution.

Keep A/B/native/guest/GPU controls. Arm from boot or every covering A after
its write; do not depend on a stopwatch or run-lifetime budget. Positive
control BOTH guest-store and host-zero paths in the SAME run on a reserved,
non-game scratch word: visibly produce known nonzero->zero transitions and
recover the expected PC/caller. Do not inject zero into the real depth image.
A branch count or a silent log is not a control. If only one writer class
passes its control, repair before interpreting a null. Preserve diagnostic
changes through existing fixup scripts if generated code needs edits.

Commands after implementing the complete witness:

    python3 tools/g1d_floor_depth.py --selftest
    python3 tools/g1d_floor_attachment.py --selftest
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
    python3 tools/g1d_floor_depth.py --output-root scratch/agent/s6629_writer
    ./submodule-patches/export.sh

Extend the existing runner/classifier to analyze the writer table, not only
A/B; add synthetic classifier cases for both writer classes, unchanged
writes, missing controls and unmatched transitions. For a host-only callback
change regeneration is unnecessary; any generated change follows
make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake, with the actual
local paths checked first. Do not hand-edit load-bearing generated logic.
The runner checks screen unlock, runs from build/ beside the ROM, phase-gates
the route, runs one instance at a time and SIGKILLs it. Preserve s6624..s6628
artifact roots. No repeat-hold soak or aim/steering work.
