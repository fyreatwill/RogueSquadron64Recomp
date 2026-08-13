# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. 28 passes so far
   (git log has per-pass targets; PROJECT-OVERVIEW §16-§27 hold the most recent arcs) kept the file
   oscillating around the cap as new session detail accrues. 35 KB remains a stretch target, not a
   hard floor -- the "Current truth" env-var/timeline prose and the Regeneration section's Standing
   warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (PROJECT-OVERVIEW §10-§12). Next
   M5 work needs a genuinely new lead (rechecked s582 SOAK-RESULTS: no new audio-family
   crash leads since s487; due again s585+).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket from
   the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW §18-§19). The
   `DL_LIST_APPEND_GUARD`→`HEAPLISTDEQ_ATTR_WRITE_GUARD` lineage (items -312..-348, s481-569) is all
   fully CLOSED — PROJECT-OVERVIEW §20-§25; see individual items below for closure notes.

## Current truth (reviewed through s759; compacted in maintenance s729)

**s759:** fixup 6q routes dest `0x12A0` / `153==0x20` →
`OVL20_12A0` (keep `OVL24_12A0` and default `L_12A0`), rewrites
the six `jal 0x1ED4` to `OVL1C_1ED4`, and widens `0x1F04` /
adds `0x1ED4` for `153==0x20`. Soak
`s759_ovl20_route_20260812-193904` (crash at 105 s leave-Start,
wrapper rc=3): `[ovl-route] res=0x20 tgt=0x12A0` last n=54848
LIVE (173 logged, first task 188 `via=l1298-other`); ovl24 dest
`0x12A0` still LIVE; ovl1c `0x1EA8` LIVE. UJ **0**. Predicted
`0x1E6C/20` leftover **0**. 4/4 boot `dl06=2/2/0`. Boot E9
still 4/4 match=1; sec2 3/64 unevaluable (died before outdoor).
rdpFs 0→3836. Residual `[clip-stray] 0x13B8/04` n=419
line=2852 — ovl20 `jal L_17F0` return after the clip hand
(same class as s744 `0x1364`). Hangar SIGSEGV
`si_addr=0x4000cd6d3` `last-guest-pc=0x800ac8c0` (sticky
case-5 checkpoint); do not revert dest route. **H-ovl20-route-
runs SELECTED. H-ovl20-route-breaks-06 REFUTED.
H-ovl20-needs-1ed4-keep REFUTED** as the failure mode (no UJ
`0x1ED4`; common path is `jal L_17F0`). **H-ovl20-route-
restores-e9 UNEVALUABLE** for sec2; boot-shaped holds.
**ORIGIN:** dest `0x12A0` / `153==0x20` is skipped ovl20 ROM
`0x27108`. Residual writer: `OVL20` `jal L_17F0` r31=`0x13B8`;
`L_17F0` hand `r5=4; goto L_1268` → `CLIP_1E48` `jr`.

**s758:** static overlay-0x20 successor audit
(`docs/M3-OVL20-SUCCESSOR-AUDIT.md`). Table desc `0x2157` at
ROM `0x3999A` independently decodes dest `0x12A0`, len `0x157`,
DRAM `0x1AF8`, image ROM `0x27108`. First word `lbu $2, -4($17)`
≠ main `L_12A0` (`0x8E43005C`) ≠ ovl24 (`ori $10,4; j L_15D0`)
≠ ovl28 (`addiu $17,32`). Diffs 308/344 vs main, 219/228 vs
ovl24. Body: 6× `jal 0x1ED4` (ovl1c trampoline, window stays
resident), then `jal L_17F0` / `jal L_112C`, exit
`j L_1268; ori $5, 0x28`. Zero `0xE9` bytes. **H-ovl20-skipped-
12a0-emit SELECTED. H-ovl20-is-restore REFUTED.
H-ovl20-is-1db0-sibling REFUTED. H-ovl20-not-the-e9-hole
SELECTED.** Live consume is s759. **ORIGIN:**
`OVL1C_1ECC` is `j L_1268; ori $5, 0x20`; skipped IMEM writer
is `dma_rdram_to_dmem` bit-12 reject of dest `0x12A0`.

**s757:** fixup 6p routes dest `0x1EA8` / `153==0x1C` →
`OVL1C_1EA8`. Soak `s757_ovl1c_1ea8_20260812-191445` (350 s,
CRASH=0): `[ovl-route] res=0x1C tgt=0x1EA8` last n=32896 LIVE;
UJ `0x1EA8` **1403→0**. ovl1c `$30` pair complete. 4/4 boot
`dl06=2/2/0`. E9 still 3/64. Do not route n=1 `0x1E7C`; do not
widen `0x1E6C` to `153==0x20`. **H-1ea8-ovl1c-30ret SELECTED.**
Consumed by s758. **ORIGIN:** ovl1c jal IMEM `0x1E9C` r31=`0x1EA8`
→ `OVL1C_1ED4` → `jr $30`.

**s756:** fixup 6o routes dest `0x1E6C` when `153==0x1C` to
`OVL1C_1E6C`. Soak `s756_ovl1c_1e6c_20260812-190418` (348 s,
CRASH=0): `[ovl-route] res=0x1C tgt=0x1E6C` last n=7744
LIVE; UJ `0x1E6C` **1570→0**. Residual was sibling UJ
`0x1EA8` n=1403 (consumed s757). **H-1e6c-ovl1c-30ret
SELECTED.** **ORIGIN:** ovl1c jal at IMEM `0x1E60` sets
`r31=0x1E6C` and `goto OVL1C_1ED4`.

**s755:** fixup 6n routes dest `0x1F04` when `153==0x1C` to
`OVL1C_1F04`. Soak `s755_ovl1c_1f04_20260812-185242` (350 s,
CRASH=0): `[ovl-route] res=0x1C tgt=0x1F04` last n=55232
LIVE; UJ `0x1F04` **3185→0**. Residual was `$30` restores
`0x1E6C` n=1570 / `0x1EA8` n=1609 (consumed s756 for
`0x1E6C`). **H-1f04-ovl1c-jalret SELECTED.**
**ORIGIN:** ovl1c `OVL1C_1ED4` saves `$ra` to `$30`, jals
`0x1F0C` with return `0x1F04`.

