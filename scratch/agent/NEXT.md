# NEXT (s7638)
HYPOTHESIS-ID: post-sweep-revisit

G6a/G6b/G6c and the G5 looks still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Do NOT take the generated-symbol renaming sweep: it is CLOSED (s6268 + s6868, CURRENT-TRUTH item 19; 139 address-named entries left,
all shape names such as data_gap_*, noopHandler_*, lv*; the 3 func_ entries are a function tail (80018ED4), data (8002BB34) and a
TOML-only tail (80092F10)). s7637 found this the hard way. Item 17 (SP_LATE AC repeat) is closed too (s7637: 60.0/60.0 on AC).
Work unit: ladder item 4 REVISIT. Re-attempt CURRENT-TRUTH's "M4 accumulator boundary" (Durable boundaries) or the external
retail-entry boundary with a new angle. Start by grepping CURRENT-TRUTH/PROJECT-OVERVIEW for the last stated blocker and naming ONE
measurement the oracle (tools/oracle/README.md, mupen64plus retail watches) can answer that our runtime cannot.
Hypotheses to write down before any build: H-ours (the boundary value comes from our runtime/host code) vs H-game (retail
produces the same value at the same PC); the oracle watch at the physical address splits them; arm a whole-RDRAM positive control first.
Never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
