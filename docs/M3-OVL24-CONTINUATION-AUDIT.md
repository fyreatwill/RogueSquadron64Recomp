# `L_1268` continuation overlays 0x14 / 0x24 (s742)

Static only. No rebuild, no splice, no game run. Sources: ROM
`build/rogue_squadron.z64`, ucode data at `0x39900`,
`factor5_rsp.toml` (`text_offset=0x25610`, `text_address=0x04001080`),
generated `build/factor5_ucode/factor5_ucode_recompiled.c` and
`factor5_ucode_ovl12_recompiled.c`, `dma_rdram_to_dmem` in
`lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp`, and
GLideN64 `F5Rogue.cpp` `F3DSWRS_TriGen` (`PC += 32` at line 1044).

## Verdict

**H-ovl24-skipped-imem SELECTED.**
**H-ovl14-window-collision** is a real sibling image but cannot explain
the dominant `L_1F64` exits.
**H-r17-not-advanced** is the skip consequence of losing the
`0x24 → 0x28` chain, not a third writer: overlay 24 never does
`r17 += 32`; overlay 28 does.

The skipped IMEM writer of the post-s739 UJ storm is overlay **0x24**
(ROM `0x27260`, dest `0x12A0`). `jr 0x12A0` lands in main `L_12A0`
(DL push), which treats TriGen `w1` (`r20`) as a child display list.
The GLideN64 extra `PC += 32` lives in overlay **0x28** (ROM `0x27348`,
dest `0x1DB0`, 0x1B B): `addiu $17, $17, 32` then a restore-DMA of
main `L_12A0`. That DMA is also skipped.

Do not permanently splice overlay 24 over `L_12A0`. Hardware overlay 28
restores that image because overlay 24 occupies the same IMEM range as
DL-push / EndDL. Fixup 6c is a route swap, not a resident overwrite.

## 1. Overlay table (ROM `0x39900`, two independent reads)

`L_1268` does `r4 = lhu 0x7A($5)`, `r3 = r4 >> 12`, delay-slot
`r3 = lhu 0x76($3)`, then `L_122C` `SET_DMA_MEM(r3)`.

| DMEM | word |
|---|---|
| `0x76` | `0x1DB0` |
| `0x78` | `0x12A0` |

Matches the s46 capture `tbl76=1DB0,12A0,...`.

| `r5` | desc | `r3` | dest | len | dram off | ROM (`0x25610+off`) |
|---:|---:|---:|---:|---:|---:|---|
| `0x0C` | `0x022F` | 0 | `0x1DB0` | `0x22F` | `0x1060` | `0x26670` (spliced ovl12) |
| `0x14` | `0x021F` | 0 | `0x1DB0` | `0x21F` | `0x14A8` | `0x26AB8` |
| `0x18` | `0x021F` | 0 | `0x1DB0` | `0x21F` | `0x16C8` | `0x26CD8` (ovl14 successor) |
| `0x24` | `0x20E3` | 2 | `0x12A0` | `0x0E3` | `0x1C50` | `0x27260` |
| `0x28` | `0x001B` | 0 | `0x1DB0` | `0x01B` | `0x1D38` | `0x27348` |

`0x1DB0 & 0x1000` and `0x12A0 & 0x1000` are both set.
`dma_rdram_to_dmem` returns without writing. Independent second line:
generated `L_122C` really does `SET_DMA_MEM(r3)` with that delay-slot
load, so both continuation DMAs and overlay 28's window DMA skip.

## 2. Overlay 24 vs main `L_12A0`

Main `L_12A0` is ROM `0x25830` (`0x25610 + (0x12A0-0x1080)`), first
word `0x8E43005C` (`lw $3, 0x5C($18)`). NEXT.md's `0x257D0` is the
`L_122C` / `L_1268` helper, 0x60 bytes earlier; the 215/227 figure
there compared the wrong image. vs the toml address: **212/227**
bytes differ.

| IMEM | ovl24 (ROM `0x27260`) | main (ROM `0x25830`) |
|---|---|---|
| `0x12A0` | `ori $10, $zero, 4` | `lw $3, 0x5C($18)` |
| `0x12A4` | `j L_15D0` | `lbu $2, 0x52($18)` |
| `0x12A8` | `ori $30, $zero, 0x12AC` | `sw $3, 0x650($2)` |

Overlay 24 is not a DL-push variant. It handshakes into the shared
`L_15D0` vertex helper (`jal L_1780` / load `$v8..` from `0x610`)
with `$30` as the return into its own body, then copies inline words
at `r17+4 / +8 / +12 / +16` into DMEM `0x670 / 0x698 / 0x6C0 / 0x6E8`
via an in-overlay `L_136C`, emits through `L_1358` / `L_17F0` /
`L_112C` (RDP submit), and exits `j L_1268; ori $5, 0x28`.

Main `L_12A0` saves the parent PC/chunk, increments depth, and
`j L_11B4` with `r2 = r20`. After a skipped overlay-24 DMA that is
TriGen `w1` used as a child display-list address.

## 3. Overlay 14 vs the `0x1DB0` window