**s754:** fixup 6m routes dest `0x1E2C` when `153==0x1C` to
`OVL1C_1E2C`. Soak `s754_ovl1c_1e2c_20260812-184124` (348 s,
CRASH=0): `[ovl-route] res=0x1C tgt=0x1E2C` last n=53440
LIVE; UJ `0x1E2C` **3213→0**. Residual was UJ `0x1F04`
n=3185 (consumed s755). **H-1e2c-ovl1c-jalret SELECTED.**
**ORIGIN:** ovl1c jal at `OVL1C_1E18` → callee `0x1F0C`,
return `0x1E2C`.

**s753:** fixup 6l routes dest `0x1E18` when `153==0x1C` to
`OVL1C_1E18`. Soak `s753_ovl1c_1e18_20260812-183025` (351 s,
CRASH=0): `[ovl-route] res=0x1C tgt=0x1E18` last n=6464 LIVE;
UJ `0x1E18` **5879→0**. Residual was UJ `0x1E2C` n=3213
(consumed s754). **H-1e18-ovl1c-jalret SELECTED.**
**ORIGIN:** ovl1c jal at IMEM `0x1E10` → callee `0x1F0C`,
return `0x1E18`.

**s752:** fixup 6k splices overlay `0x1C` (`OVL1C_*`, dest
`0x1DB0`, `153==0x1C`, no jal-return cases). Soak
`s752_ovl1c_route_20260812-181705` (350 s, CRASH=0):
`[ovl-route] res=0x1C tgt=0x1DB0` last n=5888 LIVE; stray
`0x1F40/00` **3767→0**. Residual was UJ `0x1E18` n=5879
(consumed s753). **H-ovl1c-stops-1f40-00 SELECTED.**
**ORIGIN:** dest `0x1DB0` / `153==0x1C` is the skipped ovl1c
image (ROM `0x26EF8`).

**s751:** fixup 6j routes ovl10 `L_15D0` handshake return
(`0x1F40` extra target + `OVL10_1F40` + case `153==0x18||0x10`).
Soak `s751_ovl10_1f40_20260812-180004` (351 s, CRASH=0 UJ=0):
`[ovl-route] res=0x10 tgt=0x1F40` last n=7488 LIVE;
`last_ovl=0x10/0x1F40` 61/64. Stray `0x1F40/10` **5501→0**.
Pred first-edge `resident:0x1C` **61/61**. 4/4 boot
`dl06=2/2/0`. E9 still 3/64 boot-shaped. **H-1f40-ovl10-
handshake SELECTED.** Consumed by s752. **ORIGIN:** ovl10
`ori $30, 0x1F40; j L_15D0` at IMEM `0x1F38`.

**s750:** fixup 6i splices overlay 10 (`OVL10_*`, dest `0x1DB0`,
`153==0x10`, no jals; external helpers `L_1268` and `L_15D0`).
Soak `s750_ovl10_route_20260812-174446` (331 s, UJ=0, wrapper rc=3
from a late SIGSEGV `si_addr=0x10` at 283 s; `last-guest-pc`
`0x8000b650` is the stale `beginFrameDLChunk` checkpoint): ovl10
LIVE via `[ovl-route] res=0x10` last n=5440 and
`last_ovl=0x10/0x1DB0` 122/128 (`ovl10=1` on those 122). ovl18
stays LIVE (n=6464). Leftover-`$ra` `/00` `L_11B0` strays
**2619+2345+901+56→0**. New stray is `0x1F40/10` n=5501 line=1421
(`L_1778` `jr $30`). 4/4 boot `dl06=2/2/0`. E9 match **6/128** is
two copies of the boot-shaped `2/2/0` triplet; rdpFs 0→5169.
**H-ovl10-stops-1db0-reset SELECTED. H-ovl10-not-the-l11b0-path
REFUTED. H-ovl10-breaks-06 REFUTED. H-ovl10-restores-e9 REFUTED.**
Consumed by s751. **ORIGIN:** dest `0x1DB0` / `153==0x10` is the
skipped ovl10 image (ROM `0x268A0`).

**s749:** fixup 6h splices overlay 18 (`OVL18_*`, dest `0x1DB0`,
`153==0x18`). Soak `s749_ovl18_route_20260812-172852` (348 s,
CRASH=0): ovl18 LIVE n=6848, `last_ovl=0x18/*` 183/192; pred
`resident:0x18` **61→0**; leftover `/00` `L_11B0` strays grew
(1DF4/1E28/1F40/1EEC). 4/4 boot `dl06=2/2/0`. E9 9/192 boot-
shaped. **H-ovl18-stops-1db0-reset SELECTED.** Consumed by s750.
**ORIGIN:** dest `0x1DB0` / `153==0x18` is the skipped ovl18 image
(ROM `0x26CD8`).

**s748:** fixup 6g splices overlay 14 (`OVL14_*`, dest `0x1DB0`,
`153==0x14`, jal-returns `0x1E28`/`0x1E94`/`0x1EEC`). Soak
`s748_ovl14_route_20260812-171325` (350 s, CRASH=0 UJ=0): ovl14 LIVE
via `last_ovl=0x14/*` 61/64 (`0x1E28` 50, `0x1DB0` 10, `0x1EEC` 1).
Sec2 first-edge pred `resident:0x14` **61→0**; all 61 then
`dest=0x1DB0,line:621,resident:0x18`. Stray `0x1DF4/00` **3157→1395**
plus leftover-`$ra` `0x1E28/00=1200` `0x1EEC/00=77`. 4/4 boot
`dl06=2/2/0`. E9 match still **3/64**. **H-ovl14-stops-1df4-stray
SELECTED** for dest-`0x1DB0`/`153==0x14`. **H-ovl14-not-the-1df4-path
REFUTED. H-ovl14-breaks-06 REFUTED. H-ovl14-restores-e9 REFUTED.**
Consumed by s749. **ORIGIN:** dest `0x1DB0` / `153==0x14` is the
skipped ovl14 image (ROM `0x26AB8`).

**s747:** static `$ra=0x1DF4` audit (`docs/M3-1DF4-PROVENANCE-AUDIT.md`)
plus s746 re-read. Only writer is ovl12 `jal L_122C` at IMEM `0x1DEC`
(ROM `0x266AC`). Stray line 451 is leftover `$ra` after skipped ovl14
falls into main `L_1DB0` (`153=0`) then `L_11B0`. **H-1df4-stale-ra
SELECTED.** Live consume is s748. **ORIGIN:** `$ra` writer `OVL12_1DD8`;
`153=0` writer main `L_1DB0` after skipped ovl14 DMA.

