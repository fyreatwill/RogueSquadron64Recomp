# Session 2966 source table

Candidate: `0x800EC6EC`, generated as `fake_func_800EC6EC` in the mission
overlay.

| Test | Evidence | Result |
|---|---|---|
| Generated body | `funcs_40.c` contains exactly one invalid COP2 word, `0x4B140BE8`, emitted as `do_break(2148452076)`; no MIPS prologue, return, or callable body | H-DataGap |
| Predecessor | `destroyObjectOwnedNpcSlot` occupies `0x800EC6C0`–`0x800EC6E8`; its final instruction at `0x800EC6E8` is the stack restore and its body returns | Separate complete body |
| Successor | `tickCraftMountedAnimationEffect` begins at `0x800EC6F0` with its own `addiu sp, sp, -0xA0` prologue | Separate complete body |
| Generated callers | No `jal` or direct call to `fake_func_800EC6EC`, `func_800EC6EC`, or `0x800EC6EC`; the only nearby call is to the successor at `0x800EC6F0` | No callable evidence |
| Independent lookups | No runtime/source lookup of the candidate address found in the generated tree, tools, or companion source | No callable evidence |
| Companion map | `mission_overlay.txt` retains `fake_func_800EC6EC = 0x800EC6EC`; it has no semantic name and names the successor `tickCraftMountedAnimationEffect` | Confirms unresolved placeholder, not a callable mapping |
| Overlay map | `syms/rogue_squadron.syms.toml` records size `0x4`, immediately between the two complete bodies | Mechanically bounded gap |

Decision: rename to `data_gap_800EC6EC`. This is a non-callable generated
fixup/data record, not a game function. No semantic rename is justified.
