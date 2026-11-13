# NEXT (s7273): fold s7272_219_hold (G5c image holds at 21:9 on the WIDEWIN auto-stack path), then pick the next ladder rung
HYPOTHESIS-ID: g5c-freeze-widewin-stack
State: s7272 16:9 L4 dd4: H-none (0 in-flight holds >= 120 ms in off/stack/R88 phases; holds 250-442 ms all cutscene transitions; SIGSTOP
control 3/3). Soak scratch/agent/soak_queue/s7272_219_hold.sh runs the same at 21:9 (out scratch/s7272/s7272w/hold.txt; rc 3 = control miss).
Fold: if SOAK-RESULTS has it, read scratch/s7272/s7272w/hold.txt. Any non-control hold >= 250 ms: view its frames (tools/s7272_image_hold.py
times; sheet like scratch/s7272/holds_sheet.jpg) - transition = load-side, flight = real. Outcomes: H-none219 -> close the thread;
H-merge219 (flight holds cluster in ph1) -> profile rs64_s7239 merge with `sample` on a live run; H-general219 -> host/present, [s7064] timing.
If not run yet (gated on idle), run it in-session if HID idle >= 120 s and unlocked: `zsh scratch/agent/soak_queue/s7272_219_hold.sh`.
After closing: Next steps items 2-16 are owner looks; take the first ladder rung (ITERATION.md 3c) not closed and write NEXT.md for it.
