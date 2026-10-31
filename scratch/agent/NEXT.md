# G1(d): level8 named objective contract + per-target spawn path
HYPOTHESIS-ID: g1-coverage-cd

Level7 counter20 is parked (s6686): tanks are grid items that spawn only when
the craft is within 48 XZ units (updateActiveGridCellState 80047368); the
scripted route stays >=63 units away. Steering there is owner playtest.

Unit: static contract for lv8_checkComplexObjectives (original ELF 80104AA0)
using the s6684 method (tools/g1_dat_inventory.py, retail ROM + original ELF):
counters/Booleans read, thresholds, latches, failure calls; named DAT targets
whose damage effect feeds those counters; AND for each target its spawn path:
- parseDatSpawnPositions (80065790, table 8003BFF0[subtype]) category 1 =
  grid/proximity (<=48 units, +-10 cells), category 2 = condition list
  (801375D0, isDatItemConditionMet), +34&0x80 = spawned at load;
- isDatItemConditionMet gate fields (table 8003C140[subtype-12]).
Hypotheses for the live follow-up:
H-load: some level8 counter target is load-time/condition spawned -> ownable
  on the scripted route -> one API10 ordinary run is admissible.
H-prox: all level8 counter targets are proximity grid items -> check with
  ROGUESQ_LOG_GRIDSPAWN=1 whether the route enters 48 units before any run.
H-none: no counter-only damage target -> record the boundary, go to level9.

Commands:
    python3 tools/g1_dat_inventory.py --level 8 --output scratch/agent/s6687_level8.json
    mips64-elf-objdump -d --start-address=0x80104aa0 --stop-address=0x801051cc ../rogue_squadron64/build/roguesquadron.elf
    # if a live run is justified (runner supports levels 0..7 today; extend first):
    env ROGUESQ_LOG_GRIDSPAWN=1 python3 tools/g1_objective_response_run.py <tag> --level 8
Constraints: no FFFF fallback, lethal request, direct stores, threshold or win.
Note: --flight-vi >5400 is honoured only for level 2 in the C patch.
