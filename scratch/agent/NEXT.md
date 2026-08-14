# NEXT work unit (s1096)

HYPOTHESIS-ID: retail-loop-pc-delay-classification

Perform one bounded static audit of the taken branch at `0x8006D9B4`. Inspect
the generated function and raw ROM words through the branch target, then
enumerate the target's immediate control-flow successors and any reads or
writes relevant to the loop's failure to return to `0x8006D9BC`. Do not build
the recomp or change runtime code.

Competing hypotheses:

* H-target-loop: the branch target is a valid loop-back path whose successors
  explain the retail execution observed by s1095.
* H-target-exit: the branch target exits the loop/callee, explaining the
  missing fall-through without a loop-back.
* H-static-mismatch: generated output and raw ROM disagree at the branch or
  target, so the runtime interpretation needs a corrected address mapping.

Discriminator: the generated instruction words and independently mapped ROM
words must agree; classify the branch target and its first successors as
loop-back, exit, or another explicit transfer. Agreement plus a loop-back or
exit target selects the corresponding hypothesis. Any disagreement selects
H-static-mismatch and requires stopping before further runtime probing.

Exact commands:

```sh
rg -n "8006D9(80|84|88|8C|90|94|98|9C|A0|A4|A8|AC|B0|B4|B8|BC)" \
  RecompiledFuncs build tools docs
rg -n "func_8006D9|8006D9" RecompiledFuncs tools/oracle docs
sed -n 'START,ENDp' RecompiledFuncs/funcs_*.c
```

Use bounded windows around the grep hits, and record the raw ROM words with
the established `ROM = VRAM - 0x80000000 + 0xC00` mapping. No mitigation is
authorized by this work unit.
