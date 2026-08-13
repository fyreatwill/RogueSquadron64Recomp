# `$ra=0x1DF4` provenance (s747)

Static only, plus a re-read of the already-collected s746 soak. No
rebuild, no IMEM DMA, no case widen. Sources: ROM `rogue_squadron.z64`,
generated `build/factor5_ucode/factor5_ucode_recompiled.c` /
`factor5_ucode_ovl12_recompiled.c` / ovl4 / ovl24, overlay table from
`docs/M3-OVL24-CONTINUATION-AUDIT.md`, and
`scratch/agent/soak_results/s746_ovl24_04ret_20260812-164346/run.log`.

## Verdict

**H-1df4-stale-ra SELECTED.**
**H-1df4-main-jal REFUTED.**
**H-1df4-window-still-ovl12 REFUTED.**
**H-1df4-ovl14 REFUTED** as owner of the `0x1DF4` jal-return. Overlay 14
is the *next* skipped image (`L_1268(r5=0x14)` dest `0x1DB0`), not a
`$ra=0x1DF4` writer.

The only `$ra=0x1DF4` writer in main, clip, ovl12, ovl14, ovl18, ovl24,
ovl28, and the full main text window is overlay 12's `jal L_122C` at
IMEM `0x1DEC` (ROM `0x266AC`). `L_122C` already returns successfully to
`OVL12_1DF4` while `0x153==0xC` (s746 `last_ovl=0x0C/0x1DF4`). The
`[clip-stray] tgt=0x1DF4 153=0x00 line=451` is a *later* `L_11B0` `jr`
of that leftover `$ra`, after the skipped ovl14 DMA falls through to
main `L_1DB0`, which stores `0` to `DMEM[0x153]` and jumps to `L_11B0`
without rewriting `$ra`.

Do not widen case `0x1DF4` to `153==0`. Main IMEM `0x1DF4` is
`lw $2, 4($1)` in the middle of the bootstrap reset. Next is an ovl14
route at dest `0x1DB0` when `153==0x14`, not an ovl12 widen.

**ORIGIN:** `$ra=0x1DF4` writer = `OVL12_1DD8` `jal L_122C` (ROM
`0x266AC`). `153=0` writer = main `L_1DB0` `sb $zero, 0x53($18)` with
`$18=0x100` (ROM `0x2634C`, IMEM `0x1DBC`), entered because dest
`0x1DB0` / `153==0x14` has no splice.

## 1. Every `$ra=0x1DF4` writer

Scan: every `jal` whose `pc+8 == 0x1DF4`, and every
`ori`/`addiu $ra, $zero, 0x1DF4`, across the packed window and every
`L_1268` overlay image.

| Image | ROM | IMEM dest | jal-return `0x1DF4` | `ori/addiu $ra, 0x1DF4` |
|---|---|---:|---|---|
| main window | `0x26340` | `0x1DB0` | none | none |
| main full text | `0x25610` | `0x1080` | none | none |
| ovl4 clip | `0x26420` | `0x1DB0` | none | none |
| ovl12 | `0x26670` | `0x1DB0` | IMEM `0x1DEC` `jal L_122C` | none |
| ovl14 | `0x26AB8` | `0x1DB0` | none | none |
| ovl18 | `0x26CD8` | `0x1DB0` | none | none |
| ovl24 | `0x27260` | `0x12A0` | none | none |
| ovl28 | `0x27348` | `0x1DB0` | none | none |

Generated C matches: `r31 = 0x1DF4` exists only at
`factor5_ucode_ovl12_recompiled.c:2143` and the spliced
`OVL12_1DD8` copy (`factor5_ucode_recompiled.c:3160`).

```
OVL12_1DD8:          # IMEM 0x1DD8, ROM 0x266A8
    # dest 0x380 color scratch, DRAM = lw 4($17)
    jal L_122C       # IMEM 0x1DEC, ROM 0x266AC
    r31 = 0x1DF4
OVL12_1DF4:          # IMEM 0x1DF4, ROM 0x266B4
    lw $22, 0($17)   # vector-prep; does not write $ra
    ...
    j L_1268
    ori $5, 0x14
```

