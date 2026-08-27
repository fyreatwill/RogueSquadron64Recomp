# s2501 M5 generated AI-ring writer audit

## Scope and discriminator

This static census searched the active sibling generated tree at
`../N64Recomp/RecompiledFuncs` (51 `funcs_*.c` files) for direct stores,
constant address construction, the two AI consumers, and the s2308 fixup
rewrite. The discriminator is the complete generated-store/callee table for
the stated ring root `0x801096B0` and its derived slots.

## Generated-store and call-edge table

| source / guest PC | operation or edge | effective destination / argument | classification |
|---|---|---|---|
| all active `funcs_*.c` | direct literal/reference scan for `0x801096B0`, `0x801096B4`, `0x167000`, `0x169B00` | no direct data-store rows; the only `0x801096B0`/`0x801096B4` text is the code listing in `funcs_49.c` at those guest PCs | no AI-ring writer |
| `funcs_49.c:0x801096B4` | `sd $ra, -1($ra)` | `ADD32(ctx->r31, -1)`, not `0x801096B4`; this is an instruction at the address, plus the s2190 parity probe | unrelated malformed/generated code path, not a PCM store |
| `runAiAudioStreamPlaybackLoop:0x8008EDA4` | `sw $v0, 0($v1)` after `rs_malloc(0x3000)` | `0x80150000 - 0x6950 = 0x801496B0` | initializes the pointer-table root actually used by the active output |
| `runAiAudioStreamPlaybackLoop:0x8008EDB8` | sixteen-loop `sw $v0, 0($a0)` with `a0 += 4`; value advances by `0x300` | `0x801496B4..0x801496F0` (16 entries), each a heap pointer | initializes derived AI-buffer slots; no image/task field |
| `runAiAudioStreamPlaybackLoop:0x8008EE08` | `jal 0x80029E80` → `osAiSetNextBuffer_recomp` | `a0 = MEM_W(0x801496B0)`, `a1 = 0x300` | first AI consumer; no generated callee body in the tree |
| `runAiAudioStreamPlaybackLoop:0x8008EE84` | `jal 0x80029E80` → `osAiSetNextBuffer_recomp` | `a0 = MEM_W(0x801496B0 + 4 * index)`, `a1 = 0x300` | second AI consumer; no generated callee body in the tree |
| active tree, all callers | `rs64_m5_pcm_writer_store` | zero callsites | no kind=1 writer edge |

The active generated output therefore contains no direct store whose proven
effective destination is `0x801096B0` or a slot derived from it. The only
reachable ring/table initialization is at `0x801496B0`, four megabytes above
the address named in the work-unit brief; its two consumers are the known
`osAiSetNextBuffer_recomp` calls. The active output has no generated body for
`0x80029E80`, so there is no generated callee chain to census below that
boundary.

## Fixup check

`fixup_game_funcs.py` contains `apply_s2308_m5_pcm_writer_provenance()`, but
it is opt-in under `RS64_S2308_M5_PCM_WRITER=1`. Its rewrite surrounds the
generic scalar-store helper and labels the two AI callsites; it does not add
an AI-ring writer or change the active generated output. Historical backup
trees containing the helper are not active callers.

## Discriminator result

`H-ring-unresolved` is selected, specifically because the named root
`0x801096B0` does not match the active generated loop’s proven root
`0x801496B0`. `H-ring-direct` is not selected for the stated root: no direct
store reaches it. `H-ring-callee` is not selected: no generated callee body or
writer call edge exists below the two AI consumers. `H-ring-absent` is not
claimed for the physical AI ring as a whole because the active output clearly
initializes and consumes the distinct `0x801496B0` table.

No runtime field, instrumentation, behavior, address remap, guard, or
mitigation was added. The next probe must resolve whether `0x801096B0` is a
documentation/address typo or a separate retail/runtime-owned object before
any writer attribution is attempted.
