# The Factor 5 graphics microcode: reference implementation and what it tells us

Rogue Squadron's graphics microcode was reverse-engineered and implemented at
the *semantic* level in 2017 by olivieryuyu (decode) and gonetz (implementation)
for GLideN64, funded by an Indiegogo campaign, and shipped in GLideN64 Public
Release 3.0 that December. The game is fully playable HLE there. The
implementation is `src/uCodes/F5Rogue.cpp` in <https://github.com/gonetz/GLideN64>.

**We have been emulating this microcode instruction-by-instruction (RSPRecomp
LLE) for 40+ sessions without ever consulting the published description of what
it means.** That is the single largest missed lever on this project. This
document exists so nobody re-derives from a disassembler what is already
written down.

## Getting the reference

    tools/oracle/fetch_reference.sh

drops `F5Rogue.cpp/.h` and `F5Indi_Naboo.cpp/.h` into `reference/gliden64/`,
which is gitignored. **Do not vendor these files into the repo and do not copy
code out of them into our tree.** GLideN64 is GPL-2.0-or-later; this project is
not, and the LLE path means we never needed the code, only the semantics. Read
it, take the meaning, write our own.

`F5Indi_Naboo.cpp` is the sibling microcode for Indiana Jones and Battle for
Naboo — same house, same era, "almost as large", and useful when the Rogue
implementation is terse about something.

## The command table (verified against F5Rogue.cpp:25-43, 1320-1342)

The dispatch is a normal F3D-style GBI with Factor 5 opcodes substituted in:

| Opcode | Name                       | Handler                     |
|--------|----------------------------|-----------------------------|
| 0x01   | `G_MTX`                    | `F3DSWRS_Mtx`               |
| 0x02   | `F3DSWRS_VTXCOLOR`         | `F3DSWRS_VertexColor`       |
| 0x03   | `F3DSWRS_MOVEMEM`          | `F3DSWRS_MoveMem`           |
| 0x04   | `F3DSWRS_VTX`              | `F3DSWRS_Vtx`               |
| 0x05   | `F3DSWRS_TRI_GEN`          | `F3DSWRS_TriGen`            |
| 0x06   | `F3DSWRS_DL`               | `F3DSWRS_DList`             |
| 0x07   | `F3DSWRS_BRANCHDL`         | `F3DSWRS_BranchDList`       |
| 0xB3   | `F3DSWRS_SETOTHERMODE_L_EX`| `F3DSWRS_SetOtherMode_L_EX` |
| 0xB4   | `F3DSWRS_TRI2`             | `F3DSWRS_Tri`               |
| 0xB5   | `F3DSWRS_JUMPSWDL`         | `F3DSWRS_JumpSWDL`          |
| 0xB8   | `F3DSWRS_ENDDL`            | `F3DSWRS_EndDisplayList`    |
| 0xBC   | `F3DSWRS_MOVEWORD`         | `F3DSWRS_MoveWord`          |
| 0xBD   | `F3DSWRS_TEXRECT_GEN`      | `F3DSWRS_TexrectGen`        |
| 0xBE   | `F3DSWRS_SETOTHERMODE_H_EX`| `F3DSWRS_SetOtherMode_H_EX` |
| 0xBF   | `F3DSWRS_TRI1`             | `F3DSWRS_Tri`               |

### Correction to our own notes

PORTING-STATE's session-8 entry says the gfx tasks carry "F5 custom geometry
ops 0x01/0x02/0x03" and that RT64's `GBI_F3DFACTOR5` stubs them. Those three
opcodes are **matrix load, vertex colour, and movemem** — none of them emits
geometry, so "the geometry ops emit nothing" was never a statement about the
geometry ops. Real geometry comes from `0x05 TRI_GEN`, `0xBF TRI1`,
`0xB4 TRI2`, and `0xBD TEXRECT_GEN`. Any future reasoning that starts from the
old naming is starting from a wrong premise.

## Commands carry inline data — the pointer advance is not uniform

This is the structural fact that makes the microcode unlike F3D, and the one
most likely to be behind a stream that decodes into nonsense. Six commands
consume display-list words *beyond* their own 8 bytes (F5Rogue.cpp line refs):

