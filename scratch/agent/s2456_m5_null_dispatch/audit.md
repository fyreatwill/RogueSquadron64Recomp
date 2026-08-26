# s2456 pre-phase null-dispatch audit

## Static call/symbol table

| Layer | Site or expansion | Target form | Result |
|---|---|---|---|
| Runtime API | `lib/N64ModernRuntime/librecomp/src/overlays.cpp:545` | `get_function(int32_t addr)` | The only checked-in runtime resolver; missing entries assert and exit unless the existing opt-in stub is enabled. |
| Thread entry | `lib/N64ModernRuntime/librecomp/src/recomp.cpp:477` | `get_function(addr)` | Resolves a thread start address; not inside `convertMat3x4ToN64Mtx`. |
| Generated indirect calls | `LOOKUP_FUNC(val)` in `lib/N64ModernRuntime/N64Recomp/include/recomp.h:450` | `get_function((int32_t)(val))` | External generated tree has 28,385 expansions: 28,183 literal, 113 register, and 89 zero-valued expressions. |
| Generator | `lib/N64ModernRuntime/N64Recomp/src/cgenerator.cpp:408-414` | literal or register `LOOKUP_FUNC` | No alternate resolver or zero-target special case is emitted. |
| Generated target function | external `RecompiledFuncs/funcs_4.c:33477` | `convertMat3x4ToN64Mtx` | No `LOOKUP_FUNC` expansion. It directly calls `packMtxRowFloatToFixed` at `0x80018DB8`, `0x80018DC8`, and `0x80018DD8`. |
| Reported port PC | external `RecompiledFuncs/funcs_0.c:4898-4903` | `0x80001F88` | Only the `nop` in the epilogue after `jr $ra` of `buildHeapFreeList` (`0x80001F8C`); no lookup site. |

The 89 non-literal/non-register expansions are all `LOOKUP_FUNC(0)`; none is
at `0x80001F88` or in `convertMat3x4ToN64Mtx`. The external generated tree is
not part of this checkout, but was available at the documented sibling path
and was included in the census above.

## Symbol ranges

The checked-in symbol map identifies `convertMat3x4ToN64Mtx` as
`0x80018D80..0x80018E60` and `rs_memset` as `0x800078E0..0x80007908`.
The companion decomp symbol file identifies `buildHeapFreeList` at
`0x80001F8C`; it has no symbol at `0x80001F88` because that address is the
return delay slot.

## Independent retail result

Command: the prescribed 60-second Rice run with whole-RDRAM watch,
`--watch-pc 0x80001F88`, explicit `0x6AB400:512` phase logging, and repeated
Start presses. The log is `scratch/agent/s2456_oracle.log`.

- Positive controls passed: `[gpr-ctl]` fired; whole-RDRAM watch produced
  10,000 callbacks and was removed while the target watch stayed armed.
- Retail ran 3,557 VI in 59.3 emulated seconds and reached the end of the
  driven schedule.
- `0x80001F88` had 0 execution hits; `execution watch hits: 0`.
- The explicit hangar phase join had 0 rows, so no hangar-specific claim is
  made from this run.

## Classification

This is a non-result for the original three hypotheses, not a selection:
the port crash's reported last PC is not a generated/runtime lookup callsite,
and retail did not execute that PC on the driven route. The evidence instead
opens a new boundary hypothesis: the first `get_function(0)` must be captured
at the resolver with its native caller and the immediately preceding guest-PC
state; the current `g_rs64_last_guest_pc` breadcrumb is insufficient to
attribute it to `convertMat3x4ToN64Mtx`.
