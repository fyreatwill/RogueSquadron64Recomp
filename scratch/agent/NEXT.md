# NEXT (s7584)
HYPOTHESIS-ID: generated-symbol-renaming-sweep

gen-c-residual-ub-audit CLOSED s7583 (H-clean; PLANT=6 + PLANT=u fired; 0 reports L1/L4/L12). The UBSan campaign over the game C
(s7578 null/wrapv, s7579 bounds, s7580 shift/align, s7582 pointer-overflow, s7583 residual) is complete: every C-applicable check
has run. -fsanitize=function is a no-op on this Apple clang (arm64), and TSan (tools/build_tsan.sh) and strict aliasing were covered
earlier (grep PORTING-STATE). CURRENT-TRUTH item 19: take the next ITERATION.md 3c rung.

Unit: resume the generated-symbol renaming sweep (ITERATION item 4).
0. First run `grep -n '^## Session ' PORTING-STATE.md | tail -15`. If all 15 are sweep sessions, do the REVISIT instead (external
   retail-entry boundary / M4 accumulator boundary, new angle).
1. Count the remaining placeholder names: `grep -c 'func_0x\|func_80' <symbol map used by tools/rename*>` (find the mapping file
   via `ls tools/rename*`), and pick the next address block in the existing order.
2. Name each function from the evidence (callers, the strings it touches, MusyX/libultra signatures). Record the evidence per name.
3. Regenerate in order (make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake) and build build/. Smoke-test L1 dd1 60 s.
Hypotheses: H-name (every candidate has a unique evidence-backed name) vs H-ambiguous (several are helper thunks with no distinct
role; leave those as func_ and list them). Discriminator: the per-function evidence table.
CHURN WARNING: a rename-mapping edit alone counts as NO engineering change (the gate's 6/12 counter). Pair the sweep with any real
fix it turns up, or switch to an owner-reported item if the owner has written one (check ITERATION.md G-list for new dates).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
