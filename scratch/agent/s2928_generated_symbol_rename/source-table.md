# Session 2928 generated-symbol source table

Scope: the next remaining placeholder after `0x80069AF0`, ending before the
next established symbol. No runtime instrumentation or behavior change was
performed.

| Address | Size | Generated body | Predecessor / successor | Companion or m2c name | Callers / lookups | Classification |
|---|---:|---|---|---|---|---|
| `0x8006B704` | `0x0C` | `sw $a1,0($a0)`; `addiu $a2,$fp,0x28`; `lw $a0,0x5C($fp)` | `getLevelTimeLimit` ends with `jr $ra` at `0x8006B6FC` and delay-slot `nop` at `0x8006B700`; `loadCraftShadowTextures` begins at `0x8006B710` with its stack prologue | No semantic companion/m2c name; companion map retains `fake_func_8006B704` | `rg` across checked-in sources, symbol maps, rename tables, and the generated snapshot finds no call or independent lookup; only declaration/definition/registration surfaces | `ambiguous-or-fake` |

## Evidence and decision

The generated snapshot at `scratch/agent/s390_verify/before_current_applied/funcs_16.c:12997`
contains three valid instructions but no prologue, branch, jump, or return in
the 12-byte record. The surrounding functions independently establish both
boundaries. The checked-in symbol map assigns the record `size = 0xC`, while
the generated header and source contain only its definition and registration,
not a caller. These are independent structural and reference-based checks,
but neither proves that an external or hand-written MIPS caller cannot enter
the fragment. Therefore H-Ambiguous is selected; no rename is authorized.

The prior global sweep table also recorded this address as ambiguous, but that
is historical context rather than the basis for this decision.
