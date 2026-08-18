# NEXT work unit (s1895)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** Next census: leftover `func_800F2D38`
at `0x800F2D38` (size `0x3C`, `syms/rogue_squadron.syms.toml:1990`).
Preliminary peek: the generated body immediately after
`initAnimSubstructFromParams` in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_41.c`
is already `RECOMP_FUNC void applyToObjectSubstructByFlag` (address
arithmetic checks out: `0x800F2C6C + 0xCC = 0x800F2D38`). Repeat the
s1887/s1893/s1894/s1895 procedure exactly:
1. `grep`/`awk` RECOMP_FUNC adjacency pairing in `funcs_41.c` to confirm
   `applyToObjectSubstructByFlag` truly follows `initAnimSubstructFromParams`
   (not a stray substring match).
2. Check `funcs.h` declares it in the right order.
3. Check `recomp_overlays.inl` — offset must be
   `initAnimSubstructFromParams`'s offset (`0x0004DB3C`) `+ 0xCC = 0x0004DC08`,
   and `rom_size` must be `0x0000003C` (matching TOML `size = 0x3C`).
4. `grep -rln 'func_800F2D38\b'` across generated RecompiledFuncs tree —
   must be zero hits (non-collision).
5. If all four agree, rename the TOML entry only — no build/regen needed
   (this class of change is metadata-only sync; the generated tree already
   has the correct name from N64Recomp's own matching, independent of this
   repo's TOML).

**Before starting**, check whether `vi1024-reachability-regression` has
been unblocked: run `python3 scratch/agent/thermal_probe.py` and read
`isLowPowerModeEnabled`. If it now reads `False` (a human toggled Low Power
Mode off in System Settings > Battery since s1892/s1895), STOP the sweep
and instead re-run the unmodified `s790_postsec2_reachability.sh` once,
with `vm_sampler.py` and `thermal_probe.py` running the same way s1892 did,
and compare directly against s1892's result (`640 origin=0x00696100` stall
@ 7.2s, then `fillSampleStreamRange`/`musyxRenderVoiceSamples` SIGBUS
@ ~27s). A VI-1024 reach or a different crash signature/timing selects
H3a-lowpower; an identical stall with Low Power Mode confirmed off refutes
it — one clean A/B closes it either way, no third run needed. If it still
reads `True`, stay on the sweep — do not repeat a same-recipe reachability
soak with no new measurement axis (iron rule 8). As of s1895 it still reads
`True` (unchanged since s1892).

Also check the sweep's 15-title REVISIT gate: `grep -n '^## Session '
PORTING-STATE.md | tail -15`. If all 15 titles belong to the sweep
(contain "synchronized" or "confirmed ... symbol"), this iteration is a
REVISIT instead of another census — spend it re-attempting the external
retail-entry boundary or M4 accumulator-origin threads with a genuinely
new angle. As of s1895 this gate does NOT fire (s1888-s1892 in the window
are the reachability investigation, not sweep entries) — but s1888 is about
to age out of the tail-15 window in the next iteration or two, so check
again next iteration.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed, no candidate
  found beyond `rs64_is_hangar_vi()`, already refuted.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed, refuted.
- A same-recipe `s790_postsec2_reachability.sh` run with no new measurement
  axis while Low Power Mode is still ON and unchanged since s1892 — that's
  now 10 confirmations of the 7.2-7.4s stall; an 11th adds nothing.
- Ask (b) from s1891 (disposable clone + `git submodule update` bisect at
  `ef7a0fb9`) is still open and still legitimately human-only per CLAUDE.md's
  hard rule — do not attempt a workaround.
