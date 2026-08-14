# NEXT work unit (s1094)

HYPOTHESIS-ID: retail-loop-pc-delay-classification

Perform one bounded static audit of the retail ROM/generated instructions at
`0x8006D980..0x8006D9BC`. Classify every watched PC from s1092 as a branch,
delay slot, taken target, or ordinary sequential instruction, using the ROM
disassembly/symbol context and the generated function. No ROM run is planned.

Competing hypotheses and discriminator:

* H-zeroes-are-delay: every zero PC in the s1092 bracket is a delay slot, so
  the callback-semantic result fully explains the missing PCs.
* H-nondelay-missing: at least one zero PC is an ordinary or taken-target
  instruction, leaving a genuine retail control-flow boundary open.
* H-address-map-error: the static address mapping does not correspond to the
  watched generated function, so the classification cannot be transferred.

Discriminating measurement: one complete instruction table for the inclusive
bracket, with opcode/address/role and an independent ROM-vs-generated address
check. All-delay classification selects H-zeroes-are-delay; any verified
non-delay zero selects H-nondelay-missing; a failed address check selects
H-address-map-error.

Exact commands:

```sh
rg -n -C 8 "8006D980|8006D9(8[048]|9[048]|A[048]|B[048C])" \
  docs syms RecompiledFuncs tools
rg -n -C 6 "func_8006D9|8006D980|8006D9B4" RecompiledFuncs tools
```

Keep the oracle capacity increase; it is required by the established
discriminator.
