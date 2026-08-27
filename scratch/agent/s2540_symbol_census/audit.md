# s2540 generated-symbol census: `0x8009D7CC`

## Work unit

The bounded sweep target was `0x8009D7CC`. The discriminator was whether the
complete generated span had an exact human mapping, was a boundary fragment,
or had no defensible mapping.

## Region table

| placeholder | complete span | generated body | companion/project evidence | result |
|---|---|---|---|---|
| `fake_func_8009D7CC` | `0x8009D7CC–0x8009D7CF` (4 bytes) | `mtc1 $zero,$f4` | `main_overlay.txt` retains the fake symbol; `filterVoiceSampleBlock` independently starts at `0x8009D7D0`; no exact-address, source, m2c, or caller match exists | `H-no-match`; unchanged |

## Evidence

The active generated implementation in `RecompiledFuncs/funcs_27.c` contains
only `ctx->f4.u32l = 0` for the four-byte span. The generated declaration and
overlay table preserve the same fake name and 4-byte size. The companion
symbol file places `filterVoiceSampleBlock` at the next instruction and has no
human symbol for `0x8009D7CC`. Repository searches across the companion
project's C/header/assembly sources found no exact-address definition or m2c
candidate; caller searches found calls to `filterVoiceSampleBlock`, not to the
four-byte fragment.

This is consistent with a function-boundary/preamble fragment, but the
available static evidence does not prove that it is independently callable or
that it belongs to `filterVoiceSampleBlock`. Renaming it would therefore be
speculative. No generated source, symbol input, runtime, or behavior changed.

## Commands

```sh
rg -n 'fake_func_8009D7CC|8009D7CC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
rg -n -C 8 'fake_func_8009D7CC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
find /Users/williambuckley/Documents/Tools/rogue_squadron64 -type f \( -name '*.c' -o -name '*.h' -o -name '*.inc.c' -o -name '*.s' \) -print0 | xargs -0 rg -n -i 'filterVoiceSampleBlock|fake_func_8009D7CC|8009D7CC'
```

