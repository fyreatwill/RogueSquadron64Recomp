# NEXT work unit (enumerate the reachable VI state writers)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s806 batched trace selected the reachable state gate: direct callers
repeatedly publish width-640 rows while the selector publisher is silent. The
next single unit is a bounded source audit of every writer and predicate for
the pending masks (`0x80128E90/0x80128E94`) and selector/config bytes
(`0x8011A862/0x8011A865–868` and init stack/config fields). Do not build or
run unless the audit identifies one concrete writer whose reachability cannot
be classified statically; if so, rewrite NEXT before that later experiment.

## Competing hypotheses

- H-state-writer: a reachable game function writes the 640-only pending or
  selector/config state. Prediction: the audit finds a concrete store and its
  caller path reaches one of the s806 direct publishers.
- H-missing-state-dispatch: the 1024-producing state writer exists but its
  overlay/function dispatch is absent. Prediction: the audit finds a 1024
  capable writer whose call or overlay route is not reachable in the port.
- H-recipe-state: the port's 640 values are legitimate for this driven recipe,
  and no missing writer is implied. Prediction: all reachable stores are
  initialization or 640-path logic, with no concrete 1024 producer.

## Discriminating measurement

The audit's complete writer inventory is the discriminator: a reachable store
that selects or publishes the 640 state advances H-state-writer; a concrete
1024-capable store with an absent route advances H-missing-state-dispatch; an
exhaustive inventory with only initialization/640-path stores advances
H-recipe-state. Record every store, address, function, and reachability proof;
do not infer from a single grep hit.

## Exact commands

```sh
rg -n -C 4 '0x80128E90|0x80128E94|0x8011A862|0x8011A865|0x8011A866|0x8011A867|0x8011A868|-0x716C|-0x7170|-0x579B|-0x579C|-0x579E' ../N64Recomp/RecompiledFuncs ../N64Recomp/fixup_game_funcs.py
rg -n -C 3 '80128D50|80128C90|width.*1024|width.*640|osViSetMode_recomp' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 3 'pending.*Vi|Vi.*pending|selector|mode table|set.*ViMode' src ../N64Recomp/RecompiledFuncs
```

Use the generated source as the implementation witness and update the audit
with a complete classified list. If a future run is needed, retain the s806
oracle positive controls, `[vi-gate]` direct-call controls, and silent selector
control; phase-gate on VI 640 and do not compare stopwatch windows.
