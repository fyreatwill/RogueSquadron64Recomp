# NEXT work unit — M3 A12 0x8014974C spin-flag publication census

HYPOTHESIS-ID: m3-a12-8014974c-publication

## Single work unit

M5 target-phase qualification remains blocked: do not repeat the `s2618`
or eleven-Start routes. A8 key-on divisor/descriptor is closed (s3220:
sole cmd-list divisor store `0x80090768` in `musyxRenderVoiceSamples`,
value `0xC0`; four `break 6` sites unreachable). Next eligible unit is
the A12 idiom-class audit of every generated store of the unbounded
spin flag at `0x8014974C`.

Competing hypotheses:

- `H-NamedFlagWriter`: every store of `0x8014974C` is in a named
  MusyX/synth path with a finite range (including a legitimate zero).
- `H-InvalidFlagProducer`: at least one generated store writes a
  non-terminal or overlapping value the unbounded spin is papering over.
- `H-NoLiveFlagWriter`: the generated tree has no remaining store into
  that word beyond already-named sites; the spin stays safety-only.

Discriminator: a complete grep census of every `lui 0x8015` / `-0x68B4`
(and `0x974C` / literal `0x8014974C`) store and load, companion names,
and caller fan-in. Classify each writer as in-range, out-of-range at
source scope, or unresolved. No port run. No timeout or force-clear
without a named legitimate writer.

Exact start: grep `RecompiledFuncs/funcs_*.c` for `MEM_W(-0X68B4`,
`sw …, -0x68B4`, `0x974C`, and `0x8014974C`; recover the storing
functions; census every store and the `waitForMusyXAudioTaskDone` /
`shutdownAudioEngine` loads.
