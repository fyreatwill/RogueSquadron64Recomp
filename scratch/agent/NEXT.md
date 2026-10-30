# Finish the level-2 original handler ownership class
HYPOTHESIS-ID: g1-coverage-cd

s6663 completed the ownership correction and one validation flight. Original
unregister8003E88C..E8C8 retains legitimate stale word0 pointers; BB4 free-list
membership matters. Corrected flight VI4939..10339,171.84s,0 crashes/forces:
20 valid lists,0..235 stale free pointers,33..516 active SLOTS,23 handlers.
22 kinds remain unresolved; no absent-target conclusion. Mark-all15/17/11,
local selector fixtures all arms,6 natural counter changes. Detailed results
and handler roster: scratch/agent/s6663_lvl2_owner/summary.json; full lifetime
rows in scratch/agent/m6/g1_lvl2s6663_owner/response.json. Do not repeat this
sparse-map run, add another join key, or infer that every slot is an object.

ONE bounded original-backed ownership-map correction: classify the ENTIRE
23-handler roster (22 unresolved) as an established descriptor path OR
non-objective/message-ineligible with original-code evidence. The existing
instrument already carries all lifetime, candidate, SEND, health/effect and
objective-store keys. Extend the map and safe target predicate together.
No lethal level2 dose, arbitrary victim, direct counter/health write, aim,
win or mission progression. Preserve level0/1 and ordinary default TELE.

Hypotheses:
- H-kind: count40 target belongs to another handler/payload layout. Original
  producers and objective consumers plus a matching same-flight typed
  descriptor establish it. Relevant leads: npcWingmanUpdate800D93C0,
  npcTieVariantUpdate800DB11C, datItemActorNpcHandler800ECE10.
- H-script: count40 belongs to a script-generated loss path rather than a
  forceable damage descriptor. Original producer references/spawn conditions
  and a complete type map establish the boundary; choose another named
  non-win objective response if count40 is not safely forceable.
- H-late: relevant target arrives later than the original census windows.
  Existing persistent transition records and uncapped candidates show it;
  unknown kinds cannot establish a null. Do not repeat holds awaiting luck.

Discriminator: original-handler table of spawn message, payload source,
descriptor offset, objective-field layout, damage-message consumer and
counter/Boolean writer, joined to the existing23-kind live roster. If a
safe count40 target exists, one corrected off/on/off validation flight must
show a real selected descriptor, exact SEND and ordinary health change.
If no safe forceable target is proved, land the complete original-backed
map and explicit script boundary; never promote an unresolved-kind zero.
Local selector fixtures validate only predicate sensitivity, NOT existence.

Read ground truth first, no runtime as its own witness:
    mkdir -p scratch/agent/s6664_lvl2_kinds
    python3 - <<'PY'
    import json
    from pathlib import Path
    d=json.loads(Path('scratch/agent/s6663_lvl2_owner/summary.json').read_text())
    for h,v in d['handlers'].items(): print(h,v)
    PY
    rg -n 'npcWingmanUpdate|npcTieVariantUpdate|datItemActorNpcHandler|npcShuttleUpdate' syms/rogue_squadron.syms.toml
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800D93C0 0x800D9F90 > scratch/agent/s6664_lvl2_kinds/wingman_elf.txt
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x800DB11C 0x800DC228 > scratch/agent/s6664_lvl2_kinds/tie_elf.txt
    rg -n 'jal|52\(|112\(|116\(|120\(|124\(' scratch/agent/s6664_lvl2_kinds/*_elf.txt
Read bounded windows <=60 lines, not whole disassemblies. Expand to ALL
roster handlers in this work unit; no one-kind-per-session campaign.
s6663 already independently disassembled shuttle D3894: node+4 payload,
payload+34 desc set at D3920 or flag0x20 variant D394C; objective writer
call D4BA8. Shuttle is NOT in s6663's observed roster or binary type map.
Dat actor ECE10: node+4 payload, payload+0 descriptor stored ECE48; payload
+34 is a float zero at ECEC4. Do not interpret it as an NPC descriptor.
Original slot rules: s6663_lvl2_owner/{slots,table,send}_elf.txt and original
ELF hash in elf_manifest.json. Level2 init tracks objective handles, not
necessarily the game object's spawn list. Find actual count40 producer.

Before build, rewrite this file with the final map, target, controls and
expected outcomes. Then apply only this adapter (no full-tree fixup):
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6664_kinds --level 2
Only run if the corrected map can distinguish the competing outcomes.
Fresh paths, unlocked screen, build/ROM, SIGKILL watchdog. Regression controls
from s6663_lvl2_owner/check.py extract the CURRENT helper, preserving level1
behavior and testing live/free/unknown/cyclic-list cases; add checks for
new original-proven descriptor variants. No lib edits needed. No new soaks.
