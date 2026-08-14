# NEXT work unit (s1097)

HYPOTHESIS-ID: retail-loop-submit-return-boundary

Perform one bounded static audit of `submitGfxFrame` (`0x8000C07C`) and its
immediate callers/return assumptions on the `runIdleFramesAndLoadSaveData`
loop path. Use the generated/companion sources available in the checkout and
the retail ROM if needed. Do not build the recomp or change runtime code.

Competing hypotheses:

* H-submit-returns: `submitGfxFrame` has a normal return path and the remaining
  boundary is outside this callee.
* H-submit-nonreturn: a call or return assumption in `submitGfxFrame` can
  explain why the callee fails to reach its post-loop cleanup.
* H-submit-mismatch: generated/companion evidence disagrees about the target's
  call or return contract, so the boundary cannot yet be classified.

Discriminator: enumerate every immediate return/transfer from the target and
the called function's generated/companion return contract. A reachable normal
return with matching evidence selects H-submit-returns; a reachable non-return
or explicit blocking transfer selects H-submit-nonreturn; disagreement selects
H-submit-mismatch and stops further runtime probing.

Exact commands:

```sh
rg -n "8000C07C|submitGfxFrame" RecompiledFuncs build tools docs
rg -n "8000C07C|submitGfxFrame" scratch docs
sed -n 'START,ENDp' <generated-or-companion-file>
```
