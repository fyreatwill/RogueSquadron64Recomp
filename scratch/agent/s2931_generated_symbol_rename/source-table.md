# Session 2931 generated-symbol source table

Scope: the next unresolved placeholder after `0x8007A86C`, through the next
established symbol boundary. This is a static reconciliation; no runtime
instrumentation, generated-code edit, or behavior change was performed.

| Address | Size | Generated body | Predecessor / successor | Companion or m2c name | Generated callers / lookups | Classification |
|---|---:|---|---|---|---|---|
| `0x8007C298` | `0x08` | `sll $a1,$a2,1`; `addu $a1,$a1,$a0`; no prologue, branch, jump, or return | `loadShieldPalette` ends at `0x8007C294` (the `jr $ra` delay slot); `initNpcTexturedEffectFromTemplate` begins at `0x8007C2A0` with `addiu $sp,$sp,-0x38` | Companion map has only `fake_func_8007C298`; no semantic companion or m2c definition | Repository search across checked-in symbol maps, generated sources, tools, and companion project finds only declaration, definition, and overlay registration; no call or independent lookup | `ambiguous-or-fake` |

## Decision

The exact eight-byte record is valid executable-looking arithmetic between two
independently complete function boundaries, but it has no callable prologue or
return and the companion project supplies no semantic name. The generated
snapshot and companion/source search provide no caller or independent lookup
beyond the generated definition and overlay registration. Those facts do not
mechanically prove that a valid two-instruction fragment cannot be entered as
a callable or branch target, so the bounded discriminator selects
H-Ambiguous. The placeholder remains unchanged.
