# NEXT work unit — recover the missing `allocVoiceHandleNode` producer edge

HYPOTHESIS-ID: m3-stop-voices-by-handle-audit

## Single work unit

Complete the open edge from Session 3150: recover all references to guest
`0x80086450`/`allocVoiceHandleNode` (including tables, indirect dispatch, and
unresolved `jal` targets), then trace each `$a3` setup to the node `+0x8`
write. Do not add a guard, change audio behavior, or run the blocked M5 route.

## Competing hypotheses

- `H-HandleBound`: every recovered producer path establishes `$a3 < 0x20`.
- `H-HandleUnbounded`: a recovered producer path reaches `$a3` without a
  `<0x20` proof.
- `H-HandleIndirectOnly`: the allocator is only reachable through an
  indirect/table edge not represented by direct generated calls.

## Discriminating measurement

Build one complete reference/producer table: reference PC or table entry,
dispatch mechanism, `$a3` setup, range operation, and path to node `+0x8`.
`H-HandleBound` requires every recovered path to establish `< 0x20`; an
unbounded recovered path selects `H-HandleUnbounded`; only indirect/table
reachability with no recoverable input selects `H-HandleIndirectOnly`.

## Exact commands

```sh
rg -n 'stopVoicesByHandle|0x8013D880|0x80141AD0|0x17C|0x17c|0x64\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'startNoteOnVoice|allocateSynthVoice|freeSynthVoiceFromActiveList' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n '80086450|0x80086450|allocVoiceHandleNode|0x86518' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/N64Recomp/*.toml
git diff --check
```
