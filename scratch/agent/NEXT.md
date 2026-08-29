# NEXT work unit — bounded generated-symbol sweep for the live-tail candidate

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

M5 target-phase qualification is blocked pending a human-selected route or
new retail-grounded boundary. Do not repeat the two tested routes unchanged.
Use this unit to audit unresolved live-tail `func_80092F10` before any rename;
do not launch the game.

Competing hypotheses and the discriminating measurement:

- `H-RealFunction`: companion source/m2c, callers, and registration boundaries
  identify a defensible semantic name.
- `H-DataOrGap`: the body is a data-gap/fake fragment or lacks callable
  registration evidence, so renaming is unsafe.
- `H-Unresolved`: it is callable but available evidence cannot distinguish its
  role from neighboring live-tail fragments.

The discriminator is one joined table containing the candidate's generated
body/range, every caller and call target, companion source/m2c matches, and
symbol/registration boundaries. A complete semantic match selects
`H-RealFunction` and permits one bounded regeneration-safe rename; data-gap or
fake-fragment evidence selects `H-DataOrGap` and forbids a rename; otherwise
select `H-Unresolved` and record the missing proof.

Exact commands:

```sh
rg -n 'func_80092F10|80092F10' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  syms tools docs --glob '!*.log' --glob '!PORTING-STATE.md'
sed -n '1,220p' scratch/agent/s3210_generated_symbol_rename.md
rg -n 'func_80092F10|80092F10' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/src \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/mips_to_c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob '*.c' --glob '*.h' --glob '*.txt'
```

Expected outcome: one complete candidate table selecting a defensible rename,
data-gap exclusion, or exact unresolved proof gap. If `H-RealFunction` is
selected, apply the existing bounded rename tool and syntax-check changed
generated files; otherwise land only the evidence report. After a route
selection, return to the existing contract-pair command from the M5 plan.
