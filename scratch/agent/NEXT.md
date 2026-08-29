# NEXT work unit — audit 3D voice-list publication and traversal

HYPOTHESIS-ID: m3-voice-list-publication-bound

## Single work unit

M5 target-phase qualification is blocked pending a human-selected route or new
retail-grounded boundary. Do not repeat the two tested routes unchanged. Use
this unit to classify the remaining `tickAndReap3DAudioVoices` list-head guard
without launching the game.

Competing hypotheses and the discriminating measurement:

- `H-LegitimateSentinel`: all list-head publications preserve the companion's
  sentinel/invariant and the traversal has a finite source-visible exit.
- `H-BadProducer`: a reachable writer can publish an invalid node/head with an
  identifiable ordering edge.
- `H-Unbounded`: publication is legitimate but the generated walk has no
  defensible finite bound or termination invariant.

The discriminator is one joined static table containing every write to
`0x80153414`, every node next/prev dereference in the generated body, the loop
exit condition, and companion symbol/source matches. A complete legitimate
writer plus finite exit selects `H-LegitimateSentinel`; an invalid writer plus
ordering edge selects `H-BadProducer`; otherwise classify the missing proof as
`H-Unbounded` or leave it unclassified.

Exact commands:

```sh
rg -n 'tickAndReap3DAudioVoices|0x80153414|factor5RemoveListNode|reset3DAudioLists' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  RecompiledFuncs src docs --glob '!*.log' --glob '!PORTING-STATE.md'
sed -n '4180,4320p' scratch/agent/s389_verify/before_current_applied/funcs_26.c
rg -n '0x80153414|tickAndReap3DAudioVoices|factor5RemoveListNode|reset3DAudioLists' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '*.c' --glob '*.h' --glob '*.txt'
```

Expected outcome: one complete publication/traversal table that either proves
the sentinel and bound, identifies a named invalid producer and ordering edge,
or records the exact unresolved invariant for a later ground-truth request.
After a route selection, return to the existing contract-pair command from the
M5 plan.
