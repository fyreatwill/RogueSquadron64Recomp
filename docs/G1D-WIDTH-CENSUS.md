# s6848 G1d wide-width idiom census (tools/g1d_wcensus.py + manual read)
Sources: every load of the screen width global 0x8011A838 (19, matches the s6847 NEXT.md count) and every screen-struct
`lw p,0(x); lw w,0x10(p)` / +0x18 double-deref (35; heuristic, includes false positives). Forward taint 48 insns.
Extra sweep: every `andi 0x3FF; sll 14` (10-bit integer coord pack, 10 sites) and every `andi 0xFFF` (50 sites, listed).
Positive control: the census re-finds the s6846 epsilon site 0x800C1A9C and the s6694 scissor sites 0x80017370/0x80017814.

| site(s) | function | idiom | W=1024 | class |
|---|---|---|---|---|
| 80009124/80009614/8000985C/80017470 | SetColorImage builders | (W-1)&0xFFF in a 10-bit width field | 1023 fits | (c) safe |
| 8000A194/8000A2F0/8000A5CC | emitColorFillRect (setScreenColorOverlay) | (W&0x3FF)<<14 G_FILLRECT lr.x | wraps to 0 | **(b) FLIPS -> s6848 fix** |
| 8000A4B8 | emitColorFillRect | x1 < W (right band gate) | integer, scales | (c) |
| 8000A6D0 | disableScreenColorOverlay / init | W-1, H-1 stored as shorts | fits | (c) |
| 8001578C | drawTextGlyphRect | x0 < W<<2 (int16) | 4096 fits int16 | (c) |
| 800157FC | drawTextGlyphRect | lr = min(lr, W*4) & 0xFFF | wraps to 0 | (b) already handled downstream (s6844/s6845 rs64_g1d_rect_wrap, texrects incl. ul.x 0) |
| 8001731C/800177B4 | setupCameraMatrices scissor | (int)(W*4)&0xFFF | wraps | (b) fixed s6694 |
| 80016CA0/8001DE64/8001E134 | projection/aspect | (double)W in fp ratio | scales | (c) |
| 8001BC60/8001BC80 | fb size | W*H*bpp | scales | (c) (s6689 heap) |
| 80017458 | setupCameraMatrices | no sink | - | (c) |
| 800C1A88 | initHudStruct wipe | ox <= -W/2 + 1 epsilon | flips | (a) fixed s6846 |
| 800C19E4/800C1A2C | initHudStruct wipe | ox = W/2 - W*f | scales | (c) |
| 800FD6B4..800FE330 (5) | HUD layout | W/2*scale - k stored floats | layout (s6156 anchor family) | (c) |
| 8005BAEC..8005BBF8 (4) | rect clipper | clamp x to [0, W-1] | scales | (c) |
| 80057AAC, 80071390..800718BC (19), 80057570, 80059620, 80071F04 | other structs (+0x10 is not width: flags &0x200, pointer walk) | - | - | false positive |
Other 0x3FF<<14 packs (80009374, 80009ABC, 8000A470, 8000A61C, 800240C4): coordinates from args/x0 halfwords, not W.
Verdict: one NEW flipping site (emitColorFillRect, 3 packs); the class is otherwise closed (every other W read scales or is
already fixed). Limitation: values passed through memory beyond the 48-insn window are not followed.

## Runtime witness (s6848, same build, 21:9, two run pairs)
emitColorFillRect only runs when setScreenColorOverlay armed it (mission-end transition step 6; never on the
boot -> hangar -> lvl1 -> abort route: tools/g1d_fillscan.py on the s6841 p21/p43 streams shows 0 fills with lr.x == W).
ROGUESQ_S6848_FORCE_OVL=4400:4700 arms it in flight (window 128,64-896,384, red F801). tools/g1d_fillscan.py on the
RDP bins, per colour image, ~75 frames each:

| band | off (ROGUESQ_G1D_OVL_WRAP=0) | on |
|---|---|---|
| top (0,0)-(W,64) | lr.x 0.00 ZERO-W | lr.x 1023.00 |
| bottom (0,384)-(W,448) | lr.x 0.00 ZERO-W | lr.x 1023.00 |
| left (0,64)-(128,384) (positive control) | 128.00 | 128.00 |
| right (896,64)-(W,384) | 1023.75 (s6844 rect_wrap, ul.x > 0) | 1023.00 |

Both run pairs (o21*, w21*) give identical tables. Window caps do not discriminate in flight: the fills are emitted before
the 3D scene, which overdraws them (the red right band shows only through terrain gaps). The real mission-end overlay is
reached only after a mission win (owner playtest), so the on-screen effect of the fix is not yet observed.
