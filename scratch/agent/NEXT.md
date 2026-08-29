# NEXT work unit — obtain an independent M5 upstream handoff source

HYPOTHESIS-ID: m5-audio-route-upstream-retail-boundary

## Single work unit

Human-provide or restore one actionable independent source for the missing
640-to-1024 handoff: an equivalent generated body/disassembly, or a newly
static-selected retail PC outside the closed wrapper/callsite set. Do not
build, add a port probe, or change audio/route behavior before that source
exists.

## Competing hypotheses

- H-RetailNewEdge: independent static evidence identifies one new
  transition-capable retail instruction outside the rejected set.
- H-SnapshotRestored: a complete equivalent generated/disassembly source
  makes the pending-to-descriptor edge mechanically enumerable.
- H-StaticInsufficient: no independent source or new edge is available; the
  route remains blocked pending a supplied artifact.

## Discriminating measurement

Run the bounded census below after the source is supplied. A new exact PC
selects H-RetailNewEdge; a complete body/data flow selects H-SnapshotRestored;
continued absence selects H-StaticInsufficient. The falsifier for the current
blocking explanation is the same census rerun with the supplied artifact in
the searched trees.

## Exact command

```sh
rg -n '80128E90|8012A86[245]|8013.*73(70|40)|requestViFeatureChange|applyPendingViChanges|selectAndApplyViMode|800356AC|80035788' /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp --glob '!PORTING-STATE.md' --glob '!scratch/agent/soak_results/**'
```

If H-RetailNewEdge is selected, the following iteration must run one oracle
watch for that exact PC with whole-RDRAM and title/hangar controls.
