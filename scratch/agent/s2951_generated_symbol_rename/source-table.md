# s2951 source table — `0x80099FDC`

## Competing hypotheses

- H-Callable: a standalone CPU function exists at this address.
- H-Fragment: the placeholder is an executable split/fixup record whose
  callable status is not independently established; preserve its name.
- H-DataGap: the record is mechanically proven non-callable and can be
  renamed `data_gap_80099FDC`.

## Evidence

| Check | Result |
|---|---|
| Project symbol span | `fake_func_80099FDC`, `0x80099FDC`, size `0x4`; the next CPU entry is `findVoiceSlotByAge` at `0x8009AF60`. |
| Exact generated body | `funcs_26.c` starts at `0x80099FDC` with `bne $v0,$zero,0x80099FEC`; its delay slot at `0x80099FE0` is the first word of `aspMain` text. The generated record then continues through `0x8009AF5C`, decoding RSP microcode as CPU instructions, so the generated extent is not a callable CPU body. |
| Boundary evidence | Companion data names `aspMainTextStart = 0x80099FE0`, size `0xF80`, ending at `0x8009AF60`; the next generated callable begins at that endpoint. |
| Companion naming | `rogue_squadron64/symbol_files/main_overlay.txt` retains `fake_func_80099FDC = 0x80099FDC` and separately names `aspMainTextStart`; it supplies no real CPU-function name. |
| Caller evidence | No generated `jal 0x80099FDC` or independent call-site lookup was found. |
| ROM semantic check | The retail word at file offset `0x9ABDC` is the branch `0x14400003`; the following `0x40065800` is `mfc0 $a2, Compare`, matching the start of `aspMain` text. |

## Classification

H-Fragment is selected. H-Callable is ruled out because the next three
instructions are the delay slot and entry of RSP text, and no callable
boundary or caller exists. H-DataGap is not selected: the word is a real
branch in the ROM stream and the independent map intentionally preserves it
as an already-fake record rather than declaring it data. Keep
`fake_func_80099FDC` synchronized in the generated C/header, overlay table,
project TOML, and companion map.