| Image | First instruction at `0x1DB0` | Diff vs ovl14 |
|---|---|---|
| ovl14 ROM `0x26AB8` | COP2 `0x4A052955` (vector) | — |
| ovl12 ROM `0x26670` | `lbu $4, -6($17)` (TriGen flag) | 503/543 |
| ovl4 ROM `0x26420` | `sh $ra, 0x50($18)` (clip) | 507/543 |
| packed window `0x26340` | zeros then bootstrap reset | 509/543 |

Overlay 14 is not clip and not TriGen. It runs a vector loop
(`jal 0x1F14` is inside its own image) and exits
`j L_1268; ori $5, 0x18`. It does not write `r17`. It cannot be the
~31k `L_1F64` continuation (`r5=0x24`). It is the rare bit-1-clear
path's next overlay, also skipped into the spliced ovl12 window.

## 4. GLideN64 `PC += 32` vs `r17`

`F3DSWRS_TriGen` reads `_params` from `RDRAM[PC]` (the 32 extra
bytes after the 8-byte header; dispatcher already did `r17 += 8`)
and then `RSP.PC[RSP.PCi] += 32`. Reference total 40.

Overlay 12 (`L_1DB0` / `L_1F64`) uses `r17` as a base
(`-6`, `+0..+0x1E`) and never increments it. Overlay 24 uses the
same base (`+4..+16`, `-6`) and never increments it.

Overlay 28, ROM `0x27348`, loaded at `0x1DB0`:

```
1DB0  addiu $17, $17, 32
1DB4  lw    $2, 0x10($1)        # OSTask.ucode
1DB8  ori   $3, $zero, 0x12A0   # IMEM dest
1DBC  ori   $4, $zero, 0x32F    # inclusive length → 0x330 B
1DC0  addiu $2, $2, 0x220       # ROM 0x25830 = main L_12A0
1DC4  j     L_122C
1DC8  ori   $31, $zero, 0x10D8  # fetch continuation
```

That `+32` is the reference extra advance. The following DMA writes
main `L_12A0` back over `0x12A0..0x15CF` (first word independently
`0x8E43005C`) so the next `0x06` sees DL-push again. Both the window
DMA that would install overlay 28 and this restore DMA target IMEM
and skip.

## 5. Dominant chain and what the skip executes

```
0x05 → L_15AC → L_1268(r5=0x0C) → spliced ovl12 @ 0x1DB0
  bit1 set (s740: ~31k): L_1F64 → L_1268(r5=0x24)
    intended: ovl24 @ 0x12A0 → emit → L_1268(r5=0x28)
              ovl28 @ 0x1DB0 → r17+=32 → restore L_12A0 → L_10D8
    actual:   skip, jr 0x12A0 → main DL-push(r20=TriGen w1)
  bit1 clear (s740: 0x1DD8 n=2 / 0x1DF4 n=1; s746 last_ovl 0x0C/0x1DF4 61/64):
    L_1268(r5=0x14)
    intended: ovl14 @ 0x1DB0 → L_1268(r5=0x18)
    actual:   skip, jr 0x1DB0 with 153=0x14 → main L_1DB0
              (case 0x1DB0 does not route 0x14; s747)
```

## 6. Outcomes vs NEXT.md

- ovl24 ≠ main `L_12A0` and ovl24 is the emit step →
  **H-ovl24-skipped-imem SELECTED.** Named writers: overlay 24
  (emit / UJ cause) and overlay 28 (`r17 += 32` / restore).
- ovl24 is not a DL-push variant. Overlay 14 is the rare-path
  continuation, not the ~31k writer.
- ovl24 does not `r17 += 32`. Overlay 28 does. H-r17-not-advanced
  is what the skip drops, not a separate missing add in overlay 12
  or 24.

**s743 live:** fixup 6c landed that route. Soak
`s743_ovl24_route_20260812-160417` (349 s, CRASH=0): ovl24+ovl28
LIVE, UJ 2931→0, 0x06 push/pop/resume still 2/2/2, dest-`0x12A0`
`L_1298` resident other=0. Sec2 E9 match stayed 3/64. Residual
`[clip-stray] tgt=0x1364 153=0x04` (n=4434) is the ovl24 `jal L_17F0`
return hitting the new case while clip is resident.

**s744 live:** static + soak
`s744_clip_stray_1364_pred_20260812-162040` (349 s, CRASH=0).
Clip C has no `0x1364`. Lifetime `jal17f0=j1364=64192`,
`clip1e48_1364=res04=4452`, res24=59740, oth=0. Two classes only:
`L_1DA8` res=0x24 (reject, routes) and `CLIP_1E48` res=0x04
last_ovl=`0x04/0x1DB0` (stray). **H-l17f0-dispatches-clip SELECTED.**
**H-clip-uses-1364 / H-stale-ra REFUTED.** Writer is `CLIP_1E48` `jr`
of the `OVL24_135C` jal return after `L_1268` sets `0x153=4`.
Legitimate; IMEM `0x1364` remains ovl24 (clip dest `0x1DB0`). Next
is the 0x04 arm on case `0x1364`.
