# s2605 — convertMat3x4ToN64Mtx jr-$t9 host return

## Discriminator result

Selected `H-BrokenJrT9Patch`.

| Evidence | Result |
|---|---|
| Generated tail before patch | `jr $t9` / s2190 `writer_parity` / `SD` / s2467 probe / `LOOKUP_FUNC(ctx->r25)` |
| `$t9` source | `addu $t9, $ra, $zero` at `convertMat3x4ToN64Mtx` entry |
| `$ra` at the aborting callsite | s2475 writes `ctx->r31 = 0x800155EC` before the direct call |
| `0x800155EC` | `lw $v0, 0x4($s3)` continuation after `jal 0x80018D80`, not a function |
| Fixup regex | missed because s2190 inserts `rs64_m5_writer_parity` before `SD` |
| After patch | host `return`; canary `tools/check_jr_t9_host_return.py` passes |
| AUTOPILOT 45s run | 0 `Failed to find function`, 0 `[CRASH]`; 640 @ 5.0s; title `1024 @ 0x00790400` @ 13.5s; hangar `512 @ 0x006AB400` @ 21.8s |

ORIGIN: looking up `0x800155EC` is a recompiler lowering defect. The legitimate
control flow is a host return to the `after_4` continuation.

Log: `scratch/agent/s2605_jrt9_host_return.log`.
