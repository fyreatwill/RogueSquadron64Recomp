# NEXT work unit (route 0x1364 for clip-resident return)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s744 named the writer: `[clip-stray] tgt=0x1364 153=0x04` is
`CLIP_1E48` `jr $ra` of the `$ra` set by `OVL24_135C` `jal L_17F0`
after `L_17F0` handed to clip via `L_1268`. The value is legitimate.
Widen the 0x1364 case to `OVL24_1364` when resident is 0x24 **or**
0x04. Do not use a bare "always OVL24": after overlay 28 restores
main `L_12A0`, IMEM 0x1364 is main bytes (no live `j1364` with
resident 0x28 in s744, but keep the gate). Do not enable IMEM DMA.

## Competing hypotheses

- **H-1364-restore-e9:** returning those ~4454 clip-complete emits
  into `OVL24_1364` → `L_112C` restores post-sec2 FULL_SYNC (E9
  match rises; rdpFs climbs with GFX).
- **H-1364-needed-but-not-e9:** stray 0x1364 goes to 0 and ovl24
  emit continues, but E9 match stays 3/64. Remaining leak is
  elsewhere (ovl14 skip, or `[clip-stray] tgt=0x1DF4 153=0x00`).
- **H-1364-breaks-06:** the extra 0x04 arm steals a main-image
  0x1364 and breaks the four boot `dl06=2/2/0` controls.

## Discriminating measurement

One build: fixup 6c case `0x1364` accepts `0x153==0x24 || ==0x04`,
keep the s744 predecessor counters (posctrl: `jal17f0` still
equals `j1364`; `clip1e48_1364` now equals successful
`[ovl-route] res=0x24 tgt=0x1364` instead of stray). One soak,
same recipe as s743/s744. SIGKILL.

Outcomes:

- stray `0x1364/04` → 0 AND sec2 E9 match >> 3/64 →
  H-1364-restore-e9; productize the case.
- stray → 0, `dl06` still 2/2/0, E9 still 3/64 →
  H-1364-needed-but-not-e9; next is 0x1DF4/ovl14, not more 0x1364.
- `dl06` breaks or UJ returns → H-1364-breaks-06; revert the arm.

## Commands

    # edit tools/fixup_factor5_ucode.py case 0x1364 (and the already-
    # applied generated case), then
    #   python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    #   DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    # one s744-shaped soak. SIGKILL. do not enable IMEM DMA.

ORIGIN: s744 named the writer (CLIP_1E48 jr of OVL24_135C jal).
The 0x04 arm is a route of a legitimate return, not a guard.