| Command                  | Extra advance | Line |
|--------------------------|---------------|------|
| `MoveMem` (0x03)         | `PC += 16`    | 164  |
| `TriGen` (0x05)          | `PC += 32`    | 1044 |
| `Tri` TRI1/TRI2          | `PC += 16` **only when `w0 & 2`** (textured), then `PC += 8` | 1126, 1143 |
| `TexrectGen` (0xBD)      | `PC += 16`    | 1178 |
| `SetOtherMode_H_EX` (0xBE)| `PC += 8`    | 1298 |
| `SetOtherMode_L_EX` (0xB3)| `PC += 8`    | 1306 |

`Tri` is the dangerous one: its advance is **conditional on a bit in w0**, it
reads its colour indices from `PC+8` and its texture coordinates from `PC+16`,
and it peeks at `PC+16` again to decide whether the next command continues a
triangle run. A consumer that gets that bit wrong does not fail loudly — it
resumes decoding mid-way through inline vertex data, and every subsequent
"command" is manufactured from triangle coefficients.

`SetOtherMode_*_EX` is the subtle one: it reads a **mask word from RDRAM at the
new PC** (`otherMode.h &= *(u32*)&RDRAM[PC]; otherMode.h |= w1`), so it is a
read-modify-write against inline data, not a plain set.

## No F5 handler synthesises a colour image

There is no `gDPSetColorImage` / SETCIMG anywhere in F5Rogue.cpp. Read this
precisely: it means none of the *Factor 5 specific* handlers computes a
colour-image command. It does **not** mean the stream cannot contain one — raw
RDP commands sitting in the display list are dispatched by the shared RDP
command table that every ucode uses, so a legitimate SETCIMG can and does pass
through. The claim is about who *computes* the operands, not about whether the
opcode can appear.

**Consequence for the wild-CIMG line of work (items -405..-407, s640-s659):**
the anomaly in `SETCIMG addr=0x1F0D74 w=1161 siz=3` is the *operands*, and no
F5 handler is in the business of producing them. 1161 is not a width this game
is known to use — the measured set is 320, 512, 640, 1024 — though note a
render-to-texture target need not match a VI width, so the width alone is
suggestive rather than conclusive. What makes it worth settling first is that
two very different mechanisms explain it and they call for opposite fixes:

- the command is present in the stream as written, and the game (or our ucode)
  really does target that address, or
- the stream is being decoded at a desynchronised offset and those operands are
  inline vertex/coefficient data being read as a command.

The second dissolves the entire mitigation stack. Neither has been tested. Our
own notes already record that the `[seq]`/`[full-hist]` RDP walkers desync on
triangle commands because they step a fixed 8 bytes, which is precisely the
failure mode the second mechanism describes — that was recorded as a
diagnostic-only limitation and never checked against the real parser.

## TriGen is a mesh generator with selectable subsets

`F3DSWRS_TriGen` (F5Rogue.cpp:1012) switches on two bytes of w0 into three
generators: `TriGen0000`, `TriGen0001` (mode 0x00, sub-mode 0x00/0x01) and
`TriGen02` (mode 0x02). Each has a *default triangle order* table —
`TriGen0000_defaultTriangleOrder[32]`, `TriGen0001_defaultTriangleOrder[8]`
(lines 62, 113) — plus `option_*` variants selected by the command parameters,
and separate `PrepareVtxData` / `PrepareColorData` steps that fetch vertex and
colour arrays from RDRAM addresses in the parameter block.

This is the "microcode command which generates all terrain polygons" that
gonetz singled out as a milestone in the 2017 development log.

**Consequence for the hangar band (a confirmed coverage hole, s41/s42/s43):**
we established that geometry *is* submitted through the band's rows (s42), that
its raster state is identical to its neighbours' (s43), and that the orange
pixels receive no geometry at all (s41) — i.e. some polygons that should fill
those rows are never emitted while their neighbours are. A generator whose
emitted subset is chosen by an option code and a triangle-order table is
exactly the shape of defect that produces that. The next instrument should
compare our LLE ucode's per-`TriGen` emitted triangle count and option code
against what the reference implementation selects for the same parameters,
rather than adding another RT64-side census.

## How to use this as an oracle

Three questions this reference answers directly, without a build:

1. *Can the real microcode emit command X?* — read the handler. If there is no
   code path to it, our emitter invented it.
