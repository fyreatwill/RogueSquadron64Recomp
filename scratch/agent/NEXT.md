# Level-2 objective response
HYPOTHESIS-ID: g1-coverage-cd

s6661 closes the level1 named loss-response unit: ordinary seq4 HP390→386,
then exact later seq6 requested387, HP386→−1, death effect→writer8006594C
id13 0→1→callback at+4 VI. No repeat dose, success claim or full VERIFIED.
Read CURRENT-TRUTH,NEXT,SOAK-RESULTS tail first; maintenance at>60000 bytes.

ONE bounded adapter extension and ONE forced-route level2 flight. First
establish level2 counter/Boolean meanings from original ELF; do not borrow
level1 ids/thresholds. Ground truth commands (save outputs, bounded reads):
    mkdir -p scratch/agent/s6662_lvl2
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80101EF4 0x80102A98 > scratch/agent/s6662_lvl2/callback_elf.txt
    rg -n '800C759C|800C761C|800C7738|800C776C|800C76B0' scratch/agent/s6662_lvl2/callback_elf.txt
    python3 tools/disasm_mips_elf.py ../rogue_squadron64/build/roguesquadron.elf 0x80102A6C 0x80102A98
    rg -n 'RECOMP_FUNC void lv2_checkComplexObjectives|RECOMP_FUNC void lv2_calculateFriendliesSaved' ../N64Recomp/RecompiledFuncs/funcs_4[34].c
Read <=60-line windows around the ELF hits. Friendlies callback lead is
1−counter40 (generated source, confirm original). Read the actual end/fail
gates before allowing a forced hit; exclude completion Boolean setters.
Original descriptor/damage references remain s6661_dose/*_elf.txt.

Hypotheses and discriminator:
- H-response: exact accepted victim/descriptor hit invokes a level2-named
  objective writer and callback readback. Full force→SEND→actor HP→effect
  →actual store→readback selects it; count activity alone does not.
- H-dose: exact relevant accepted hits reduce HP but return positive and
  skip death effects. Original branch plus actual positive returns selects
  survival, not broken objective logic.
- H-routing: named live victims never become eligible or accepted, or the
  health actor/descriptor join differs. Whole live/candidate/SEND/actor table
  with mark-all eligibility control selects the first missing boundary.
No null without changing-value and same-phase eligibility controls.

Extend tools/apply_s6657_objective_response.py and runner --level2 with all
counters/readbacks, relevant Boolean gates, live census, candidates, exact
force/SEND identities, actual health actor and effect-call victim context.
Replay extra generated files as needed. Preserve level0/1 and ordinary TELE
behavior. Start with ordinary damage only; LETHAL must remain disabled on
level2 unless independent original semantics establish a single loss target
that cannot trigger a win/failure. If no safe target exists, implement the
whole ordinary-dose table and report the selected boundary honestly.
Natural/off then forced/on in one flight; stop further forcing on first
named changing store and finish callback readback. No direct health/counter
stores, intentional win/failure, steering, aim, progression or repeat holds.
Before build rewrite this file with final targets, exact gates and controls.

    python3 tools/apply_s6657_objective_response.py
    cmake --build build --target RogueSquadron64Recomp -j5
    /usr/sbin/ioreg -n Root -d1 | rg 'CGSSessionScreenIsLocked'
    python3 tools/g1_objective_response_run.py s6662_lvl2 --level 2
    python3 tools/g1_objective_response_run.py s6662_lvl2 --level 2 --analyze
Fresh paths, unlocked screen, build/ROM, SIGKILL watchdog. Do not full-fixup
an existing tree; regen only in prescribed order if necessary. Preserve lib.

Current evidence: scratch/agent/m6/g1_lvl1s6661_dose/ and
scratch/agent/s6661_dose/chain.json. 128.32s, VI5265..7748, 0 crashes.
The early readback stop intentionally omits arm2. No queued soak additions.
