# M3 Session 3790 — audited the complete `rs_zcfree` incoming `$a0` idiom

## Scope and naming

The worklist address `0x80005268` is the `jal rs_free` instruction inside
function entry `0x8000525C` (`rs_zcfree`). The wrapper first skips on a null
incoming `$a0`, then forwards that unchanged register to `rs_free`.

## Complete generated callsite census

| Site | Operation | `$a0` setup | Classification |
|---|---|---|---|
| `funcs_7.c:18467`, `zcfree` entry `0x80029CF4` | `jal 0x8000525C` at `0x80029CFC` | delay slot `addu $a0,$a1,$zero` | sole direct caller; zlib callback payload |
| `funcs_1.c:6197`, `rs_zcfree` entry `0x8000525C` | `jal 0x80001C98` at `0x80005268` | incoming `$a0`, after `beq $a0,$zero` | sole wrapper-to-`rs_free` edge |

The generated tree contains no other `jal 0x8000525C`, no other
`rs_zcfree(rdram, ctx)` call, and no alternate incoming setup at the wrapper
edge. The apparent `0x80005268` callsite therefore cannot receive the
manifest fields, DMA-slot payloads, or service-worker words audited by the
preceding `rs_free` classes.

## Callback and lifetime provenance

`inflateInit2_` initializes the zlib stream's allocator callbacks. At
`0x80026CE4` it installs `rs_zcalloc` at stream offset `0x20`; at
`0x80026D00` it installs `rs_zcfree` at offset `0x24`; and at `0x80026D04`
through `0x80026D14` it invokes the allocator with the stream opaque value at
offset `0x28`. The zlib `zcfree` adapter at `0x80029CFC` receives the object to
release as its `$a1` callback argument and copies it to `$a0`.

The paired `rs_zcalloc` implementation at `0x8000527C` computes `nmemb * size`
and calls `rs_malloc` at `0x80005298`, with a fallback `rs_malloc` call at
`0x800052AC`. Its result becomes the zlib allocation returned to the caller.
The corresponding zlib free callback is therefore the expected lifetime
consumer for allocations created through this callback pair. The generated
source provides no writer that substitutes a non-allocation value before the
`rs_zcfree` edge.

These are two independent static lines of evidence: (1) exhaustive target and
caller enumeration across all generated files, and (2) the zlib callback-field
setup plus the paired allocator implementation. Neither proves the runtime
allocator's internal freelist state or whether a corrupt caller outside this
generated tree can enter the callback.

## Hypothesis result

- **H1 selected at static source scope:** every reachable generated call uses
  the zlib callback contract, with `$a0` supplied from the callback's object
  argument and backed by the paired allocator path.
- **H2 not selected:** no concrete invalid writer or alternate `$a0` idiom was
  found, so no guard is justified.
- **H3 refuted at static scope:** this is not an unresolved register/ABI
  interpretation; the delay-slot forwarding and callback field layout are
  explicit in the generated MIPS translation.

No runtime mitigation was added. Runtime allocator legitimacy remains an
open qualification boundary, not evidence for a guard.

