# NEXT work unit — trace the `stopVoicesByHandle` handle bound

HYPOTHESIS-ID: m3-stop-voices-by-handle-audit

## Single work unit

Complete the open edge from Session 3149: enumerate every writer and allocator
that can produce the handle passed to `stopVoicesByHandle`, and prove or fail
to prove that its low byte is in `0..0x1F` before the 0x17c-stride table access.
Do not add a guard, change audio behavior, or run the blocked M5 route.

## Competing hypotheses

- `H-HandleBound`: all reachable handle writers/allocators clamp or construct
  an index below 32 before the four callers pass node `+0x8`.
- `H-HandleUnbounded`: at least one reachable writer can publish a low byte
  from 0x20..0xFF, leaving the callee's table access unclassified.
- `H-HandleCallerMismatch`: the four callers do not all pass the same handle
  field or one caller bypasses the documented active-list contract.

## Discriminating measurement

Build one complete writer/caller table: guest PC, destination address/field,
writer function, input provenance, range operation, and each path to node
`+0x8`. `H-HandleBound` requires every reachable path to establish `< 0x20`;
one reachable path without that proof selects `H-HandleUnbounded`, and a
field/caller mismatch selects `H-HandleCallerMismatch`.

## Exact commands

```sh
rg -n 'stopVoicesByHandle|0x8013D880|0x80141AD0|0x17C|0x17c|0x64\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'startNoteOnVoice|allocateSynthVoice|freeSynthVoiceFromActiveList' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
git diff --check
```