**s746:** fixup 6f widens the ten leftover ovl24-only clip-stray
cases to `OVL24_*` when `0x153==0x24 || ==0x04`. Soak
`s746_ovl24_04ret_20260812-164346` (348 s, CRASH=0 UJ=0): stray
`0x1320/04`+`0x1330/04`+`0x1344/04` **3681+1165+485→0**; no ovl24-only
stray remains. `jal17f0` 68672→**879232** (12.8×); clip1e48_1364
5279→175093; last reset `last_ovl=0x0C/0x1DF4` 61/64. 4/4 boot
`dl06=2/2/0`. E9 match still **3/64**; rdpFs 0→4117 (flat; s745 4030).
**H-ovl24-class-needed-but-not-e9 SELECTED. H-ovl24-class-restores-e9
REFUTED. H-ovl24-class-breaks-06 REFUTED.** Residual was
`[clip-stray] 0x1DF4/00` n=3157 (consumed s747). **ORIGIN:** `L_112C`
`jr` of `OVL24_1358`-saved `$ra` after the 6e `0x1364` clip return.

**s745:** fixup 6e widens case `0x1364` to `OVL24_1364` when
`0x153==0x24 || ==0x04`. Soak `s745_1364clip_route_20260812-163229`
(348 s, CRASH=0 UJ=0): stray `0x1364/04` **4454→0**; `jal17f0=j1364=
68672`; res04=`clip1e48_1364`=5279; last reset `last_ovl=0x24/0x1364`
LIVE. 4/4 boot `dl06=2/2/0`. E9 match still **3/64**; rdpFs 0→4030
(flat; s744 4141). **H-1364-needed-but-not-e9 SELECTED.
H-1364-restore-e9 REFUTED. H-1364-breaks-06 REFUTED.** Residual was
the ovl24-only `0x1320`/`0x1330`/`0x1344` `153=0x04` class (consumed
s746). **ORIGIN:** `CLIP_1E48` `jr` of `OVL24_135C` jal; 0x04 arm is
a route of that return.

**s744:** named the s743 `[clip-stray] tgt=0x1364 153=0x04` writer.
Static: clip C has no `0x1364`; only `OVL24_135C` sets `r31=0x1364`
(`jal L_17F0`). `L_17F0` hand is `r5=4; goto L_1268` → `0x153=4` →
`CLIP_1DB0` saves `$ra` → `CLIP_1E48` `jr`s it. Clip dest is `0x1DB0`,
so IMEM `0x1364` is still ovl24. Soak
`s744_clip_stray_1364_pred_20260812-162040` (349 s, CRASH=0):
`jal17f0=j1364=64192`, res04=`clip1e48_1364`=4452, res24=59740, oth=0;
stray `0x1364/04` n=4454. Two classes only: `L_1DA8` res=0x24 (routes)
and `CLIP_1E48` res=0x04 last_ovl=`0x04/0x1DB0` (stray). Boot
`dl06=2/2/0` LIVE. E9 match still 3/64; rdpFs 0→4141. **H-l17f0-
dispatches-clip SELECTED. H-clip-uses-1364 REFUTED. H-stale-ra
REFUTED.** Residual was the 0x1364 0x04 leak (consumed s745).
**ORIGIN:** `CLIP_1E48` `jr` of the `OVL24_135C` jal return. Legitimate
ROM clip dispatch; the `153==0x24`-only case was the leak.

**s743:** fixup 6c route swap (ovl24 emit @ `0x12A0` + ovl28 `r17+=32`).
Soak `s743_ovl24_route_20260812-160417` (349 s, CRASH=0). UJ **2931→0**.
**H-ovl24-route-restores-fetch SELECTED. H-l1298-12a0-not-only-ovl
REFUTED.** E9 match still 3/64. Residual was the 0x1364 clip-stray
(consumed s744). **ORIGIN:** route, not a guard. Writers overlay 24/28.

**s742:** static `L_1268` continuation audit (`docs/M3-OVL24-CONTINUATION-AUDIT.md`).
**H-ovl24-skipped-imem SELECTED.** Overlay 24 (ROM `0x27260`, dest `0x12A0`)
is emit (`ori $10,4; j L_15D0; ori $30,0x12AC`), not DL-push. Overlay 28
(ROM `0x27348`, dest `0x1DB0`) is `addiu $17,32` then restore-DMA of main
`L_12A0`. Overlay 14 is the rare `0x1DB0` sibling. Do not overwrite
`L_12A0`. 6c is the route; live consume is s743.

**s741:** static `L_122C` wrap audit (`docs/M3-OVL12-L122C-WRAP-AUDIT.md`).
**H-ovl12-dma-legit-payload SELECTED. H-ovl12-dma-wrap-stomp REFUTED.**
dests `0x4E0`/`0x380` are TriGen vertex/color scratch above `0x64..0x2D4`;
our DMA clamps at `0x1000`. s739 re-count: 2927 UJs, 0 in the ovl12 window;
payload DMA 2/1 vs ~31k `L_1F64`. Do not add hardware wrap.

**s740:** consumed `scratch/agent/soak_results/s739_ovl12_splice_20260812-152309/run.log`
(353 s, rc=0, CRASH=0). Same-run CLIP `[ovl-route] res=0x04` n=1033 (n up to
65088) and OVL12 `res=0x0C` n=155960 (n up to 9980416, `tgt=0x1DB0` plus the
four jal-returns) are LIVE. All 64 section-2 `[e9-prov-reset]` rows have
`active=0 unpaired_reuse=0` with per-task `ovl12=5 ovl12_ret=4` once the
route is warm (vs s736 61/64 `active!=0`). **H-splice-correct SELECTED.**
**H-ovl12-return-incomplete REFUTED** for the wired jal-return set.
**H-reset-independent REFUTED.** Residual, new vs s736 (UJ=0, defer-drop=0):
2935 `Unhandled jump` (1937 OOB IMEM, 878 in-IMEM, **0** overlay-12 window)
and 79 `[defer-drop]`; dominant post-sec2 target `0xFA92` from the main
command-table `jr` at line 238 (`DMEM[0x64]`). Section-2 E9/FS is unchanged
(match=3/64 both soaks; rdpFs 3933→3948 vs s736 4020→4023). Next is a
static DMEM-map / `L_122C` wrap audit of dests `0x380`/`0x4E0` vs tables
`0x64`/`0xD6` — no rebuild. **ORIGIN:** the reset writer remains main
`L_1DB0` `DMEM[0x152]=0`; the splice now runs the ROM-backed image instead.

**s739:** landed the regeneration-safe resident-`0C` splice (fixup 6b,
`OVL12_*`, id-`0xC` at `0x1DB0`, jal-returns through `L_122C`/`L_1268`).
Build-time extraction/sanity passed. Live consume is s740.

