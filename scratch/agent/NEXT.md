# G1(d): qualify one ordinary level-3 building response
HYPOTHESIS-ID: g1-coverage-cd

s6669 completed a bounded original-contract/tool change BEFORE runtime enabling.
--check-level3 verifies62 original instruction anchors, four named definitions;
95 subtype0x14 c28+1-only candidates, selected City_1 DAT+048C. All19 level
inventories preserve old fields; level2 checks pass;11 mutation fixtures reject.
No game build/run or response qualification. See docs/G1-OBJECTIVE-RESPONSE.md
s6669 and scratch/agent/s6669_lvl3_response/{checked,validation}.json.

ONE unit: extend the adapter/runner for one ordinary City_1 damage response,
with complete typed slot/health/effect/store/friendlies-reader evidence in one
build/flight. FIRST follow original registered-slot handler. Do not assume
level2 NPC+34 or D3894 applies to buildings. No lethal dose by default.

Original contracts:
- City_1 subtype0x14, detail0 health word2000, effectc28+1 only.
- GVT main also sets failureBoolean4; Tech main sets18; Madine shuttle sets21
  but no counter. EXCLUDE them and all success/failure Boolean setters.
- Original80103530 reads c27/c28 and reports100-(c27+c28). Complex callback
  80102D08 checks failureBooleans4/18/21 and successcounter22.
- C7390 DAT halfword+6==FFFF branch C748C subtracts damage, subtype0x14
  effectcallC74E0 runs WITHOUT a death threshold. Registered branch sends
  message5 atC73F8. Actual live slot and its handler must choose the route.

Competing hypotheses and discriminator:
H-fallback: live named DAT has slotFFFF; one accepted ordinary request takes
C748C/C74E0, original6594C incrementsc28, original103530 reader sees new sum.
H-registered: live named DAT has a slot; message5 reaches a typed building
handler whose ordinary-vs-death ordering differs. Trace that ORIGINAL handler
before enabling; do not use a lethal request simply to rescue a silent result.
H-observation: actual counterstore occurs but readback misses it; compare store,
actual countergetter return and friendlies computation with changing controls.
WHOLE table: DAT-base/offset/name, slot/node/generation/context/handler,
projectile/seq/message, health actor/current detail/ordinary request/result,
effect arguments, actual writer and exact callback/getter result. One ordinary
named request; disable all later forcing after the first accepted request or
named store. No health/objective/timer writes, wins or mission progression.
Null only controlled when a same-run real changing value is detected; heartbeat
or local mark-all branch control alone does not qualify a silent value null.

Starting commands (repo root):
    python3 tools/g1_dat_inventory.py --level 3 --check-level3 --output scratch/agent/s6670_lvl3_original.json
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800C7390 0x800C7500
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80103530 0x8010357C
    rg -n 'parseDatItemSubtypes1To5|dealDamagetoDatItem|City_1' ../rogue_squadron64/symbol_files/*.txt tools/apply_s6657_objective_response.py
Follow original DAT lookup80047B48 and registered message5 dispatch8003E8DC
through actual subtype0x14 slot registration/handler; bounded disassembly only.
Reuse existing named lookup; capture loadDatFile's returned DAT base persistently.
Audit raw fields with original consumers before assigning names.

Before building record selected route and stop ordering here. Extend the existing
persistent fixup adapter + runner choices to3, complete all controls/join fields
at once, add positive/negative analyzer fixtures for named ordinary response.
Existing runner only accepts0/1/2: do not invoke level3 without extending it.
    python3 tools/g1_objective_response_run.py --self-test
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
Check actual screen unlock and no existing game process before input recipe.
After runner/adapter extension:
    env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=0 python3 tools/g1_objective_response_run.py s6670_response --level 3
Use phase/VI keys, retail settings, one build/flight. Manifest all source/env/
binary hashes; stop via SIGKILL. No win, failure or progression experiments.
No repeat level2 soak. If the route needs a different activation interval, derive
it from original conditions, not an arbitrary timeout. No library edits expected.

Update objective table/CURRENT-TRUTH, append Session6670, rewrite NEXT,
write STATUS/OUTCOME and create a new iter commit. Keep static contract versus
live causality distinct; no promotion without the required dynamic evidence.
