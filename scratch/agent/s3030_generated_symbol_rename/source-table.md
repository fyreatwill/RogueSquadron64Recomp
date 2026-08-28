# Session 3030 — `0x800668B0`

| Evidence source | Observation | Classification |
|---|---|---|
| Companion map `rogue_squadron64/symbol_files/main_overlay.txt:812` | Names `waitForAnyAudioSlot` at `0x800668B0` and describes a loop calling `anyAudioSlotActive` until a slot is active. | Exact semantic identity |
| Generated body `RecompiledFuncs/funcs_15.c` | Standalone `RECOMP_FUNC void waitForAnyAudioSlot(...)` begins at `0x800668B0` and ends at `0x80066917`; the next function starts at `0x80066918`. Size is `0x68`, matching the symbol table and overlay entry. | Callable boundary agrees |
| Generated body operations | Ticks MusyX if active, calls `anyAudioSlotActive`, loops while the returned mask is zero, then frees three audio resources and returns. | Body matches companion description |
| Generated callers | Calls appear from `menuOverlayInit` at `0x800C5CF4`, `cinematicDeactivator` at `0x800A64D4`, and the generated teardown path at `0x800FBA8C`; all target the named generated function. | Caller references are coherent |
| Generated header `funcs.h:848` | Declares `waitForAnyAudioSlot(uint8_t*, recomp_context*)`. | Header agrees |
| Overlay registration `recomp_overlays.inl:849` | Registers `waitForAnyAudioSlot` at offset `0x00066470` with ROM size `0x68`; the next entry begins at `0x000664D8`. | Registration agrees |
| Project symbol TOML before this audit | Had `func_800668B0`, VRAM `0x800668B0`, size `0x68`. | Stale name only |

## Decision

Selected **H-exact-callable**. Synchronized the project symbol TOML to
`waitForAnyAudioSlot`. No duplicate generated callable definition or inline
fragment was found, so no placeholder preservation or ambiguity handling is
needed.
