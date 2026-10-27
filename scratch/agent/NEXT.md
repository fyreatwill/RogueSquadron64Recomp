# NEXT: per-node terrain submit counters, dd2 vs dd3 (H-submit)
HYPOTHESIS-ID: g1c-dd8-limit
Established (s6473): window/grid tables are not the limiter (post-clamp w,d<=64, saturated in 2-6/47 dd3 rows); pool, cap, farclip, pin ruled out (s6414/6416/6471). kept grows at dd3 but DL shrinks 961->575 tri.
Hypotheses: H-guestcull (a second per-node visibility/frustum test downstream of streamTerrainGridCellsByDistance drops far nodes), H-vtxdl (per-node vertex/DL build bails, e.g. on a per-frame budget), H-lod (far nodes get a lower-LOD/empty slot).
Work: find the per-node submit loop that consumes the list returned from streamTerrainGridCellsByDistance (funcs_9.c after 0x80043A98); add counters via a fixup script (apply_s64xx_*.py style): nodes entering, nodes rejected per return path, DL words emitted per node; one run each dd2/dd3 on the pinned recipe (s6470_dd3_break_ab.sh). Outcome: the reject path whose count jumps at dd3 names the lever.