**s738:** static audit selected **H-stale-main-image**. Resident 0C's `L_1DB0`
is distinct TriGen (ROM `0x26670`, 0x230 B); the runtime was falling through
to the main bootstrap reset. Table: `docs/M3-OVERLAY12-AUDIT.md`.

**s737:** consumed the clean 347-second `s736_reset_predecessor` soak. Its
four balanced direct boot controls remain intact; all 61 retained section-2
cap rows reproduce active resets with zero unpaired reuse and a live target
marker. Every reset's predecessor is the `L_1298` indirect relay
(`target=0x1DB0`, line 615, `ra=0x1088`, resident `0x0C`, `l1298=1`). Thus
**H-trigen-relay-entry is selected**, while H-direct-bootstrap-entry and
H-predecessor-latch-broken are refuted. The reset callback itself sees
resident 0 because `L_1DB0` has already begun; that is not evidence against
the predecessor's resident-`0C` route. Next is a bounded static provenance
audit of resident `0C`'s `L_1298→0x1DB0` image/semantics before any change.
No mitigation changed.

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- `ROGUESQ_LOG_FL_ZERO_WATCH=1` (s640+): soft poller on freelist header phys
  `0x1F3CC0` **plus** s646/s647 mprotect page-fault watch (`[fl-zero-fault]`).
  Arms PROT_READ while header is zeros (boot `want=1`) or freelist-shaped
  `0x2/0x60` (`want=2`); write SIGSEGV/SIGBUS logs host PC via local-symtab +
  guest sticky, re-enables RW. 16KB Apple pages → filter `in_hdr=1`. s647:
  freelist window uses busy re-arm spinner (20µs hold-off after fault; poller
  10µs) + `to_zero_correlate`. **ARM64 SS via `thread_set_state` from SEGV
  REFUTED** (nested SIGTRAP → CRASH). **s648:** freelist-window fault lines/BT
  **rate-limited** (first 32/16, all in_hdr, every 256th). **s649:** recover
  watch-page faults even when `armed==0` (concurrent/stale-TLB race; s648
  att4 SIGBUS in `buildModelViewerTextPage` at fa on page after peer disarm
  fell through to `[CRASH]`). Count `late=1` recovers. Posctrl LIVE s649
  (fault_n LIVE, `late=` field, CRASH=0). **s650 freeroll Outcome B**
  (recovery-active): arm_fl + freelist `0x2/0x60`→0 + `fault_hdr=0`;
  ~15s quiet while `armed=1` then silent zero → **H-busy-rearm REFUTED**
  freelist-class. **s651 freeroll:** same shape + **adlb_tgt=0** →
  **H-adlb-writer REFUTED**; rate-limit hole → **fault_ring** +
  **near_hdr** (-405). **s652 freeroll consume:** ring LIVE near=9;
  **H-ssnr380-writer REFUTED** (payload of LIVE alloc). **s653 freeroll
  Outcome B CONFIRMED:** freelist to_zero 0x2/0x60@165665ms immediately
  after `[fb-fl-writeback] HIT` `addrStart=0x1F0D74` range covers phys
  `0x1F3CC0` (w=1161); ssnr_tgt=0 → **H-ssnr-zero-stores REFUTED**;
  **H-fb-writeback-stomp CONFIRMED**. Product: `SKIP_WILD_W` allowlist +
  `SKIP_FL_HDR` + HIT early-return (-407). **s654 freeroll Outcome A
  CONFIRMED dual-source:** SKIP_WILD_W of exact killer CIMG
  (`addr=0x1F0D74 w=1161`) mid freelist-window + freelist 0x2/0x60
  survived post-arm; **H-fb-skip-stops-stomp CONFIRMED**; wild CIMG also
  fires on silent → H-recov-co-gate-stomp partly recharacterized.
  **s655 Outcome C:** post-SKIP freeroll 0/7 recovery-active engaged
  (s654 soak 2 silent + s655 in-session 5 silent); freelist 0x2/0x60
  survival reconfirmed 5/5; **H-fl-survive-unblocks-thr11d UNEVALUABLE**.
  **s656 Outcome B:** `ROGUESQ_ALLOW_WILD_W=1` A/B **0/6 recovery-active
  engaged** → **H-skip-suppresses-recov REFUTED** for SKIP_WILD_W alone;
  freelist still protected by SKIP_FL_HDR. Landed `ROGUESQ_ALLOW_FL_HDR=1`.
  **s656 soak Outcome C:** ALLOW both still HIT_SKIP in
  `copyNativeToRAM` last-line (not gated) — freelist never stomped.
  **s657:** gate last-line on ALLOW_FL_HDR → **HIT_WRITE LIVE**; freelist
  to_zero 0x2/0x60 returned; complete-ALLOW freeroll **1/3 recovery-active**
  (att3 recov768=7948 thr11d_new=1 fail136c=1) →
  **H-fl-survive-suppresses-recov SUPPORTED** (under permanent stomp).
  **s658 Outcome A CONFIRMED triple-source:** `ROGUESQ_FL_HDR_RESTORE=1`
  (ALLOW path) snapshots 16B @ phys 0x1F3CC0 around HIT writeback;
  `HIT_WRITE_RESTORE` classic killer + `[fb-fl-hdr-restore] match=1`
  pre=0x2/0x60 mid=0/0 post=0x2/0x60; freelist heartbeats survive past 170s;
  recovery-active **3/5 engaged** (att2/4/6; thr11d_new=0 fail136c=0) →
  **H-wb-complete-not-stomp SUPPORTED**. Product SKIP drought recharacterized
  as **writeback-skip** of freelist-range wild CIMG, not freelist integrity.
  **s659 productize LIVE (Outcome A):** freelist-range writeback
  snapshot/write/restore default ON. Policy A: wild freelist-range →
  `ALLOW_WILD_FL` + restore; non-freelist wild still `SKIP_WILD_W`. s659
  freeroll: recov 3/3 thr11d 3/3 fail136c 2/3. **s660:** offline zero_node
  next=`node+size+0x10` → **H-body-stomp STRUCTURAL**; full-body 64KB →
  next_ok=1 but recov drought 0/3 → body bytes co-gate recovery. **Product
  mode=headers:** restore only 16B freelist headers along chain; leave body
  writeback intact. A/B: `FL_RESTORE_MODE=body` / `FL_RESTORE_BYTES=N`.
  Opt-out: `FL_HDR_HARD_SKIP=1` / `FL_HDR_RESTORE=0`.
  **s662–s663 cimg-origin-desync CLOSED for class:** hangar wild SETCIMG
  **and** the exact freelist killer (`w=1161`/`0x1F0D74`) are **garbage
  ring content** after wrap. Length-respecting RDP walker lands SETCIMG
  after garbage prev (hangar: TRI op 0x09; killer: zeros+op 0x3F).
  Hangar **104/104 in_wrap=1** ring start=0x781800; killer **in_wrap=1**
  ring start=0x766000 (same class, different ring). Submit sticky
  contains killer task → not a deferred-merge sticky bug. **ORIGIN:**
  freelist stomp host writer = RT64 color writeback of that garbage
  SETCIMG (range covers phys 0x1F3CC0); operands not legitimate (w=1161
  never used). Instruments: `ROGUESQ_LOG_CIMG_RAW`, `ROGUESQ_LOG_DL_SYNC2`.
  **s664 Outcome B:** env-gated `ROGUESQ_DROP_WRAP_RDP=1` (default OFF)
  drops any submit with `lo ∈ [last_wrap_start,seen)` — **too coarse**:
  sticky never expires, so legitimate ring reuse after wrap is starved
  (~30k drops on early ring `0x4B7800`); cinematic SIGBUS; hangar never
  reached (A+B dual-source). Control C filter OFF + restore OFF still
  hits exact KILLER + freelist `0x2/0x60`→0. **s665 Outcome A:**
  `ROGUESQ_DROP_GARBAGE_CIMG=1` (default OFF) at processRDPLists —
  drop wild SETCIMG when prev ring garbage OR operands addr=0/w=1161.
  **H-prev-garbage-kills-killer CONFIRMED** dual-source: B drop ON +
  restore OFF → exact 1F0D74=0, freelist to_zero freelist-shaped=0;
  C control exact KILLER + HIT_WRITE + to_zero. Hangar craft_stable
  content LIVE both arms → false-drop REFUTED for hangar. v1 last-4
  hole fixed same-iter (full 8-deep + operand gate).
  **s666 productize REJECTED:** default-ON freeroll A+B (restore ON/OFF)
  freelist+content OK (kill_applied=0 flz=0 OK×8) but **recov 0/4 eng
  both arms** vs s659 restore 3/3 under drop OFF →
  **H-drop-suppresses-recov SUPPORTED** (writeback-prevent = skip-class
  drought; H-wb-complete-not-stomp). Reverted default OFF; product path
  remains multi-header restore. Drop stays opt-in experiment only (-418
  CLOSED).
  **s667 freeroll SCORE (headers product, drop OFF, BUDGET=1200):**
  posctrl LIVE mode=headers nhdr=45 next_ok=1; fail136c=0 both
  recovery-fired → **H-headers-fail136 SUPPORTED**. thr11d_new=0/2
  UNEVALUABLE (ship n≤2; holds truncated/silent shape).
  **s668 thr11d multi-hold freeroll (BUDGET=1800, product headers):**
  recov_full=2/3 eng thr11d_hit=**2/2** dual-source →
  **H-headers-thr11d CONFIRMED**; ship n=3 + mv-b8=27 both →
  **H-headers-shipn3 CONFIRMED**; fail136c=0; next_ok=1.
  **Pipeline LIVE:** thr11d → ok136c (rs_malloc 0x136C succeeds) →
  thr12 create (ltexmg=0) → **section 2** mission overlay → thr12
  recreate; crash=0 packTlut=0 both holds. s667 thr11d=0 recharacterized
  as ship-n3-miss (holds never reached B8 gate), not headers regression.
  **s669 offline post-sec2 SCORE (s668 att2+att3 dual-source):**
  **H-sec2-mission-live CONFIRMED** — ~195–200s outdoor VI 512
  origins 0x620000↔0x690000 continuous present FIRE swap pairs=4,
  ~5900 GFX tasks tris=42; thr12 id=13 long-lived then menu sec3 return.
  **H-thr12-churn-normal CONFIRMED** (not immediate death).
  **H-postsec2-fs-plateau CONFIRMED** — thr13 life rdpFs delta 0/+2 while
  synth +~5864–5892; runner syncs=0 ~5866–5894 vs syncs>0 only 3;
  fs_b0=E9=6 vs F7~11.7k. packTlut=0 crash=0. Residual → -421
  (post-sec2 FS plateau / menu return / packTlut never).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  per-pixel (s24→s26), `ROGUESQ_FIX_ZERO_SHADE` (s20), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15),
  `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough + forceAdvance +
  `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10), **s78 wild/OOB FB refuse** in `FramebufferManager::get`
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present),
  **s182 `[fbsync-oob-skip]` guard** in `State::fullSync`'s color/depth read-into-`fbStorage`
  blocks (`rt64_state.cpp`) — s78's refuse gate returns a `refuseFb` that still carries the wild
  width/height, and this downstream RDRAM read had no bounds check of its own; same family as
  s72/s78. **s653 `rs64_writeback_sane`:** `SKIP_WILD_W` (allowlist 320/512/640/1024,
  matches s82) + freelist-range allow. **s659–s660 product (default ON):**
  freelist-range writeback + surgical multi-header restore @ phys 0x1F3CC0
  (`mode=headers`, walk_cap 64KB); wild freelist-range `ALLOW_WILD_FL`.
  `SKIP_WILD_W` still ON for non-freelist wild. A/B: `FL_HDR_HARD_SKIP=1`,
  `FL_HDR_RESTORE=0`, `FL_RESTORE_MODE=body`, `FL_RESTORE_BYTES=N`,
  `ALLOW_WILD_W=1`.
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30, pad-only), `ROGUESQ_SHADE_WRAP=3` (s31), `ROGUESQ_SHADOW2`,
  `ROGUESQ_RING_RESYNC`, **`ROGUESQ_DROP_WRAP_RDP`** (s664 Outcome B — too coarse; experiment
  only), **`ROGUESQ_DROP_GARBAGE_CIMG`** (s665 Outcome A / s666 REJECTED
  productize — decode-site wild+garbage SETCIMG drop; default OFF forever
  under current recovery co-gate; opt-in freelist-origin experiments only).
  Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1` (s47, lib-side) dumps every skipped
  IMEM DMA to `build/imem_dma_dump.bin` (`scratch/s47_parse_imemdump.py` decodes).
  `ROGUESQ_LOG_RUNNER=1` prints a per-task RDP-opcode histogram (1-in-32 sampled by default --
  `ROGUESQ_LOG_RUNNER_ALL=1`, s64, prints every task unsampled; the sampled mode misattributes
  31 tasks' counts onto whichever task is next sampled). `ROGUESQ_LOG_SEQ=1` dumps a task's raw
  pre-translation DL bytes -- not valid for "does this task emit SYNC_FULL" (needs the
  post-translation histogram above, s64).
- Deleted from the code (s44): `ROGUESQ_DPC_WRAP` / `ROGUESQ_WRAP_DEDUP` (s11), `ROGUESQ_FORCE_PAL15`
  (s14), `ROGUESQ_FORCE_SHADE_WHITE` (s19). `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times
  since s11 but is KEPT deliberately -- OOM insurance for future FULL_SYNC-less phases (M3
  missions), turns a 22 GB Metal abort into a capped workload (s44).

