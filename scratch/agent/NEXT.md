# NEXT (s7656)
HYPOTHESIS-ID: gate-sweep-standing

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7655 closed closed-gate-drift: tools/s7651_gate_sweep.py is 0 RED (120 GREEN, 2 NEEDS-INPUT, 13 NEEDS-ARGS). The drift happened
because nothing re-runs the sweep after a session adds code. Work unit: make the sweep a standing check.
1. Make the sweep cheap enough to run every iteration: per-gate result cache keyed by (tool file hash, hash of the files the tool
   reads = its scan roots), so an unchanged tree re-runs nothing. Measure full vs cached wall time.
2. Run it from tools/agent/stop_gate.sh --verify (or loop.sh after the iteration) when the iteration's diff touches src/ lib/ or
   tools/s7*_census.py; a NEW RED gate (not red at the iteration's starting commit) blocks with the gate name + tail.
   Contract rules go in stop_gate.sh (CLAUDE.md). Positive control: a planted rowless static in a scratch copy -> RED -> blocked.
3. The 13 NEEDS-ARGS gates: list which have an input on disk (scratch/s70xx) and give the sweep that argument, so they count.
Hypotheses: H-cheap (cache makes it < 30 s on an unchanged tree) vs H-cost (scan roots too broad; needs per-tool roots).
Rules: never touch build/saves; one game at a time; SIGKILL only.
