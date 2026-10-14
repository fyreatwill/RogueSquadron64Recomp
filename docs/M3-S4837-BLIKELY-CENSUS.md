# M3 branch-likely census (s4837)

## Scope and discriminator

This is a static census of the current generated files at
`../N64Recomp/RecompiledFuncs/funcs_*.c`; no regeneration or runtime
instrument was added. The class under test is MIPS branch-likely control flow,
where the delay slot executes only when the branch is taken. For each site the
structural discriminator was:

1. the generated condition is an `if` around the delay-slot body;
2. the taken arm reaches the decoded target label;
3. the untaken arm jumps over the delay-slot body; and
4. the delay-slot body is present again at the fall-through copy.

The qualified title/hangar route (VI 1024, VI 512, SP completions, and PCM
activity) is the route positive control. It proves the generated runtime is
executing the covered game path, but this static census does not claim that
each of the 893 sites is reached by that route.

## Complete census

| Opcode | Sites | Structural matches |
|---|---:|---:|
| `bc1fl` | 197 | 197 |
| `bc1tl` | 597 | 597 |
| `bgezl` | 36 | 36 |
| `bgtzl` | 10 | 10 |
| `blezl` | 13 | 13 |
| `bltzl` | 40 | 40 |
| `beqzl`, `bnezl` | 0 | 0 |
| **Total** | **893** | **893** |

The sites span 44 generated files and 286 generated functions. Per-file counts
(files with no sites are omitted):

| File | Sites | File | Sites |
|---|---:|---|---:|
| `funcs_3.c` | 6 | `funcs_4.c` | 20 |
| `funcs_5.c` | 4 | `funcs_6.c` | 4 |
| `funcs_7.c` | 2 | `funcs_8.c` | 20 |
| `funcs_9.c` | 19 | `funcs_10.c` | 37 |
| `funcs_11.c` | 13 | `funcs_12.c` | 15 |
| `funcs_13.c` | 29 | `funcs_14.c` | 10 |
| `funcs_15.c` | 16 | `funcs_16.c` | 49 |
| `funcs_17.c` | 5 | `funcs_18.c` | 11 |
| `funcs_19.c` | 23 | `funcs_20.c` | 1 |
| `funcs_21.c` | 12 | `funcs_22.c` | 7 |
| `funcs_23.c` | 6 | `funcs_24.c` | 3 |
| `funcs_26.c` | 9 | `funcs_27.c` | 29 |
| `funcs_28.c` | 40 | `funcs_29.c` | 30 |
| `funcs_30.c` | 28 | `funcs_31.c` | 57 |
| `funcs_32.c` | 54 | `funcs_33.c` | 48 |
| `funcs_34.c` | 15 | `funcs_35.c` | 10 |
| `funcs_36.c` | 8 | `funcs_37.c` | 30 |
| `funcs_38.c` | 24 | `funcs_39.c` | 52 |
| `funcs_40.c` | 12 | `funcs_41.c` | 64 |
| `funcs_42.c` | 38 | `funcs_43.c` | 28 |
| `funcs_46.c` | 1 | `funcs_47.c` | 1 |
| `funcs_48.c` | 1 | `funcs_49.c` | 2 |

## Exceptions and classification

The first-line shape check reported 24 apparent exceptions. They are all
existing diagnostics inserted between the branch comment and the generated
`if`, not missing delay-slot control flow:

- 23 sites assign `g_rs64_last_guest_pc` for the existing guest-PC breadcrumb.
  The assignment is outside the conditional, does not alter the branch
  predicate, and the delay-slot body remains conditional and duplicated.
- One site, `funcs_33.c:23883` (`0x800C2B84`, `runMenuModelViewerScreen`),
  calls the existing `rs64_s3288_viewer_fade` observer before the `if`. It only
  receives the already computed predicate and register values; the generated
  `addiu` delay slot remains conditional, with the target and fall-through
  copies intact.

A full structural pass that recognized these intervening diagnostics matched
all 893/893 sites. No branch-likely site was found that executes its delay slot
on the untaken path, omits it on the taken path, or loses the taken target.

## Result

This census selects `H-blikely-valid` for the generated control-flow
translation. It rules out a broad generated branch-likely translation defect as
the explanation for the current crash/rendering frontier. It does not prove
that every site is reachable on the qualified route; no per-site runtime join
was attempted, so `H-blikely-route-gap` remains relevant only to reachability,
not to translation correctness. No runtime fix or guard is warranted.

The counts can be reproduced with:

```sh
rg -i -c '^[[:space:]]*// 0x[0-9A-Fa-f]+: (beqzl|bnezl|bc1[tf]l|bltzl|bgezl|blezl|bgtzl)' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c
```
