# G1d: is the 64x32 span of the up_167 texrect the game's, or widened by RT64?
HYPOTHESIS-ID: g1d-widescreen
s6236: up_167 = 672-byte f4/s2 load at tmem 0 + stale TMEM tail (see PORTING-STATE s6236). Hypotheses: H-game-span (game SETTILESIZE really covers 64x32 -> retail samples stale TMEM too; garbage is retail-faithful and only visible because of layout), H-rt64-span (RT64 derives width/height/line from the widened fb width, so it samples beyond the 672 valid bytes), H-order (draw happens before its load completes).
Discriminator: in the draw-time log (framebuffer_renderer.cpp s6234 hook) also print tile fmt/siz/line/tmem and uls/ult/lrs/lrt for hash==98bb35b7e7c80445, and run at the 4:3 control (no ROGUESQ_FB_WIDTH) where the same texture should have span <= 672 B (21x16 16bpp-ish). If 4:3 span is 672 B and wide span is 4096 B -> H-rt64-span: fix the span derivation. If both 4096 -> H-game-span.
Run: zsh scratch/agent/s6235_run.sh 900 log, plus a second arm with W0=512.
