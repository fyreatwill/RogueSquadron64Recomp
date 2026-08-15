# NEXT work unit (s1232)

HYPOTHESIS-ID: retail-entry-boundary

Run one bounded static provenance audit of the retail-entry boundary that
remains after the EEPROM comparison: enumerate every generated read and write
of the boot state triplet at `0x80130B30..0x80130B32` and every consumer of the
`mainGameLoop` handoff, then reconcile those sites against the companion
decomp symbols and the ROM-backed boot data. Do not build or run; this is one
ranked source census, not a new runtime probe.

Competing hypotheses and discriminator:

- H1: a generated producer outside the already audited idle/save chain writes
  the triplet or callback handoff and can explain the missing retail entry.
- H2: all producers are already known reset/save/default paths, so the missing
  event is outside the generated boot path and needs a new external lead.
- H3: the address identity or companion mapping is wrong, shown by a
  consistent disagreement between generated addresses, ROM bytes, and symbols.

Discriminator: a complete address-and-consumer table. A reachable, previously
unknown producer selects H1; a complete known-producer table with matching ROM
callback provenance selects H2; any address/symbol disagreement selects H3.

Exact commands:

```
rg -n -C 4 '80130B30|80130B31|80130B32|D_80130B10|mainGameLoop|gBootConfig|80037560' RecompiledFuncs tools docs
rg -n -C 3 '80130B30|80130B31|80130B32|80037560|mainGameLoop' syms rogue_squadron64 2>/dev/null
rg -n -C 3 '8003DFA0|80037564|mainBootstrapWorker|registerServiceWorker|thread3_video_handle' RecompiledFuncs tools docs
```

Record each site as read, write, ROM initializer, or indirect handoff, and
state whether it is reachable before `mainGameLoop`.
