# Session 3221 — A12 `0x8014974C` publication census

## Competing hypotheses and discriminator

- `H-NamedFlagWriter`: every store is a named audio path and writes only a
  finite gate value.
- `H-InvalidFlagProducer`: a generated store writes an out-of-range or
  otherwise overlapping value that the spin is hiding.
- `H-NoLiveFlagWriter`: no live generated store remains beyond already-known
  sites.

The discriminator was a complete static census of the generated tree for the
physical byte at `0x8014974C` (`0x80150000 - 0x68B4`), including the named
waiters and their callers. The independent cross-checks were the generated
function address comments and `syms/rogue_squadron.syms.toml`'s function
boundaries; the companion decomp's `undefined_syms_auto.txt` independently
identifies the object as `D_8014974C`.

## Census

The target is a byte, not a word: every guest store uses `sb` and every guest
load uses `lbu`.

| Guest PC | Generated function | Access | Source value / use | Classification |
|---|---|---|---|---|
| `0x8008F490` | `setupSongRenderBuffers` | `sb $zero` | initialization to `0` | legitimate initialization |
| `0x800912D8` | `musyxSynthFrame` | `lbu` | tests the gate before receiving the audio queue message | named consumer |
| `0x800912F8` | `musyxSynthFrame` | `sb $zero` | clears the gate after `osRecvMesg` | legitimate terminal clear |
| `0x80091680` | `musyxSynthFrame` | `sb $v0` | `$v0` is set immediately to `1` at `0x80091660`, before the indirect callback at `0x80091684` | legitimate binary publication |
| `0x80091DC4` | `shutdownAudioEngine` | `lbu` | busy-spins until the gate is clear | named waiter |
| `0x80091F34` | `waitForMusyXAudioTaskDone` | `lbu` | busy-spins until the gate is clear | named waiter |

The generated source also contains diagnostic helper reads at the entry/exit
logging sites in `funcs_23.c` and `funcs_24.c`; these are host-side probes, not
guest instructions or additional writers. No `sw`, `sh`, `sd`, literal
`0x8014974C`, or other generated store targets this object. The `funcs_49.c`
`-0x68B4` match is a different base/address (`0x8010A848`) and is not part of
this object.

Caller census: `shutdownMusyXEngine` calls `shutdownAudioEngine`,
`musyxNoopStub` calls `waitForMusyXAudioTaskDone`, and `musyxSynthFrame` calls
`setupSongRenderBuffers` on its initialization path. No other direct generated
callers of the two waiters or the initializer were found.

## Result

`H-NamedFlagWriter` is selected. The only live stores are the initializer's
zero, `musyxSynthFrame`'s zero after queue receipt, and a fixed one before its
indirect callback. The source scope therefore proves the flag is a binary
audio callback gate; it does not authorize removing the waiter or adding a
timeout. The unbounded spin remains a runtime/scheduling risk, but this A12
publication class has no unresolved generated writer and no mitigation-shaped
change is warranted.
