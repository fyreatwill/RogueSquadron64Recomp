# NEXT work unit (ovl20 dest-0x12A0 route)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s758 static audit (`docs/M3-OVL20-SUCCESSOR-AUDIT.md`):
overlay 0x20 is dest-`0x12A0` emit, not restore, not a
`0x1DB0` sibling, and not an E9 producer. Live consume is a
6c-style route swap. Do **not** overwrite `L_12A0`. Do **not**
splice as a `0x1DB0` sibling. Do **not** widen `0x1E6C` to
`153==0x20`. Do **not** expect E9 to leave the boot-shaped
3/64 triplet.

## Competing hypotheses

- **H-ovl20-route-runs:** dest `0x12A0` / `153==0x20` →
  `OVL20_12A0` fires LIVE; first-edge sec2 `last_ovl` becomes
  `0x20/0x12A0`; leftover `0x1E6C/20` stray drops. 4/4 boot
  `dl06=2/2/0` holds.
- **H-ovl20-route-breaks-06:** dest-`0x12A0` arm steals main
  `L_12A0` / ovl24; boot `dl06` unpaired or UJ in the 0x12A0
  window.
- **H-ovl20-route-restores-e9:** section-2 E9 match leaves
  the boot-shaped 3/64 triplet (refute of s758 static).
- **H-ovl20-needs-1ed4-keep:** dest route LIVE but body dies
  on `jal 0x1ED4` (UJ or clip-stray `0x1ED4/20`) because
  `OVL1C_1ED4` is still `153==0x1C` only. Then the same
  iteration must widen `0x1ED4`/`0x1F04` to `153==0x20` —
  without that keep-alive the overlay cannot run past the
  first jal.

## Discriminating measurement

One build, one soak (s757 recipe). Same-run controls: clip
`res=0x04`, ovl24 `res=0x24 tgt=0x12A0`, ovl1c dest + `$30`
pair, and the new `[ovl-route] res=0x20 tgt=0x12A0`.

- route LIVE + dl06 2/2/0 + E9 still 3/64 → H-ovl20-route-runs
  and H-ovl20-not-the-e9-hole hold; predicted residual is
  UJ/stray on the `jal 0x1ED4` returns (`0x12BC`/`0x12CC`/…)
  or on `0x1ED4` itself if the keep-alive was omitted.
- dl06 breaks or ovl24 `res=0x24` dies → H-ovl20-route-breaks-06.
- E9 match rises off the boot-shaped triplet →
  H-ovl20-route-restores-e9 (overturns s758).
- dest LIVE but first body jal is UJ `0x1ED4` →
  H-ovl20-needs-1ed4-keep; widen `OVL1C_1ED4`/`1F04` to
  `153==0x1C || ==0x20` in the same iteration.

## Commands

    # add OVERLAYS[0x20] = (0x27108, 0x158, "ovl20", 0x25830, None)
    python3 tools/make_clip_composite.py 0x20
    # new factor5_rsp_ovl20.toml (dest 0x12A0, extra targets:
    #   0x12A0..0x13F0 internals + 0x1ED4/0x1F04/0x1F0C +
    #   L_112C/L_1268/L_17F0). Do not name it ovl28.
    # RSPRecomp factor5_rsp_ovl20.toml
    # fixup 6q: extract L_12A0..0x13F7, rename OVL20_*, route
    #   dest 0x12A0 when 153==0x20 (keep the 0x24 → OVL24_12A0
    #   and default → L_12A0 arms). Rewrite jal 0x1ED4 to
    #   OVL1C_1ED4 (or case 0x1ED4 for 153==0x20). Widen
    #   0x1F04 to 153==0x1C || 0x20 so the trampoline can
    #   return. Shared 0x12A0-window cases get an extra
    #   153==0x20 arm; do not steal 0x24 / L_12A0.
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build -j8 --target RogueSquadron64Recomp
    # soak: copy s757 recipe; require
    #   [ovl-route] res=0x20 tgt=0x12A0
    #   [ovl-route] res=0x24 tgt=0x12A0
    #   [ovl-route] res=0x1C tgt=0x1EA8
    #   dl06=  and  no [CRASH]

ORIGIN: OVL1C_1ECC is `j L_1268; ori $5, 0x20`. Table desc
`0x2157` selects dest `0x12A0`. Route, not an overwrite of
`L_12A0`. ovl28 already restores that image.
