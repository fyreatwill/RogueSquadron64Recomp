# NEXT work unit (resume after s1218 checkpoint)

HYPOTHESIS-ID: retail-entry-capability

RESUME instruction — no experiment ran in s1218 (checkpoint-recovery only,
see PORTING-STATE.md Session 1218). The plan below is unchanged from s1217.

What already exists and is validated (do not re-validate):
- The project's DEBUGGER=1 Mupen64Plus core + console frontend expose a
  working `pause`/`write`/`mem`/`run` path (Homebrew's core has `--debug`
  disabled and cannot be used for this).
- `tools/oracle/rs64_oracle.c` has `--debug-write VADDR:VALUE`, which performs
  one 32-bit write on the first VI callback whose width is 320. It was smoke
  tested with a harmless word at `0x80007FFC` (`0xDEADBEEF`), read back
  correctly before and after resume, with whole-RDRAM/PIF/VI controls passing
  in both arms. See PORTING-STATE.md s1217.

Work unit: select ONE justified, state-changing RAM or CPU-register target at
the 320 boundary and smoke-test it with `--debug-write` (or a comparable
debugger write) instead of the harmless control word. "Justified" means
sourced from retail symbols or oracle state observations already in the
ledger/docs (`docs/F5-UCODE-REFERENCE.md`, VI descriptor boundary notes in
CURRENT-TRUTH.md) — not a guess. Write down the exact address, its symbol,
and why it is expected to matter BEFORE running anything.

Competing hypotheses and discriminator:
- H1: the justified target changes the retail state path and reaches a later
  VI width/origin phase (not width 320 / origin `0x006dd280`).
- H2: the target is not state-changing, or the run remains at width
  320/origin `0x006dd280`.
- H3: the target write disrupts the whole-RDRAM, PIF, or VI positive
  controls, making the result unevaluable.

Discriminator: a later VI width/origin ONLY in the target arm selects H1;
width 320 in both arms selects H2; a failed whole-RDRAM/PIF/VI control in the
target arm selects H3.

Required in the same run: paired undriven/control arm vs. the target-write
arm, both logging whole-RDRAM callback counts, PIF trace, and VI width/origin
records. Do not arm M4 target watches unless a later VI width/origin phase is
actually reached first.

Exact command shape (fill in the real target before running):
```
tools/oracle/build/rs64_oracle --debug --rom <ROM> --savestate ... \
  --debug-write 0xVADDR:0xVALUE --whole-rdram-watch --pif-trace --vi-trace
```
(control arm: identical command minus `--debug-write`, run concurrently per
iron rule 13).
