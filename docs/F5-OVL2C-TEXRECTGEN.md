# Overlay 0x2C = DL op 0xBD (TexrectGen): offline decode (s4750)

Source: ROM 0x27368, 0x240 bytes, resident at IMEM 0x1DB0..0x1FF0 (144 instructions, 52 COP2).
Disassembly: `python3 tools/disasm_ovl2c.py` (self-contained, no rabbitizer) -> `scratch/agent/s4750_ovl2c.asm`.
Single-source (static decode; no RSPRecomp output or runtime capture yet). RDP opcode constants below are the
standard RDP command set, which is the independent check that the stores are RDP words.

## What it is
A 3D-positioned **billboard sprite emitter**: one DL command (`w0` in r19, inline words at `r17-16..r17-1`
after the dispatcher's `+8` and this overlay's `+16` = 24 bytes total, matching F5-UCODE-REFERENCE) becomes
`[Set_Prim_Depth, Set_Prim_Color, optional Set_Fog_Color] + Texture_Rectangle` in the RDP output buffer (r16).

## Control flow
1. `0x1DB0-0x1DC8`: `r6 = 0x670 + ((w0>>5) & 0x7F8)` selects a record in DMEM; if `r6[0x24] & 0x4343` (clip/cull flags)
   the command is **dropped** -> `0x10D8` with `r17 += 16` in the delay slot (advance is 24 either way).
2. `0x1DCC-0x1E98`: vector math. Position (`llv` at `r17-12`) is multiplied by the matrix at DMEM `0x590` (lsv of v15/v16
   from `0x590/0x59A/0x5B0/0x5BA`), `r18`-relative params (+0x20,+0x3E), then reciprocal (`vrcp/vrcph` twice = Newton
   style divide) to perspective-divide a second inline vector (`r17-8`). Outputs `r11,r12` = screen-space ds/dt step.
   `w0 & 1` swaps lanes (flip), `w0 & 2` negates S, `w0 & 4` negates T (adds inline `lhu r17-8 / r17-6` as base S/T).
3. `0x1EC0-0x1F36` RDP prefix, written at r16:
   - `0x2E000000 | ...` **Set_Prim_Depth**: `sh r6[0x1C]>>11` at +4, dz=0 at +6;
   - `0x3A000000`, `r20` at +12: **Set_Prim_Color** (r20 = colour register set by earlier ops);
   - if `r18[0x34] & 1`: `0x38000000` **Set_Fog_Color**, colour = inline word `r17-16`, alpha byte = `r6[0x13]` (+8 bytes).
4. `0x1F38-0x1FE4` rectangle: `xl,yl = r9,r10; xh,yh = r7,r8` (clamped by `vge/vlt` against v30). If `r9-r7 <= 0` or
   `r10-r8 <= 0` the rect is **dropped** (jumps to `0x1FE8`) no rect is emitted, but the 16-byte (24 with fog) prefix has
   already advanced r16, so a degenerate sprite still leaves Set_Prim_Depth/Set_Prim_Color. Otherwise opcode `0x24` (`Texture_Rectangle`) or `0x25` (`_Flip`, `w0&1`),
   tile = `r18[0x3A] & 7`, S/T = `r13-16, r14-16`, DsDx/DtDy = `r11, r12`; r16 += 16.
5. `0x1FE8`: `j 0x112C` with `$31 = 0x10D8` (return to fetch loop).

## What this means for the port
- Missing 0x2C = **zero sprites** and a wrong DL advance that re-seeds the root walk (the runaway, s4738/s4749). Both
  explain "no ship/HUD" only if those are billboard sprites; the decode proves texrects exist in this path, the ship/HUD
  attribution is still a hypothesis.
- Expected steady-state output per surviving 0xBD: 32-40 bytes RDP (prim depth + prim color [+ fog] + one texrect).
  A post-splice test is therefore: per mission frame, count RDP `0x24/0x25` words from the 0xBD path; retail comparison
  via oracle RDP stream (op 0xBD count in DL vs 0x24/0x25 emitted).
- The `0x10D8`/`0x112C` externals are already routed in the generated dispatcher; no other overlay dependency.

## Open
Splice still needs RSPRecomp (human allow rules, `scratch/agent/UNBLOCK.md`). Hand-translating 52 COP2 ops (accumulator
semantics) was judged not worth the risk without a generator to cross-check.
