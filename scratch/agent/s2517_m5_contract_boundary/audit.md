# s2517 M5 independent contract-boundary audit

Date: 2026-08-26

The retail oracle ran for 70 seconds with whole-RDRAM, phase-gated task-data,
`data_ptr+0x100`, and image-range watches, plus the registered
`osSpTaskStartGo` task dump. It reached title (`1024 @ 0x00790400`) and
hangar (`512 @ 0x006AB400`). Whole-RDRAM recorded 359,402 writes; the task
watch recorded 6,178 hits; the task dump retained 1,227 phase-gated type-2
rows from 1,932 phase hits, with 705 non-type-2 rows, zero invalid pointers,
and zero overflow.

| span | writes |
|---|---:|
| `0x173C20:0x173E00` | 156,233 |
| `0x171DE0:0x171F70` | 145,489 |
| `0x178C80:0x179930` | 47,680 |

Title rows used `data_ptr=0x80171CE0` and `data_ptr+0x100=0x171DE0`;
hangar rows used `data_ptr=0x80171E70` and `data_ptr+0x100=0x171F70`.
Every retained type-2 row had `output_buff=0`, `output_buff_size=0`,
`yield_data_ptr=0`, and `yield_data_size=0`. Writer-PC tables were positive,
including `0x800908D4` for the task-data span and `0x800078EC` for the
existing image range, but no writer was shown to be an image payload or
output-consumer edge.

`H-proven-edge` was not selected. This new independent retail boundary
confirms the task/data relation and active writers, but does not name a
legitimate missing image output contract. Combined with s2516's same-build
port image execution and zero output/PCM result, it selects `H-no-edge` at the
current route scope; `H-route-only` remains possible elsewhere. No runtime
behavior, task field, output mapping, writeback, guard, or default changed.

ORIGIN: diagnostic-only. Existing oracle observation support was used; no
mitigation-shaped machinery or behavior was added.
