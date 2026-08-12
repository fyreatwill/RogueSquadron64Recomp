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

## Fetch-pointer lifecycle audit (s712)

The generated main has **16 executable `r17 =` statements**.  The apparent
duplicates are the recompilation of a MIPS delay-slot instruction on both
generated C branch arms, not independent guest instructions.  Every one has a
known source and successor; none loads a root pointer or an unmatched frame
outside the root loader and `EndDL` return described above.

| Generated sites (count) | Value source | Successor / role | Verdict |
|---|---|---|---|
| `185, 189` (2) | `r17 + 8` | main fetch dispatch | Ordinary 8-byte command advance. |
| `271` (1) | `r17 + 8` | `L_1128` → `L_10D8` | Copies the extra word of the long RDP command form before the normal fetch boundary check. |
| `408, 412, 425, 428` (4) | `0x170`, then `r17 + 8` | DMA helper return | Scratch-DMEM DMA address setup; never enters `L_1090` as a fetch pointer. |
| `644, 648` (2) | saved `DMEM[0x654 + depth]` | `L_1088` | Non-root `EndDL` restores precisely the parent PC saved by `0x06`. |
| `664, 667` (2) | `r17 + 8` | handler-local `L_1324` | Ordinary handler input advance before its boundary return. |
| `854, 858, 876` (3) | `r17 + 8`, then conditional `r17 + 16` | inline-data helper return | The conditional payload path; its shape agrees with the reference's non-uniform inline-data advances. |
| `984` (1) | `r17 + 16` | `L_10D8` | Fixed inline-data advance before the normal boundary check. |
| `2413` (1) | `DMEM[0x154]` | direct `L_1090` | Root-loader seed, supplied by `L_1E70`'s DMA as established in s711. |

There are exactly three ways to enter `L_1090`:

| Predecessor | Mechanism | Classification |
|---|---|---|
| `L_1E80` | direct `goto`; sets `r17` from root-loader DMEM | Initial root stream. |
| `L_10D8` | direct `goto` when the normal boundary check finds `r17 != 0x278` | Ordinary continuation after a handler or command copy. |
| `L_1088` → `L_11E4` → indirect `case 0x1090` | `L_1088` is the sole `r31 = 0x1090` producer; the DMA wait helper returns through `jr r31` | Normal command-buffer load completion. |

The dispatch switch contains a `case 0x1090`, but it introduces no fourth
producer: the sole generated `r31 = 0x1090` assignment is at `L_1088`.
Likewise, the only direct `goto L_1090` sites are `L_1E80` and `L_10D8`.
The exhaustive count is the positive control for this static result.

This refutes `H-r17-stale-reload` and `H-r17-unmodelled-dispatch`. It supports
`H-r17-command-advance` only in the narrow static sense: the cap can be
reached through documented lifecycle edges. It does not establish that the
bytes consumed by a particular long stream are legitimate commands; the next
question is which cap-reachable command family produces the unbounded chain.

## 0x06 push-site static audit (s730)

The resident dispatcher has exactly one materialized `L_12A0` handler and no
direct generated branch to it: repository-wide source enumeration returns its
label and the `do_indirect_jump` switch case only. The normal low-opcode table
path at `L_1090` advances `r17` by eight bytes, then maps opcode `0x06`
(DMEM table-1 offset `0xD6 + 0x0C`) to that handler. `L_12A0` is the sole
writer of the frame pair `DMEM[0x650 + depth]` / `DMEM[0x654 + depth]`;
`L_12C4` is the sole decrement/read site, and its non-root path reaches
`L_12DC`, the sole restore of the saved parent `r17`, before `L_1088` resumes
fetch. This independently matches the Factor 5 `F3DSWRS_DL` / EndDL lifecycle.

However, this does **not** close the DMA-table alternative. `L_1298` also
enters the same generated indirect-jump switch using a DMEM `0x76` entry.
The retained s46 table capture contains `tbl76=1DB0,12A0,00D3,0D38,021F,0E10,002B,1030`:
there is an opaque-table word for `0x12A0`, even though that run's active
overlay records all selected `0x1DB0`. Generated code has no writer for that
table, so static inspection cannot establish whether the `0x12A0` word is
cap-reachable or whether such an entry has the ordinary `0x06` parent-frame
lifecycle. Thus `H-dl06-unpaired-site` is refuted for resident direct paths;
`H-dl06-opaque-overlay` remains open and needs a phase-latched source-tagged
`L_1298` → `L_12A0` trace. The old table capture is supporting evidence, not a
section-2 execution result.

## Dispatch-table / inline-advance audit (s713)

The generated dispatcher performs its universal `r17 += 8` before either
table lookup. `L_10C8` reads table 2 from `DMEM[0x64 + index]`; the direct
path reads table 1 from `DMEM[0xD6 + index]`. There are **no generated
instruction stores** to either table. Their contents arrive through the RSP
DMA/overlay path, rather than being materialized as C assignments. This is
the static positive control: exhaustive `RSP_MEM_H*_STORE` enumeration has
zero table writers, while both table readers are present at `L_1090`/`L_10C8`.

