# NEXT: Retina flight cost at the owner recipe (s7203 opt-in ROGUESQ_RETINA=1), then owner picks the default
HYPOTHESIS-ID: retina-render-scale
Context (s7203): ROGUESQ_RETINA=1 (plume_apple.mm getScaleFactor, runtime) sizes the swap chain in backing pixels:
built-in fullscreen 1512x949 -> 3024x1898, RT64 WindowIntegerScale 4x -> 8x (1920 internal rows). Attract cost was
small (+0.28 ms GPU median, 30 presents/s) but flight at FPS60 dd4 16:9 has far more triangles and fill, at 2x the
present rate. Unmeasured.
Hypotheses:
- H-free: RETINA=1 holds 60 fps in flight (fl_shown), GPU median < ~4 ms, no new stalls -> recommend it to the owner as default-on candidate.
- H-fill: 8x internal (3840x1920-class target) costs enough GPU fill to drop presents below 60/s or raise p95 gpu_ms past ~10 ms
  on busy levels -> cap the internal multiplier under RETINA (e.g. ceil(points_h/240) * scale, or Manual 4-6x) and re-measure.
- H-mem: the larger targets raise RT64 memory/pipeline churn (first-use hitches; G5c 250 ms gaps) -> look at Q rows gaps.
Discriminator, one build (current), arms sequentially (one game at a time), recipe = scratch/agent/soak_queue/done/
s7198_backlog_L4_20261112-054328.sh with XENV_EXTRA adding ROGUESQ_FULLSCREEN=1 ROGUESQ_PRESENT_RING=<path> and
ROGUESQ_RETINA=0|1, LEVEL=4 and LEVEL=6, HOLD_S=180. Report per arm: [retina] swapchain create row, presents/s, gpu_ms
median/p95/max, count of Q-row gaps > 50 ms and > 250 ms, fl_shown fps, crash count. Screen must be unlocked (ioreg check).
Then an owner sheet: same-scene 1:1 crops RETINA 0 vs 1 (scratch/s7203/crop_c3.png style) in flight.
