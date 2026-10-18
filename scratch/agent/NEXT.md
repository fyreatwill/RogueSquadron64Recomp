# Next work unit: read s5444_nostart_a/b (hold 480, late keys 'a' only)
HYPOTHESIS-ID: m6-flown-render-fidelity

- Read SOAK-RESULTS.md tail + scratch/agent/m6/s5444_nostart_*/summary (now written; HOLD fits the 600 s cap). Convert late fbd dumps with `python3 -I tools/ppm2png.py in.ppm scratch/agent/m6/view/x.png` (write inside the repo; /tmp is unreadable) and view.
- Hypotheses: (H1) mission-fail/results fires and `a` advances it -> look at the transition frames, crashlines, vi_stalls30s; (H2) still flight at end -> mission just does not fail in 480 s of z-only flight; switch to a recipe that ends the mission (or accept flight endurance as the M6 datum and pivot to the title-boot plume SIGSEGV loop under lldb); (H3) stall/crash -> ASan arm for backtrace.
- Keep Hold <= 480: boot ~81 s + verify 130 s + hold must stay under the 600 s soak cap.
