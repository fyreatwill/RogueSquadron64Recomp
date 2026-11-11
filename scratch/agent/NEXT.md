# NEXT: G3 presentation geometry at 4:3 retail: is the off-centre 553x480 pillarbox what the VI asks for?
HYPOTHESIS-ID: g3-flight-fidelity
Why: s7122 found pixel fidelity H-equal in L1 flight. On the way it found that the default 640x512 window (32 pt title bar) shows the
game's 512x448 colour image at x 21..574 (553 px wide, left margin 21, right 66). That is neither a 4:3 fill nor centred. A retail TV fills
4:3 unless VI H_START/X_SCALE say otherwise.
Hypotheses:
  H-retail : the game's VI regs (H_START, X_SCALE, WIDTH, V_START, Y_SCALE) place the active picture this way on a real NTSC line
             (H_START standard 0x006C..0x02EC = 640 px). Then retail is also pillarboxed/off-centre and nothing is ours.
  H-rt64   : the VI regs ask for a (near) full 640 line, and RT64's VI->output mapping shrinks or shifts it.
  H-fit    : our window/aspect code (main.cpp WINDOW_FIT, ROGUESQ_ASPECT default path, s6885 WIDE_EARLY) offsets it at 4:3.
Discriminator, one run: log the VI registers per VI (ultramodern VI state, or osViSetMode's mode table) during L1 flight at default 4:3.
Compute the expected active rectangle on a 640x480 NTSC raster, and compare it with the presented rect measured by g5b_capture (rect search
as in tools/s7122_fidelity.py). Second line: run angrylion's VI stage (full VI filter, n64video_update_screen) on one replayed swap and
measure where the picture lands in its output. Check git log / grep "x 21" or "pillar" in PORTING-STATE first (G1f WINDOW_FIT, s6142).
Outcomes: VI rect == presented -> H-retail (report, offer an opt-in fill). VI full but presented shrunk -> H-rt64/H-fit; then toggle
WINDOW_FIT/ASPECT in the same run to split them, fix, and give the owner a before/after sheet.
Also open: texture fidelity on texture-streaming levels (L6) needs ROGUESQ_G5B_FRAME_EVERY=1 over a short FROM window, so each swap has its own snapshot.
