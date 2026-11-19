# NEXT (s7632)
HYPOTHESIS-ID: rt64-default-on-diagnostics

G6a/G6b/G6c still wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports on any of them, take that first.
Otherwise this is CURRENT-TRUTH item 22.

Class DD: diagnostic work that runs by default in lib/rt64 per-list / per-command hot paths. s7631 found the first rows.
In Interpreter::processRDPLists (lib/rt64/src/hle/rt64_interpreter.cpp ~630-640, ~786-790), every list >= 64 KB copies up
to 256 KB into g_s4281_snap and swaps it into g_s4282_prev, and every RDP command writes a g_s4271_ring entry. They are only
read by s4271DumpRing / s4282Probe, on the 0x130393/w1033 colour-image signature (rt64_rdp.cpp:514) or under ROGUESQ_S4271.
Enumerate the WHOLE class in one pass. Regex source: in lib/rt64/src (minus contrib/imgui/tools), every s<NNNN>/g_s<NNNN>
store, ring/vector write, fprintf or getenv in a function reached per list or per command (processRDPLists,
processDisplayLists, the rdpGBI/extended handlers, RDP::setColorImage/loadTile/..., TMEM loads). Second source: clang AST
(reuse tools/s7631_rp_ast.py's tree walker: calls / stores inside those functions that are not under an if whose condition
reads a getenv-initialised static or a ROGUESQ flag). Rows: gated (env / static flag), rare-signature (bad-value trigger),
ALWAYS (unconditional work). Controls: a planted unconditional ring write -> ALWAYS; a planted getenv-gated one -> gated;
drop one row from each source -> disagreement.
Then measure only the ALWAYS rows that copy or allocate. One build, two arms in the same session: default vs
ROGUESQ_S7632_DIAG=0 (gate them off). Read host-ms per processRDPLists from the existing s4267 timer (T(5)) or the G1b
instrument, on L1 and L4 dd4 owner recipe, 120 s holds. Outcomes: a measurable saving with byte-identical RDP output (s6785
RDP-hash compare) -> land gate default OFF, =1 restores. No saving -> class closed as harmless, no change.
Witness hygiene: start the game normally and kill ONLY that pid with SIGKILL. Never launch under lldb. Never touch
build/saves. Never clear ROGUESQ_NO_SAVE_WRITE. One game at a time.
