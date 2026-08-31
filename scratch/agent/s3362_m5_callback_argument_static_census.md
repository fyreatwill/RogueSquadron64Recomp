# Session 3362 — callback argument source census

## Work unit

Bounded static census of every generated reference to `0x800919D4` and
`0x800919EC`, including the argument setup immediately before the indirect
call. No build or behavior change was needed.

## Result

The current generated tree contains exactly one code site for each address,
both in `initN64RspMixer` (`funcs_24.c`). There are no generated direct calls
to either address and no second inline `jalr` site. At `0x800919D4`, the
function loads the callback target from global `0x801099D4` (the slot written
earlier in the same function at `0x80091900` with literal `0x80007910`). The
following instructions set `$a0` to literal `0x8009123C`, set `$v1` to
`0xFFFF`, and execute `jalr $v0` at `0x800919EC`.

This classifies the observed `0x800919EC -> 0x80007910, a0=0x8009123C` row as
a concrete guest caller with a literal argument. It refutes an earlier shared
register/state argument explanation and finds no unresolved generated caller
or host-side argument rewrite. The result is single-source static evidence;
the existing independent retail execution capture is the separate evidence
that this chain executes on hardware. No behavior change was made.

Commands:

```sh
rg -n -C 8 '800919D4|800919EC' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n '0x80091900|80091900' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
