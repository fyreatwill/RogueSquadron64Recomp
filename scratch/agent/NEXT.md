# NEXT work unit (s1893)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** Next census: leftover `func_800F2B88`
at `0x800F2B88` (size `0xE4`, `syms/rogue_squadron.syms.toml:1988`).
Preliminary peek: the generated body immediately after
`computeAnchorRelativePositionByDistanceRatio` in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_41.c`
is already `RECOMP_FUNC void initObjectAnimSubstruct` (address arithmetic
checks out: `0x800F2AC4 + 0xC4 = 0x800F2B88`). Repeat the s1887/s1893
procedure exactly:
1. `awk` RECOMP_FUNC adjacency pairing in `funcs_41.c` to confirm
   `initObjectAnimSubstruct` truly follows
   `computeAnchorRelativePositionByDistanceRatio` (not a stray substring
   match).
2. Check `funcs.h` declares it in the right order.
3. Check `recomp_overlays.inl` — offset must be
   `computeAnchorRelativePositionByDistanceRatio`'s offset (`0x0004D994`)
   `+ 0xC4 = 0x0004DA58`, and `rom_size` must be `0x000000E4` (matching TOML
   `size = 0xE4`).
4. `grep -rn 'func_800F2B88\b'` across generated `*.c`/`*.h`/`*.inl` — must
   be zero hits (non-collision).
5. If all four agree, rename the TOML entry only — no build/regen needed
   (this class of change is metadata-only sync; the generated tree already
   has the correct name from N64Recomp's own matching, independent of this
   repo's TOML).

**Before starting**, check whether `vi1024-reachability-regression` has
been unblocked: run `python3 scratch/agent/thermal_probe.py` and read
`isLowPowerModeEnabled`. If it now reads `False` (a human toggled Low Power
Mode off in System Settings > Battery since s1892/s1893), STOP the sweep
and instead re-run the unmodified `s790_postsec2_reachability.sh` once,
with `vm_sampler.py` and `thermal_probe.py` running the same way s1892 did,
and compare directly against s1892's result (`640 origin=0x00696100` stall
@ 7.2s, then `fillSampleStreamRange`/`musyxRenderVoiceSamples` SIGBUS
@ ~27s). A VI-1024 reach or a different crash signature/timing selects
H3a-lowpower; an identical stall with Low Power Mode confirmed off refutes
it — one clean A/B closes it either way, no third run needed. If it still
reads `True`, stay on the sweep — do not repeat a same-recipe reachability
soak with no new measurement axis (iron rule 8).

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed, no candidate
  found beyond `rs64_is_hangar_vi()`, already refuted.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed, refuted.
- A same-recipe `s790_postsec2_reachability.sh` run with no new measurement
  axis while Low Power Mode is still ON and unchanged since s1892 — that's
  now 9 confirmations of the 7.2-7.4s stall; a 10th adds nothing.
- Ask (b) from s1891 (disposable clone + `git submodule update` bisect at
  `ef7a0fb9`) is still open and still legitimately human-only per CLAUDE.md's
  hard rule — do not attempt a workaround.
