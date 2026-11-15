# NEXT (s7387)
HYPOTHESIS-ID: render-to-rdram-double-pass

s7386 selected H-partial (single-source): with ROGUESQ_RENDER_TO_RAM=0 the abort -> MISSION FAILED cut showed one frame of raw-RDRAM
stripes in the 4:3 box (scratch/s7386/aboff/w_0156.12.png) where the on arm showed black. Everything else on the route matched.

Work unit: second line + mechanism in ONE build/run set.
- Hypotheses: H-unknown-fb (VI scans out an address RT64 never drew; with readback off RDRAM still holds old data, with it on the
  game's RDP clear landed there), H-fade-fill (the game's fill-rect clear of that buffer is GPU-only with r2r off and RT64 presents
  the RDRAM copy because the fb is not in its tracked list), H-capture-artefact (one-off capture of a half-presented frame; would
  also show in the on arm on repeats).
- Run: route with abort tail, 3 abort cycles per arm (extend AP: after the debrief 181:a, re-enter mission and abort again, or 3 runs
  per arm, one at a time). `env AP=<route+abort> SECS=200 CAP0=150 RDIR=scratch/s7387 zsh tools/s7386_route_ab.zsh offN "ROGUESQ_RENDER_TO_RAM=0 <vi/fb log env>"`
  plus BURST=150,160 in-process grabs (g3_port_capture.sh BURST) for frame-exact capture. Log VI origin per VI and RT64's
  present source (follow-draw mode / fb lookup hit-miss) over t 150-160.
- Outcome: stripes in off only, repeatable, VI origin not in RT64's drawn list = H-unknown-fb -> fix: keep renderToRDRAM for fill-only
  / undrawn buffers, or present black for an unknown fb when r2r=0. Stripes in on arm too = H-capture-artefact (r2r clean).
Owner save read-only. Do NOT change the default. OWNER-OPT-INS row says not recommended until fixed.
