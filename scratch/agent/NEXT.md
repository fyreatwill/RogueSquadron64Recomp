# NEXT work unit (clip-stray 0x1364 after ovl24 route)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s743 selected H-ovl24-route-restores-fetch (UJ 2931→0) and left E9
flat (3/64). The largest NEW residual is `[clip-stray] tgt=0x1364
153=0x04` n=4434. 0x1364 is ovl24's `jal L_17F0` return, not a main
label (main has L_135C then L_1368). Do not widen the 0x1364 case to
"always OVL24" until the writer of the clip-resident jump is named.

## Competing hypotheses

- **H-l17f0-dispatches-clip:** shared `L_17F0` (or a callee) hits
  `L_1268` and sets DMEM 0x153=4 before `jr $ra` to 0x1364.
- **H-clip-uses-1364:** the clip image itself loads/jumps 0x1364
  (computed or `ori`). Our new case then steals a clip-side target.
- **H-stale-ra:** leftover `r31=0x1364` from a finished ovl24 emit is
  later `jr`'d on a clip task. Writer is stale $ra, not a live emit.

## Discriminating measurement

Static first (no rebuild): search clip overlay C + `L_17F0` body for
0x1364 / `L_1268` / stores to 0x153. Then one soak, same recipe as
s743, with a batched clip-stray predecessor (debug_line, r31, r30,
resident, last ovl-route tgt) on tgt==0x1364 only.

Outcomes:

- `L_17F0` reaches `L_1268` before returning → H-l17f0-dispatches-clip;
  next is whether that return should ignore resident.
- clip image contains 0x1364 and stray line is inside CLIP_* →
  H-clip-uses-1364; drop or relocate the 0x1364 ovl24-only case.
- stray predecessor is a clip `jr $ra` with no live ovl24 in that task
  → H-stale-ra; clear r31 on overlay swap or ignore stale 0x1364.

## Commands

    # static: grep L_17F0 / 0x1364 / L_1268 in
    #   build/factor5_ucode/factor5_ucode_recompiled.c (main L_17F0)
    #   and the CLIP_* block / factor5_ucode_ovl4_recompiled.c
    # then one s743-shaped soak with clip-stray predecessor. SIGKILL.
    # do not enable IMEM DMA globally. do not widen the 0x1364 case yet.

ORIGIN: name the writer of the 0x1364 jump while resident==4 before
any case change. s743 already showed the ovl24 emit return is
legitimate when resident==0x24.
