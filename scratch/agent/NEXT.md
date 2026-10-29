# NEXT: resolve ownership of the zlib window overlapping the depth image
HYPOTHESIS-ID: g1d-levelselect-ram

s6629 named the actual store; do not re-attribute 0xBB0020 or suppress it.
Final evidence: scratch/agent/s6629_writer_context/depth_verdict.json,
writer_origin.json, clear_interval_check.json. Initial paired capture:
scratch/agent/s6629_writer/depth_verdict.json. Both rounds pass guest-bzero,
host-memset and GPU controls, zero crash markers. The final 21:9 zero:
A n4635 raw/native/swap=0x9540, host native-swap n4636 unchanged,
rs_memset 800078EC exact post-store n4637..4640 zero all four bytes,
B n4641 zero, upload n4642 faithful. Caller stack:
mainEventQueueWorker -> processAssetLoadStep -> inflateInit_ -> inflateInit2_
-> inflate_blocks_new -> zcalloc -> rs_zcalloc -> rs_memset.
Args dst=80BADB50 fill=0 len=8000; actual range [BADB50,BB5B50).
Retail ROM offset 84EC independently contains A0450000 = sb a1,0(v0).
Generated rs_zcalloc at 8000527C allocates, then clears the returned block
(jal rs_memset 800052C4). This clear is legitimate for the zlib allocation.

Do ONE ownership experiment, the complete lifetime table in one build, both
widths; do not spend iterations adding individual join keys. First consult
existing allocation instruments and the framebuffer reservation arithmetic.
ROGUESQ_LOG_FB_ALLOC logs partitionFramebufferMemory's output. Its widening
policy is tools/apply_s6031_far.py applypfm (512x448 and 512x340); generated
function is in funcs_0.c. initVideoSubsystem is funcs_5.c. The older source
comments/symbol PCs can disagree; use the actual body and retail ROM words.
Read docs/F5-UCODE-REFERENCE.md and tools/oracle/README.md before interpreting
streams. Oracle cannot witness this above-8MB layout; label ownership claims
single-source until independently checked.

Hypotheses:
- H-live-overlap: the game still owns the depth framebuffer when rs_malloc
  returns its range to zlib (bad wide reservation, heap bound, or freeing).
- H-stale-target: the guest legally released/repartitioned that range before
  the zlib allocation; RT64 later uses an obsolete depth target/workload.
- H-address: current guest SETZIMG/size arithmetic actually names a different
  allocation; host target/range lookup manufactures the intersection.

DISCRIMINATOR: one chronological ownership table from reservation through
malloc/free, CPU clear and the specific depth read-in. Include original and
wide dimensions, complete reserved intervals and heap bounds; allocating and
freeing caller; live color/depth image command addresses and sizes; workload
creation/use identity; current-versus-retired ownership of [BADB50,BB5B50).
True simultaneous guest ownership selects live-overlap and its first faulty
reservation/free boundary. Legal reuse followed by an old workload selects
stale-target. Different guest/host intervals select address conversion. Missing
lifetime boundaries = incomplete evidence, never "no overlap". The 16:9
same-phase route is the control; real returned zlib allocation plus its exact
store is the guest-memory positive control, and existing scratch/GPU controls
must pass. No cross-run image subtraction on animation.

Full stripe caveat: the named 32KB interval accounts for 23 of 26 changed
A/B column samples (12 left head rows, 11 right). x16/y192 and x1007/y191,192
change outside it; preserve these in the ownership table and record actual
intersecting operations for those addresses in the same instrument, not another
one-word follow-up. No whole-stripe root-cause claim yet.

Existing persistent hooks: floorWriterGuest pre-store + rs64_floor_writer_post
called by all existing s6336 post hooks, before legacy 8MB gates; delayed-only
records are rejected by the classifier. rs64_m5_source_context supplies full
memset args and caller frames before its own enable gate. Unaligned helpers
have direct old/new hooks; the old g1d ustore-PC setter is not present in the
current generated files, so a zero unaligned PC is not attribution. Census
scratch/agent/s6629_store_coverage.json: all 25 missing scalar prehooks have
constant $zero-relative destinations and cannot reach these intervals.
Host coverage is paired for native-swap, renderer optional zeros, zmemcpy,
ROM DMA and RSP DMA. SRAM's legacy begin hook is after the loop: repair its
placement if SRAM is pertinent; do not claim universal host-write absence.

Commands after completing the ownership table (host callbacks need no regen):

    python3 tools/g1d_floor_depth.py --selftest
    python3 tools/g1d_floor_attachment.py --selftest
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
    env ROGUESQ_LOG_FB_ALLOC=1 python3 tools/g1d_floor_depth.py --output-root scratch/agent/s6630_ownership
    ./submodule-patches/export.sh

If generated instrumentation is required, persist it in fixup tooling and use
the safe scratch regeneration pipeline (never tools/agent/regen_n64recomp.sh,
which explicitly warns it destroys the live tree). One game at a time from
build/, screen unlocked, phase-driven runner, SIGKILL. No G4 repeat hold.
