# NEXT (s7657)
HYPOTHESIS-ID: gate-sweep-standing

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7656: the sweep is a standing check (cached 14.8 s, stop_gate --verify blocks new RED). Remaining gap: 10 NEEDS-ARGS gates
(s7031_offmap s7082_jal s7083_lowering s7210_field s7215_shape s7317_field_compare s7441_rs64 s7631_rp s7632_dd s7633_hb)
count for nothing. Work unit: for each, read its argv usage + the session entry that ran it (grep PORTING-STATE for the tool
name) and find the input it was run on (scratch/s70xx..., soak_results logs).
- Input on disk -> add it to the sweep's per-gate args table (the 3 done in s7656 are the pattern) and confirm GREEN, plus
  that a planted bad input turns it RED (not NEEDS-ARGS).
- Input gone (gitignored / deleted log) -> classify the gate NEEDS-INPUT with a printed reason, like s7316/s7573.
- Also make `--help` print usage instead of running a full sweep.
Hypotheses: H-ondisk (most inputs survive in scratch/) vs H-gone (logs pruned; they become NEEDS-INPUT). Outcome table per gate.
Rules: never touch build/saves; one game at a time; SIGKILL only.
