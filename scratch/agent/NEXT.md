# NEXT (s7439)
HYPOTHESIS-ID: rt64-perprim-diag

Class CV (CURRENT-TRUTH Next steps item 1): default-on per-primitive diagnostic hooks inside lib/rt64 hot loops.
s7438 measured ~0.10 ms/frame of our hooks under decodeTriangles alone (rs64_floor_texel 0.028, floor_note 0.018,
rs64_shade_ordinal mutex+unordered_map ~0.045, getters 0.004) with logging off.
Step 1 (offline): grep-enumerate every rs64_* call and getenv-latched block reached per triangle / per load / per draw call in
lib/rt64/src/gbi/rt64_gbi_rdp.cpp (decodeTriangles), lib/rt64/src/hle/rt64_rdp*.cpp (loadBlock/TLUT/drawTris),
rt64_state.cpp (fullSyncFramebufferPairTiles lambda), rt64_framebuffer_renderer.cpp. Classify each: GATED (cached bool checked
before any work) / UNGATED-NEEDED (value used by default-on behaviour, e.g. floor_note if a default-on fix reads it) /
UNGATED-DIAG (work done, result read only by off-by-default logs). Cost each with
  python3 tools/s7438_rt64_terms.py scratch/s7435 --under <frame>
Step 2: for UNGATED-DIAG sites, hoist behind the existing latch (e.g. compute shadeTask/shadeOrdinal/submit only when a
consumer log is on); keep an =0/old env only if behaviour could change. Rebuild (DEVELOPER_DIR=... cmake --build build),
verify with one tools/s7433_probe_cost.sh capture: control PASS and the decodeTriangles --under rows gone; 120 s lvl1 flight
0 crash. lib/rt64 edit => ./submodule-patches/export.sh + commit in the same session.
Hypotheses: H-gated (every site already gated except the ~0.10 found -> fix those, close), H-spread (ungated hooks in other
hot loops add >= 0.2 ms/f more -> fix all in one build), H-needed (floor_* values feed a default-on fix -> keep, document).
