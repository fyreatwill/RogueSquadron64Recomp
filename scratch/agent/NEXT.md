# NEXT (s7440)
HYPOTHESIS-ID: rt64-percmd-diag

Class CW (CURRENT-TRUTH Next steps item 1). Two parts, one build, one or two runs.
Part A, CV consumer positive control (s7439 gated decodeTriangles hooks behind env latches): run the owner recipe once with
  env ROGUESQ_LOG_SHADE_RAW=1 ROGUESQ_LOG_FLOOR=1 ROGUESQ_LOG_FLOOR_MESH=1 (e.g. via tools/s7431_stderr_volume.sh 150 <envs>)
  and confirm [shade-raw ...], [tri-source-join] with nonzero ord, and [floor] lines still appear (any count > 0 = PASS).
  If 0: the gate is wrong -> fix before anything else.
Part B, remaining per-command / per-rect rs64 hooks (s7439 --under tables): rs64_note_image_word (rt64_interpreter.cpp:848,
  called per RDP command, 0.016 ms/f; returns unless op FF/FE; find who reads s_rs64_ff/fe rings: rs64_img_find), rs64_floor_rect
  (rt64_rdp.cpp, per rect), rs64LogLoad, rs64SkipDraw. Classify GATED / UNGATED-NEEDED / UNGATED-DIAG; inline the op-byte check at
  the call site for note_image_word if it stays needed. Expected: H-small (all < 0.03 ms/f total -> close, no change unless free),
  H-hidden (a hook >= 0.05 under another frame -> gate it), H-needed (ring feeds a default-on fix -> keep, document).
Measure with tools/s7433_probe_cost.sh (S7431_ARM=CW) + python3 tools/s7438_rt64_terms.py /tmp/rs64_s7431/CW --under <frame>;
compare against scratch/s7439. lib/rt64 edit => ./submodule-patches/export.sh + commit.
