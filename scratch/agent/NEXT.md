# NEXT work unit (s2452) — audit the generated caller of the retail second-range path

HYPOTHESIS-ID: m5-port-second-range-caller-lowering

## Work unit

Perform a bounded static audit of the generated function containing the
retail-grounded second-range semantic caller boundary `0x8002BEEC` and its
call/continuation around the observed `rs_memset` path. Enumerate the complete
callsite lowering, especially whether the translated caller reaches the
`rs_memset` entry directly, through a generated continuation, or through a
different helper. Do not change runtime or generated output.

## Competing hypotheses and discriminator

- H-DirectCallerPresent: the translated caller contains the expected direct
  `jal 0x800078E0` and its continuation preserves the same store/data path.
- H-CallerLoweringDiverges: the translated caller has a structural lowering
  difference at the call or continuation that can account for the missing
  second-range consumer.
- H-DifferentGeneratedBoundary: `0x8002BEEC` is not represented by the
  generated function/path that performs the observed second-range stores.

The discriminator is a complete caller-boundary table: direct target,
preceding argument setup, continuation label, and all stores/data accesses in
the caller block. A matching direct call and continuation selects
H-DirectCallerPresent; a structural call/continuation difference selects
H-CallerLoweringDiverges; absence of the expected generated boundary selects
H-DifferentGeneratedBoundary. An incomplete function body is
non-discriminating and must not be promoted.

## Exact commands

`rg -n -C 8 "8002BEEC|800078E0|800078EC" ../N64Recomp/RecompiledFuncs/funcs_*.c`

`rg -n -C 3 "8002BEEC|800078E0|800078EC|after_[0-9]+" ../N64Recomp/RecompiledFuncs/funcs_*.c`

`nm -n ../rogue_squadron64/build/roguesquadron.elf | awk '$1 >= "8002be00" && $1 <= "8002c000"'`
