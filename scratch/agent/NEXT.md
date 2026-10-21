# NEXT: name the caller of spawnSceneDebrisAndEffectCluster

Do not rerun the bit1/lives soak. s5773 closed it: on the level-select route
with godmode off, all 5 life losses are bit1 at 0x800B1140, then
requestMissionTransitionMode(1), then lives[0x80130B10] N->N-1. The store
immediately before each bit1 is spawnSceneDebrisAndEffectCluster at
0x800B0348 (player slot 0x80137DBC, halfword becomes 0x0190, includes kill
bit 0x10). spawnNpcDestructionDebris (bit 0x8) is not the predecessor.

The single work unit is to name who calls spawnSceneDebrisAndEffectCluster
on that player slot. Static census first, in the generated tree. Find the
function entry (not 0x800B0348; that is the sh inside it) and every direct
jal to that entry. Only if the jal list is empty or ambiguous, add one
entry log that stamps rs64_s5773_ord/ms and the slot pointer, and rerun
scratch/agent/s5773_bit1lives.sh. Do not add a new join field if the static
jal list already names a single caller.

Competing hypotheses and the discriminating measurement:

- H1: one direct caller (collision or terrain) invokes it immediately before
  each 0x190 store. Evidence: exactly one jal site, and if a runtime log is
  still required its timestamp sits just before each [killset] pc=0x800B0348
  on slot 0x80137DBC.
- H2: several direct callers, only one of which precedes the player-slot
  deaths. Evidence: the entry log's caller PC (or a per-site counter) is the
  same site for all 5 deaths and the other sites stay at zero during the
  mission phase.
- H3: no direct jal; dispatch is a function pointer. Evidence: zero jal
  sites. Then the discriminator is the jalr table or a host backtrace at
  the entry, not another flag watch.

Require the same positive controls before using a runtime result: mission
origin, [livesctl] mission, and at least one real 3->2 lives decrement.
A null caller log with no lives decrement is void.

```zsh
python3 - << 'PY'
# print the RECOMP_FUNC that contains the sh at 0x800B0348, then count jal to its entry
PY
```

HYPOTHESIS-ID: g1-debris-caller
