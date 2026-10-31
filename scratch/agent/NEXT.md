# G1(d): level7 — what registers 20_Dest_Tanks_* (slot word DAT+6)?
HYPOTHESIS-ID: g1-coverage-cd

s6685: original lookup finds 20_Dest_Tanks_01 (desc=DAT+05D0, HP50) but its
slot word desc+6 stays FFFF for VI6888..12288 (~90 s flight, 3 arms); census
finds 0 live counter20 nodes. Request correctly withheld.

Hypotheses:
H-trigger: tanks spawn from a level7 script/trigger (zone, timer, prior
  objective) the scripted route never reaches.
H-proximity: tanks register only within a player distance (streaming).
H-never: the 05D0/0754/0818 items are only registered via some other path
  (e.g. spawned as a different object type that does not write DAT+6).
DISCRIMINATOR (static first, original ELF + retail ROM only): enumerate
original writers of the halfword at DAT item +6 (sh ...,6(desc) after a
registry slot allocate) and every lv7 script/trigger reference to the tank
item offsets or names. Classify the spawn condition: trigger state, distance
test, or none. Then ONE run (existing --level 7 runner) that additionally
logs the slot words of 05D0/0754/0818 and the identified trigger/distance
input each 300 VI, over a longer hold, with the existing mark-all control.
Admission stays: owned + surviving + HP>10 + detail observed; API10 only.
No FFFF fallback, lethal request, direct stores, threshold or win.

Commands:
    python3 tools/g1_dat_inventory.py --level 7 --check-level7
    python3 tools/g1_objective_response_run.py --self-test
    python3 tools/apply_s6657_objective_response.py   # applies to ../N64Recomp/RecompiledFuncs
    cmake --build build --target RogueSquadron64Recomp -j6
    /usr/sbin/ioreg -n Root -d1 | grep CGSSessionScreenIsLocked   # absent = unlocked
    python3 tools/g1_objective_response_run.py s6686_lvl7_spawn --level 7
