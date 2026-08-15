# NEXT work unit (s1222)

HYPOTHESIS-ID: retail-entry-capability

The s1221 paired target set `gGameSettings+0x22` via physical
`0x130B60:0x00000100`. The write fired at VI 1, both arms passed whole-RDRAM
and VI controls, and callback plus VI-poll traces stayed at width
320/origin `0x006dd280` for 75 seconds. The recipe had no input plugin, so no
PIF button events were emitted in either arm. The mission sub-state target did
not change retail entry; no further documented state-byte write is justified.

Work unit: perform a bounded static census of the generated `mainGameLoop`
state-machine consumers and writers for `gGameSettings+0x20..0x22`, using the
companion architecture description to identify one independently justified
retail-entry route or prove these bytes are only transient flags. Do not build
or run the port and do not add another debugger write target in this unit.

Competing hypotheses and discriminator:
- H1: one of the three bytes is written by a producer that the oracle probes
  have not modeled; the census identifies its writer, timing, and a justified
  next target.
- H2: the bytes are only transient/cleared flags, and their consumers explain
  why direct writes at the 320 boundary do not persist into a later phase.
- H3: the generated boundary is incomplete or misnamed, so the apparent byte
  census cannot account for all state transitions and requires a regeneration
  or symbol-boundary check.

Discriminator: enumerate every generated load/store of the three byte offsets,
map each site to its containing function and control-flow role, and reconcile
the complete set against the `mainGameLoop` pseudocode. A complete producer /
consumer map selecting a new writer or target supports H1; a complete map with
only transient clear/set/consume edges supports H2; any missing or malformed
generated interval supports H3 and stops further oracle writes.

Exact commands:
```
rg -n "80130B[456789A-F]|130B[456789A-F]|gGameSettings|unk20|unk21|unk22" \
  RecompiledFuncs tools docs/game-architecture.md
rg -n "func_8003DFA0|mainGameLoop" RecompiledFuncs/funcs_*.c
```

Read bounded windows around every hit, classify all three byte offsets, and
record the complete table in the session ledger. If H1 selects a target, write
the next oracle recipe only after it has a positive-control plan.