2. *How many DL bytes should command X consume?* — the table above. Compare
   against our LLE ucode's actual PC advance for the same command.
3. *What does this parameter mean?* — the handlers name their fields
   (`gSP.textureCoordScale`, `vertexColorBase`, viewport, fog multiplier/offset
   at `MW` sub-opcodes 0x08/0x0A).

For questions about the *machine* rather than the microcode — "does the retail
game ever write this address?" — use `tools/oracle/` instead, which runs the
retail ROM under a real emulator. See `tools/oracle/README.md`.

## LLE synthetic-cap return-path audit (s710)

`src_kind` is a host log field, not a generated-code variable. The complete
repository enumeration found exactly one producer of `src_kind=2`: fixup 10
in `tools/fixup_factor5_ucode.py` injects
`rs64_e9prov_source_end(r17, 2)` immediately before the synthetic
`return RspExitReason::Broke` at generated `L_1090`. It is therefore an
unambiguous cap marker, not a second generated return mechanism.

| Producer / edge | Guard and control flow | Command semantics | Verdict |
|---|---|---|---|
| `L_1090` cap → `source_end(..., 2)` | `++rs64_iter > 16384`; direct synthetic `Broke` return before the next fetch | Not a Factor 5 command or guest return | The only `src_kind=2` producer; it cannot be assigned off the cap path. |
| `0x06` → `L_12A0` | Dispatch table maps `0x06` to `L_12A0`; it saves the already advanced parent `r17` at `0x654+depth`, increments depth, DMA-loads child `r20`, then re-enters fetch via `L_1088` | `F3DSWRS_DL`: child display-list call | Matches call semantics. |
| child `0xB8` / EndDL → `L_12C4` → `L_12DC` | Non-negative decremented depth loads the saved child target, restores saved parent `r17`, then jumps to `L_1088` | `F3DSWRS_ENDDL`: return to caller | Matches return semantics; no child can return directly to the repeated dispatcher without restoring its parent PC. |
| root `0xB8` / EndDL → `L_12C4` → `L_10E8` | Decremented depth is negative; direct branch to natural `Broke` exit | Root display-list completion | Matches root-exit semantics. |

The static code path independently agrees with the command reference and the
earlier live paired-frame controls: `H-cap-misses-06-return`,
`H-cap-misses-enddl-exit`, and `H-probe-misattribution` are refuted for the
generated main ucode. This does not prove why the cap rows lack a root EndDL;
the next audit is root-stream lifecycle, not another unchanged recovery reroll.

## Root-loader state-field audit (s711)

The generated main ucode has exactly three instruction accesses to the
root-state field at `DMEM[0x154]` (`0x54($18)`, with `$18 = 0x100`). The
table is exhaustive for instruction accesses; the root loader also overwrites
the field by DMA, which is a separate data-flow edge.

| Site | Access / source | Successor | Lifecycle verdict |
|---|---|---|---|
| `L_1494` | `sh r11, 0x54($18)` after its `L_1484` setup path | renderer-state save; later `L_14B8` reloads the saved trio | Not a root-stream reload path. |
| `L_14B8` | `lhu r11, 0x54($18)` (with companion fields `0x56/0x58`) | resumes the renderer-state helper through `L_17F0` | Paired with `L_1494`; does not enter `L_1090`. |
| `L_1E80` | `lhu r17, 0x54($18)` | direct `goto L_1090` | The sole instruction path which seeds a fetch pointer from this field. |

`L_1E80` itself has one direct producer: `L_1E70` calls DMA helper `L_122C`
with DMEM destination `r3=0`, DRAM source `DMEM[0x38]`, and length `0xFFF`;
on return (`r31=0x1E80`) it loads `DMEM[0x154]` and starts fetching. Therefore
the loader DMA, rather than `L_1494`, supplies the root pointer for this path.
There is no edge from the synthetic cap return to `L_1E80`: cap rows return
directly from `L_1090`. This refutes `H-root-stale-or-unwritten` for the root
loader and selects `H-cap-never-enters-root-reload` for a cap row. It leaves
open whether the ongoing `r17` in a cap row is a legitimate command-chain
continuation or an incorrect continuation; audit every `L_1090` predecessor
and every `r17` writer next.
