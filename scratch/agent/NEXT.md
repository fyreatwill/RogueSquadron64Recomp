# NEXT: owner reports first; otherwise census of the bridge's own RDP edit walkers
HYPOTHESIS-ID: bridge-edit-census
Context: s7096 closed forwarding coverage. RT64 gets exactly the hardware-consumed byte stream (0 missing/dup/order over
34 GB), and every content change between DPC_END and the RT64 handoff (dd4 16:9: ~18 B/task, 399k B per 300 s; dd1: 0)
happens INSIDE rs64_dpc_record_submit (src/rsp/dpc_bridge.cpp ~5960): pre-compare 0 over every forwarded byte. Which
walker makes which change has been named only by op histogram (0x2D = rs64_g1d_title_clear scissor clamp; the bulk in
words whose head byte is 0x02/0x03 = triangle payload), so it is single-source.
Hypotheses: H-edit-intended (every changed byte belongs to a walker's documented edit, e.g. spike clamp/cull rewriting
vertex/edge words, title scissor clamp, pause dim, rect_wrap) vs H-edit-stray (some walker writes bytes it did not mean
to, e.g. misparses a command boundary and patches triangle payload as a command, the s6936 per-bump hazard) vs
H-edit-retail (an edit fires in plain flight where retail drawing should pass through untouched: a candidate for G5b/G5f
visual defects).
Unit (ONE instrument, ONE run, reuse src/rsp/s7096_fwd_cover.cpp):
1. In rs64_dpc_record_submit_impl, snapshot [lo,hi) before each walker call (census, title_clear, wipe_scan, pillar_scan,
   rect_wrap, pause_dim, spike, g5b.., floor; see the t[] timing slots) and diff after it. Per walker: bytes changed,
   commands changed (decoded at true command boundaries with the 16 B texrect / 32..176 B triangle step), op of the
   enclosing command, and the first 8 examples (old/new words). Unattributed = post diff not explained by any walker (must be 0).
2. Positive control: ROGUESQ_S7096_FWD=ctl also flips one byte inside rs64_dpc_record_submit between two walkers on 1 task
   per 1000; it must show up as "unattributed".
3. Run L6 dd4 16:9 (env NOCAP=1 ASP=16:9 zsh scratch/s7031/arm.zsh 6 4 <name> "ROGUESQ_S7096_FWD=ctl" 120 180) and dd1
   4:3 back to back.
Outcomes: every byte attributed to its walker's documented edit = H-edit-intended (close the bridge layer); a walker
patching payload words at non-boundaries = H-edit-stray, fix the walker; edits in plain flight that alter retail geometry
= H-edit-retail, report per-walker counts to the owner with before/after frames.
