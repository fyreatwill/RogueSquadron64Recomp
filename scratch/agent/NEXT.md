# G1(d): level4 owned ordinary wingman hit
HYPOTHESIS-ID: g1-coverage-cd

s6672 closes original static contract: reader80103CC4=6−(counter40+counter15).
x_wing_hobbie DAT+6A7C subtype27 HP400 detail0, effect(40,1,0,0,0,1).
Setup65510 selects handlerD93C0; message5 tableA7A10->D9BB0. Payload=node+4,
DAT=payload+34, actor=payload+38. Original F2120 writes either detail-array
health atF2148 or inline actor+190 atF2158 depending actor+1A7; positive return
atD9C5C skips effectD9D28. No live qualification yet. 332 anchors/380 mutations
pass, all19 inventories unchanged. See G1-OBJECTIVE-RESPONSE s6672 and
scratch/agent/s6672_validation.json. No new soak verdicts.

ONE work unit: extend existing persistent adapter/analyzer/runner for level4,
then one unlocked flight with ONE ordinary original named API request10 to
actually owned x_wing_hobbie. No lethal dose, direct health/counter stores,
win/progression/aim work, or repeat holds. Keep retail defaults.

Competing hypotheses:
H-registered: live original-owned Hobbie receives message5, actor health decreases
by10 through original F2120, positive return skips effect, c40 unchanged.
H-storage: actor inline/array choice differs from DAT/detail expectation; actual
writer and return explain it, not an invented health pointer.
H-unavailable: no original lookup-equal live Hobbie in the observed epoch; census
must report lifetimes/retirement and eligibility reasons, not a silent null.
Discriminator: a single exact table joining API seq/name/slot/gen/node/payload/
DAT/actor/detail/actor+1A7/actual health address, request, accepted message,
F2148 or F2158 pre/post, D9C54 return/D9D28 effect, counter40 store/readback
and explicit original getter return. Log all these in ONE build. Request once
only after lookup equality, free-list exclusion and ownership validate. No
counter-response claim from a surviving ordinary hit. Actual changing counter
getter/memory values in same run control monitoring; mark-all known owned
wingman health-address detection must fire before interpreting a missing store.

Read original contracts before instrumentation:
    python3 tools/g1_dat_inventory.py --level 4 --check-level4 --mutation-check-level4 --output scratch/agent/s6673_lvl4_original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800D9BB0 0x800D9D40
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800F20EC 0x800F215C
Use bounded windows in tools/apply_s6657_objective_response.py (rs6670_api,
level3_hooks, rs6663_descriptor/kind) and tools/g1_objective_response_run.py.
Current runner accepts levels0..3 ONLY; extend --level4, do not claim existing
command already supports it. Current City-only script request/getter/health
analyzer must be generalized deliberately; preserve old regression fixtures.

After extending persistent code, replay/batch all hooks once and build:
    python3 tools/apply_s6657_objective_response.py ../N64Recomp/RecompiledFuncs
    python3 tools/g1_objective_response_run.py --self-test
    cmake --build build --target RogueSquadron64Recomp -j5 > scratch/agent/s6673_build.log 2>&1
If full regeneration needed: make_elf -> N64Recomp -> vendored fixup -> cmake,
never regenerate without replaying persistent changes. Test idempotence/replay
on scratch copies first; do not hand-edit generated load-bearing logic.

After --level4 support exists, one fresh tag (lethal env unset):
    python3 tools/g1_objective_response_run.py s6673_lvl4_ordinary --level 4
Runner checks CGSSessionScreenIsLocked; screen must be unlocked for key route.
Use first explicit flight epoch, phase-relative arm gates, scoped budgets,
watchdog and SIGKILL cleanup. If evidence shows ownership absence, classify
exact observed boundary and choose new discriminator, not a repeat dose.
Retain manifest hashes, live identity proof, joins and failed controls.

Append Session6673, update CURRENT-TRUTH and objective table with limits,
rewrite NEXT, write STATUS/OUTCOME, git add -A and a NEW iter commit.
No lib edit expected; if needed export submodule patches in same commit.
