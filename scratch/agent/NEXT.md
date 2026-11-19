# NEXT (s7618)
HYPOTHESIS-ID: g6-upstream-features

G6a rumble landed s7617 (default on, owner to feel it). Take G6b now (ITERATION.md item 3c G6b).

G6b step 1 (this iteration): move the hard-coded pad + keyboard map in get_n64_input (src/main/main.cpp, grep
"get_n64_input"; R2 -> C-Left, L3 -> C-Right, left trigger -> Z, Back/Guide alternates, WASD/ZXC/QE/IJKL/arrows/Enter)
into a binding table whose built-in defaults equal today's mapping EXACTLY. Keep the old code path behind
ROGUESQ_BIND_OLD=1 for one release.
Proof (same run, no game needed): a unit harness that feeds every single pad button, each trigger at 0/threshold-1/
threshold/max, stick extremes and every mapped key (plus a few combos) through BOTH the old function and the table, and
asserts byte-identical N64 button word + stick bytes. Planted mutant (swap one table entry) must FAIL the harness.
Hypotheses: H-equal (table reproduces old output for all inputs) vs H-drift (some edge: trigger threshold, stick
deadzone/STICK_GATE, keyboard+pad OR, hotplug virtual pad) differs. Only H-equal may land.
Step 2: controls.json in the data folder (missing = defaults), several bindings per N64 button, triggers/stick as sources.
Step 3: F6 ImGui Controls panel (RT64 overlay is on F1). Upstream src/input/input_bindings.cpp is format/UI reference only
(`git show origin/main:src/input/input_bindings.cpp`). Do not change any default binding. README Controls + OWNER-OPT-INS.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; never launch under lldb.
