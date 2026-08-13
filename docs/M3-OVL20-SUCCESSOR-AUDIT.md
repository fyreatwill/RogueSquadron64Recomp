# Overlay 0x20 successor of ovl1c (s758)

Static only. No rebuild, no splice, no game run. Sources: ROM
`build/rogue_squadron.z64`, ucode data at `0x39900`, generated
`OVL1C_1ECC` / main `L_12A0` / `OVL24_12A0` / overlay 28 at
`build/factor5_ucode/factor5_ucode_recompiled.c`,
`docs/M3-OVL24-CONTINUATION-AUDIT.md`, and GLideN64
`F3DSWRS_TriGen` (`PC += 32` at line 1044) as already cited there.

## Verdict

**H-ovl20-skipped-12a0-emit SELECTED.**
**H-ovl20-is-restore REFUTED.**
**H-ovl20-is-1db0-sibling REFUTED.**
**H-ovl20-not-the-e9-hole SELECTED** (static; live consume will
reconfirm E9 stays boot-shaped).

Overlay 0x20 is the emit step of the ovl14→18→10→1c chain. Table
desc `0x2157` independently decodes to dest `0x12A0`, len `0x157`,
DRAM off `0x1AF8`, image ROM `0x27108`. First word is
`lbu $2, -4($17)` (`0x9222FFFC`), not main `L_12A0`
(`lw $3, 0x5C($18)`), not ovl24 (`ori $10, 4; j L_15D0`), and not
ovl28 (`addiu $17, 32`). The body jals ovl1c's still-resident
trampoline at `0x1ED4` six times, then emits through shared
`L_17F0` / `L_112C`, and exits `j L_1268; ori $5, 0x28` — the same
successor as ovl24. Overlay 28 then does `r17 += 32` and restore-
DMAs main `L_12A0`.

Do not splice overlay 0x20 as a `0x1DB0` sibling. Do not overwrite
`L_12A0`. Live consume is a 6c-style dest-`0x12A0` route swap
(`153==0x20` → `OVL20_12A0`). The image has no FULL_SYNC producer;
E9 staying boot-shaped is expected.

## 1. Overlay table (ROM `0x39900`, two independent reads)

`L_1268` does `r4 = lhu 0x7A($5)`, `r3 = r4 >> 12`, delay-slot
`r3 = lhu 0x76($3)`, DRAM off `lhu 0x7C($5)`, then `L_122C`
`SET_DMA_MEM(r3)`.

| DMEM | word |
|---|---|
| `0x76` | `0x1DB0` |
| `0x78` | `0x12A0` |

Matches s46 `tbl76=1DB0,12A0,...` and the s742 table.

Independent dest decode for `r5=0x20`:

| Field | Where | Value |
|---|---|---|
| desc | ROM `0x3999A` = DMEM `0x7A+0x20` | `0x2157` |
| dest idx | `0x2157 >> 12` | `2` |
| dest | `lhu 0x76($3=2)` = DMEM `0x78` | `0x12A0` |
| len | `0x2157 & 0xFFF` | `0x157` (inclusive → `0x158` B) |
| dram off | ROM `0x3999C` = DMEM `0x7C+0x20` | `0x1AF8` |
| ROM | `0x25610 + 0x1AF8` | `0x27108` |

`0x12A0 & 0x1000` is set, so `dma_rdram_to_dmem` returns without
writing. Same skip class as ovl24.

Full slot row (r5 step 4) independently confirms dest class:

| `r5` | desc | dest | len | ROM | first word |
|---:|---:|---:|---:|---|---|
| `0x1C` | `0x020B` | `0x1DB0` | `0x20B` | `0x26EF8` | `lbu $8, -6($17)` (ovl1c) |
| **`0x20`** | **`0x2157`** | **`0x12A0`** | **`0x157`** | **`0x27108`** | **`lbu $2, -4($17)`** |
| `0x24` | `0x20E3` | `0x12A0` | `0x0E3` | `0x27260` | `ori $10, 4` (ovl24) |
| `0x28` | `0x001B` | `0x1DB0` | `0x01B` | `0x27348` | `addiu $17, 32` (ovl28) |

Dest decode does **not** land `0x1DB0`. H-ovl20-is-1db0-sibling is
refuted by the same `lhu 0x76($3)` rule that selected dest `0x12A0`
for ovl24.

## 2. First words vs main `L_12A0` and ovl24

| IMEM | ovl20 (ROM `0x27108`) | main (ROM `0x25830`) | ovl24 (ROM `0x27260`) |
|---|---|---|---|
| `0x12A0` | `lbu $2, -4($17)` | `lw $3, 0x5C($18)` | `ori $10, $zero, 4` |
| `0x12A4` | `beq $2, $6, 0x12DC` | `lbu $2, 0x52($18)` | `j L_15D0` |
| `0x12A8` | `addiu $2, $8, 0` | `sw $3, 0x650($2)` | `ori $30, $zero, 0x12AC` |

Byte diffs over the comparable prefixes: ovl20 vs main `308/344`,
ovl20 vs ovl24 `219/228`. First words are not equal to either
image. ovl28 first word is independently `0x26310020`
(`addiu $17, $17, 32`). H-ovl20-is-restore is refuted: no
`addiu $17`, no `ori $3, 0x12A0`, no `j L_122C` restore-DMA.

