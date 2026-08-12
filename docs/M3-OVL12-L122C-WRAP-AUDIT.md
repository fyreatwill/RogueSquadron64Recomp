# Overlay-12 `L_122C` DMEM wrap audit (s741)

Static only. No rebuild, no resplice. Sources: generated
`build/factor5_ucode/factor5_ucode_ovl12_recompiled.c`,
`lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp`,
GLideN64 `F5Rogue.cpp` (gitignored reference), ROM ucode-data at
`0x39900`, and a re-count of
`scratch/agent/soak_results/s739_ovl12_splice_20260812-152309/run.log`.

## Verdict

**H-ovl12-dma-legit-payload SELECTED.**
**H-ovl12-dma-wrap-stomp REFUTED** for this runtime.
**H-ovl12-imem-gap REFUTED** (s740 + this re-count: 0 UJs in `0x1DB0..0x1FE0`).

`L_122C` dests `0x4E0` / `0x380` are TriGen vertex/color scratch. They do
not overlap command tables `0x64` / `0xD6` unless DMEM wraps, and our DMA
helper clamps instead of wrapping. Those two payload DMAs almost never run
on the live splice path. They are not the writer of the post-splice UJ storm.

## 1. DMEM map

| Address | Role | Source |
|---|---|---|
| `0x64 + (0..0x1FE)` | opcode table 2 (`0x40..0xBF`) | generated `L_10C8`; F5-UCODE-REFERENCE; `docs/factor5-ucode-dispatch.md` |
| `0xD6 + (0..0x1FE)` | opcode table 1 (`0x00..0x3F`) | generated `L_1090`; same |
| live table-1 slots | `0xD6..0x154` (op `0x00..0x3F`, idx `<= 0x7E`) | dispatch doc |
| `0x380` | TriGen color scratch | ovl12 `L_1DD8`; GLideN64 `params[3]` |
| `0x4E0` | TriGen vertex scratch | ovl12 `L_1DB0`; GLideN64 `params[2]` |

Table addressable ends: table 2 `0x262`, table 1 `0x2D4`. Both dests start
above `0x2D4`.

## 2. Size formula (both `jal 0x122C` sites)

Generated overlay-12 `L_1DB0` (not taken when `*(u8*)(r17-6) & 2`):

```
# dest 0x4E0, DRAM = lw 0(r17)
r4 = (lhu 8(r17) + 0x16) & 0xFF0
DO_DMA_READ(r4 - 1)          # hardware length is inclusive

# dest 0x380, DRAM = lw 4(r17)
r4 = (lhu 0xA(r17) + 0x13) & 0xFF0
DO_DMA_READ(r4 - 1)
```

GLideN64 `TriGen0001_PrepareVtxData` / `PrepareColorData` use the same
masks on `_params[4]` and read RDRAM directly (no DMEM dest). Max bytes
`0xFF0`.

| dest | max bytes | dest+max | hardware wrap onto `0x64`/`0xD6`? | our helper |
|---:|---:|---:|---|---|
| `0x4E0` | `0xFF0` | `0x14D0` | yes, wrap end `0x4D0` | clamp write `0x4E0..0xFFF` |
| `0x380` | `0xFF0` | `0x1370` | yes, wrap end `0x370` | clamp write `0x380..0xFFF` |

Need `len > 0xB20` (`0x4E0`) or `len > 0xC80` (`0x380`) before hardware
wrap even reaches the tables. Live sizes were not measured; they are not
required to refute the runtime-stomp claim.

## 3. `DO_DMA_READ` wrap semantics

`dma_rdram_to_dmem` (`rsp.hpp`):

```
dmem_addr &= 0xFFF;
if (dmem_addr + rd_len > 0x1000) rd_len = 0x1000 - dmem_addr;
```

RSP hardware wraps 4 KB DMEM. We truncate. Bit 12 still selects IMEM and
those DMAs return without writing. Therefore overlay-12 payload DMAs cannot
store into `0x000..0x37F` on this runtime, tables included.

Do not "fix" this to hardware wrap as a UJ mitigation: a max-size payload
*would* then land on the tables. That is the opposite of a named writer.

## 4. s740 UJ re-count (same log)

File: `scratch/agent/soak_results/s739_ovl12_splice_20260812-152309/run.log`

| class | n |
|---|---:|
| `Unhandled jump target` parsed | 2927 (s740 said 2935; 8 lines split by `[vi]`) |
| OOB (`>= 0x1000`) | 2017 |
| IMEM (`< 0x1000`) | 910 |
| overlay-12 window `0x1DB0..0x1FE0` | **0** |
| source `factor5_ucode_recompiled.c:238` (`lhu 0x64` table 2) | 2050 |
| source line 224 (`lhu 0xD6` table 1) | 760 |

Top targets: `0xFA92` 1051, `0x0000` 628, `0x7E00` 126, `0x4F42` 115.
Those are not generated handler PCs.

`[ovl-route]` residents: `0x0C` 155960, `0x04` 1033. No `0x14` / `0x24`
rows (the probe only fires on spliced window cases).

Overlay-12 targets: `0x1DB0` 31195, `0x1F9C/1FAC/1FBC/1FCC` ~31189 each
(the `L_1F64` bit-1 path), `0x1DD8` **2**, `0x1DF4` **1**. The two payload
DMAs ran about once in 353 s. They cannot explain ~2900 table-`jr` UJs.

`L_1F64` stores eight bytes at `0x280/288/290/298` via `L_1FD4`. That
range is above live table-1 (`..0x154`) and table-2 (`..0x262`). Not a
table stomp.

## 5. Named next writer (not acted on)

Both overlay-12 exits go to `L_1268` without touching `r17`:

| path | `r5` | ROM image | IMEM dest / `jr` |
|---|---:|---|---|
| DMA / vector loop | `0x14` | `0x26AB8` len `0x21F` (≠ ovl4/ovl12/window) | table `0x76[0] = 0x1DB0` |
| `L_1F64` (dominant) | `0x24` | `0x27260` len `0x0E3` | table `0x76+2 = 0x12A0` |

`0x1DB0` and `0x12A0` both have bit 12 set, so `dma_rdram_to_dmem` skips
the overlay swap. The `jr` then lands in the spliced ovl12 window or main
`L_12A0` (DL push). ovl24 vs main `@0x12A0` differs in 215/227 bytes;
ovl14 vs the ROM window differs in 509/543 bytes.

GLideN64 advances the TriGen PC by 32 after the 8-byte header. Overlay-12
has no `r17 +=` in `L_1DB0` / `L_1F64`. The next overlay is what must
consume the inline words.

## Outcomes vs NEXT.md

- Wrap-capable size + dests cover the tables + our DMA wraps → not met.
  Hardware *can* wrap at max size; we do not.
- Documented scratch + dests cannot reach the tables on this runtime →
  **H-ovl12-dma-wrap-stomp REFUTED.**
- Dominant UJs inside `0x1DB0..0x1FE0` → not met (0).
