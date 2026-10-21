# NEXT: terrain height at the player's death xz vs the rising player y

s5781: byte0=1 = sampleTerrainAtNpcPosition (0x80068D5C, a2=0x80138058) nonzero; the player's
last 0.7 s before every death is an identical rise y -2.88 -> -0.32 at +3.6/s (x~45.5, z~32.5).

Work unit: (1) static first: disassemble 0x80068D5C (ROM 0xA5D30 + off) and name what it
compares the position y against (height field / plane / triangle list). (2) One build+run on
scratch/agent/s5777_althold.sh (GODV=0) logging, every 250 ms from respawn to death, player
x,y,z + the terrain sample's height/return for that xz (hook the jal at 0x800FF3A8 in
funcs_43.c via a tools/apply_s5781_*.py fixup, hooked like apply_s5780).

- H-spawn-below-surface: height at xz > y for the whole life (player starts under ground and is lifted); death when sample first returns nonzero.
- H-surface-is-y0: height ~0 constant, death exactly when y crosses ~0 (a scripted rise through the plane is a game rule; check against retail oracle spawn y).
- H-height-wrong: height value wild/stale vs neighbouring cells (port bug in the sampler's data).

Control: [sp175]/[bit8call] lines still print; first sample return must flip 0->nonzero at death.
HYPOTHESIS-ID: g1-record-byte0
