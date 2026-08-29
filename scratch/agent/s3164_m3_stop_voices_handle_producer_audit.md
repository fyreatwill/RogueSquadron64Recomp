# Session 3164 — `stopVoicesByHandle` handle producer audit

## Scope and discriminator

This is the complete static producer-edge table for the node handle consumed
by `stopVoicesByHandle` at guest `0x8008DA98`. The competing hypotheses were:

* `H-HandlePro`: every reachable producer proves a valid handle contract.
* `H-HandleUnclassified`: a reachable producer lacks that proof; this is not
  proof of a retail-invalid value.
* `H-HandleDead`: the apparent producer edges are unreachable lowering
  artifacts.

The discriminator is one joined table of every direct caller, every `+0x8`
field writer, construction/range checks, dispatch references, and independent
companion metadata.

## Consumer and caller table

| Guest PC | Generated enclosing function | Operation | Producer contract |
|---|---|---|---|
| `0x8009590C` | `stopSongByHandle` (`0x80095850`) | `lw a0, 0x8(s0)`; call `0x8008DA98` | `s0` walks the `0xE78` linked list; no local range check on the loaded handle |
| `0x80095930` | `stopSongByHandle` (`0x80095850`) | `lw a0, 0x8(s0)`; call `0x8008DA98` | same list/field and contract as above |
| `0x80095BBC` | `tickSongSequence` (`0x80095B04`) | `lw a0, 0x8(s0)`; call `0x8008DA98` | `s0` walks the `0xE78` linked list; no local range check on the loaded handle |
| `0x80095BE0` | `tickSongSequence` (`0x80095B04`) | `lw a0, 0x8(s0)`; call `0x8008DA98` | same list/field and contract as above |

The four calls are real guest `jal` sites. `stopVoicesByHandle` rejects `-1`,
walks the sorted handle list, and has no upper-bound check on its incoming
node handle.

## Writer and dispatch table

| Guest PC | Field/value | Evidence | Contract result |
|---|---|---|---|
| `0x80086518` | `sw a3, 0x8(a1)` | `allocVoiceHandleNode` stores the candidate counter in the newly linked node | `$a3` is copied without a range check; the counter skips `-1` but has no proven upper bound |
| all generated tree | call/dispatch to `0x80086450` | only declaration, body, overlay registration, and symbol records; no `jal`, function-pointer entry, or `get_function` lookup | producer reachability is unresolved, not proven dead |

The allocator increments global `0x8013ACF8`, retries when the old counter is
`-1`, scans the sorted list, allocates a free node, and stores that old counter
at `+0x8`. No wrap/upper-bound proof is present in the generated body. Other
`+0x8` loads belong to unrelated record layouts and are not writers of this
handle-node field.

## Independent metadata

The companion `main_overlay.txt` names `allocVoiceHandleNode` at `0x80086450`,
`resolveVoiceSlotByHandle` at `0x80086534`, and `stopVoicesByHandle` at
`0x8008DA98`; its comments independently identify the sorted handle-list
roles. The companion ELF symbol table independently contains the same three
addresses. `recomp_overlays.inl` and `syms/rogue_squadron.syms.toml` also
register the exact generated bodies.

## Result

`H-HandleUnclassified` is selected. `H-HandleDead` is rejected because the
four consumer calls are real reachable guest sites and the allocator body is
registered, but `H-HandlePro` is not established because the only identified
writer copies unconstrained `$a3` and no reachable allocator edge or upper
bound was recovered. This does not establish a retail-invalid handle and
authorizes no guard, audio behavior change, build, or run.
