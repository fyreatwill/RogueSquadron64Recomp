# NEXT (s7617)
HYPOTHESIS-ID: rt64-rdram-alias-lifetime

Class RQ closed s7616 (tools/s7616_rq_census.py --controls --witness-sample scratch/s7616/sample.txt: 129 base-reference
rows 0 open, regex == clang, controls 10/10, sample witness 95 reader frames all on Gfx Thread). Its declared scope gap is next.

Class RP: RDRAM-derived pointers that OUTLIVE the call in lib/rt64. s7613 HP / s7614 HM censused pointer statics/members in
src/ + librecomp/ultramodern only. In lib/rt64 (minus contrib) enumerate every pointer-typed member, static, thread_local
and container-of-pointer whose value can derive from the RDRAM base (taint: State::RDRAM, core.RDRAM, fromRDRAM(), the
`memory` param of Application::processDisplayLists, DisplayList* from &memory[...], params named RDRAM). Examples to
expect: Interpreter / RSP display-list stack pointers, RDP partial-command buffers, g_s4271_dl-style diagnostic statics.
Rows: fresh (set and used within one send_dl/processDisplayLists), offset (stored as an address, re-based on use), copy,
gated, OPEN. Second source: clang AST (reuse tools/s7613_hp_ast.py / s7614_hm_ast.py with scope = lib/rt64/src).
Controls: planted static DisplayList* set in one call and read in the next -> OPEN; drop a row from each source ->
disagreement; planted pointer member assigned &RDRAM[x] -> OPEN. Runtime witness only for a default-on cross-call row
(e.g. compare the bytes behind a kept pointer at set time vs use time, s7523 model), else none needed.
Witness hygiene: start the game normally and kill ONLY that pid (s7616 killed a foreign game via pgrep -x). Never launch it
under lldb (ROM delete near-miss). Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE. lib/ edits need export.sh + commit.