`L_122C` has its own `jr $ra` at generated line 555. That return is
**not** the stray (stray line is 451). While `153==0xC` it routes to
`OVL12_1DF4` and is counted as `[ovl-route] res=0x0C tgt=0x1DF4`.

## 2. What sits at IMEM `0x1DF4` in each image

| Image | ROM `dest+0x44` | First word at `0x1DF4` | Role |
|---|---|---|---|
| main | `0x26384` | `8C220004` `lw $2, 4($1)` | mid `L_1DB0` bootstrap |
| ovl4 | `0x26464` | `005A3024` `and $6, $2, $26` | mid clip loop |
| ovl12 | `0x266B4` | `8E360000` `lw $22, 0($17)` | `OVL12_1DF4` vector-prep |
| ovl14 | `0x26AFC` | `9047FFFE` `lbu $7, -2($2)` | mid vector loop |

Main has no `L_1DF4` label. Jumping `0x1DF4` with `153==0` lands inside
the reset body. That is why a `153==0` widen is not a route.

## 3. Who enters `L_11B0` (line 451)

`L_11B0` is the command-chunk DMA helper: `lw $2, 0x30($18)`, DMA
`0x10F` bytes to DMEM `0x170`, `jr $ra`, delay `r17 += 8`.

| Caller | Sets `$ra` first? | Can `jr` `0x1DF4`? |
|---|---|---|
| `L_10E0` | yes, `ori $ra, 0x1088` | no |
| `L_12B8` | yes, `ori $ra, 0x1088` then `j L_11B4` | no |
| `L_12C4` | yes, `jal L_11B4` `$ra=0x12DC` | no |
| `L_1E5C` (tail of main `L_1DB0`) | **no** — `j L_11B0` | **yes** |

`L_122C` does not fall into `L_11B0`. The stray cannot be "the return
of `L_122C`". It is `L_1E5C` jumping to `L_11B0` with leftover `$ra`.

## 4. Who writes `DMEM[0x153] = 0`

Two stores in the generated main image:

| Site | Instruction | When |
|---|---|---|
| `L_1278` | `sb $5, 0x153` | overlay switch; `$5` is the new id |
| `L_1DB0` | `sb $zero, 0x53($18)` with `$18=0x100` | bootstrap reset |

ROM for the reset store: IMEM `0x1DB8` `34120100` `ori $18, 0x100`,
IMEM `0x1DBC` `A2400053` `sb $0, 0x53($18)` (ROM `0x26348` /
`0x2634C`). No overlay calls `L_1268` with `$5=0` except the boot
`L_125C` path (`ori $5, 0` at IMEM `0x1084`), which is the initial
resident-0 install, not the section-2 stray.

`OVL12_1DF4` does not write `0x153`. It leaves `$ra=0x1DF4` and
`j L_1268; ori $5, 0x14`. `L_1268` then stores `153=0x14`, saves
`$ra` to `0x16A`, skipped-DMA dest `0x1DB0`, and `L_1298` restores
`$ra` from `0x16A` (still `0x1DF4`) in the delay slot of `jr $3`.

Case `0x1DB0` only routes `153==0x4` / `0xC` / `0x28`. `153==0x14`
falls through to main `L_1DB0`, which writes `153=0` and `j L_11B0`.

```
OVL12_1DD8 jal L_122C ($ra=0x1DF4)
  → L_122C jr → OVL12_1DF4          # 153 still 0xC; last_ovl=0x0C/0x1DF4
  → L_1268(r5=0x14)                 # 153 := 0x14; 0x16A := 0x1DF4
  → L_1298 jr dest 0x1DB0           # $ra restored 0x1DF4; 153=0x14
  → no ovl14 splice → main L_1DB0   # sb 0 → 0x153
  → L_1E5C j L_11B0                 # $ra still 0x1DF4
  → L_11B0 jr → clip-stray 0x1DF4/00 line=451
```

## 5. Overlay 14 is the skipped dest, not the `$ra` writer

ovl14 ROM `0x26AB8`, dest `0x1DB0`, len `0x21F`. First word
`4A052955` (COP2), not clip and not TriGen. JALs are internal
(`0x1F14` ret `0x1E28`, `0x1F60` ret `0x1E94`/`0x1EEC`). Exit
`j L_1268; ori $5, 0x18` at IMEM `0x1F0C`. ovl18 (ROM `0x26CD8`)
is the successor and exits `ori $5, 0x10`.

