# NEXT: RESUME s6169 — qualify width-aware menu/hangar framebuffer allocation
HYPOTHESIS-ID: g1d-widescreen

s6168 selected H-menu-fb-allocation. This retry did not rerun the experiment;
the existing s6168 artifacts are the evidence to resume from. The opt-in video-state writer changes
512x340 menu/hangar calls to width 796, but `partitionFramebufferMemory`
still receives and allocates 512x340. The paired control/wide traces also show
the expected 0x400000 12 MB relocation and the wide crash remains in
`renderLitTexturedMeshFaces+7948`; no RT64-only explanation is needed yet.

Checkpoint close-out: do not rebuild or rerun from this retry. The next iteration
must begin with the allocation rewrite below and preserve both control and wide
arms in the same build.

Next work unit: extend the regeneration-safe `ROGUESQ_FB_WIDTH` rewrite in
`tools/apply_s6031_far.py` so the matching 512x340 partition call uses the
opt-in width, rebuild once, and run concurrent 4:3 control plus 16:9/12 MB
arms with `ROGUESQ_LOG_FB_ALLOC=1 ROGUESQ_LOG_RDP_ROUTE=1`. Keep default
retail unchanged.

Competing hypotheses and discriminator:

- H-menu-fb-fixed: the 512x340 allocation is the contract defect; after the
  change the wide allocation trace shows the menu call as 796x340, the phase-5
  RDP/VI join remains width-consistent, and the render crash disappears or
  moves to a newly attributable guest site.
- H-menu-render-input: allocation becomes 796x340 but the same
  `renderLitTexturedMeshFaces+7948` failure persists with a bad input/backtrace;
  allocation was necessary but not sufficient.
- H-wide-RT64: allocation becomes 796x340 and the guest/RDP rows are sane, but
  an RT64 consumer still rejects the target; retain the first RT64 failure and
  its address/width as the next discriminator.

Required positive controls: control must emit `512x340` allocation rows and
512-wide phase-5 RDP/VI rows; wide must emit the changed `796x340` allocation
row and 796-wide phase-5 rows. Capture the first wide framebuffer dump or
crash/backtrace. Exact run shape:

    python3 tools/apply_s6031_far.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    # concurrent arms from build/, using the s6168 fixed-run env and SIGKILL watchdog

Do not add a guard or alter the default 4:3 path.
