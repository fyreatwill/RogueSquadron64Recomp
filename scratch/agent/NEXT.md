# G1(d): level6 owned ordinary Barracks API health response
HYPOTHESIS-ID: g1-coverage-cd

s6678 closes the bounded offline static contract. Original callback80104210
reads c34..39/98/50/99; friendlies reader80104444 returns0. Retail Barracks
+4A2C subtype14 nominal detail0HP500, effect(50,1,0,0,90,1). This is TWO
counters, not an isolated c50 effect. Counter90 consumers remain unqualified;
no lethal admission. Setup653F4 -> handler6CBB0/message5CF88, health writer
6CFE8, death gate6D278, effect6D6F0. DAT+a0 source gate(selected0), global
80130B39 effect gate, live detail and FFFF API fallback must remain explicit.
294 original anchors/334 mutations pass; all19 inventories and level5 contract
unchanged. Proof scratch/agent/s6678_validation.json, full semantics/hashes
in docs/G1-OBJECTIVE-RESPONSE.md s6678. No new queued-soak verdicts.

ONE bounded opt-in adapter/analyzer change plus one flight: ordinary original
named API10 on ONE owned OBJ_ConYard_Barracks with detail0, HP>10 and named
lookup equality. Reuse the original-backed City subtype14 route helpers, NOT
the wingman actor+38 health layout. Disable level6 generic TELE and every
lethal branch. No direct health/counter stores. Scope counters/budgets to
first actual flight epoch, validate selector B40=6 plus executing lv6 callback.

Competing hypotheses:
H-registered: exact owned request dispatches message5 to6CF88, writer6CFE8
subtracts10 from DAT+6C, health remains positive, API returns the new health.
H-route: original lookup/dispatcher chooses FFFF fallback or another handler;
observe it and do not pool its immediate effect with registered damage.
H-ownership: named DAT definition is not live or ownership/detail/source gates
differ; record which checked field inhibits the request rather than guessing.
DISCRIMINATOR: exact API sequence + slot/gen/node/NPC/DAT/message identity,
registered entry, pre/post health address/store, damage/API return and original
getters50/90 compared with memory. Carry all keys in one build. An owned
mark-all candidate must visibly fire in each reached arm; actual changing
original-getter readbacks are the value-detection control. Silent surviving
victim counters cannot prove an objective null. Positive health means no
registered death effect is expected. If fallback appears, stop before issuing
further damage and classify its effect explicitly. No wins/progression.

Start:
    wc -c < docs/CURRENT-TRUTH.md
    python3 tools/g1_dat_inventory.py --level 6 --check-level6 --mutation-check-level6 --output scratch/agent/s6679_lvl6_original.json
    rg -n 'rs6670|level3_hooks|level5_hooks|OBJECTIVE_RESPONSE_LEVEL|FILES' tools/apply_s6657_objective_response.py
    rg -n 'qualify_level3|api_self_test|choices=|args.level|manifest' tools/g1_objective_response_run.py
    rg -n 'npcDebrisFieldUpdate|lv6_checkComplexObjectives' ../N64Recomp/RecompiledFuncs/funcs_*.c
Read bounded windows only. Consult original ELF before new assumptions, using
mips64-elf-objdump ranges from s6678. Extend existing adapter and analyzer for
level6, including complete/absent-link/wrong-route/wrong-detail/identity/
HP/return/getter fixtures; preserve existing level3/4/5 hooks exactly.

After implementing level6 support (current runner choices stop at5):
    python3 tools/g1_objective_response_run.py --self-test
    python3 tools/apply_s6657_objective_response.py ../N64Recomp/RecompiledFuncs
    python3 tools/apply_s6657_objective_response.py ../N64Recomp/RecompiledFuncs
    cmake --build build --target RogueSquadron64Recomp -j 6 > scratch/agent/s6679_build.log 2>&1
    python3 tools/g1_objective_response_run.py s6679_lvl6_ordinary --level 6
    python3 tools/g1_objective_response_run.py s6679_lvl6_ordinary --level 6 --analyze
Require 13-file idempotence and hook-free replay through fixup; any full regen
must follow make_elf -> N64Recomp -> fixup -> cmake. Runner checks screen lock,
launches from build, records all6 manifest hashes and SIGKILLs the game. Screen
must be unlocked. No parallel game runs. Never overwrite a tag; if correcting
and rerunning, suffix v2 and preserve failed evidence. Keep passive instruments.

Qualify ordinary health only when exact joins pass. If getters never actually
change, explicitly leave counter sensitivity unqualified even if health chain
passes. No live availability conclusion from static DAT. Counter90 consumers
must be proven before a later destruction step, not hidden by a guard. Write
Session6679/CURRENT-TRUTH/response table/NEXT, STATUS/OUTCOME and NEW iter commit.
