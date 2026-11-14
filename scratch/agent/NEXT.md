# NEXT (s7335): idiom-class audit — consumers of the frame-buffer layout bound (fb / FIFO tail base)
HYPOTHESIS-ID: fb-layout-bound-audit
Context: s7334 closed item 24: the persistent arena ends at hi-0x10, hi = output of the fb-layout routine 0x80000DD4 (sp+0x48 at caller
0x80001430 in 0x80001354) or the global 0x801163E4; above it live the scene's framebuffers + gfx RDP FIFO (boot tail at 0x80B69FF0, i.e.
above 8 MB because RAMTOP is 24 MB since s7326). Question: does every guest consumer of that bound agree with the 24 MB RAMTOP / spill
arena 0x81000000-0x81800000 layout, or does any assume the tail ends at osMemSize (8 MB) or sits below 0x80800000?
Hypotheses: H-clean (all readers derive from the same bound, no fixed 8 MB assumption), H-cap (a reader clamps or masks to 8 MB / 24-bit,
latent like class D), H-overlap (fb tail at some dd/aspect width reaches 0x81000000 = the spill arena base).
Method (static first, one tool): tools/s7335_fb_bound_census.py: disassemble 0x80000DD4 and list every load of 0x801163E4 / stores of its
output across funcs_*.c asm comments (grep '0x63E4(' with lui 0x8011, plus the sp+0x48 out pointer passers), classify each site
(derives-from-bound / fixed constant / mask). Exit 1 on unclassified. Then ONE runtime check only if H-overlap is possible: log
max(fb tail end) per scene on the dd8 21:9 abort route (scratch/s7334/run2.zsh recipe + a new [s7335] line at the 0x80001430 call: a3 and
the 0x80000DD4 args) vs 0x81000000. Positive control: the boot hi must equal 0x80B6A000 (s7334 sentinel B69FF0+0x10).
Outcomes: all derive -> H-clean, close; a constant 0x80800000/0x00800000 or 0xFFFFFF mask on the bound -> H-cap, classify reachability;
tail end >= 0x81000000 at any scene -> H-overlap, a real defect: fix the spill base or the bound.