Unattended timeline (VI width, ±1 s over 9 runs, s18; content counts s9/s20/s22/s23):

| t | VI | scene |
|---|---|---|
| 0.0 s | 0 → 320 | boot |
| 1.7 s | 640 | attribution → N64 logo → cinematic geometry → star flare → **Factor 5 logo**, all correct (content in 24/60 frames over ~2–44 s) |
| ~46.5 s | 1024 | **title screen** — logo, pilot, X-wing, START/OPTIONS; 5/5 content frames, ~20.9k colours |
| ~72 s | 640 | transition |
| ~90 s | 512, origin 0x690400 | **outdoor scene** — sky, clouds, horizon, sand; 6/6 content frames |

**s39/`-O2` harness note:** the game now progresses further per unit time, so the old
`PROBE_KEYS="3:start 7:start 11:a 15:a 19:a"` schedule overshoots the hangar into a later exterior
scene that shares VI origin **0x6AB400** — origin alone no longer identifies the hangar. Use
`"3:start 7:start"`. The phase timeline below is unchanged (transitions are not render-rate bound).

Driven from the title with `PROBE_KEYS_FROM_PHASE=1` (s23, scene names corrected s48):

| t | VI | scene |
|---|---|---|
| 46.7 s | 1024 | clean title |
| ~50 s | 1024 | **SELECT GAME** (photographic hangar backdrop, AAA save, ERASE GAME) — waits for input indefinitely |
| +1 press | 512, origin 0x6AB400, colour 0x656000/0x6AB000 | **level-select war room → SELECT LEVEL — "AMBUSH AT MOS EISLEY"** with X-wing hologram (the scene s12–s47 called the "main-menu hangar"; see s48 below) |
| ~93 s | 640 | transition — process died here in the undriven-era observation and in every crashing run of the post-s86 family; on later crash-free runs the process instead survives past here |
| leave SELECT YOUR CRAFT (1 Start press) | 512→640, origin 0x6AB400→0x6A2900ish | **s162: a Chapter-1 mission-intro cutscene** — gold "STAR WARS" logo bumper → "Chapter 1"/"THE RED…" crawl text → black → desert-planet horizon widening into a fast dive toward a hangar structure (establishing shot, not gameplay). The s75/s76/s161 "hangar-flight" label for this window was an unverified inference from title-yellow color decay, not from the picture itself — **see the s150 overturned-conclusion entry below: it is the SAME craft-select scene under a corrupting camera move, not gameplay.** |
| ~+90-115s post-leave | varies | **graphics-task-submission stall** — `[vi-fs-decision]` reports `stalled=1 pairs=0` continuously, RDP `fs` counter frozen. Not a crash; a staggered subsystem shutdown (s178). Open, unresolved as of s183 (last dedicated session). Full detail: `PORTING-STATE` Sessions 176-183. Note s579: post-exit `rdpFs` plateau with live GFX is a *different* class (FULL_SYNC starvation, item -349) — do not merge. |

