# G1(d): level4 original objective and target contracts
HYPOTHESIS-ID: g1-coverage-cd

s6671 closes level3 named loss response: same-flight original City_1 script
request10 HP2000→1990 then request1991 HP1990→−1, effect8006D6F0,
writer8006594C counter28 0→1, callback/getter1, flags4/18/21 and c22=0.
Original effect tuple is(28,1,0,0,0,1): counter2=0 disables that slot even
though delta2=1. Analyzer corrected post-run; same capture qualifies, binary
unchanged. Dynamic causality single-flight, not player-shot/retail-equivalence
or full VERIFIED. Evidence scratch/agent/s6671_qualification.json and
G1-OBJECTIVE-RESPONSE s6671. No new queued soaks.

ONE bounded change: add original-backed level4 contract checks and target
selection to tools/g1_dat_inventory.py, with mutation fixtures. Reconcile
historical ids15 and5 against the actual callback/reader. Choose one named
loss/neutral counter target whose effects cannot set success/win or immediate
failure; if none exists, enumerate/prove the original restrictions instead.
No game build/run or dose until the original contract is established.

Hypotheses and discriminator:
H-counter: one of historical ids15/5 participates in the actual named level4
objective arithmetic, and a DAT target's original effect writes it.
H-incidental: those shared baseline transitions do not belong to this level's
objective reader; select the actual named reader/callback counter instead.
H-route: a plausible DAT definition uses a different registered handler or
health/effect gate; do not inherit the City_1/shuttle layouts blindly.
Measurement: original ELF instructions plus independently parsed retail DAT
produce a complete table of callback reads/gates, named reader arithmetic,
subtype setup/handler, health storage, death/effect arguments and target
exclusions. Assert instruction words and mutate each assertion plus selected
DAT effect fields. A function name or pointer-shaped record is not proof.

Commands (bounded output; never read whole ledger/generated files):
    python3 tools/g1_dat_inventory.py --level 4 --output scratch/agent/s6672_lvl4_original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80103720 0x80103994
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80103CC4 0x80103D08
    rg -n 'lv4_checkComplexObjectives|lv4_calculateFriendliesSaved' ../N64Recomp/RecompiledFuncs/funcs_45.c
Use bounded windows around each hit and table-derived handler; compare to
retail ELF, not generated diagnostics as sole witness. Read existing level3
contract code (rg then bounded sed) to extend the tool. Label subtype20's
static unregistered-damage-objective inventory layout separately from actual
registered route; s6670 established those differ.

Implement --check-level4 plus a mutation fixture batch in the existing tool
or its existing validation mechanism, preserve all earlier level2/3 checks,
and reconcile docs/G1-OBJECTIVE-RESPONSE. Do not run a live response with an
unqualified new level or spend this iteration adding one diagnostic field.
Keep defaults retail; no lib edits expected. Original static proof is not a
live-response/absence or VERIFIED claim. After qualified contract choose the
single next live ordinary-control unit with whole-chain instrumentation.

Append Session6672, update CURRENT-TRUTH, rewrite NEXT, STATUS/OUTCOME,
and create a NEW iter commit. G4 remains parked; no repeat holds/aim work.