Routing `0x1DF4` to an `OVL14_*` label would be a mis-splice: that
address is mid-loop in ovl14 (`lbu $7, -2($2)`). The missing route
is dest `0x1DB0` when `153==0x14`.

## 6. Live s746 (second line; same-run as the stray)

File: `scratch/agent/soak_results/s746_ovl24_04ret_20260812-164346/run.log`

| Measurement | n |
|---|---:|
| `[clip-stray]` all / `0x1DF4` / `153=0x00` / `line=451` | 3157 / 3157 / 3157 / 3157 |
| sec2 first-edge `[e9-prov-reset-predecessor]` | **61/61** `pred=target:0x1DB0,line:621,ra:0x1DF4,resident:0x14` |
| same rows, reset callback | `ra=0x1DF4 resident=0x00` (L_1DB0 already stored 0) |
| sec2 `last_ovl=0x0C/0x1DF4` | 61 |
| `[ovl-route] res=0x14` / `0x18` / `0x10` | **0** / 0 / 0 |
| UJ / CRASH | 0 / 0 |
| boot control `dl06=2/2/0` | 4/4 |

`line=621` is `L_1298` `jr $3`. `resident:0x14` is the value `L_1268`
wrote before the skipped DMA. The reset callback then sees `resident=0`
because `L_1DB0` has already executed `sb $zero, 0x53($18)`.

## 7. Outcomes vs NEXT.md

- only ovl12 writes `$ra=0x1DF4`, and `L_11B0` is **not** the
  `L_122C` return — `L_122C` already returned to `OVL12_1DF4` with
  `153==0xC`. The stray is leftover `$ra` after skipped ovl14 →
  main `L_1DB0` → `L_1E5C`. **H-1df4-stale-ra SELECTED.** Named
  writers: `OVL12_1DD8` (`$ra`) and main `L_1DB0` (`153=0`).
- main never writes `$ra=0x1DF4`. **H-1df4-main-jal REFUTED.**
- `153=0` is a deliberate `L_1DB0` store, not a desynced ovl12
  window. IMEM `0x1DF4` is main bytes. **H-1df4-window-still-ovl12
  REFUTED.** Do not widen.
- ovl14 does not own `0x1DF4`. **H-1df4-ovl14 REFUTED** as a
  `0x1DF4` splice. It remains the next dest-`0x1DB0` sibling.

Routing ovl14 will stop this fall-through. ovl14 then exits to ovl18
(`r5=0x18`); that sibling is the residual after the ovl14 route, not
part of this unit.

**s748 live:** fixup 6g landed that route. Soak
`s748_ovl14_route_20260812-171325` (350 s, CRASH=0): `last_ovl=0x14/*`
61/64, pred `resident:0x14` → 0, all 61 first-edge preds
`resident:0x18`. Stray `0x1DF4/00` 3157→1395 (no-jal ovl14 path);
new `0x1E28/00=1200` `0x1EEC/00=77`. E9 match still 3/64. Next is
ovl18 dest-`0x1DB0` when `153==0x18`.

**s749 live:** fixup 6h landed the ovl18 route. Soak
`s749_ovl18_route_20260812-172852` (348 s, CRASH=0): `last_ovl=0x18/*`
183/192, pred `resident:0x18` → 0, all 183 first-edge preds
`resident:0x10`. New leftover `$ra=0x1F40` stray (ovl18 jal
return). E9 still the boot-shaped triplet. Next is ovl10 dest-
`0x1DB0` when `153==0x10`.

**s750 live:** fixup 6i landed the ovl10 dest route. Soak
`s750_ovl10_route_20260812-174446` (331 s, wrapper rc=3 from a
late SIGSEGV): `last_ovl=0x10/0x1DB0` 122/128, leftover `/00`
`L_11B0` strays → 0. New stray is `0x1F40/10` n=5501 line=1421
(`L_1778` `jr $30`), not leftover `$ra`. Writer is ovl10
`ori $30, 0x1F40; j L_15D0` at IMEM `0x1F38`. Next is an
`OVL10_1F40` handshake route, not ovl 0x1C and not an OVL18 widen.
