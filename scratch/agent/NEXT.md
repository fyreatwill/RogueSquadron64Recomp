# NEXT: G1d 21:9 per-mission RDP sweep for wrapped / zero-width rects (runtime check of the closed width census)
HYPOTHESIS-ID: g1d-21x9-mission-sweep

State (s6849): the static width-idiom census is closed (docs/G1D-WIDTH-CENSUS.md, 0 new flippers through memory).
Static evidence only; the 21:9 runtime has been exercised on boot -> hangar -> lvl1 -> abort (s6841-s6848) and menus.

Hypotheses: H-clean (no mission at 21:9 emits a fill/texrect with lr.x < ul.x, lr.x field 0 with W-wide intent, or a
rect_wrap clamp outside the known wipe) vs H-site (some mission-only path, e.g. a cockpit/radar/overlay variant the
static taint missed because W reaches it through a pointer chain or a different global, does).
Method (one build, current binary; no code change needed):
1. Positive control in the same run set: ROGUESQ_S6848_FORCE_OVL=4400:4700 with ROGUESQ_G1D_OVL_WRAP=0 on lvl1 must show
   ZERO-W fills in tools/g1d_fillscan.py (s6848 recipe scratch/s6848/port_ovl.sh).
2. For levels 1..19 via the forced level-select route (G1 recipes) at ROGUESQ_ASPECT=21:9, RS64_RDP_BIN_PORT capped
   (RS64_RDP_BIN_PORT_MAX_MB), ~60 s of flight each; queue as soaks (scratch/agent/soak_queue/) in pairs.
3. Offline: g1d_fillscan.py + a texrect pass (ul.x > lr.x, lr.x in {0..3} with ul.x 0, or any rect_wrap counter line)
   per level. Any hit -> name the emitting function (PC from the DL builder), fix with a W<=640 bit-identical apply.
Expected: 0 hits on all levels with the control firing -> G1d runtime-closed; hits -> fixes.
