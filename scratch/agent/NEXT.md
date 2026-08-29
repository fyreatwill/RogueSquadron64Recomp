# NEXT work unit — obtain the missing independent M5 handoff source

HYPOTHESIS-ID: m5-audio-route-upstream-retail-boundary

## Single work unit

The static census remains insufficient: the matching generated snapshot is
absent and the companion bodies are `INCLUDE_ASM` stubs. Obtain one
independent actionable source (a restored equivalent generated
body/disassembly or a newly static-selected retail PC outside the closed
wrapper/callsite set), then document exactly one candidate edge and its oracle
watch recipe. Do not add a port probe or change behavior before that source
exists.

## Competing hypotheses

- H-RetailNewEdge: independent static evidence identifies one new
  transition-capable retail instruction outside the rejected set.
- H-SnapshotRestored: a complete equivalent generated/disassembly source makes
  the pending-to-descriptor edge mechanically enumerable.
- H-StaticInsufficient: no independent source or new edge is available; this
  remains selected until a human supplies an artifact or source.

## Discriminating measurement

The next source must identify either one exact new PC or a complete body/data
flow. A new edge selects H-RetailNewEdge; a complete source selects
H-SnapshotRestored; continued absence remains H-StaticInsufficient and
requires a human-provided artifact. The single experiment that refutes that
blocking explanation is to rerun the same bounded census after placing the
artifact in the searched trees.

## Exact commands

```
grep -n '^## Session ' PORTING-STATE.md | tail -15
rg -n '80128E90|8012A86[245]|8013.*73(70|40)|requestViFeatureChange|applyPendingViChanges|selectAndApplyViMode|800356AC|80035788' /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp --glob '!PORTING-STATE.md' --glob '!scratch/agent/soak_results/**'
```

If H-RetailNewEdge is selected, the following iteration must run one oracle
watch for that exact PC with whole-RDRAM and title/hangar controls.
