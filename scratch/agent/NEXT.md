# NEXT work unit (s1098)

HYPOTHESIS-ID: submit-blocking-queue-contract

Perform one bounded static audit of the two blocking queue waits inside
`submitGfxFrame` (`0x8000C0B4`, `0x8000C2B8`). Identify each queue, its producer
and consumer paths, and whether the companion/generated sources establish a
legitimate message path on the idle-loop call. Use static generated/companion
evidence only; do not build, run, or change runtime code.

Competing hypotheses:

* H-queue-legitimate: both waits have identified producers and consumers that
  can satisfy them on the idle-loop path.
* H-queue-unmatched: at least one wait has no statically reachable producer or
  has a producer/consumer contract incompatible with this call.
* H-queue-mismatch: generated and companion queue identities or blocking modes
  disagree, so the wait boundary cannot yet be classified.

Discriminator: produce a two-row queue table containing physical queue address,
block mode, message producer, message consumer, and idle-loop reachability. Two
matched producer/consumer rows select H-queue-legitimate; any unmatched or
incompatible row selects H-queue-unmatched; source disagreement selects
H-queue-mismatch and stops runtime probing.

Exact commands:

```sh
rg -n "8000C0B4|8000C2B8|osRecvMesg|submitGfxFrame" ../N64Recomp/RecompiledFuncs ../rogue_squadron64
rg -n "8011A7E8|8012A7E8|800331D0|submitGfxFrame" ../N64Recomp/RecompiledFuncs ../rogue_squadron64
sed -n 'START,ENDp' <generated-or-companion-file>
```