| Reference inline command | Opcode | Statically attributable target / path | Generated advance proven by this audit | Reference total | Verdict |
|---|---:|---|---|---:|---|
| MoveMem | `0x03` | table 1 → `L_14D4` | universal `+8`, then `L_14D4` `+16` | 24 | Equal. |
| TriGen | `0x05` | table 1 → `L_15AC` → overlay selector `L_1268` (`r5=0x0C`) | only universal `+8` is resident; selected overlay continuation is DMA-populated | 40 | Opaque. |
| Tri (TRI2) | `0xB4` | table 2 entry not materialized in generated C | no handler-local total can be statically assigned | 8 or 24 (`w0 & 2`) | Opaque. |
| TexrectGen | `0xBD` | table 2 entry not materialized in generated C | no handler-local total can be statically assigned | 24 | Opaque. |
| SetOtherMode_H_EX | `0xBE` | table 2 entry resolves through resident `L_12E4`/`L_12F0` family, but the exact table word is DMA data | resident helper has `+8` after its inline-word read; target attribution still needs the live table word | 16 | Single-source candidate, not certified. |
| SetOtherMode_L_EX | `0xB3` | table 2 entry not materialized in generated C | no handler-local total can be statically assigned | 16 | Opaque. |
| Tri (TRI1) | `0xBF` | table 2 entry not materialized in generated C | no handler-local total can be statically assigned | 8 or 24 (`w0 & 2`) | Opaque. |

This selects **H-dispatch-table-opaque**, not H-advance-conformant or
H-advance-mismatch. The absence is structural, not a null runtime counter:
the generated source contains only table loads and the checked-in toml lists
the indirect targets as values extracted from the ucode data section.

## Live table / fetch-loop probe (s714)

The regeneration-safe probe sampled both live table loads and reset its fixed
96-detail/32-summary budgets at each in-process VI phase. In the driven 512
phase (ordinal 6), the positive control was live: `0x03` resolved table 1 to
`0x14D4`, `0xB4` to table 2 `0x1484`, `0xBF` to `0x146C`, and `0xBE` to
`0x12E4`. MoveMem was 0/720--743 mismatch per sampled task (extra `+16`);
extended OtherMode-H was 0/186--202 mismatch (`+8`). These are independent
live confirmations of the static MoveMem result and the resident OtherMode
candidate.

TriGen was 15/15 mismatch in the first dense phase-6 task and Tri was
1,245--1,372 mismatch per sampled task under a dispatcher-to-*next fetch*
comparison. That is **not evidence of an advance defect**: the exact live
triangle entries show both `+24` and `+8` fetch-loop deltas, while the
reference says Tri may consume inline data and continue a triangle run. A
single next-fetch point therefore collapses multiple internal command steps
into one delta. The probe correctly establishes its table-word control and
rules out a zero-count interpretation, but it leaves
H-advance-conformant/H-advance-mismatch unevaluable for Tri/TriGen. The next
probe must reconstruct `r17` at the internal advances in `0x146C`, `0x1484`,
and the live TriGen overlay path before comparing reference totals.

## Internal Tri steps (s715)

The v2 probe retained the phase-6 live-table control and added calls directly
after both `r17` advances in the shared `L_13A8` Tri helper. In task 3391, the
live `0xB4 → 0x1484` and `0xBF → 0x146C` entries reached the textured branch
at `0x13B0` (`delta=16`) and the non-textured branch at `0x13A8`
(`delta=8`). These are the two conditional steps described by the independent
reference: no wrong individual generated increment was observed. The old
dispatch-to-next-fetch `+8/+24` differences consequently remain attributable
to continuation between triangle commands, not evidence of a wrong Tri
increment. This is support for H-tri-run-conformant, not a complete generated
total proof.

The same run had `tg=9--15/9--15` live TriGen samples per phase-6 task, but
no `L_15AC` overlay marker. Thus the resident `L_15AC` relay is not the live
continuation entered by those table words; it cannot instrument TriGen's
internal advance. TriGen remains opaque and is the next discriminating target.

## Live TriGen route (s716)

The v3 route trace gave `0x05` a separate per-phase budget. In qualified
phase 6, task 3391 had 15 live TriGen samples and retained the established
table controls. Every first route was `table1:0x15AC → L_15AC` (generated line
211), followed by selector `0x0C` at `L_1268`, then `L_1298` and `L_1DB0`.
This is two-line support (the resident generated route and the live
DMA-provided table word) for the resident relay; the old s715 zero marker was
a shared-budget failure, not an opaque direct-overlay continuation. It does
not measure TriGen's handler-local `r17` increments: the next probe must
instrument `L_1DB0`'s actual advances while retaining this route control.
