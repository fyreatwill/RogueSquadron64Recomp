# NEXT work unit (s1105)

HYPOTHESIS-ID: submit-producer-boundary

Perform one bounded runtime-free audit of non-generated and companion ownership
for SP bytes `0x8011A89F/0x8011A8A0` and the DP handler byte/object at
`0x8011A408`. Do not change queue behavior or build.

Competing hypotheses:

* H-external-writer: companion, host, or patch code supplies the missing
  nonzero producer gate and identifies the lifecycle boundary.
* H-gate-stale: the generated clear/reset is the only writer, leaving the
  producer send suppressed while the consumer blocks.
* H-gate-alias: the SP bytes or `0x8011A408` are fields reached through an
  object/index boundary, so fixed-address ownership is misleading.

Discriminator: enumerate every companion/host/patch read and write and map it
to the exact generated boundary. A nonzero external writer selects
H-external-writer; only generated clears with no nonzero writer selects
H-gate-stale; object/index-mediated access selects H-gate-alias. A null result
is valid only if the same audit visibly fires a positive-control symbol/path.

Exact commands:

```sh
rg -n -C 6 "8011A89F|8011A8A0|8011A408|A89F|A8A0|5BF8" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64 src lib patches docs
rg -n -C 5 "8011A89F|8011A8A0|8011A408|A89F|A8A0|5BF8" /Users/williambuckley/Documents/Tools/rogue_squadron64 src lib patches docs
git diff --check
```
