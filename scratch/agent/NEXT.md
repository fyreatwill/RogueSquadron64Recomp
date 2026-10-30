# Level-1 single-victim lethal-dose response
HYPOTHESIS-ID: g1-coverage-cd

s6660 completed one descriptor-targeted flight. Do not repeat that dose:
46 forces→23 exact projectile SENDs, but target health remained positive
(999→859 and400→322). Original transport code skips descriptor effects
while damage return>0. id10 mark-all and changing-value controls fired.
No named13/40/41 response, no win/progression, no full VERIFIED promotion.
Read CURRENT-TRUTH, NEXT, SOAK-RESULTS tail in order; maintenance at>60000.

ONE bounded change and ONE level1 flight: keep descriptor targeting, add
an opt-in single-victim damage-dose lever that exercises the actual death
branch. Do not directly write health/counters/Boolean6, force a win, steer,
or run repeat holds. Defaults and ordinary TELE remain unchanged.

Hypotheses:
- H-dose: a proven named-loss victim survives ordinary damage, but one
  accepted lethal message reaches the death branch, descriptor writer and
  callback readback. This establishes a loss response, not success progress.
- H-routing: the accepted victim's actual health actor differs from the
  assumed actor. Exact original load chain plus before/after actor identity
  selects this; repair the test join before interpreting behavior.
- H-effect: actual remaining health<=0 and death branch execute for the
  selected victim, yet its descriptor writer/readback does not respond.
  This requires same-run changing-value and eligibility controls; absent
  controls/route/death remain unknown, not broken-logic conclusions.

Ground truth BEFORE instrumentation (original ELF;40/28-line windows):
    cat scratch/agent/s6660_targeted/transport_damage_elf.txt
    cat scratch/agent/s6660_targeted/health_elf.txt
    cat scratch/agent/s6659_response/lv1_callback_elf.txt
    cat scratch/agent/s6659_response/lv1_friendlies_elf.txt
    sed -n '1,60p' scratch/agent/s6660_targeted/chains.tsv
    rg -n 'RECOMP_FUNC void npcGroundTransportUpdate|0x800DF830|0x800DF840|0x800DF8C8' ../N64Recomp/RecompiledFuncs/funcs_38.c
    rg -n 'rs6660_|rs6657_write|def apply' tools/apply_s6657_objective_response.py
    sed -n '30,35p' docs/debug-trace-env-vars.md
Original: health actor=NPC+38; message damage=lhu(message+6); call800F2120;
return>0 at800DF840 skips to800DF928; death loads descriptor+70/+74,
+78/+7C,+80/+84 then calls80065914 at800DF8C8. Counter writer8006594C/74.
NPC is node+4, descriptorNPC+34. Do NOT treat node+34 as descriptor.
Counter13 address80138090,40=801380FC,41=80138100; Boolean6=801388A5.
Friendlies saved=19-(40+13+41); c13>=5 fails; Boolean6 completes.

Implement the WHOLE table in one persistent adapter/build, not one join
field per session. Extend FILES/replay to funcs38 as necessary. Hook the
original damage call and return/death branch with selected NPC/node,
health actor, descriptor counter/delta, message identity/raw damage,
actual requested damage and returned HP, force seq/projectile/SEND VI,
actual counter PC/old/new and independent callback readback. Do not guess
health pointer layout: use original ELF health accessor and existing fixed
s5857 helper arithmetic (unsigned offsets once manufactured a4GiB read).

Use a new explicit opt-in env, e.g. ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1,
passed and hashed by the runner. In the existing on window: select ONE
actual accepted ground-transport counter13 target (nonzero delta, Boolean6
not set). First accepted hit uses original damage and must visibly reduce
positive HP (dose control). A subsequent accepted hit to the SAME live
node/NPC/descriptor may set only the call's requested damage register to
currentHealth+1, ONCE globally. This is a test input at the real hit path,
not a counter or health store. Log the change and original values. Exclude
all other victims from the lethal lever; continue mark-all eligibility
controls. Inhibit further forces immediately on a named changing store,
finish callback readback, then SIGKILL. Keep fallback c13>=3/Boolean6 and
5400-VI stops; no intentional failure/completion. If exact eligibility
cannot be established, do not apply the dose and classify the failed join.

Before build, write exact final lever/controls/stop design into this file.
Then:
    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    env ROGUESQ_OBJECTIVE_RESPONSE_LETHAL=1 python3 tools/g1_objective_response_run.py s6661_dose --level 1
    python3 tools/g1_objective_response_run.py s6661_dose --level 1 --analyze
Use fresh paths, unlocked screen, build/ROM and SIGKILL watchdog. No full
fixup on existing tree. If regen is needed: make_elf→N64Recomp→fixup→cmake.
Preserve lib worktrees; no export needed unless you edit them.

s6660 evidence: scratch/agent/m6/g1_lvl1s6660_targeted/ and
scratch/agent/s6660_targeted/.175.61s, VI5234..10634,0 crashes. Eight unique
named live/eligible identities per arm; candidate4096-row budgets reached,
so later unlogged identities stay unknown.46 exact force rows,23 SENDs:
14 id40 node8021b358/NPC8035ab5c/desc8031b278;9 id13
node8021b628/NPC8035b35c/desc80319af4. Six id10 readback changes0→5→6→6.
The health-parent association is currently single-source temporal/layout
support: legacy damage matching reports force_seq0 for actor subobjects.
Original ELF independently proves the damage/death-gate semantics.
