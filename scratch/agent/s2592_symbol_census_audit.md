# s2592 generated-symbol census: `0x800C64A4`

## Discriminator result

Selected `H-ToolMismatch`, with the underlying span classified as
`H-BoundaryOnly`. The rename generator already had an explicit
`fake_func_800C64A4 -> initHangarDisplayItemTimersPreamble` override, but the
generated overlay table and the companion symbol input both retain the exact
placeholder. The override was unsupported by the available source evidence,
so it was removed. No generated source or runtime behavior was changed.

## Evidence table

| Source | Result |
|---|---|
| Generated implementation | `funcs_34.c` defines `fake_func_800C64A4` over `0x800C64A4–0x800C64AF`; instructions are `lw ra,0x14(sp)`, `lw fp,0x10(sp)`, `addiu sp,sp,0x18`. |
| Generated overlay table | `recomp_overlays.inl` retains `fake_func_800C64A4`, ROM offset `0x21374`, size `0x0C`; the next body is `initHangarDisplayItemTimers` at `0x800C64B0`. |
| Companion symbol input | `mission_overlay.txt` explicitly retains `fake_func_800C64A4 = 0x800C64A4`; it names `initHangarDisplayItemTimers` only at `0x800C64B0`. |
| Companion source/m2c | `func_800C0084.c` declares `func_800C6498`, but no `0x800C64A4` definition or semantic name was found. |
| Exact-address/caller search | No independent source, m2c, caller, or alternate semantic mapping for `0x800C64A4` was found. |
| Rename coverage before/after | Before: one explicit override emitted. After: no `800C64A4` mapping is emitted; the placeholder remains available for regeneration. |

The epilogue shape and adjacent named entry do not prove that this fragment is
part of `initHangarDisplayItemTimers`; assigning a `Preamble` name would be a
speculative boundary rename.

