# NEXT work unit (s955)

Pre-run decision: ground-truth audit of the runtime callback entries used by
`runInMissionFrame`; do not build, run, or land a guard. The static arm in
s954 is complete and found no target-side non-frame `$sp` writer.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

The 144 direct callers and all statically addressed targets are frame-balanced
or leaf functions. `runInMissionFrame` still loads an indirect callback from
the runtime table beginning at `0x8010B350`, and that target/value lifecycle
could still mutate the shared context before a later dispatcher call.

Competing hypotheses:

- H-slotdispatcheriter-stacksp-indirect-corruption: a runtime callback in the
  table writes or fails to restore the shared guest `$sp`.
- H-slotdispatcheriter-stacksp-indirect-balanced: all runtime callbacks
  preserve the context, leaving no caller-side writer.
- H-slotdispatcheriter-stacksp-stub-artifact: a runtime callback is a known
  degenerate stub and is the corruption origin.
- H-slotdispatcheriter-stacksp-unclassified: callback writer/value provenance
  remains unresolved.

Discriminating measurement: use the retail oracle's physical-address watch to
record writes to callback entries `0x8010B350 + i*8` and the function-pointer
words at `+4`, with a whole-RDRAM positive control armed in the same run; then
cross-reference observed callback addresses against generated bodies and
`funcs.h`. A callback address with a non-frame `ctx->r29` write selects
indirect-corruption; only balanced observed callbacks select
indirect-balanced; a known stub selects stub-artifact; absent writer/value
coverage selects unclassified.

Exact starting commands:

`sed -n '1,220p' tools/oracle/README.md`

`rg -n "0x8010B350|runInMissionFrame|callback" tools/oracle docs ../rogue_squadron64/symbol_files/main_overlay.txt`

Arm a whole-RDRAM positive control and physical watches for
`0x8010B350..0x8010B6?` in the oracle recipe, run the retail ROM from the
documented boot/attract path, then inspect the callback writer PC and values.
Do not use the recomp runtime as ground truth for this table.
