# M3 s4816 — COP1 control-register (ctc1/cfc1 $31) idiom census

Tool: `tools/census_ctc1.py <rom>` (opcode 0x11, sub 6 = ctc1, sub 2 = cfc1, rd=31).

## Concern
Runtime lowering (`lib/N64ModernRuntime/N64Recomp/include/recomp.h` `set_cop1_cs`/`get_cop1_cs`) keeps ONLY rounding-mode bits [1:0] (via per-host-thread `fesetround`). `get_cop1_cs` returns 0..3 and never any flag (bits 2-6), enable, FS or cond (bit 23) bits. Any game code that does `cfc1; andi 0x78/0x7C/0x800000` after an FP op therefore always sees "no exception".

## Result
ROM scan: 6 ctc1 with resolved constant, all `1` (round-to-zero); 5 unresolved (all adjacent to a cfc1 save/restore, i.e. restoring the saved value); 12 cfc1 sites. Generated code contains `get_cop1_cs`/`set_cop1_cs` in exactly ONE function: `guPerspective` (N64Recomp/RecompiledFuncs/funcs_8.c:1770-1861, 0x8002EAE0-0x8002EB5C), the libultra `perspNorm` double->u16 conversion: save FCSR, set RZ, `cvt.w.d`, test `andi 0x78` (V/Z/O/E flags); if set, take the unsigned fixup (subtract 2^31, re-convert, OR 0x80000000) or -1.
The other 9 ROM hits have no generated counterpart (data / non-recompiled regions).

Port behaviour: flags always 0 -> the fixup branch is never taken; result is `(int32_t)lrint(d)`. Differs from MIPS only when the double is >= 2^31 or NaN. In guPerspective the input is `1/(near+far)`-scaled and guarded by `c.le.d` (near+far <= 2 -> 65535), so it lies in (0, 65536]; inf (division by zero) gives lrint=LONG_MAX -> low 32 bits -1 -> same 0xFFFF as MIPS. Rounding mode is set and restored within the function with no yield in between, so the per-thread fesetround is not observable by other game threads.

## Verdict
Class closed: no reachable divergence from dropped FCSR flags. No guard added (nothing to guard). Caveats: static, single-source (no runtime counter); the inf/NaN lrint behaviour on arm64 was reasoned from s4814's lrint finding, not re-measured; the 9 non-recompiled cfc1 sites were not examined.
