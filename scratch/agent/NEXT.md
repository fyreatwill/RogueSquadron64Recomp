# NEXT work unit (s2687) — audit the M5 mixer callback boundary

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit of `initN64RspMixer` and the callback table at
`0x801499D0..0x801499E0`, then follow every named callback consumer far enough
to determine whether it is the first service boundary after the voice object's
`+0x140` mixed output. Use companion address/name evidence and generated
callers. Do not add runtime watches, writeback, remaps, or mitigation from
unresolved pointer shapes.

## Competing hypotheses and discriminator

- `H-mixer-publish`: the callback table or its consumers names a legitimate
  destination and ordering edge from rendered voice output toward PCM/AI.
- `H-service-boundary`: the path reaches a service/slot boundary but the
  publication destination remains outside the audited caller.
- `H-unresolved-address`: the table is initialization-only or its callbacks do
  not consume the rendered voice object, so no legitimate publication edge is
  named.

The discriminator is a complete callback/destination table for all eight table
entries: each outcome must identify the callback writer, destination, payload
polarity, and ordering relation, or explicitly show which field is absent.

## Ground-truth prerequisite

No runtime watch, build, or soak is authorized until the static table names a
ground-truth target.

## Exact commands

1. `rg -n -H 'initN64RspMixer|0x801499D0|0x801499E0|0x8009189C' ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows for the initializer and every callback consumer; use companion names/source matches for each entry.
3. Record the complete eight-entry destination/order table and selected hypothesis in the ledger.
