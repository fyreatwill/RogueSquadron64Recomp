# G1(d): one controlled level-3 City_1 destruction response
HYPOTHESIS-ID: g1-coverage-cd

s6670 ordinary script-damage unit finished. Original-backed City_1 DAT+048C,
subtype20, c28+1 only, no Boolean/second counter. Original registered handler
8006CBB0 differs from FFFF fallback: message5 subtracts health at8006CFE8;
8006D278 skips death effect8006D6F0 while health positive. Corrected flight
VI5291..10692,178s,0 crashes: original named API10 -> exact message5 ->
2000→1990 -> return1990, counter28 stays0. Pure original getter3 changes0→1;
probe getter28 returns0 afterward. Script API/getters are explicitly probes,
not player-shot or game-invoked friendlies proof. Compact proof:
scratch/agent/s6670_qualification.json; full details G1-OBJECTIVE-RESPONSE s6670.
Two prior flights had NO request (failed hit controls), not damage nulls.

ONE bounded unit: qualify ONE original City_1 death -> counter28 response.
In one flight/binary, baseline off then one ordinary10 request, require exact
same owned slot/node/payload/DAT handler6CBB0 and actual health reduction,
then at most one currentHealth+1 argument through original named API. Never
store health/objective/timer values directly. Original API caps message damage
to16 bits; require health+1<=FFFF. No fallback/other victim for lethal dosing.
The current level3 adapter ignores the lethal flag; implement its explicit
opt-in state machine first. Ordinary control and dose must be SAME flight.

Hypotheses and WHOLE discriminator:
H-dose: actual2000→1990 control, dose1991 -> nonpositive original health ->
effect8006D6F0 -> writer8006594C c28 0→1 -> callback + original getter28=1.
H-route: damage accepted, health/death branch differs from the original gate;
join actual message, health address/detail, store, return and effect, not stale
payload aliases. Do not add a skip/guard to rescue the outcome.
H-observation: actual counter store differs from callback/getter; compare all
three values and same-run changing getter3/counter monitor control.
H-lifetime: exact-controlled owner is retired/replaced before dose; show the
whole name/lookup/DAT slot/node/payload/handler/health tuple and inhibit dose.
A missing dose/target is not a counter null. Do not assume why s6670's second
recipe issued no request; third recipe logs its whole eligibility tuple.

Before build, read original relevant paths with bounded disassembly:
    python3 tools/g1_dat_inventory.py --level 3 --check-level3 --output scratch/agent/s6671_original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x8006CF88 0x8006CFF8
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x8006D264 0x8006D284
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x8006D6B8 0x8006D744
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800C7390 0x800C7500
Original lv3 friendlies100-(c27+c28); complex callback checks failureBooleans
4/18/21 and successcounter22. City_1 sets none. Do not call the friendlies
routine as a probe: it writes UI state. Pure getterC761C is stackless/read-only;
probe calls with copied context are already implemented and labelled.

Extend tools/apply_s6657_objective_response.py + runner/analyzer fixtures in
ONE batch: ordinary exact control, one dose, actual health store/return,
death effect args, counter store, callback readback and pure getter; reject
repeat doses, changed ownership, wrong request/message/health/store/return.
End at first c28 response with flags4/18/21 and c22 still0. No win/progression.
No TELE/aim changes. Keep defaults retail; no lib edits expected.
    python3 tools/g1_objective_response_run.py --self-test
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
Check screen unlock and no existing game, then after implementation:
    env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py s6671_dose --level 3
Run from build via existing wrapper, phase/VI gates, manifest all hashes;
SIGKILL. No repeat endurance/crash-hunt soak. A silent hook needs an actual
positive control; branch execution alone does not qualify a null.

Update objective table/CURRENT-TRUTH, append Session6671, rewrite NEXT,
write STATUS/OUTCOME and create a NEW iter commit. No VERIFIED promotion
without the required evidence; dynamic causality remains single-source.
