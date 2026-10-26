# G1d: which draw (triangle) samples up_167 / produces the garbage region
HYPOTHESIS-ID: g1d-widescreen
s6239: maskt==5 texrect logger fired 0 times (control: 20 any-tile lines) -> no texrect samples up_167. Next: add the same tile logger on the triangle path (tile, maskt, lrt, screen bbox), keyed to the corrupt screen region; run s6238_run.sh wide; if maskt==5 triangles exist, check their t range vs 21 loaded rows (H-sample-stale); if none, up_167 is loaded but unused and the garbage is another draw (key by bbox).