Menu state machine (s48, extended through s75; hold/crash triage s76-s114): title --start--> SELECT
GAME --start--> war room / SELECT LEVEL --start--> **AVAILABLE CRAFT** (war-room craft holograms; `a`
does **not** show a level description card, s61-s69). With process alive 65s+ post-`a` (s72/s73):
black ~5s -> capital-ship flash -> stable **SELECT YOUR CRAFT** (hangar pad + full X-wing; `a`
no-ops, s74; camera orbits). A single Start leaves the menu, but what it leaves INTO is unresolved
(s75's "hangar-flight" claim was **OVERTURNED s150**, see Overturned conclusions -- same craft-select
scene under a corrupting camera move, not a new environment). VI stays on the 0x6AB400/0x656400 pair
throughout -- **origin cannot identify these menu scenes**, only phases. ~20 crash classes closed
getting through this chase (mechanisms/tags: `docs/PROJECT-OVERVIEW.md` §3/§7/§9).

Remaining visual defects, all parked as M4 except where noted: outdoor 512 zero-shade masked not
fixed (`baseFixed = −32768` root cause unknown, s19/s20); S=0 triangles in the 640 attribution phase,
uninvestigated (s18); `[dpc-behind]` ring-wrap drops with `DPC_WRAP` off (not a black-screen cause,
s11). Hangar floor multi-hue band, hangar dimness, and the post-leave black/SIGBUS chain are all
FIXED (M1 closed s48; `SHADE_WRAP` s25; ImemOverrun s69 + depth-writeback SIGBUS s72) — mechanisms in
`docs/PROJECT-OVERVIEW.md` §3.

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep. 0
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. The `[missing-func]` saga
(s49's original 3 addresses plus ~801-803 further phantom `main_overlay.txt` entries found while
fixing them) is fully **CLOSED** (items -6/-249) — every clean live-verify should show 0
`[missing-func]` lines. Post-`a` process now soaks well past 65s without death.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism: `docs/PROJECT-OVERVIEW.md` §3.

