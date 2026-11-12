# NEXT (s7230): owner-path frame headroom in the heaviest L4 window
HYPOTHESIS-ID: owner-path-frame-headroom
Context (s7229): the FPS60 flat-30 runs were the coverage harness's diagnostic ucode path. On the owner path the L4 t=77-97 window
(windowed ASPECT=auto dd4) costs 12.8-13.0 ms per gfx task of the 16.7 ms budget, the thinnest margin measured. Question: which
owner-reachable setting or host condition pushes that window over 16.7 ms and drops the owner to 30/s?
Hypotheses: H-dd (dd6 / 21:9 wide window adds per-cell RSP cost, s7019-s7029), H-retina (RETINA=1 adds CPU-side cost; s7204 says GPU only
+0.1 ms), H-host (busy host / E-cores: run a CPU burner on 4 threads during the arm), H-safe (all stay < 16.7 ms, 0 flat runs).
Run (one game at a time, quiet host, screen unlocked; one binary):
  env R=$PWD/scratch/s7230 HOLD=200 ARMS="4:base:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_FULLSCREEN=0+ROGUESQ_ASPECT=auto+ROGUESQ_RETINA=0+ROGUESQ_G1B=1+ROGUESQ_STORE_DIAG=0 \
    6:dd6w:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_FULLSCREEN=0+ROGUESQ_ASPECT=21:9+ROGUESQ_G1B=1+ROGUESQ_STORE_DIAG=0 \
    4:ret:...base...+ROGUESQ_RETINA=1" zsh tools/g1e_owner_quiet_arms.zsh
  busy arm: same as base with `yes > /dev/null` x4 running (kill after); the quiet harness's idle watch is unaffected by it.
Score: python3 tools/s7229_flat30_cost.py scratch/s7230/log_*.txt plus the t=77-97 awk (tasks/s, sd_wall) from s7229 ledger entry.
Outcomes: an arm with flat runs / t77-97 < 55/s names the tipping term (then cut that cost on the owner path); all arms 60/s -> H-safe,
close the thread and record the margins.
