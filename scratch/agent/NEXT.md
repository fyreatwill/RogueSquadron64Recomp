# NEXT: audit backward non-self zero-offset MEM_H pointer transitions
HYPOTHESIS-ID: m3-idiom-class-audit

The s4674 self-referential-walk class and s4675 `MEM_W` transition class are
closed provisionally. Do not repeat either class.

Before any build, enumerate every backward loop containing a non-self
zero-offset `MEM_H(ctx->rN, 0X0)` transition in
`../N64Recomp/RecompiledFuncs/`, using a fresh scan rather than
`find_unguarded_walks.py`. Reconcile the count with the source positive
controls in `funcs_0.c` (`rs_malloc`, `buildHeapFreeList`, and
`coalesceFreeHeapBlocks`), then classify each site by bound/sentinel, pointer
writer, and legitimacy. If no complete class and positive control can be
named, write BLOCKED instead of adding instrumentation.

Competing hypotheses:

- H-safe: every site is a bounded table walk or sentinel-checked list walk
  with a legitimate pointer writer.
- H-gap: a site consumes an unbounded guest field or failed allocator without
  a guard; its writer and reachable noncanonical path can be named.
- H-scan-invalid: the fresh scan cannot reconcile its complete count with the
  existing positive controls.

Exact starting commands:

    rg -n 'MEM_H\(ctx->r[0-9]+, 0X0\)' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n 'goto L_|MEM_H\(ctx->r[0-9]+, 0X0\)|sltiu|sltu|beq|bne' ../N64Recomp/RecompiledFuncs/funcs_*.c

Expected discriminator: zero sites with a reachable noncanonical pointer
selects H-safe; one or more sites with a named writer that can publish an
out-of-range pointer selects H-gap; a census mismatch or missing positive
control selects H-scan-invalid.
