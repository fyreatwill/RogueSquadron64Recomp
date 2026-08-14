# NEXT work unit (s1115)

HYPOTHESIS-ID: retail-oracle-mode-state-route

Perform one bounded static audit of the retail writer PCs identified in s1114:
`0x80017CA0`, `0x80017CB0`, `0x80017CD0`, `0x80017CEC`, `0x8001BA80`,
`0x8001BA88`, `0x80019D9C`, and `0x80019F60`. Locate each instruction in the
generated function files and the independently mapped retail ROM, then compare
the surrounding control flow and companion symbols. Use bounded searches such
as:

```sh
rg -n -i '80017ca0|80017cb0|80017cd0|80017cec|8001ba80|8001ba88|80019d9c|80019f60' RecompiledFuncs tools syms docs
rg -n '8011A864|80128E90|80128E94|8011A8A0' RecompiledFuncs tools syms docs
```

Classify every writer as boot initialization, per-frame scheduler state, or
phase-transition state. Do not edit code or run another oracle capture unless
the source audit cannot locate a writer.

Competing hypotheses:

- H-mode-init — selector/pending writes are boot/config initialization and do
  not drive the missing phase.
- H-mode-loop — they are repeatedly refreshed scheduler state and the port's
  lifecycle is the likely boundary.
- H-mode-transition — at least one writer is dominated by the 512/1024 mode
  selection predicate and is the phase-transition producer.

Discriminator: the writer's surrounding branch/caller and ROM match. A boot-
only store selects H-mode-init; a recurring unconditional or frame-gated store
selects H-mode-loop; a writer dominated by the 512/1024 mode-selection
predicate selects H-mode-transition.
