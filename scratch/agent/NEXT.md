# NEXT work unit (fixup 6c route: ovl24 emit + ovl28 PC+=32)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s742 selected H-ovl24-skipped-imem. Do not permanently splice overlay 24
over `L_12A0` (that is DL-push / EndDL; overlay 28 exists to restore it).
Land a route swap: `L_1298` dest `0x12A0` + resident `0x24` → generated
ovl24 C; resident `0x28` → the seven-instruction `r17 += 32; goto L_10D8`.
See `docs/M3-OVL24-CONTINUATION-AUDIT.md`.

## Competing hypotheses

- **H-ovl24-route-restores-fetch:** routing those two residents stops the
  post-sec2 table-`jr` UJ storm (s740: 2935, top `0xFA92`) and is the
  missing extra `PC += 32`. Sec2 E9 match / rdpFs may move.
- **H-ovl24-not-sufficient:** ovl24+ovl28 fire on the dominant `L_1F64`
  path only. The rare `r5=0x14` → ovl14 → `r5=0x18` chain stays skipped
  into spliced ovl12; UJs remain or E9 stays flat.
- **H-l1298-12a0-not-only-ovl:** `L_1298` dest `0x12A0` is also a live
  non-0x24 path (ovl20 / something else). Blind 0x24 routing would
  mis-enter emit. Discriminate by resident byte at the `jr`.

s731 tagged every *direct* `L_12A0` as table-1 `0x06` (not `L_1298`).
That is the positive control that a dest-`0x12A0` `L_1298` route does
not steal DL-push — confirm it still holds after 6c (paired 0x06
push/pop/resume in the same soak).

## Discriminating measurement

One build, one driven soak (same recipe as s739/s740). Batch:

1. `[ovl-route]` / new 6c markers: ovl24 entries and ovl28 `r17+=32`
   must be LIVE in section 2 (positive control).
2. Unhandled jump count and overlay-12-window UJs vs s740 (2935 / 0).
3. Sec2 `[e9-prov-reset]` match and rdpFs delta vs s740 (3/64, flat).
4. Direct `0x06` push/pop/resume still balanced (must not regress s731).

Outcomes:

- ovl24+ovl28 LIVE, UJ collapse, 0x06 still balanced →
  H-ovl24-route-restores-fetch SELECTED. Score E9/rdpFs same run.
- ovl24+ovl28 LIVE, UJs stay / E9 flat → H-ovl24-not-sufficient;
  next is ovl14/ovl18, not another 0x24 tweak.
- dest-`0x12A0` entries with resident ≠ `0x24` → H-l1298-12a0-not-only-ovl;
  gate the route on resident before shipping.

## Commands

    # extract ovl24 (ROM 0x27260, 0xE3) and ovl28 (ROM 0x27348, 0x1B)
    # into composites / RSPRecomp inputs; do NOT overwrite main L_12A0
    # in factor5_ucode_recompiled.c.
    # fixup: L_1298 dest==0x12A0 && resident==0x24 → ovl24_L_12A0
    #        dest==0x1DB0 && resident==0x28 → r17+=32; goto L_10D8
    # then the s739-shaped soak. Kill with SIGKILL.
    # do not enable IMEM DMA globally.

ORIGIN: the writer is overlay 24's skipped IMEM image (emit) and
overlay 28's skipped `r17 += 32`. The values are legitimate ucode.
6c is a route, not a guard.
