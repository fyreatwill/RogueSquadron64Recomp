# NEXT (s7631)
HYPOTHESIS-ID: rt64-rdram-alias-lifetime

G6a/G6b/G6c all landed and wait only on the owner (rumble feel, controls, stand-ins look: docs/OWNER-OPT-INS.md). If the owner
reports on any of them, take that first. Otherwise resume backlog item 21 (deferred behind G6 since s7616):

Class RP: RDRAM-derived pointers that OUTLIVE the call in lib/rt64. s7613 HP / s7614 HM censused pointer statics/members in
src/ + librecomp/ultramodern only. In lib/rt64 (minus contrib) enumerate every pointer-typed member, static, thread_local
and container-of-pointer whose value can derive from the RDRAM base (taint: State::RDRAM, core.RDRAM, fromRDRAM(), the
`memory` param of Application::processDisplayLists, DisplayList* from &memory[...], params named RDRAM). Examples to
expect: Interpreter / RSP display-list stack pointers, RDP partial-command buffers, g_s4271_dl-style diagnostic statics.
Rows: fresh (set and used within one send_dl/processDisplayLists), offset (stored as an address, re-based on use), copy,
gated, OPEN. Second source: clang AST (reuse tools/s7613_hp_ast.py / s7614_hm_ast.py with scope = lib/rt64/src).
Controls: planted static DisplayList* set in one call and read in the next -> OPEN; drop a row from each source ->
disagreement; planted pointer member assigned &RDRAM[x] -> OPEN. Runtime witness only for a default-on cross-call row
(compare the bytes behind a kept pointer at set time vs use time, s7523 model), else none needed.
Outcomes: 0 OPEN with controls passing -> RP CLOSED; an OPEN default-on row -> witness it, then fix (lib/ edit => export.sh + commit).
Witness hygiene: start the game normally and kill ONLY that pid. Never launch under lldb. Never touch build/saves; never clear
ROGUESQ_NO_SAVE_WRITE.
