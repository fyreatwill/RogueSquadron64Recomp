# NEXT (s7633)
HYPOTHESIS-ID: bridge-default-on-diagnostics

G6a/G6b/G6c still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Otherwise this is CURRENT-TRUTH item 23.

Class HB: default-on diagnostic work in the HOST bridge per-task / per-submit paths (src/rsp/dpc_bridge.cpp, 8608 lines,
170 getenv sites; src/main/rt64_render_context.cpp send_dl). s7632 closed the same question for lib/rt64 (class HD): the only
default-on copy was the s4281 list snapshot, measured at 0.82 ms/s (0.37% of processRDPLists) and kept. s7068 already gated
three per-command calls in the bridge; nobody has enumerated the whole bridge.
Tools exist: `python3 tools/s7632_dd_scan.py --hot src/rsp/dpc_bridge.cpp,src/main/rt64_render_context.cpp --out S.json`,
`python3 tools/s7632_dd_ast.py --hot <same> --out A.json` (both run clean on dpc_bridge: 874 / 1554 raw rows), then
`python3 tools/s7632_dd_census.py S.json A.json --plant-scan .. --plant-ast .. --drop-control` (plant: scratch/s7632/plant_hd.cpp).
Expect to extend CLASS / FNCLASS in the census for the bridge's names (functional rows: dpc_record_submit_impl, spike_scan,
CULL_SPIKE, G1d rect/pause/title glue, s7018). Rows: ONCE / ENV / BUDGET / SIG / ALWAYS -> classify every ALWAYS row
(functional / scalar / copy / UNCACHED getenv). Controls as s7632: planted ring + snap -> ALWAYS, planted env print -> gated,
drop-one-row -> disagreement.
Then measure ONLY rows that copy, allocate, hash or call getenv per task: one build with a ROGUESQ_S7633_STATS timer
(steady_clock, one line per 10 s, like the [s7632] line in lib/rt64/src/hle/rt64_interpreter.cpp) around each candidate, and a
=0 gate per candidate, same session arms via `env R=.. HOLD=120 ARMS="4:hL1:..+ROGUESQ_FORCE_SAVE_MISSION=1 4:hL4:.." zsh
tools/g1e_owner_quiet_arms.zsh` (s7632 recipe, needs host idle >= 120 s and AC). Decision rule (s7632): gate default OFF only
if the same-run timer shows >= 1% of the measured call cost or >= 2 ms per second (0.2% of a core); otherwise close as
harmless, no change (the s7632 snapshot, 0.82 ms/s = 0.37%, was kept by this rule).
Witness hygiene: start the game normally and kill ONLY that pid with SIGKILL. Never launch under lldb. Never touch
build/saves. Never clear ROGUESQ_NO_SAVE_WRITE. One game at a time. Do not rebuild while a soak arm is running (each arm
re-launches the binary).