**M2 — post-clip-fix regression sweep: DONE (s49).** Stability baseline: 1138 tasks, fanjal=9448,
0 cull-census-identity violations. The 3 `[missing-func]` addresses **DONE/CLOSED s399** (item -6).

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT reachable
and stable; ~20 crash classes closed s50-s294. Leave-key "hangar-flight" OVERTURNED s150; **s577
REAL hangar exit CONFIRMED** (case 3→5→6→8). Post-exit FULL_SYNC starvation product-fixed via
`ROGUESQ_FS_PIPE_INJECT` (default OFF; items -354..-358). Pipeline status as of **s671**:
- thr11 (`saveServiceWorker` `0x8006F2CC`) → sec4 → thr12 (`hudDisplayUpdateWorker` via
  `loadLevelTextureCache`) → **sec2 LIVE** under product multi-header restore.
  **s668 dual-source:** thr11d→ok136c→thr12→sec2. **s669 dual-source offline:**
  post-sec2 outdoor content LIVE ~195–200s (VI 512 0x620000/0x690000, present
  swap FIRE) then **menu sec3 return**; thr12 long-lived; **rdpFs plateau**
  (syncs=0 / E9 starved) entire thr13 window; packTlut=0. **s670 split:**
  menu-return/thr12-teardown is **input-gated** (-422). **s671: -422
  CONFIRMED dual-source and CLOSED** (2/2 pulsed attempts: thr12 alive
  >1000s, 0 sec3 return, 0 packTlut) while the **rdpFs plateau itself is
  untouched by both inject (Arm A) and input (Arm B)** — stays open as -421,
    **s675 confirms command-boundary E9 is abundant** in two independent
  post-sec2 samples (4,444/12,924 and 9,549/13,135 tasks) while runner
    FULL_SYNC appears in only 3 tasks per sample. Walker misalignment is
    refuted as the sole explanation. **s676 dispatch discriminator:** one
    recovery-active post-sec2 run had aligned walker E9 sum **32,150** in
    **6,719** positive task probes, while the authoritative RDP parser's
    cumulative E9 count advanced by only **2**. Every authoritative E9 seen
    reached `GBI_RDP::fullSync` and `State::fullSync`. Thus the dominant loss
    is before authoritative dispatch; map/handler and State accounting are
    ruled out for those commands. Residual rank: (1) **-421 authoritative
    parser advance/control-flow mismatch** then rdpFs
  starvation mechanism / packTlut (-373), (2) B8
  co-gate -393, (3) -387 **5×**. Do **not** productize DROP_GARBAGE_CIMG; do
  **not** re-soak thr11d rate (-419 CLOSED) or re-run the -422 input pulse
  (CLOSED, no residual).
- Co-gates: recovery (-374/-413/-414/-418), mat3inv (-375), ship (-376/-377/-392/-393),
  class-D (-378), FORCE_STATE6 (-381 CLOSED), freeroll (-382..-384), thr12 path
  LIVE under headers (-385 dissolved), sinfApprox (-386 1×), do_rom_read
  (-387 **5×**). thr11d metric = post-hsel destroy of `0x8006F2CC` only (s618).
  Tools default OFF: `FORCE_STATE6_AFTER`, `FORCE_CASE6_START`, `FS_PIPE_INJECT`,
  `ALLOW_WILD_W`, `FL_HDR_HARD_SKIP`, `FL_HDR_RESTORE=0`, `FL_RESTORE_MODE=body`,
  `DROP_WRAP_RDP`, `DROP_GARBAGE_CIMG`. Product ON: freelist multi-header restore.
  Diagnostics: `ROGUESQ_LOG_CIMG_RAW`, `ROGUESQ_LOG_DL_SYNC2`.
- Full durable arc: **`docs/PROJECT-OVERVIEW.md` §27**; items -349..-422; Sessions 577-675.
DoD = **cutscene→in-mission** + craft input.
*Done when:* 60s in-mission render, craft responds to synthetic input, stability 0, phase timeline
covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it. The 3 `[missing-func]` addresses, the `main_overlay.txt` phantom-overlay-function
family, and its `0x800290d4` clustering are all **DONE/CLOSED** (items -6/-249/-259).

**M5 — audio de-stubbing: DONE and fully CLOSED (s297-376).** No outstanding thread; next M5 work
needs a genuinely new lead (rechecked s570: zero new leads, intentionally-left stubs still C88
force-zero + default `real_ucode=0`; due again s573+). Full arc: `docs/PROJECT-OVERVIEW.md` §9-§12.

## Backlog — one monotonic sequence (reviewed and compacted s729)

Legacy negative identifiers remain searchable in `PORTING-STATE.md` and
`docs/PROJECT-OVERVIEW.md`; this active backlog uses the single monotonic sequence below. Closed lineages are not backlog items.

1. **M3 / legacy -421 — post-sec2 FULL_SYNC plateau: OPEN.** Outdoor rendering and presentation remain live through section 2, but genuine FULL_SYNC commands are scarce while GFX continues. **s759:** ovl20 dest-`0x12A0` route LIVE; UJ 0; residual is clip-stray `0x13B8/04` (ovl20 `jal L_17F0` return after clip hand). Sec2 E9 unevaluable (hangar leave SIGSEGV). Do not revert dest. Next is a 6e-style `0x13B8` widen for `153==0x20||0x04`. **s758:** overlay 0x20 is dest-`0x12A0` emit, not restore, not a `0x1DB0` sibling, not an E9 producer. **s757:** ovl1c `$30` pair complete. E9 still boot-shaped 3/64 through s757. Do not route n=1 `0x1E7C`. **s756–s752:** ovl1c dest + jal-returns + trampoline LIVE. **s751–s748:** ovl10/18/14 LIVE. **s743:** ovl24+ovl28 route **stops the post-s739 UJ storm** (2931→0). **s740:** resident-`0C` splice stops the section-2 `L_1DB0` reset.

2. **M3 co-gates / legacy -374, -375, -378, -382..-384, -387, -393.** These are passive
   recurrence breadcrumbs, not reactive work: recovery-cell silence, one-off math/scene crashes,
   craft-shadow, `do_rom_read+608`, and the B8 ship gate. Enqueue self-contained soaks when a
   recipe adds information; pursue only a systematic idiom-class audit after recurrence.

3. **M4 correctness.** Outdoor `baseFixed=-32768` zero-shade, attribution S=0 triangles, then
   I4 `sample=64x128`; each needs an independently controlled experiment.

4. **Tooling / legacy -20.** Intermittent regeneration omission: delete generated `funcs_*.c`
   before regen and audit `fixup_game_funcs.py` counts. Escalate only with a reproducible case.

## Closed lineages — do not reopen

- **M5 audio (legacy -160..-230): CLOSED.** A new audio lead is required; see
  PROJECT-OVERVIEW §9–§12 and `docs/M5-AUDIO-PLAN.md`.
- **Hangar-exit → sec2 pipeline (legacy -349..-422): CLOSED except backlog item 1.** Product
  multi-header freelist restore is ON. `DROP_WRAP_RDP` and `DROP_GARBAGE_CIMG` remain OFF:
  suppressing the garbage SETCIMG writeback also suppresses recovery. The exact w=1161 CIMG was
  proven garbage after ring wrap, not a legitimate game command. Detail: PROJECT-OVERVIEW §27.
