# NEXT work unit — audit the pending-request-to-descriptor handoff

HYPOTHESIS-ID: m5-audio-route-upstream-retail-boundary

## Single work unit

Perform a bounded static audit of the handoff between the pending feature word
at `0x80128E90`, the mode-selection bytes/descriptor records used by
`selectAndApplyViMode`, and the VI consumer. Enumerate every generated/decomp
writer and reader in that data path, excluding the already exhausted wrapper
chain and closed direct callsites. Select exactly one new transition-capable
instruction for a later oracle capture; do not add a port probe or change
behavior in this unit.

## Competing hypotheses

- H-AlreadyEnumerated: all pending-word/descriptor writers and readers are
  already known and none is a transition-capable untested edge.
- H-NewStaticEdge: one untested instruction transfers the pending request into
  the descriptor/consumer path and supplies the next oracle PC.
- H-StaticInsufficient: the available generated/decomp evidence cannot
  distinguish the handoff or its instruction identity.

## Discriminating measurement

The complete census must include every generated/decomp reference to
`0x80128E90`, the selector bytes/descriptor bases in `selectAndApplyViMode`,
and the VI consumer handoff, with each writer/reader classified from its
surrounding control flow and known phase markers. One transition-capable edge
yields H-NewStaticEdge and one exact PC; all edges already classified yields
H-AlreadyEnumerated; missing or contradictory identity yields
H-StaticInsufficient.

## Exact commands

```
rg -n '80128E90|8012A86[245]|8013.*73(70|40)|requestViFeatureChange|applyPendingViChanges|selectAndApplyViMode|800356AC|80035788' /Users/williambuckley/Documents/Tools/rogue_squadron64 /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp --glob '!PORTING-STATE.md' --glob '!scratch/agent/soak_results/**'
rg -n '80128E90|8012A86[245]|8013.*73(70|40)|requestViFeatureChange|applyPendingViChanges|selectAndApplyViMode|800356AC|80035788' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s390_verify --glob '*.c' --glob '*.h' --glob '*.toml' --glob '*.txt'
```

Record the complete caller list and the selected classification in a new
`scratch/agent/s3132_m5_vi_caller_audit.md`. If H-NewStaticCaller is selected,
the following iteration must run one oracle watch for that exact PC with the
same whole-RDRAM, title, and hangar controls.
