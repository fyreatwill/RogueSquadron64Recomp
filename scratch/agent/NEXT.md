# G1(d): level4 one-shot named loss response
HYPOTHESIS-ID: g1-coverage-cd

s6673 lands level4 support and one exact owned ordinary wingman health chain.
Corrected run g1_lvl4s6673_lvl4_ordinary_v2, VI4971..10371/172.03s/0 crashes:
Hobbie DAT803239CC, slot187/gen1,node8021B268,NPC8035F68C,actor80361D58,
mode0/detail0, address80323A38. API10 atVI6777 -> message80165E80 -> actual
F2148 health370→360, damage/API returns360. Getter40 returns0 afterward.
Health controls fire; NONE of128 original counter getters changes. Analyzer
exact_health_chain=true but qualified_ordinary=false. This is NOT a controlled
counter null. First run stopped73.03s/no epoch/no API because adapter compared
decimal27; correct original subtype is0x27=39. Never pool those attempts.
Static original contracts from s6672 still stand; dynamic causality single-flight.

ONE work unit: extend existing opt-in level4 API/health analyzer for one ordinary
control and one same-owned lethal request, then one unlocked flight; stop at actual
counter40 response before later mission script progression. No direct guest health/
counter stores, player aim, wins or mission-to-mission tests. Do not repeat an
ordinary-only hold in search of a changing counter. Retail defaults stay unchanged.

Hypotheses:
H-death: the same named actor gets requestHP+1 through original message5, its
selected-detail health becomes−1, original effectD9D28 passes(40,1,0,0,0,1),
original writer8006594C increments40; callback and getter return the new value.
H-route: health depletion happens but original routing does not invoke that tuple
or counter store. Identify the actual observed branch/arguments, do not add a guard.
H-identity: live slot/generation, actor, mode/detail/storage or health changes before
the dose, so a valid same-owned experiment cannot issue. Log the exact eligibility
failure/retirement; absence is not evidence that the death effect is broken.
Discriminator: ONE seq-keyed table joining lookup/live ownership/API pre/accepted
message/live handler arguments/actual actor+address/writer pre+post/return/effect
args/objective writer/readback/getter plus safety flags. All fields in ONE build.

Read original ground truth before edits:
    python3 tools/g1_dat_inventory.py --level 4 --check-level4 --mutation-check-level4 --output scratch/agent/s6674_lvl4_original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800D9C4C 0x800D9D40
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800F2120 0x800F215C
Read bounded rs6673 helpers/level4_hooks and qualify_level4 in existing tools.
Current level4 code ALWAYS requests10; merely setting LETHAL does not implement
this next unit. Generalize fixed api_seq=1 before any claimed dose run. Preserve
level2/3 and ordinary-only fixtures. Dose opt-in only; without opt-in preserve s6673.

Require an actual prior same-owned request10/store/return control. Validate the
six-field original DAT effect, original name equality, free-list exclusion,
canonical slot, generation, mode/detail, exact actor/address and positive health.
Dose once atHP+1 (<65536) only with counter40 initially0 and no failure/success
state. Never assume nominal400 after natural damage. Ideally issue the pair
synchronously after validation; otherwise revalidate all identities and health.
Original array vs inline branches both stay supported. Add real effect args at
D9D28 and keep actual store observations. Record unused counter2=0/delta2=1
as original, not a second active effect. Keep named relevance/stop handling level4
aware: rs6657_flight's observed latch must not close before actual getter join.
After writer+callback+getter agree, log all counters15/16/28 and Boolean26, then
SIGSTOP/SIGKILL before unrelated progression. No host-written fake counter control.
The dose's actual counter change can control sensitivity. If no counter changes,
report an uncontrolled null unless another actual changing getter controls it.

Test hook-free replay + idempotence on scratch copies, both ordinary/dose fixtures,
wrong/missing actor/message/writer/getter/ownership/flags/duplicate dose negatives.
    python3 tools/apply_s6657_objective_response.py ../N64Recomp/RecompiledFuncs
    python3 tools/g1_objective_response_run.py --self-test
    cmake --build build --target RogueSquadron64Recomp -j5 > scratch/agent/s6674_build.log 2>&1
Only AFTER dose support exists, fresh tag, unlocked screen checked by runner:
    env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py s6674_lvl4_loss --level 4
Keep first flight epoch and phase-relative arms; no stopwatch A/B or run-lifetime
budgets. Manifest all6 hashes, retain failed attempts separately. One instance at a
time, run from build with ROM; SIGKILL cleanup. No lib edit expected. If needed,
export submodule patches before committing. No new soak verdicts in s6673.

Append Session6674, update CURRENT-TRUTH/objective response table with explicit
control/source limits, rewrite NEXT, STATUS/OUTCOME, git add -A/new iter commit.