- **Idiom-class audits (legacy -231..-348): CLOSED.** The duplicate-symbol, frequency-scan,
  `DL_LIST_APPEND_GUARD`, and sibling/freelist campaigns are archived in PROJECT-OVERVIEW §13–§26.
  Do not revive an individual crash without a new class-level enumeration.

### Standing / open non-pipeline items

-20. **Regen-pipeline reliability bug (s120, intermittent).** `N64Recomp` skips rewriting existing
    `funcs_*.c`; delete all before every regen is mandatory but residual intermittency unknown.
    **Standing rule**: audit patch report for unexpected counts after every `fixup_game_funcs.py`.
    PORTING-STATE 120/121/126.

-11. **`advancePlayerAnimationPhase` SIGBUS: PARKED s89, RECURRED s424, GUARDED s425** (see -261).

-10/-9. **Metal-shader-compiler SIGSEGV** (s83, one data point). **s83 spline div0 guard**: 0/5
    fires; real fix by inspection, no same-run positive control yet.

-8. **`frameStartReset` SIGBUS** — 3 occurrences (s85/s108/s156); no located faulting insn.

-7. **M3 DoD gate.** Mission-entry pipeline is live through sec2; the only active blocker is
    backlog item 1. Product settings and the durable causal chain are in PROJECT-OVERVIEW §27.

-6. **(s53→s399) M4 `[missing-func]` addresses: DONE, CLOSED s399.** PORTING-STATE 399.

-5. Past first sustained mission hold: expect new failure classes (mission overlay DMA,
    missing-func/UJ, new VI phase, overlays 12/44, texture corruption). Each is its own unit.

-3. **Sibling-repo housekeeping (not autonomous):** `~/Documents/Tools/rogue_squadron64`
    carries uncommitted symbol-file edits. Ask user before committing there.

-2/-1. **Band-row coverage history** (settled s41-49). **GPU->CPU present PNG** via
    `NativeTarget::copyToRAM` — convenience, not a blocker.

**Done, do not redo:** optimising the ucode vector path (s38: `-O0`→`-O2` gave 41x); the
ucode-performance→DL-submission-collapse→RDP-census→draw-loss chain (s33-s37); coverage
attribution/format-mismatch (`LOG_BBOX`/`LOG_UPLOAD`); the s27-s31 I4-decode line.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, re-applies hand-edits
   idempotently: `$zero` writes commented (~2700); `fake_func_*` → `__builtin_trap()`; cross-
   function branch traps; audio-engine gate stores → 0 in `funcs_23.c` for
   `setDisplayMode`/`reapplyDisplayMode` only (`initMusyXEngine` site reversed s302); `jr $t9`
   in `convertMat3x4ToN64Mtx` → plain `return`; `musyxKeyOnVoice` break 6/7 → early return;
   `evalCubicSplineAtTime` div0 guard (`[spline-div0]`).
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. **s47/s739: before the fixup, also run
`python3 tools/make_clip_composite.py [4|10|12|14|16|18|24|0x1C|28|0x20|32]` + RSPRecomp on
`factor5_rsp_ovl4.toml`, `factor5_rsp_ovl10.toml`,
`factor5_rsp_ovl12.toml`, `factor5_rsp_ovl14.toml`,
`factor5_rsp_ovl18.toml`, `factor5_rsp_ovl1c.toml`,
`factor5_rsp_ovl20.toml`, and
`factor5_rsp_ovl24.toml`**. `factor5b_rsp.toml`
is the **MusyX audio** ucode; stays in the build as a never-called artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches** — never
  `git submodule update --force`. Mirror via `submodule-patches/export.sh`.
- ROM must sit next to the executable in `build/`; otherwise silent "place your ROM" dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` / `RecompiledFuncs` die on regen — put them
  in fixup scripts.
- settings.json Bash allowlist matches FIRST WORD: prefix env assignments with `env` (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill with SIGKILL, not SIGTERM (s9).
  Python decoders: `scratch/venv/bin/python` (s18).
- `regress.sh` must not write probe images as `.*` hidden names (s26).
- ~~Screen Recording permission intermittent~~ — overturned s32: wrong window id, not permission.
- `winctl activate` ignored while another app holds focus — use `probe.sh`/`regress.sh`
  `raise_game()` (System Events `set frontmost`) instead (s45).

## Overturned conclusions — do not act on these

Full list (11+ entries spanning s2-s422, each with why it was believable and what refuted it),
plus the early-era dead-ends list: `docs/PROJECT-OVERVIEW.md` §26. Load-bearing for active work:
- **(s400-421→s422)** `0x800290d4` "six independent triggers" is `inflate_fast`'s clean return.
- **(M5-AUDIO-PLAN.md §4→s371)** host audio `queue_samples`→`SDL_QueueAudio` unit-mismatch, fixed s371.
- **(s578→s579)** post-exit `rdpFs` plateau is **not** the s178 graphics-task-submission stall —
  s178 is `stalled=1 pairs=0` + producer stop; s577 post-exit keeps submitting GFX with present
  FIRE pairs=4 while only FULL_SYNC dies (item -349).
- **(s715→s716)** zero `L_15AC` markers meant live TriGen bypassed the resident relay. This was
  believable because phase-6 summaries showed 9--15 live TriGen samples with no marker. It was
  refuted by s716's separate TriGen route budget: the live DMA word is `0x15AC` and every first
  route enters `L_15AC`, selector `0x0C`, then `L_1298→L_1DB0`; the old shared detail budget had
  already been consumed by other inline commands.

### Dead ends — labelled as such in the log, do not retry

Full list (early ucode/DMA/overlay hacks, s2b-s91) migrated to `docs/PROJECT-OVERVIEW.md` §26.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here:
- §4.1 instruments-that-lie; §4.2 attribution errors; §4.3 cross-run comparison on animating
  scenes (gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`); §4.6 missing protocol events.
- Other instrument traps: PROJECT-OVERVIEW §8.
- **crash-signature blindness (s344)**: soak "any `[CRASH]`" is not evidence for a SPECIFIC target
  unless `last-guest-pc`/`pc-symbol` matches — ~20+ independent crash families. Also: grepping
  game `run.log` for driver `[keys]` is wrong (launcher log only). Item -200.
- **repeated-`last-guest-pc` is not repeated-bug proof outside the audited set (s595)**: only
  ~52/2499 functions track `g_rs64_last_guest_pc`. N identical addresses can be N different
  crashes sharing one instrumented caller. Check audited set before "Nth occurrence" escalation.
  Item -347.
