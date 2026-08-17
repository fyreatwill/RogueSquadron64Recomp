# NEXT work unit (s1824)

HYPOTHESIS-ID: m4-accumulator-boundary-revisit

Mandatory 15-title REVISIT. Last-15 ledger titles after s1823 are
s1809–s1823, all sweep (`confirmed` / `synchronized` leftover
symbols). Do not resume the generated-symbol sweep this iteration.
Do not repeat any `submitGfxFrame` entry/jal/`prev_pc` recipe
(s1744 / s1760 / s1776 / s1792 / s1808). The extra +104 presenter
is closed (s1808 H2).

Parked M4 remainder: source state vs later DMA/consumer identity.
Closed already and must not be re-run as the work unit:
- Local VMADH matched 128/128 then 32/32 lanes; VGE mutated 0
  (s1135, s1602). Do not recapture those lanes.
- `0x688:0x710` is not a retail CPU-written shade record; SP-DMEM
  `0x04000670:0x04000720` had zero CPU writes (s1512). Do not
  re-watch either range.
- Port DMA dest `0x4B7800..0x4B7808` is runtime-allocated; the
  Rice hangar watch of that exact range was unevaluable (s1602).
  Do not re-watch `0x4B7800`.

New angle (ground truth first, no new instrument until the table
exists): statically enumerate every overlay-0x20 consumer of the
DMEM `0x670` shade record after `L_1740` (`sdv v6` to `0x18($9)` /
`0x40($9)`), and whether those stored bytes can reach the only
`SP_WR_LEN` DMA. Generated overlay 0x20 already has `ori $9,
$zero, 0x670` at line 1078 and `mtc0 $4, SP_WR_LEN` at line 337
with `ori $16, $zero, 0xD60` staging. s1512 says that DMA sources
DMEM `0xD60`, not `0x670`. The open split is whether `0x670`
bytes are copied into `0xD60` (RDP consumer / later DMA) or never
leave `0x670` (source-state / dead record).

Read first: `docs/M4-ACCUMULATOR-GROUND-TRUTH.md`,
`docs/M4-V6-PRODUCER-AUDIT.md`, `docs/F5-UCODE-REFERENCE.md`
(inline-data pointer advances and what the ucode can emit).

Competing hypotheses:

- H-rdp-consumer: after `L_1740`, overlay 0x20 copies or
  restages the `0x670+0x18`/`+0x40` bytes into the `0xD60`
  staging buffer before `SP_WR_LEN`. Later consumer is the RDP
  command stream.
- H-later-dma-raw: some `SP_WR_LEN` / `SP_RD_LEN` sources DMEM
  `0x670` directly (would contradict s1512's "only DMA is from
  `0xD60`"; confirm or refute against the live generated file).
- H-source-state: `L_1740` stores the sentinel, `SP_WR_LEN`
  fires from `0xD60`, and no generated path copies `0x670+0x18`
  / `+0x40` into that staging buffer. The RDP never sees this
  record; the defect is upstream of the store.
- H-dead-store: no post-`L_1740` load, copy, or DMA of
  `0x670+0x18` / `+0x40` exists at all (record unused).

Exact commands (static; no game run unless the table names one
register-backed dest that is not `0x4B7800` / `0x688`):

```
# every 0x670 / 0xD60 / SP_* site in the live overlay
grep -n '0x670\|0xD60\|SP_WR_LEN\|SP_RD_LEN\|SP_DRAM_ADDR\|L_1740\|sdv' \
  build/factor5_ucode/factor5_ucode_ovl20_recompiled.c
# confirm the only-WR_LEN claim across sibling overlays
grep -n 'SP_WR_LEN' build/factor5_ucode/factor5_ucode_ovl*.c
```

Then read each hit's surrounding block (at most 40 lines) and
classify it as: store of `v6` to `r9`, copy `0x670`→`0xD60`,
DMA source `0xD60`, DMA source `0x670`, or unrelated addend.
Build the complete consumer table in one pass. Do not add a
runtime field until that table selects one hypothesis.

Expected splits:

- H-rdp-consumer: at least one generated copy/restage of the
  stored `0x670` bytes into `0xD60` before `SP_WR_LEN`. Next
  measurement is the RDP command shape in that payload, not an
  absolute port address.
- H-later-dma-raw: a live `SP_WR_LEN` source is `0x670`. Document
  the site; only then may a port DMA-src capture be added.
- H-source-state: store exists, `SP_WR_LEN` is only from `0xD60`,
  and no copy of the stored bytes into `0xD60` exists.
- H-dead-store: no post-store reader of `0x670+0x18` / `+0x40`.

Sweep cursor (parked until after this revisit): leftover
`func_800ECE10` (`0x800ECE10`, `0x338`). Companion and generated
headers/body/INL already `datItemActorNpcHandler`; TOML still
leftover. First insn `addiu $sp, $sp, -0x140`; last `jr $ra` /
`addiu $sp, $sp, 0x140` at `0x800ED140` / `0x800ED144`. No
generated `jal 0x800ECE10`. Next leftover `fake_func_800ED148`
(`0x800ED148`, `0x8`).
