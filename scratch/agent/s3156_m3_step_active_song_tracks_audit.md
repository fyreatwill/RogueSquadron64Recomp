# Session 3156 — `stepActiveSongTracks` song-tempo reader audit

## Discriminator

The selected class was the final 12 readers of `D_801529C0` (`0x801529C0`)
inside `stepActiveSongTracks`. The complete table below records each guest
reload PC, the first use of the loaded pointer, its control-flow context, and
the producer edge. A reachable row without a local proof would select
`H-M3-Unclassified`; a lowering-only row would select
`H-M3-LoweringOnly`.

## Site table

| Site | Reload PC | First loaded-pointer use | Control-flow role | Result |
|---|---:|---|---|---|
| ast1 | `0x8009498C` | `+0x570` after `+s1` | outer 64-channel loop head | proven by writer/range and channel skip edge |
| ast2 | `0x800949C8` | `+0x570`, then `+0x0` through channel node | active-channel node entry | proven by writer/range; local node path follows active check |
| ast3 | `0x80094B20` | `+0xEF4` byte store | queued-message attach block | proven by same producer; bail converges at `L_80094D48` |
| ast4 | `0x80094B48` | `+s2`, then `+0x58B` | queued-message attach block | proven by same producer; same convergence |
| ast5 | `0x80094BC0` | `+s2`, then `+0x589` | queued-message attach block | proven by same producer; same convergence |
| ast6 | `0x80094C18` | `+0x4` list-link store | queued-message attach block | proven by same producer; same convergence |
| ast7 | `0x80094C38` | `+0xE78` list-head store | queued-message attach block | proven by same producer; same convergence |
| ast8 | `0x80094C58` | `+s2`, then `+0x528` | queued-message attach block | proven by same producer; same convergence |
| ast9 | `0x80094CB4` | `+s2`, then `+0x570` | post-dispatch node update | proven by same producer; node path is already active |
| ast10 | `0x80094D1C` | `+0xE78` write target | detached-node/list-head case | proven by same producer; independent `0x29C4` path follows |
| ast11 | `0x80094D4C` | `+s2`, then `+0x570` read/modify/write | cursor advance at `L_80094D48` | proven by same producer; ast12 independently rechecks |
| ast12 | `0x80094D64` | `+s1`, then `+0x570` read | cursor recheck before node-loop backedge | proven by same producer; false/invalid path finishes channel |

The generated body has exactly these 12 address rows and one unique function
epilogue at `0x80094DAC`; none is a duplicate delay-slot-only row. The outer
loop initializes `s1=0`, advances by `0x24`, and stops at `0x40` channels.
The inner song cursor uses `s2`, which is initialized by the caller's active
song loop and is advanced in the producer's bounded eight-slot loop by
`0xEF8`.

## Producer and ordering evidence

The complete generated tree has one store to `0x801529C0`: guest PC
`0x80096D88` in `tickAllActiveSongs`. It stores
`0x8014AA00 + s2`; `s2` starts at zero and the producer loop executes at most
eight iterations, advancing by `0xEF8`. Thus every published base is in the
KSEG0 RDRAM range. The caller sequence is
`advanceSongRegion` (`0x80096EEC`) → `stepActiveSongTracks`
(`0x80096EF4`) → `stepSongPitchBendLanes`, so the producer's current-song
base publication dominates the reader call in the represented generated
control flow.

Independent companion metadata identifies `D_801529C0 = 0x801529C0` with
size `0x900`, `stepActiveSongTracks = 0x80094958`, and
`tickAllActiveSongs = 0x80096D08` in `main_overlay.txt`. The local ELF also
exports both function symbols at those exact addresses.

## Result

`H-M3-Proven` is selected for this complete 12-site slice from generated
control flow plus companion symbol/ELF metadata. The existing guards remain
diagnostic/safety machinery; this audit does not authorize removing them,
adding another guard, or changing audio behavior. No build or runtime soak
was needed because the discriminator was a bounded static producer/data-flow
table.
