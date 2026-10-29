# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6628 (2026-10-29).
`PORTING-STATE.md` is the chronological ledger. Historical detail, the
retired backlog, and the verbatim s6378-s6551 body of this file are in
`docs/PROJECT-OVERVIEW.md` ("Migrated from CURRENT-TRUTH (s6552 maintenance)"
and "Archive: CURRENT-TRUTH body s6378-s6551").

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins; mission input reaches flight code.
- M5 audio de-stubbing, M3 idiom audits, generated-symbol renaming (G5), M6
  first-mission endurance (3x600 s lvl1/5/7, s6442), and G2 audio are closed.
  G4 crash hunting is parked after clean coverage. G1 is mission coverage and
  visual quality, not autopilot work.
- **Active thread: G1d 21:9 level-select tear (HYPOTHESIS-ID g1d-levelselect-ram).**
  - s6628: paired live-RDRAM reads select H-between (single-source runtime
    evidence). One Debug binary, 16:9 35.0 s / 21:9 33.5 s, 54/55 good
    frames, alive, 0 crash markers; all controls pass. Last covering native
    write n=3499 is rawBe `0x9EC4`; site A n=3500 reads that same value
    after the byteswap and at function exit, freelist restore off. Site B
    n=3501 reads `00000000` before depth storage. Both point at
    `0x300bb0020`, base `0x300000000`, eq=1. Upload n=3502 has 13 zero
    head words and guest/GPU MAE 0. This narrows the writer to between the
    two sites; it does not name it. H-swap and H-alias are refuted in this
    run. Evidence `scratch/agent/s6628_rdram/depth_verdict.json`. No fix
    or default change. Next: attribute the actual intersecting store/copy.
  - s6627: the 0x0000 stripe is not a `copyToRAM` payload. One Debug binary,
    both widths. 16:9 34.2 s / 21:9 33.5 s, 54/52 good frames, alive,
    0 crash markers. Classifier selects H-later-zero; upload control
    stays H-guest, mae 0. All 935 wide writebacks before that upload
    are 1024x447 at phys `0x00B20000` (rows 0..447). That span covers
    `0x00BB0020` (depth x=16, y=180 = this image's y=288). The native
    rawBe there is `0x9F4C` on every one of them, never `0x0000`; other
    sampled words in the same write include `0xFFFC`. The upload is the
    next log event (n=2093, 16-bit call count still 2092) and its head
    is still `0x0000`. Image y=180 of the same write is rawBe 0 at
    `0x00B7A020`, a different pixel. The only later rawBe 0 at
    `0x00BB0020` is the depth image's own writeback at `0x00B56000`
    after the upload. 16:9 floor z store is 0.99195..0.99669. No
    default change. Evidence `scratch/agent/s6627_ram/depth_verdict.json`.
  - s6626: `copyFromChanges` is faithful. One Debug binary, both widths.
    16:9 35.5 s / 21:9 33.5 s, 52 good frames, alive, 0 crash markers.
    The only depth `copyFromChanges` is `state.cpp:2604` on the 21:9
    1024x339 floor depth (guest `0x00B56000`, stride 2048, rowStart 0,
    lookup address equals store address). `ColorConverter::D16::toF` of
    the shader-endian guest words matches the GPU columns on all 142
    samples, max abs 0. The head is literal `0x0000` (x=16, y=180..192;
    x=1007, y=180..191), not the RDP clear word `0xFFFC`, which does
    appear on later rows of the same columns. `clearDepthTarget` still
    read back 1.0 before that upload; floor-enter matches it. 16:9 has
    no `copyFromChanges`; floor-enter is 1.0; a later floor op stores
    z 0.99416..0.99574. Magenta and pix-match pass. This refutes the
    depth shader, the boolean mask, and the viewport as the stripe
    writer. `workload_queue.cpp:966` and `framebuffer_manager.cpp:345`
    did not run. The color-width stride lead does not apply to this
    call. No default change. Evidence
    `scratch/agent/s6626_guest/depth_verdict.json`; runner
    `tools/g1d_floor_depth.py`.
  - s6625: named that upload and showed the clear read back as 1.0.
    Its "x=16 is a 0.964 ramp and x=1007 stays 1.0" sentence is not the
    column record; both columns interleave ~0.96 and 1.0 after a shared
    exact-0 head. Evidence `scratch/agent/s6625_depth/depth_verdict.json`.
  - s6624: pre/post color+depth witness selects H-late-test (single-source). One
    Debug binary, both widths. 16:9 36.2 s / 21:9 33.4 s, 50 good frames,
    alive, 0 crash markers, magenta/binding/fixed-function/checker controls
    pass. Every 16:9 scene enters these columns at depth 1.0. Picked serial 2
    floor op 10 is LESS, 95/95 pass, shader z 0.99524..0.99667, step
    40.4/36.9 -> 5.0/5.7. 21:9 picked serial 7 enters already torn (step
    60.5/51.7); floor op 14 LESS covers 122, passes 10, fails 112 because
    shader z (med 0.99364) is farther than pre-depth (med 0.9839).
    rejected_frac 0.873, later_frac 0, sim MAE 0, no CPU/Metal mismatch on
    that scene. The 9 wide16 blend mismatches are early zCmp=0 tris (ops
    1-9), not the floor. First 21:9 scene (serial 1, frame 1351, 0x961000)
    creates the step: entry 19.3/18.8 with 25 samples at depth 0 on rows
    0..12 (y 180..192). Op 14 passes only where pre-depth is 1.0 (36/92)
    and fails on 0 or ~0.961/0.967/0.984; the columns are largely out of
    phase. Depth-0 pixels are never rewritten. That striped depth is already
    present at sample 0, before any op in the submission. s6625 names that
    writer: copyFromChanges, after a clear that still read back as 1.0. Not a floor blend
    bug. No render/default change. Evidence
    `scratch/agent/s6624_attachment/attachment_verdict.json`; sheet
    `docs/owner_sheet_s6624_attachment.png`; runner
    `tools/g1d_floor_attachment.py`.
  - s6623: actual GPU fragment records select H-backend (single-source).
    One Debug binary, phase-driven 796/1024 arms: 16/24 complete scenes,
    2313/3450 fragment records. Every fragment recovers its sampled uploaded
    checker; independent snapshots recover all 64 checker pixels. All referenced
    textures captured, all grayscale; sampled tex0 chroma 0 on both. Actual
    smooth/wrapped shade row steps 2.66/2.51 vs 1.95/1.97, no wrapped pixels.
    Combiner/result RGB steps 4.39/5.32 vs 4.98/4.78; original non-MSAA
    attachment steps 4.39/5.32 vs 47.61/51.02. Shader-to-attachment MAE is
    0.00096 vs 37.08 (0..255 scale). This excludes colored texture binding
    and shade wrap as the first divergence at these samples; the tear exists
    before resolve in the original attachment. A fragment record witnesses
    execution, not passage of late depth tests. s6624 is that measurement:
    the 21:9 disagreement is a LESS reject, not a blend store. Prior floor/alpha/fill controls
    pass, 52/53 stop-gate frames, 0 crash markers. GPU/native/RAM checker also
    passes in both arms. Evidence `scratch/agent/s6623_shader/shader_verdict.json`;
    owner sheet `docs/owner_sheet_s6623_shader.png`; persistent runner
    `tools/g1d_floor_shader.py`. Exported renderer/shader/converter changes;
    converter selects MSL 2.2 only when PrimitiveId requires it. No rendering
    fix/default change.
  - s6622: three-stage GPU/native/RAM capture selects H-raster
    (single-source runtime evidence). After retaining only the final recorded
    pair per submission frame and displayed framebuffer address, 39 captures
    at 796 and 63 at 1024: GPU edge row steps 4.084/4.992 versus
    36.809/33.671; native 6.494/7.077 versus 39.307/35.320. RAM matches
    native exactly at all 142 floor pixels per capture (0 mismatches).
    All 64 GPU-uploaded checker pixels pass in GPU, native and RAM in every
    retained capture. Both source targets are RGBA16 UNORM per component,
    scale 1; pitch 8192. The GPU image visibly contains the 21:9 rainbow
    row tear before native conversion. Conversion/copy cannot be its first
    writer. This does not identify the actual shader/interpolant/texture or
    blend-state defect; no render fix/default change. One binary, both
    phase-driven arms, 62 closed floor frames each, prior controls pass,
    0 crash markers. Evidence: `scratch/agent/s6622_pipe/verdict.json`;
    owner sheet `docs/owner_sheet_s6622_pipe.png`; persistent runner
    `tools/g1d_floor_pipe.py`. Metal texture-to-buffer blit support added
    and exported. Diagnostic flag injects a 64-pixel checker outside the
    sampled floor band; keep it disabled during play. Next: actual GPU
    fragment values plus sampled texture/binding, not another CPU replay.
    Snapshot is after resolveTarget: resolve/downsample remains a possible
    upstream writer along with raster/shader/blend state.
  - s6621: emitted-mesh replay does not reproduce the tear (single-source).
    Both widths: 66 closed frames, 54 stop-gate frames, 0 crash markers,
    all earlier controls pass. Legacy samples: 9372/9369 common points;
    actual half-pixel-corrected samples: 9372/9370. All five missing points
    across both sample conventions lie 0.005..0.020 px outside reconstructed
    edges (retained, not filled); no interior coverage mismatch. Actual
    coefficient/mesh |ΔT|: 4.789/4.789 at 796, 4.889/4.889 at 1024;
    |Δ shade luma|: 2.943/2.948 and 2.978/2.966. Wrapped luma gives the
    same numbers. UV error is 0.000009/0.00926 texel. Perspective shade
    differs from the reference affine model by 0.191/0.887 luma, far too
    small for framebuffer edge steps 6.75/5.68 vs 56.45/53.40. Synthetic
    vertex W/UV perturbation raises row steps from 0.425 to 208.230.
    This selects H-pipe under the prewritten 25% step-agreement test,
    not a verified backend writer: this is CPU replay, not independent
    GPU/RDP execution. Independent paraLLEl-RDP documentation supplies
    plane/edge semantics only. No render fix or default change. Evidence:
    `scratch/agent/s6621_mesh/verdict.json`; persistent discriminator:
    `tools/g1d_floor_mesh.py`. Next: capture the GPU target, native-converted
    pixels and post-writeback RDRAM together to split raster from conversion.
  - s6620: fill-word H-mem refuted at the edge samples (single-source).
    One Debug binary, 64 closed frames per width, 9088 samples each:
    exactly one fill word `FFFCFFFC`, dF=0, nFs=9088 on both. Alpha
    equation is `(0-0)*0+0` throughout both arms. Shade-alpha |Δ| is
    0.08538 vs 0: the proposed larger 21:9 step is contradicted, but
    the strict 25% agreement test FAILS, so the prewritten verdict is
    unresolved, not H-pipe. Shader equation evaluation also shows that
    this equation does not consume shade alpha (same-runtime source,
    not an independent hardware witness). Positive injected checker:
    nFw=2/dF=255/dA=64 on both. Framebuffer edge steps 7.31/7.92 vs
    65.80/60.49; dy 8.40 vs 29.05. All prior controls passed, 0 crash
    markers. No rendering fix/default change. Evidence:
    `scratch/agent/s6620_alpha/verdict.json`; persistent runner
    `tools/g1d_floor_inputs.py`. Next: compare actual emitted mesh
    interpolation against the original RDP coefficient walk as one
    complete table; do not assume the CPU walk is what the GPU shaded.
  - s6619: the last primitive at x=16 and x=w-17 is the floor triangle on
    both widths. One binary, 68 and 63 closed frames. lastF is 1.0
    vs 1.0, both columns. A fill rect touches every sample
    (touchR 1.0, touchU 0) and is overwritten on every sample
    (over 1.0). Median multi_frac is 0 vs 0.18, so most torn pixels
    are one floor triangle over that fill. Pixel step 5.36/5.19 vs
    44.07/35.74, including x=16. |ΔI| 45.21 vs 42.15 and |Δ shade|
    2.95 vs 2.96. Blender and combiner unchanged. This refutes
    H-last. The tear is the blend memory term or the pixel pipe.
    No patch. Evidence: `scratch/agent/s6619_last/verdict.json`.
  - s6618: filtered I4 and shade at x=16 and x=w-17 are not the tear. One
    binary, 69 and 65 closed frames. Pixel step on fb 1400 is 5.71/5.04
    vs 54.37/51.82. |ΔI| is 46.03 vs 41.18 (rel 0.11, 21:9 smaller).
    |Δ shade| is 2.94 vs 2.97. Blender string matches. |ΔT| 4.61 vs
    4.99 stays inside 25% of 4.70 vs 4.15. This refutes H-i4-edge and
    H-shade-edge. The tear is after the combiner. No patch.
    Evidence: `scratch/agent/s6618_edge/verdict.json`.
  - s6617: I4 intensity, untextured/rect coverage, and the blender are not
    the tear at x=w/6 and x=5w/6. One binary, 66 and 69 closed frames.
    I4 self-test passed. Tile is fmt 4 / siz 0, bilerp, no TLUT, on both.
    Pooled |ΔI| is 51.18 vs 45.16 (21:9 smaller, rel 0.12). Untex fraction
    is 1.0 on both (a fill and a 2-cycle rect cover every sample; same
    blender set). Floor blender is
    `cyc0f0(CC*CCA+MEM*MEMA)|(CC*CCA+MEM*MEMA)` on both. |ΔT| 4.70 vs 4.15
    and |Δ shade| 2.65 vs 3.45 stay inside 25% of s6616. Raw S matches
    s6616 to 0.02. Outer-third dy is 5.55 vs 23.11. This refutes H-i4,
    H-untex, and H-blender at that sample. On the same fb 1400 frames the
    row step at x=16 and x=w-17 is 3.9 vs 46.2 and 4.5 vs 46.4, while
    x=w/6 is only 5.9 vs 12.7. The next sample is the edge. No patch.
    Evidence: `scratch/agent/s6617_i4/verdict.json`.
  - s6616: outer-third S and shade luma are not the tear. One binary, both
    arms, 67 closed frames each, same edge walk as s6615. floor_frac 1,
    badw 0, nS=nL=npair=9380. Raw T matches s6615 to the printed digits.
    Pooled |ΔT| is 4.79 vs 4.09 (within 25% of 4.32 vs 3.63). dy 5.97
    vs 20.0. Combiner is `(T0-0)*SHADE+0` on every frame of both arms.
    othermode L alternates `00552230` and `00552078` on both arms
    (AA_EN|IM_RD vs CVG_DST_FULL); not a width split. Within-frame
    second identity is 0.5% / 5.2% of sample points, same equation.
    Pooled |ΔS| is 3.93 vs 2.69 (21:9 smaller, rel 0.32). Pooled
    |Δ shade luma| is 2.66 vs 3.52 (rel 0.24). Neither is more than
    twice on 21:9, so H-s-row and H-shade are not selected. |ΔS| is
    outside the 25% band, so the strict both-agree refutation is not
    met; the predicted direction is contradicted in every quartile.
    Pixel dy is 3.3x and shade is 1.3x. No patch. Evidence:
    `scratch/agent/s6616_ss/verdict.json`.
  - s6615: perspective-correct texel T at x=w/6 and x=5w/6 does not
    jump more on 21:9. One binary, both arms, the s6614 edge walk.
    Floor texel is (T/W)*1024 from the last op 0x0F tile 0 line 4
    triangle. Pooled mean |ΔT| is 4.32 (16:9, 49 frames, 6860 pairs)
    vs 3.63 (21:9, 46 frames, 6440 pairs), relative gap 0.16.
    other_frac is 0 on both. floor_frac is 1.0, badw 0, dy 5.42 /
    24.82. Raw texels at y=200 and y=230 agree to about 0.05
    (9.99 vs 10.00, 32.92 vs 32.92); dtdx scales by about 796/1024
    and cancels the wider x. This refutes H-t-row and H-overdraw.
    Median multi_frac is 0.007 vs 0.38, so 21:9 overlaps more floor
    tris, and the last-writer T still matches. No patch. Evidence:
    `scratch/agent/s6615_tex/verdict.json`.
  - s6614: those floor triangles cover both outer thirds. One binary.
    Edge spans (not bboxes) of op `0x0F` tile 0 line 4, scanlines
    180..250, clipped to the scissor. Every closed frame is solid:
    16:9 n=44 median 223 tris, 21:9 n=26 median 163 tris, hole_rows 0,
    rect_gap_rows 0, hull_frac 1, mean hull equal to the third
    (265 and 341). rect_frac 0.9981 / 0.9985 is about one uncovered
    pixel per row, and no run is longer than 2 px. Scissor is the
    full framebuffer (0..795 and 0..1023). x0spans stays 6-23 while
    a frame has ~160-230 tris, so the walker is not painting every
    triangle full-width. dy control 7.61 / 26.08. This refutes
    missing coverage, an edge walk, and a scissor clip. The tear is
    inside covered pixels. No patch. Evidence: `scratch/agent/s6614_cov/`.
  - s6613: S at screen x=0 is not a 21:9-only walk off the 64-wide mask.
    One binary, both arms. Perspective on, shift 0, uls 0, texel
    (S/W)*1024. 16/16 early-table triangles pair on base S and dtde.
    12 inside [0, 64) on both, 4 outside on both, 0 inside only on
    16:9. The 4 that cover x=0 are inside on both. Census
    st_in=21 st_out=19 cover_in=4 cover_out=0 on both widths. Texel S
    agrees to about 0.2. x_major moves and dsdx shrinks by 796/1024,
    so they cancel. Per-pixel outer-third dy on rows 180..250 is 5.48
    (16:9) and 26.9 (21:9); the same scorer on the s6612 dumps is
    8.32 and 25.4. No patch. Evidence: `scratch/agent/s6613_st/`.
  - s6611: the step-column metric is blind. Control passed (flight `none`; a
    pasted 200×640 block scores H-composite at x=640). n=1400/1500/1600
    score `none`; stride fit R≤0.061 for slopes ±384/±512. Outer-third
    row-to-row luma in the worst 70 rows is 24.3/19.1/18.3 versus 7.7 on
    the 16:9 level-select and 3.8–5.1 on the quiet rows of the same 21:9
    frames. Shift 384 or 512 makes that window worse (SAD ~50–62 vs
    ~17–22). Refutes a 1024-vs-640/512 framebuffer shear and a stable
    512/640 seam. The pixels are horizontal slices of the hangar floor
    in the outer thirds; the center ring stays near the 16:9 ring.
    Summary: `scratch/agent/s6611_tear/summary.json`. No default change.
  - s6612: the floor primitive is an RDP triangle, op `0x0F`, tile 0,
    TMEM line 4, fmt 4 / siz 0, mask 6. Logged from RT64's decoded
    triangles (the DPC byte walk had 0 sane of 3577 and 3389). On the
    same route, dtde matches across FB 796 and 1024 (19.53, 20.42,
    29.79, 31.27, 50.12, …) and Y spans match; X span and dsdx scale by
    1024/796. Same-run floor-band dy is 8.47 (16:9) vs 24.55 (21:9).
    Not a stride or derivative that jumps with width. No patch.
    Guest PC `80007904` is on every row and is not the writer.
  - s6610: 16:9 flight-radar clip fixed (opt-in only). The s6155 right-half add
    places the ring at retail_right+second. second=A+RA (334 at fb 796) is
    50 px past that frame. second=fbw-512 alone moved the ring to x 671..764
    (inset 31, width 94; retail measurer 387..480, same inset and width) but
    split the disc: wedge stayed at 769..792, 0 orange pixels inside the ring.
    Disc tris are selected pre-shift; the shift that tracks the ring is
    second-A, which is A once second=ex. With shift=A, 16:9 wedge 719..742 is
    271/271 inside and 21:9 wedge 947..971 is 417/417 inside. Both rings
    inset 31, width 94. Left shield stayed x 44..71 (16:9 x1=72). Both arms
    reached flight, 0 crash lines. Retail was not rerun. Sheet:
    `docs/owner_sheet_s6610_radar.png`. Defaults unchanged.
  - s6609: retail, 16:9 and 21:9 hangar+flight, window backing-store paired
    with VI-bounded source. Screen was unlocked. All three arms alive, 0 crash
    lines. Extra width is additional scene (level-select text and side walls
    that retail crops). Left flight shield stays at source x 44..71 on every
    width. Retail radar x 388..476 (inset 35, width 89); 21:9 radar x 903..991
    (inset 32, width 89); 16:9 radar x 722..794 (inset 1, width 73) and the
    window shows the same clip. Those edges are exactly retail+334 and
    retail+515, the logged `ROGUESQ_HUD_ANCHOR` right terms (A+RA in
    `rs64_g1d_apply_aspect_policy`, consumed by `tools/apply_s6155_hudcpos.py`).
    Per-sprite f4 was not logged. 21:9 level-select source is torn across the
    middle on n=1400/1500/1600 and the paired window matches; 16:9 and retail
    level-select are not torn. Later 21:9 bay/craft frames and flight are
    clean. Black bars (none / ~120 px / ~205 px) are the fixed 640x480 SDL
    window letterboxing a wider framebuffer, not missing source rows. This
    selects H-game for the 16:9 radar clip and the 21:9 level-select tear, and
    refutes H-present for both. Sheet: `docs/owner_sheet_s6609_aspect.png`.
    Defaults unchanged. fb-flip-range logs only 64 rows per phase, so the
    21:9 hangar copy (still phase 4 after the 512 title) is not in that log.
  - s6608: VI fbSize/fbAddress dumper. Retail and 16:9 copies match
    512x444 / 512x336 / 796x336. Window captures lack the old bottom tail;
    +112-row references show pixels outside the source. Selects
    H-dump-overread for that band, not renderer corruption. Sheet:
    `docs/owner_sheet_s6608_capture_bounds.png`. Do not repeat the band census.
  - s6607: a before/after colour-writeback witness passed its injected-byte
    control in retail and ASPECT 16:9 (12 MB); both 95 s arms finished alive,
    0 crash markers. In hangar phase 5, the two wide sources had 48/25
    intersecting writebacks, all changing the watched columns with changing
    control pixels; non-overlapping writes changed none. This refutes only
    "no RT64 writeback touches the region", not the artifact's origin.
    No preceding post-writeback hash matched the eight initial source
    fingerprints. Crucially, raw PPMs extend past the logged source:
    retail dumps 512x358 versus copy 512x336 (+22 rows), wide 796x448
    versus copy 796x336 (+112). The wide bottom garbage is below the copy
    boundary in the same captured frame; source code hardcodes the excess
    height. The earlier column fingerprint does not measure that bottom band.
    **s6606's H-source attribution is superseded.** Real window appearance is
    unmeasured; capture bounds must be corrected before a rendering fix.
    Evidence: `scratch/agent/s6607_band_wb/summary.json`,
    `docs/owner_sheet_s6607_capture_bounds.png`; analyser
    `tools/g3_hangar_writeback.py`. No mitigation/default change landed.
  - s6606 (source attribution superseded s6607): the phase-gated source fingerprint ran immediately after the
    `present.storage` copy. Retail 4:3 fired its control at width 512/origin
    `0x790400` (nonzero 512, transitions 82, hash `42020AE708518CD0`). A
    clean ASPECT 16:9 arm fired at width 796/origin `0xA631B8`, exactly across
    the measured band 269..335 (first/last nonzero 269/334, nonzero 7722,
    transitions 2336, hash `02408104333BE1AE`). Together with the s6602
    owner-visible wide-only band, this selects H-source: the band is already
    in source pixels before presentation. The 21:9 retry reached only a
    pre-hangar 1024 phase and then returned to 640; its 512 control was all
    zero and is not evidence about the wide band. Retail completed a 131 s
    mission hold clean (0 VI stalls, 0 crash lines). No mitigation landed.
  - s6603: a phase-gated witness at RT64's actual `present.storage` framebuffer copy ran in retail 4:3, ASPECT 16:9, and ASPECT 21:9 from one Debug build. All arms held clean (0 crash lines, 0 VI stalls) and the witness fired in each positive-control phase. Retail used 512-wide rows with a 1024-byte stride; 16:9 used 796-wide rows with a 1592-byte stride; 21:9 used 1024-wide rows with a 2048-byte stride. Each source range covered the complete selected framebuffer. This rules out a malformed wide copy/flip stride as the band writer, but does not distinguish whether the band is already in source pixels or is introduced by viewport/RDP presentation. The local retail oracle cannot currently run: `tools/oracle` has no built core/plugin dylib. Next: phase-gated source-pixel fingerprint versus the owner-visible output in the same hangar phase.
  - s6602: same-route hangar captures completed for retail 4:3, ASPECT 16:9,
    and ASPECT 21:9 in one Debug build. All three phase controls fired and
    all arms held clean (0 crash lines, 0 VI stalls). Retail's 512-wide hangar
    frames have no interior roughness band; the 16:9 arm has a visible striped
    band at approximately x=269..334 of 796 pixels, and 21:9 has one at
    x=347..639 of 1024 pixels. Contact sheets are in
    `scratch/agent/s6602_hangar_capture/`. This selects a wide-only stale
    framebuffer/row-stride family over identical game geometry, but is not yet
    a writer attribution: the existing `[tricnt]`/`[rt64drawn]` logs report
    task ordinals and do not join commands to the dumped framebuffer. No guard
    or skip landed. Next: instrument the wide framebuffer write/flip stride
    and join its source range to the same hangar phase.
  - s6601 pivoted after three stalled `g1c-dd-phase2` iterations. The retained
    G3c camera-jerk analyzer was rerun with its positive control: synthetic
    smooth motion scored 0.152 sign alternation and injected alternating shake
    scored 1.000. Archived flight arms scored retail 0.395, FPS60 0.625, and
    FPS60+21:9 0.632, with the same camera-minus-craft heading offset (~1.566
    rad). This does not identify a new FPS60-owned shake defect and supports
    the existing retail-cadence closure. The next work unit is the parked
    hangar-artifact audit, with a same-phase framebuffer comparison as the
    discriminator.
  - **G1c draw-distance phase 2 is paused, not resolved.** The TLUT-return
    witness remains unevaluable because the last dd4 wrapper ended before its
    witness phase; do not repeat it under the old hypothesis ID without a new
    discriminating design.
  - s6598: static Mach-O mapping resolves `hudDisplayUpdateWorker+5532` to
    generated guest store `0x800496A8: sw v0,0(a0)`. The host instruction is
    `str w8,[x9,x10]`, with `x10 = ctx->r4 + 0x80000000`; the old source copy
    confirms `r4` is the return saved from `getTextureTlutEntry` at
    `0x8002333C` (`0x80049660`), while `r2` is the copied value. This rules
    out a host/runtime dereference and the already-witnessed `0x80049644/54`
    reads; H-other-generated-load/H-stale remains open. A persistent
    `tlut_return` witness was added beside the existing controls and the binary
    rebuilt. Retail completed route/130 s verification clean
    (`alive_at_end=1`, `vi_stalls30s=0`, `crashlines=0`); the concurrent dd4
    harness cycled retries without a durable summary before SIGKILL, so it
    supplies no dd4 witness verdict.
  - s6598: static Mach-O mapping resolves `hudDisplayUpdateWorker+5532` to
    generated guest store `0x800496A8: sw v0,0(a0)`. The host instruction is
    `str w8,[x9,x10]`, with `x10 = ctx->r4 + 0x80000000`; the old source copy
    confirms `r4` is the return saved from `getTextureTlutEntry` at
    `0x8002333C` (`0x80049660`), while `r2` is the copied value. This rules
    out a host/runtime dereference and the already-witnessed `0x80049644/54`
    reads; H-other-generated-load/H-stale remains open. A persistent
    `tlut_return` witness was added beside the existing controls and the binary
    rebuilt. Retail completed route/130 s verification clean
    (`alive_at_end=1`, `vi_stalls30s=0`, `crashlines=0`); the concurrent dd4
    harness cycled retries without a durable summary before SIGKILL, so it
    supplies no dd4 witness verdict.
  - s6594: the regenerated store watch covered `[0x951335A0,0x951335C0)` and
    fired its active player-record positive control (retail 392 rows; dd4 36
    rows) but saw zero target-range stores in both arms. Retail held clean;
    dd4 still reproduced phase-7 `hudDisplayUpdateWorker+5084` with pointer
    `0x951335B0`. Direct generated-store writer H-dd-writer is refuted; the
    pointer source/read path or a host/DMA writer remains open. `prev` is only
    last-observed because the existing hook runs after stores. No guard landed.
  - s6595: the generated read witness at `0x80049644/54` fired its same-worker
    positive control (retail 276 rows; dd4 258 rows) and the active player-record
    store control also fired (retail 400; dd4 251). The witnessed source address
    stayed `0x80137634` for the phase-7 worker, but the loaded material pointer
    differed (`0x80361808` retail vs `0x811DDDFC` dd4); neither arm read
    `0x951335B0` at these sites. dd4 still reached the known
    `hudDisplayUpdateWorker+5532` SIGBUS in one captured run. This selects a
    draw-distance-dependent source difference for this worker path but does not
    identify the crash dereference: the symbol/offset path or another generated
    load remains open. The independent retail oracle could not run because its
    `libmupen64plus.dylib` core/plugin was absent.
  - s6549-s6551: `ROGUESQ_DD_POOLX` > 1 at dd4 lvl1 lifts the 0x80130C4C
    2048-cell cap (2400 observed) but SIGSEGVs in `renderFlatMeshFaceGroup`
    (si_addr=0x380000004). px2/px3/px4 (cap 800/1200/1600) ALL fault at the
    same store, 0x80011524 `sw v0,4(a0)` with a0=0x80000000 (a NULL list
    node); px1 clean. Deterministic (5/5); BIGARENA pool divert does not change
    it (2/2), so not a heap-alloc failure and not a cap threshold (H-table
    refuted). `docs/DRAW-DISTANCE.md`'s "POOLX 1..2.5 fit" is therefore stale.
    Open hypotheses (NEXT.md): H-uninit (extra pool entries never linked),
    H-fixedarr (retail-sized parallel array read past its end), H-clamp
    (ddclamp window feeds an entry the game never built).
  - s6588: the s6586/87 "pc 0x800547bc" is the stale breadcrumb, not the fault. Real fault = streamTerrainGridCellsByDistance guest 0x80042D88/9C (and a later store site): record table *(0x80136DC0+4) is NULL, idx 1/3 *30 -> far 0x22/0x5e/0x1e/0x5a. 5/5 deterministic first bad cell ptr 0x803118E2 cellh 0x8001. Skip guard (ROGUESQ_TBLNULL_SKIP) only moves crash to a store 5/5. Leading (unverified) cause: CAPX=2 window overruns the real cell array. See PORTING-STATE s$N.
  - s6587: lvl7 dd4 CAPX=2 with an 8 MB DL pool (new opt-in ROGUESQ_SPILL_HI=1 + DLPOOLX_MB<=8): still 4/4 Bus error far=0x380000022; only 256 chunks allocated, so pool capacity is NOT the lever (H-pool refuted). Last cellprobe: tbl=0 window 64x65 on terr 93x96 -> suspect a 64-wide per-cell table (H-table64, single-source).
  - s6586: lvl7 dd4 with host-side clamp cap x2 (ROGUESQ_DD_CAPX=2, toggled 1x/2x in one run): admits 3200-3850-cell footprints but 5/5 attempts Bus error (far=0x380000022, pc 0x800547bc) in the 2x window; 0/10 without (s6585). Cap 700*px is the pool capacity, so lvl3/lvl7 beyond dd4 needs a bigger DL-chunk pool paired with CAPX. Harness mission regex for lvl7 is 62BD00 (reported allattempts-failed though flight ran).
  - s6585: dd4/dd6 bundle runs on lvl3/lvl7 (150 s, harness mission-detect said failed but flight ran; no 300 s hold): lvl3 cap-trim 1/9 at dd4, 0/10 at dd6; lvl7 3/6 at dd4, 2/5 at dd6 (cap-bound even at dd6). Single-source, small n. Next: lvl7 cap/px raise test with fixed pose (NEXT.md).
  - s6584: census over existing logs: with the dd4 bundle (px4) cap trimming is gone on lvl5/lvl10 (0/48, 0/6); lvl1/5/10 are extent-bound, dd>4 cannot add terrain there. Only lvl3 (78x78) and lvl7 (93x96) can still pay at dd5+ (pre-bundle logs only). Next: dd5/dd6 bundle runs on lvl3/lvl7 (NEXT.md).
  - s6578: ROGUESQ_DRAW_DISTANCE>1 now bundles the validated recipe (RAMTOP_MB=16, MALLOC_SPILL, DLPOOLX 4MB@3000, DD_POOLX=ceil(dd)<=5) in main.cpp; lvl1 dd4 bundle-only 130 s clean vs vetoed control Bus error si_addr=0x380000004 (single run/arm). The s6549-s6551 NULL node = DL-chunk pool exhaustion (not unknown corruption). s6579: "multiplier 3" at dd4 is the s6446 cap (apply_s6036_dd.py:7, dd>3 -> 3 unless ROGUESQ_DD_UNSAFE=1), so this "dd4" run was dd3 (code reading; confirm via log). True-dd4 300 s soaks queued: soak_queue/s6579_dd4_unsafe_lvl5/lvl10.sh.
  - s6548: `[ddclamp]` lvl1 terrain is 64x64 with a 2048-cell cap; dd4
    (~88x137) and dd6 (~101x174) footprints both clamp to the terrain, so dd6
    draws no more than dd4 on lvl1 (s6547: dd6 cheaper, 56 vs 109 ms/s).
  - Span-reject bypass is default-on for dd>1 (s6529). The dd>=4 missing
    ground was the per-cell span filter rejecting saturated (-128) cells
    (s6515-s6528; same-run SPANFORCE terrain 0.047 -> 0.209). The saturation
    writer is unnamed; the bypass is a workaround.
  - Bypass cap (`ROGUESQ_BYPASS_MAXCELLS`, default 120 for dd>1, s6540):
    cap120 buys no terrain over cap0 in either rotation order (two-source,
    s6543 + same-pose sheet s6546); only unlimited accept buys terrain (~3x
    tight) at ~1.7x wall. Owner recommendation pending: inf for dd>1 (cap0
    visibly drops ground).
  - Rare dd4-family gfx-thread SIGBUS (factor5_ucode, si_addr ~17 MB above
    rdram base; s6461 lvl10, s6466 dd8 lvl1 att1, s6529 lvl5): 0 crashes in
    the last 8 lvl5 dd4 runs, rate <=~1/9, not bypass-specific (s6534).
  - s6556: DL-chunk census (s6287) shows pushes == real pops per frame at px1 and px2 (counted pops = pops+pushes because push sites also load head). Yet px2 len falls ~600 chunks/frame (1553->0 in 24 begins ~5932-5956) with ~20 pops/frame: chunks leave the free list off-census (chain cut / unmatched consumer). Leak and bad-free refuted. Next: log the list cut point (NEXT.md). s6558: instrument ROGUESQ_CHUNKCUT built; run e3 partial (begin 41 cut only, uncontrolled); read g1_lvl1s6553_dd4_px2_e3/run.log past begin 5900, then run the _st selftest arm.
  - s6559: guest-store watch on head 0x801163B0 (ROGUESQ_HEADWATCH=1): over begins 5800-6240 at dd4 px2, 0 far pops, 0 mid pops, 0 null stores; only ~4 real pops/begin.
  - s6560: tracked-vs-actual head check (positive-controlled by SELFTEST poke): mismatch 0 / match 199 over begins 5800-6047, so the head is never rewritten outside the hooked guest-store path (MEM_W grow, fixup zeroing, host writes all refuted). New suspect: the 134+ OTHER head stores at guest pc 80007A44/AA0/AFC install a node off the old chain. Reclaim (kind 1) never runs. Next: walk lengths before/after those stores and read the function (NEXT.md).
  - s6561: the 134 OTHER head stores (pc 80007A44/AA0/AFC) are heapWalker (0x800079F0) splicing per-mode lists IN FRONT of the free list (tail->next=oldhead): old chain stays reachable (REACH>=0, lenNV~=lenOH+k) in all but 1-2/attempt. Not the loss writer (refutes H-A/H-C). Only REACH=-1 cases: oh=0, and pc 80018094 = the DL-chunk pool (re)initialiser (relinks 2909 chunks, head=base) at begin 6016-6067. Open: caller (ra) and trigger of that reinit vs the cache emptying ~6047; and supply (heapWalker returns) vs demand (pops) at px2.
  - s6562: pool reinit at pc 80018094 = `buildAndRegisterDefaultMaterial` called from `advanceVideoFrame` (0x800183F8) at flight-scene start (switch to 512x448 = the flight view, confirmed by framebuffer). It is legitimate and happens in px1 too. In 14/14 px2 runs the cache empties 70-130 begins after it; px1 (4/4) never. So the collapse is real in-flight demand>supply at px2 on a fresh 2909-chunk pool, not corruption. Open: per-begin demand after reinit at px2 vs px1.
  - s6563: px2 head pops/begin ~100 vs px1 ~50 (2x demand); splice (supply) rate identical in both arms (0.3-1.0/begin). H-D3 unsupported; H-D1/H-D2 (pool fixed at 2909) remain. Post-reinit returns unmeasured (OTHER-row cap ~120, DLPOOLLOG off). Next: scale reinit chunk count by px at 0x80018044 and rerun px2.
  - s6564: `ROGUESQ_DD_REINITX=k` (apply_s6564_reinitx.py) prepends extra chunks after the flight reinit. It faults with the SAME NULL-node signature at px1 (control c3) and px2 (r4, 6/6) ~105 log lines after `2909 -> 5853`, so the test is confounded (manipulation itself breaks; census blind >= 0x80800000). H-D2 undecided.
- **G3c (owner visual report): engineering closed, owner judgement pending.**
  (a) far-edge stair: no opt-in rougher than retail (s6449, s6544);
  (b) spike wedges: H-hw-draws, angrylion lights the same 16/79 wedges
  (s6454), `ROGUESQ_CULL_SPIKE` stays opt-in; (c) turning shake: retail 30 fps
  judder (s6455, s6458).
- **G1d (aspect): flight radar inset matches retail (s6610).** Extra width
  is real scene and the left HUD stays pinned. Open opt-in defect: 21:9
  level-select floor is sliced into horizontal scanlines in the outer
  thirds (s6611). s6612 named the triangles (op 0x0F, line 4); their T
  derivative does not change with width. s6613: S at x=0 does not
  change either, and it is not outside the 64 mask only at 21:9.
  s6614: the same triangles cover scanlines 180..250 in both outer
  thirds with no gap above 2 px, on either width. The tear is inside
  covered pixels. s6615: texel T at x=w/6 and x=5w/6 has the same
  row step on both widths (mean |ΔT| 4.32 vs 3.63) and no other
  textured triangle covers the sample. The sampler's T is not the
  tear. s6616: that sample's S is smaller on 21:9 (3.93 vs 2.69),
  shade luma agrees within 25% (2.66 vs 3.52), and the combiner is
  `(T0-0)*SHADE+0` on both widths. s6617: I4 |Δ| there is 51 vs 45,
  untex coverage is 1.0 on both, and the blender string matches. The
  4x row step is in the outer 1/12 of the width, not at x=w/6.
  s6618 measured those columns: filtered I4 and shade agree, and the
  pixel step does not, so the tear is after the combiner.
  s6619: that triangle is also the last primitive on every edge sample.
  A fill rect touches first and is overwritten. H-last is refuted.
  The tear is the blend memory term or the pixel pipe.
  The OS window remains 640x480, so wider modes letterbox.
- **G1e (frame rate): closed** (retail ~30 fps vs FPS60 ~59, s6452).

## Superseded conclusions — do not act on these
- s6628 closes H-swap/H-alias for the measured upload (single-source): believable because the earlier native witness preceded byteswapping and did not record the live mapping. Post-swap and exit preserve `0x9EC4`, and both sites use the identical host address; the zero appears between them.
- s6627 closes "the 1024x447 `copyToRAM` at `0x00B20000` writes the `0x0000` stripe" (it covers `0x00BB0020`). Believable because that span contains every stripe address and the same write's own image y=180 is rawBe 0. Refuted: the absolute sample is rawBe `0x9F4C` on all 935 covering writebacks, the call count does not move, and the upload still reads `0x0000`. The image-y zero is phys `0x00B7A020`.
- s6626 closes "fbChangesDrawDepth, its boolean mask, or its viewport manufactures the 21:9 depth stripe from a clear or smooth guest field" (H-upload). Believable because the GPU image goes from a read-back clear of 1.0 to the stripe inside copyFromChanges, and a discard mask cannot paint 0 by itself. Refuted: the guest words already are the stripe and match the GPU on 142/142 samples (mae 0), shader endian, site state.cpp:2604.
- s6625 "after the zero head, x=16 is a smooth 0.964..0.961 ramp and x=1007 stays 1.0". Believable because x=16 does contain 0.96408 and x=1007 has more exact-1 samples (31 vs 13). Both columns actually interleave ~0.96 and 1.0. The stable part is the exact-0 head.
- s6625 closes "the 21:9 zeros are unwritten depth tiles (create-clear never applied, so a readback of 0)". Believable because Metal does not clear a D32 texture at creation, and a different 1024x480 target's first sample in the same run was exact 0. Refuted on the floor texture: clearDepthTarget read back 1.0 on both columns, and the following copyFromChanges replaced those pixels.
- s6623 "shader-to-attachment MAE 37 at 21:9 means the first wrong stage is an attachment write after a sane shader" (s6624: the same shader color is stored at 16:9, where depth is 1.0 and LESS passes, and rejected at 21:9, where a nearer striped depth already occupies the columns). Believable because the UAV record is written before the depth test and matched the 16:9 attachment exactly.
- s6614 lead "dtdx*x at the outer third diverges on 21:9" (s6615: dtdx shrinks by about 796/1024 and the texel matches to about 0.05). Believable because the sample x grows with the framebuffer and s6613 only cancelled that product at x=0.
- s6612 "21:9 S at the left edge walks off the 64-wide mask while 16:9 stays inside" (s6613: 0/16 pairs do that; S at x=0 matches). Believable because the x span and dsdx scale with width. x_major moves the other way and the product cancels.
- s6610 ring-only "second=fbw-512 fixes the 16:9 radar" (the ring reached the retail inset, but the wedge stayed at 769..792 with 0 pixels inside the ring). Believable because s6609's red-ring edge equalled retail+second. The disc is a separate pre-shift `ROGUESQ_SHIFT_REGION` writer; shift must be A, not RA.
- s6602 "wide-only bottom garbage selects a stale/stride renderer family"
  (s6607-s6608: diagnostic height exceeded the VI source; corrected bounded
  dumps and OS window captures lack the tail). Believable because raw guest
  PPMs looked like window captures. This does not close native geometry issues.
- s6606 "the wide hangar band is already in source pixels" (s6607: source
  fingerprint checks columns 269..335 in 336 rows; visible bottom garbage is
  in a raw 448-row dump beyond that copy). Believable because the raw PPM
  looked like window output and nonzero/transition counts appeared to confirm
  it. The PPM header explicitly says rdram-readback-not-window; its fixed
  height is not the actual VI source height. Actual window fidelity remains
  open; the source-versus-presentation split was not closed.
- (s6579) "dd4 bundle-only / dd4 holds without ROGUESQ_DD_UNSAFE ran at dd4" (superseded: they ran dd3). Believable because the knob was set to 4 and nothing warned except a "multiplier 3" log line, which looked like a display quirk; the s6446 cap in apply_s6036_dd.py:7 clamps silently otherwise.
- s6576 "lvl1 ddclamp area saturates at level extent by dd6, not an engine table" (s6577: at dd6 the cell cap trims the window below the extent in ~55% of samples on lvl1/5/10; the earlier 4096 maximum was a single sample).
- s6574 "dd12 holds clean": believable because the env var was 12 and the run was clean; overturned s6575 - the multiplier is clamped to 8, so it was dd8. Raising the clamp is not the next step; the 64-wide terrain table saturates first (single-source, one run's log).
- (s6559, superseded s6560) "The ~600 chunk/frame loss comes from a head write the store hook cannot see (MEM_W grow hooks, fixup force-zero)." Believable because the hook showed no far/mid/null stores yet the list shrank. Refuted: tracked==actual head 199/199 with a firing positive control; the off-chain stores are in the hooked path, mislabelled 'splice'.

One line each: claim (superseded by; why it was believable).

- s6555/s6554 "chunks consumed by a runaway consumer / free path leaks" (s6556: pops==pushes per frame; chunks vanish without a pop).
- s6554 "runaway consumer in traverseSceneGraphRecursive" (s6555: sibling loop visits 8-17 nodes/frame, 0 revisits at the fault frames; the fault stack merely passes through it).

- s6553 "dd>1 NULL node = DL-chunk supply shortfall" (s6554: a 12x larger arena is consumed in ~24 frames; chunk-empty is the symptom of a runaway scene-graph walk).
- s6550 "split POOLX=3 vs 4 for a threshold" (s6551: px2-4 all fault; the cap scaled with POOLX).
- s6545 "cap0 vs inf undecided" / s6544 "pinned pose" sheet (s6546; s6544 pinned only the stair-metric window, not the camera).
- s6539 cap ordering 0<40<120<inf for terrain (s6541 retracted as run-to-run scatter; 4-10 frames/arm looked monotonic).
- s6542 cap0 dearer than cap120 (s6543: post-inf hysteresis; rotation order confounded it).
- s6540 "default path differs from explicit cap120" (s6541 H-noise; single runs differed).
- s6537 "a cell cap keeps most of the gain cheaply" (s6543: gain is all-or-nothing; cap arms were cross-run).
- s6525 dd4-rejected cells have sentinel recs -2 (s6526 raw dump: normal recs; the joined log read unpopulated bytes).
- s6520 span bytes 0x80 "never written" (s6521: clamp/clear values; 0x80 resembled an init fill).
- s6516 dd4 EMPTY reads another table (s6517: sampling-phase confound; dump rows covered different key ranges).
- s6509 DC0 writes outside a 24-byte span table (s6510/s6511: it is a 64x64 grid; only 24 bytes were dumped).
- s6502 thread-local / s6500-s6505 cumulative writer joins (s6505/s6506: cross-function shared counter; guest IDs matched).
- s6495 all-127 table = rasterizer produced no rows (s6514; snapshot is taken after the filter's own 0x7F stamp).
- s6491 cell list never empty (s6492: read stale r16; head is v0).
- s6488/s6489 low-vs-high-ground tri split (suspect: tool hardcodes non-flight fbs).
- s6472 fixed 64x64 grid tables limit dd3 (s6473 offline: window is post-clamp, kept<cap).
- s6470/s6471 "game submits shorter DL at dd3" break point (explained by the span-filter chain; pinned vs unpinned recipes disagreed).
- s6466 dd8 att1 "route failure" (real SIGBUS; soak summary alone mislabelled it).
- s6446: s6420 "dd3+fix lvl1/5/10 clean" holds were dd2 (run.log said `capped to 2`).
- s6414 durable constraint "dd>2 exhausts the DL chunk supply" ([dlpool] identical across arms; H-chunk refuted).
- s6407 ~5% HUD-absent at dd3/dd4 (s6409: scorer counted menu frames).
- s6399 aspect side-edge lean (s6401 withdrawn: outer-column scalars are noise).
- s6393/s6391 fixed wide-flight origin gate (origin is allocator-dependent).
- s6380 zero-FD57 interpretation (s6380long route audit: retry arm took a different route).
- s6292 FPS60 owns the turning shake (s6455: VI wall-stamp artifact).
- s6426 menu garble = wide-FB stride defect (s6427: 640-wide cam scaling).
- s6434 hangar only ~340/448 rows (s6438: 436-448 lit; dumps misread).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Current pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`.
- dd>2 needs `ROGUESQ_DD_UNSAFE=1` (clamp 8); confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Wide soaks need
  `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_PIN_POSITION=1`; dump
  ordinal is not a phase key, join dumps to `[vi]`/origin
  (`tools/g1c_fbdump_join.py`).
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` /
  `crashlines`, never rc. A queued repeat soak is not a work unit.
- Per-frame cost meter: `[g1b]` lines in run.log (sd_wall, tasks/s).
- Full dd knob/instrument table: PROJECT-OVERVIEW "G1c draw-distance knob and
  recipe reference"; owner guide `docs/DRAW-DISTANCE.md`.

## G1 mission coverage

Playable levels are 0..18 (`NUM_LEVELS=0x13`; 19 and 20 are sentinels). Levels
1–9 and 11–18 have route/hold coverage; levels 10 and 15 need the planet
unlock or its long retail intro. Verification still needs framebuffer evidence
of terrain, craft, and HUD plus a forced-hit objective response. Mission wins,
autopilot aim, and mission-to-mission progression are owner playtest scope.

## Durable constraints

- Retail defaults remain unchanged. Opt-ins include draw distance, aspect,
  FPS60, spike culling, and audio control. Do not make an opt-in default from
  a single-source result.
- `ROGUESQ_DRAW_DISTANCE`: dd2 qualified lvl1/5/10; dd3/dd4/dd6 300 s holds
  clean lvl1/5/10 under DD_UNSAFE; dd8 lvl1/5 clean. Crash-free holds do not
  mean "renders correctly" (s6468: dd>=4 ground missing before the bypass).
  No mitigation is acceptable without naming the writer and establishing value
  legitimacy; dd>1 fixes live in `tools/apply_s6*.py` and fixup scripts.
- Wide rendering uses runtime RAM-top handling and a larger reported memory
  arm; default remains 4:3/retail. Native hangar artifacts remain parked.
- The title plume is parked after clean boots. Reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams.
  Ground truth must precede new instrumentation; every null needs a positive
  control and two independent lines of evidence before changing this file.
- Generated diagnostics must survive regeneration through fixup tooling.
  Never reset, clean, checkout, or update submodules. If editing `lib/`, run
  `./submodule-patches/export.sh` and commit the refreshed patches.

## Next steps (single monotonic backlog)
1. **(s6628) Attribute the write between copyNativeToRAM and depth storage.**
   Same pointer, native/post-swap/exit rawBe `0x9EC4`, then pre-store zero.
   Build the complete writer discriminator in one binary: generated stores
   (including unaligned/64-bit/FP), host bulk-copy/zero/DMA paths, and the
   existing A/B witnesses on the same event sequence. A record must include
   exact intersecting physical range, before/after bytes, guest PC or host
   caller, and operation length/source. Positive-control both writer classes
   on a reserved scratch word, then arm only the real target interval.
   Guest writer selects H-guest-store; host copy/zero selects H-host-write;
   neither with a reproduced A/B transition selects incomplete coverage,
   never "no writer". No guard or rendering change before naming the writer
   and deciding whether its range is legitimate. See NEXT.md.

### Archived historical next-step entries
-1. **(s6602) Attribute the wide-only hangar bands to the framebuffer stride path.**
  Build one instrumented binary and rerun the three same-phase arms only if
  needed for the new witness. Log, per hangar VI phase, the selected width,
  VI origin, source framebuffer address, row stride, and the copy/flip source
  range; include a positive control from the retail 512-wide arm. Discriminator:
  a source range or row stride that lands on the measured 16:9/21:9 band selects
  H-stride; matching stride with a fixed screen-space scissor selects
  H-viewport/H-RDP; identical source geometry and pixels across arms selects
  H-game. Do not add a cull, skip, or default change until the writer is named.
-1. **(s6601) Audit the parked hangar artifacts under `g3-hangar-artifacts`.**
  Build/run one same-phase capture table for retail 4:3, ASPECT 16:9, and
  ASPECT 21:9 at the hangar origin, joining the framebuffer dumps to the VI
  origin and width. Competing hypotheses are H-viewport (wrong scissor or
  viewport exposes the rim band), H-stride (wide framebuffer row/flip stride
  leaves stale right-edge data), H-rdp (RT64/RDP edge treatment produces the
  holo spikes), and H-game (the submitted hangar geometry itself contains the
  artifact). Discriminator: the artifact's first/last changed pixel bounds
  and command-range attribution in the same phase; width-proportional stale
  bands select H-stride, fixed screen-space clipping selects H-viewport or
  H-rdp, and identical geometry in the retail control selects H-game. Keep
  default retail behavior unchanged and produce an owner-viewable contact
  sheet before any mitigation.
-1. **(s6598) Read the mapped `getTextureTlutEntry` return before the `0x800496A8` store.** The new `tlut_return` witness is persistent but the dd4 run did not finish. Run one bounded dd4 route with `ROGUESQ_HUDPTRWATCH=1` and inspect `[hudptrr] stage=tlut_return` against the known controls. Hypotheses: H-return-wild (the function returns `0x951335B0`), H-between-store (the return is valid but another generated store changes `r4`), H-host-alias (valid guest state is changed by host address conversion), H-stale (the return is an old object). Discriminator: return value equal to `0x951335B0` selects the return writer; a valid return followed by the mapped store selects an intervening generated write; a host-only mismatch selects conversion; retail/dd4-valid returns with divergent lifetime select stale state. Do not add a guard.
-1. **(s6581) True dd4 (DD_UNSAFE=1, bundle) is clean on lvl1/5/10: 300 s holds each, 0 stall, 0 crashlines, log `multiplier 4` (one run per level; the rare dd4 gfx SIGBUS, rate <=~1/9, is not excluded). (s6582 DONE: cap lifted, dd4 allowed without UNSAFE, 150 s lvl1 clean.) Remaining: a valid same-pose dd1-vs-dd4 sheet (log g_rs64_dd_blk per fb dump; s6582 sheet invalid). Old text: lift the dd>3 cap in apply_s6036_dd.py:7 (cap to 4 without DD_UNSAFE) -> regen/rebuild, then dd1-vs-dd4 same-pose contact sheet for the owner. Default stays retail.** (s6583 DONE: valid same-pose dd1 vs dd4 sheet at docs/owner_sheet_s6583.png, [fbdump] now carries dd= tag; dd4 shows only slightly more far terrain at lvl1 pose 3 — extent-bound per s6576; sheet sent to owner for judging.)
- [s6576, do first] lvl1 footprint saturates at the level's own terrain extent by dd6 (post area 4096=64x64; s6575's 'table too small' was mis-framed - tw/th are level dims). Census tw/th/cap per level (1,5,10 + others) via ROGUESQ_DD_LOG; if every level is extent-bound, dd range is done at ~6: bundle far/pool/cap behind the single knob and run 300 s holds on lvl 1,5,10 at dd6 + contact sheet for owner. See NEXT.md.
- [s6567] dd6 px2/px3 with RAMTOP_MB=16 all die with Bus error si_addr=0x38000000x (A/B/C identical): pool size is NOT the px2 limit; the chunk list also still collapses. Next: symbolize the crash pc / backtrace, name the writer of the 0x80000000-offset access (see NEXT.md).

0. **(s6572 SOLVED the px3+spill hud fault; supersedes s6570/s6571 "zeroed/empty record" framing.) ROOT CAUSE = `TO_PTR` in lib/N64ModernRuntime/ultramodern/include/ultramodern/ultra64.h masked guest addresses to 8 MB (`& 0x7FFFFF`, s5240), so host osCreateMesgQueue/osSendMesg/osRecvMesg on a queue above 8 MB (record 0x80954F60 + 0x1D0 = 0x80955130, which exists only with RAMTOP_MB=16 + spill) read/wrote the ALIASED low-RAM copy 0x80155130 while generated guest code (MEM_W, unmasked) saw the real address, still all-zero. Two lines of evidence: (a) ROGUESQ_RECV_TRACE `[createmq] mq=0x80955130 msg=0x80955150 count=66` fired while a 16-byte poller watch on 0x955138..0x955147 saw 0 writes over a whole run (same-arm positive control: the record head 0x954F60 showed writes); (b) mask widened to 0x1FFFFFF -> px3+spill hold `mission_verified_130s`, 0 CRASH, svcrecv now returns real slots (validCount=31) vs 8/8 faults before. 1 clean run so far -> NEXT: 3-run px3/px4 confirm, then re-measure the dd3/dd4 limits. Any other host-side `& 0x7FFFFF` on guest pointers (ultramodern/librecomp, src/main) is the same bug class: audit them.** 
0. **(s6569) px3 NULL = guest heap0 exhaustion** (malloc 0x192CC -> NULL, 5.4 MB live). `ROGUESQ_MALLOC_SPILL=1` (+RAMTOP_MB=16) serves NULLs from 0x80800000-0x80C00000; px1+spill clean, px3+spill gets past the pool but faults NULL+0x14 in hudDisplayUpdateWorker+3332. NEXT: name that NULL's writer (what hud pointer is 0 at px3?). Single-run each.
1. **(s6567 SOLVED the px1 arena-chunk fault: ROOT CAUSE = `rs64_ram_top` (default 0x80800000, set from osMemSize in recomp.cpp:565) is the limit of 442 generated `RS64_RAM_TOP` pointer guards in funcs_3.c plus the RT64 DL-read masks (rt64_render_context.cpp), so every arena chunk at 0x80F… was rejected as a wild pointer. `ROGUESQ_RAMTOP_MB=16` (new, widens only the guard limit, not osMemSize) makes head-prepend +384 at px1 clean (0 crashes, alive 131 s; ASC order and prior 4/4 runs without it fault) -- single-source until repeated.)** NEXT: with RAMTOP_MB=16 retest REINITX=2 at px2 and px3 (H-D2: does a scaled DL-chunk pool stop the px2 chunk collapse?), then fold RAMTOP_MB=16 into the ROGUESQ_DRAW_DISTANCE bundle for dd>=3. (g1c-dd-phase2, top; NEXT.md). Older: s6555 REFUTED traverseSceneGraphRecursive as the runaway. Chunk drain is inside per-node submit work or a failed chunk return (reclaim=0 everywhere; px1 len rises, px2 leaks ~5/frame then collapses).
2. **Lift the 0x80130C4C 2048-cell cap with its pool** once item 1 is fixed;
   qualify on lvl1, then on a level with terrain larger than 64x64 (s6548).
3. **Owner decision: dd>1 bypass cap.** cap120 is pointless; choose cap0
   (cheap, drops ground) or inf (terrain, ~1.7x wall). Sheets
   `docs/owner_sheet_s6546.png` (same-pose), `docs/owner_sheet_s6540_cap.png`
   (not pose-matched).
4. **Name the span-grid saturation writer** (edge loop at 0x80042820/0x800426D8
   `sb trunc(clamp(f0,f12,f10))`, s6521) and fix at the writer to retire the
   bypass workaround; two-arm qualify.
5. **dd4/dd8 gfx-thread SIGBUS (rare).** On recurrence: backtrace, map si_addr
   to a guest address, test H-16MB (keep gfx-read data below 0x81000000).
6. **dd8 hangar scanline garbage** (s6468, unresolved, single-source).
7. **G3c owner judgement**: edge sheet `docs/owner_sheet_s6449_edge.png`,
   `docs/owner_sheet_s6439.png`; ask whether `ROGUESQ_CULL_SPIKE` should be
   default-on.
8. **G1d owner sheets: aspect `docs/owner_sheet_s6609_aspect.png`, radar
   `docs/owner_sheet_s6610_radar.png`.** Follow-up is the level-select tear
   (next-steps 1), not another radar capture.
9. **G1 coverage (c)+(d)**: framebuffer terrain/craft/HUD evidence and a
   forced-hit objective response for every level 0..18.
10. **Ladder (ITERATION.md 3c)**: after the above, G3 render fidelity
    (hangar artifacts, in-flight diffs vs retail frames). G4 and aim/steer stay
    parked; G2, G5 closed.

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6378–6551. Durable
background, closed threads, and the archived backlogs are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`.

The s6596-s6597 retries were checkpoint close-outs only: they did not rerun the
s6595 experiment or add a conclusion. The s6599 retry was also a checkpoint
close-out: the s6598 retail arm completed, while the dd4 wrapper produced no
witness-phase summary before termination. The saved s6595/s6598 artifacts
remain the active evidence for the HUD SIGBUS mapping work.

## Update s6568
- s6567 conclusion 'pool size not px2 limit' SUPERSEDED: recipe lacked ROGUESQ_DLPOOLX=1. px2 with DLPOOLX=1 DLPOOLX_MB=4 DLPOOLX_AT=3000 RAMTOP_MB=16 holds clean (1/1 90s; control 3/3 crash). px3 5/5 crashes in allocAndInitDoublyLinkedNodePool12 (NULL+2): next binding limit is that node-pool allocator, not the DL arena.

- s6571 (SUPERSEDED by s6572: queue was never zero-written, the host aliased it to 0x80155130 via the 8 MB TO_PTR mask).  Tool note s6572: ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FL_ZERO_ADDR=<phys hex, now up to 32 MB> ROGUESQ_FL_ZERO_ALWAYS=1 is a no-lldb 16-byte write watch with function attribution (lldb launch hangs in dyld under this harness).

- s6573: px3+spill dd6 confirmed 4/4 clean after TO_PTR mask widening (s6572); px3 fault CLOSED. Next: px4/dd=8 (see NEXT.md).
- s6574: px4/dd8 (2/2) lvl1 130 s clean with spill recipe. The px5 "dd12" run was really dd8 (s6575: clamp [0.25,8] under DD_UNSAFE, apply_s6036_dd.py:7; run.log prints multiplier 8) - no dd12 evidence exists.

- s6579/6580: true dd4 (DD_UNSAFE=1) lvl5 300 s clean; lvl10 s6579 failure was MISSION_RE false-nomission (needs MISSION_RE='6A2900|644D00'); s6580 lvl10 (MISSION_RE='6A2900|644D00') and lvl1 true-dd4 300 s holds PASS (s6581).

- s6589: lvl7 dd4 CAPX=2 fault: window (x0=0,w=64,z0=31,d=65) is inside the 93x96 grid, so not an overrun; desc 0x80136DC0 words +0/+4 are NULL. Next: is desc+4 ever filled in retail on lvl7 (NEXT.md).
- s6591: lvl7 dd4 desc+0/+4 NULL root-caused: streamTerrainGridCellsByDistance slot-clear (pc 80043020) indexes a 64x64-word slot array at 0x80132DC0 that ends at the descriptor 0x80136DC0; window d=65 rows overran it. Fixed by capping the dd clamp window at 64x64 (apply_s6037_ddclamp.py). Supersedes s6586-s6590 (overrun/unbuilt/load-race hypotheses). New open: phase-7 SIGBUS in hudDisplayUpdateWorker (wild ptr 0x951335B0) on lvl7 dd4 after the fix. ROGUESQ_DESCWATCH=1 is the store-watch for 0x80136DC0..+0x40.
- s6593: one-setting removal bisect: retail and the full dd4 bundle reached the route cleanly, while removing any one of SPILL_HI, RAMTOP_MB=20, DLPOOLX_MB=8, DD_CAPX=2, or DD_UNSAFE reproduced the same phase-7 SIGBUS at hudDisplayUpdateWorker+5084 with guest pointer 0x951335B0 (5/5 attempts per arm; all arms reached mission before dying). This rules out H-retail and any single bundle setting as sufficient; H-dd-interaction remains. No guard is justified: the writer and legitimacy of 0x951335B0 are still unknown.
