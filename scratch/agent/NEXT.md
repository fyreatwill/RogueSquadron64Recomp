# NEXT work unit (s1126)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the producer and boot-time value of
`gameConfig+0x44`, which feeds the selector bits in
`buildAndRegisterDefaultMaterial` at `0x80017B88`. The prior audit established
that `thread3_video_handle` loads this field and forwards it through
`initVideoBootWrapper`; the retail width-320 path must choose copied-record
offsets `0x00/0x50/0xA0` (indices `{0,2,4,6}`).

Competing hypotheses and discriminator:

- H-config-field-literal: `gameConfig+0x44` is initialized with a concrete
  value before `thread3_video_handle`, selecting one of `{0,2,4,6}`.
- H-config-field-runtime: the field is populated or merged from runtime or
  non-generated display/config state, so static source cannot resolve its
  initial selector value.
- H-config-field-non320: the field's concrete value selects a non-320 record,
  requiring reconciliation with the independent retail width-320 observation.

Discriminator: enumerate all generated, host, patch, companion, and ROM/data
initialization paths for the game-config object and offset `+0x44`, then
decode bits 2, 3, 4, 5, 7, and 8 at the boot call. A concrete pre-call store
selecting `{0,2,4,6}` proves H-config-field-literal; a runtime/non-generated
producer proves H-config-field-runtime; a concrete non-320 value requires
reconciling or overturning the retail observation. Do not build or run.

Exact commands:

```sh
rg -n -C 25 'thread3_video_handle|0x800012B8|0x800012BC|0x44\\(\\$a3\\)|getGameConfig' ../N64Recomp/RecompiledFuncs/funcs_0.c
rg -n -C 20 '0x8011.*63E4|gameConfig|0x44|thread3_video_handle' ../N64Recomp/RecompiledFuncs/funcs_0.c ../N64Recomp/RecompiledFuncs/funcs_*.c src patches syms
rg -n -C 10 'getGameConfig|D_8011.*63E|0x801163E|0x44' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/mips_to_c
```

Use bounded `sed` windows around the config getter, all exact `+0x44` stores,
and the boot call. Append the producer/value classification to the ledger and
current truth. No mitigation is authorized.