## 3. Body, exit, and the ovl1c trampoline

Disassembly of ROM `0x27108` for `0x158` bytes at IMEM `0x12A0`:

- Flag split on `lbu -4($17)` / `lbu -3($17)` vs `$6`, then six
  `jal 0x1ED4` with `$2/$3/$4 = $8 + {0,0x28,0x50,...}` triples.
  `0x1ED4` is `OVL1C_1ED4` (save `$ra`→`$30`, `jal 0x1F0C`,
  return `0x1F04`, `jr $30`). Overlay 0x20 dest is `0x12A0`, so
  the `0x1DB0` window keeps ovl1c. Hardware `153` becomes `0x20`
  before the first jal, so the live route must keep `OVL1C_1ED4`
  / `OVL1C_1F0C` / `OVL1C_1F04` reachable at `153==0x20`.
- Then vertex/param setup (`sll`/`addu` into `$7`, DMEM
  `0x670`/`0x698` + `$7`) and emit:
  `jal L_17F0` at `0x13B0` (return `0x13B8`),
  `jal L_112C` at `0x13B8` (return `0x13C0`).
  These are the same shared helpers ovl24 uses (s743–s746: not a
  FULL_SYNC producer).
- Exit at `0x13F0`: `j L_1268; ori $5, 0x28`. Same successor as
  ovl24. Overlay 28 is already routed (fixup 6c).

No `addiu $17, $17, N` anywhere in the image.

Jal-return / `$30` landings inside the image (predicted residuals
after a dest-only route): `0x12BC`, `0x12CC`, `0x12DC`, `0x12FC`,
`0x1310`, `0x1320` (the six `jal 0x1ED4` returns, delivered by
`OVL1C_1F04` `jr $30`), plus `0x13B8` / `0x13C0` (`L_17F0` /
`L_112C`). Internal merge labels include `0x12C0`, `0x12DC`,
`0x1300`, `0x1320`, `0x133C`, `0x1390`, `0x139C`, `0x13D8`,
`0x13F0`.

ovl20 is longer than ovl24 (`0x12A0..0x13F7` vs `0x12A0..0x1383`)
and overlaps main `L_1390` (opcode-table store, not emit). Shared
`do_indirect_jump` cases already claimed by ovl24 / main
(`0x12A0`, `0x12B8`, `0x12C4`, `0x12DC`, `0x12FC`, `0x1320`,
`0x1390`, …) need an extra `153==0x20` arm; do not steal the
`0x24` / default-`L_12A0` arms.

## 4. FULL_SYNC

Two independent static lines, neither a runtime counter:

1. The `0x158`-byte image contains **zero** `0xE9` bytes and no
   word whose high byte is an RDP command other than the COP2
   `swc2`/`lwc2` pair at `0x13AC`/`0x13CC` (`0xE8411002` /
   `0xC8411002` — vector element moves, not `G_RDPFULLSYNC`).
2. The only RDP-submit path is `jal L_17F0` / `jal L_112C`.
   Those helpers are the ovl24 emit path. s743–s757 routed that
   path LIVE and left section-2 E9 match at the boot-shaped
   `3/64` triplet. Overlay 0x20 cannot be a new FULL_SYNC
   producer.

H-ovl20-not-the-e9-hole is selected alongside the dest/class
outcome. Live consume should still treat a 3/64 hold as the
expected arm, not a surprise.

## 5. Dominant vs rare chain

```
bit1 set  (s740 ~31k): ovl12 @ 0x1DB0 → ovl24 @ 0x12A0 → ovl28
bit1 clear (s746 last_ovl 0x0C/0x1DF4 61/64, then s748–s757):
  ovl14 → ovl18 → ovl10 → ovl1c @ 0x1DB0
    intended: ovl20 @ 0x12A0 → emit → L_1268(r5=0x28)
              ovl28 @ 0x1DB0 → r17+=32 → restore L_12A0
    actual:   skip, jr 0x12A0 → main DL-push (r20 as child DL)
              while 153==0x20
```

s757's three `[clip-stray] 0x1E6C/20` hits are leftover `$30`
after `OVL1C_1ECC` requests this DMA, not a reason to widen
`0x1E6C` to `153==0x20`.

## 6. Outcomes vs NEXT.md

- first words emit-shaped (flag split + `jal L_17F0`) and dest
  `0x12A0` → **H-ovl20-skipped-12a0-emit SELECTED.** Live consume
  is a 6c-style route swap. Do not overwrite `L_12A0`.
- first words ≠ main `L_12A0` and ≠ restore-DMA →
  **H-ovl20-is-restore REFUTED.**
- dest decode `0x2157 >> 12 == 2` → `0x12A0` →
  **H-ovl20-is-1db0-sibling REFUTED.** The s757 "do not splice as
  a 1DB0 sibling" warning stands.
- no E9 / no new RDP-submit → **H-ovl20-not-the-e9-hole
  SELECTED.**

**ORIGIN:** `OVL1C_1ECC` is `j L_1268; ori $5, 0x20`. Table desc
`0x2157` at ROM `0x3999A` selects dest `0x12A0`. The skipped
image is legitimate table-selected ucode (ROM `0x27108`), not
garbage. The skip writer is `dma_rdram_to_dmem` bit-12 IMEM
reject, same as ovl24.
