# NEXT work unit (s1897)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

**Primary path — resume the sweep.** Next census: leftover `func_800F2DA4`
at `0x800F2DA4` (size `0x24`, `syms/rogue_squadron.syms.toml:1992`).
Preliminary peek: `recomp_overlays.inl:1879` already shows
`{ .func = setAnimSubstructValueIfActive, .offset = 0x0004DC74, .rom_size =
0x00000024 }`, immediately following the newly-renamed
`setObjectSubstructF10IfReady` entry. Repeat the
s1887/s1893/s1894/s1895/s1896/s1897 procedure exactly:
1. `grep`/`awk` RECOMP_FUNC adjacency pairing in `funcs_41.c` to confirm
   `setAnimSubstructValueIfActive` truly follows `setObjectSubstructF10IfReady`
   (not a stray substring match).
2. Check `funcs.h` declares it in the right order.
3. Check `recomp_overlays.inl` — offset must be
   `setObjectSubstructF10IfReady`'s offset (`0x0004DC44`) `+ 0x30 =
   0x0004DC74`, and `rom_size` must be `0x00000024` (matching TOML `size =
   0x24`).
4. `grep -rln 'func_800F2DA4\b'` across generated RecompiledFuncs tree —
   must be zero hits (non-collision).
5. If all four agree, rename the TOML entry only — no build/regen needed
   (this class of change is metadata-only sync; the generated tree already
   has the correct name from N64Recomp's own matching, independent of this
   repo's TOML).

**Where the generated tree actually lives (found s1897):** it is gitignored
(`RecompiledFuncs/` in `.gitignore`) and does NOT exist under this repo's
`build/` right now. It was found at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/` (an
additional working directory) — `funcs_41.c`, `funcs.h`, and
`recomp_overlays.inl` are all there. Check there first; don't re-search the
whole filesystem.

Further-out preview (not yet verified via the full procedure, just spotted
in the same `.inl` block): `func_800F2DC8`/`0x148` lines up with
`generatePerpEmitDirectionWithJitter` at offset `0x0004DC98`. Confirm with
the full four-step procedure when you reach it — don't skip steps just
because the preview looked right.

**Before starting**, check whether `vi1024-reachability-regression` has
been unblocked: run `python3 scratch/agent/thermal_probe.py` and read
`isLowPowerModeEnabled`. If it now reads `False` (a human toggled Low Power
Mode off in System Settings > Battery since s1892/s1895/s1896/s1897), STOP
the sweep and instead re-run the unmodified `s790_postsec2_reachability.sh`
once, with `vm_sampler.py` and `thermal_probe.py` running the same way
s1892 did, and compare directly against s1892's result (`640
origin=0x00696100` stall @ 7.2s, then
`fillSampleStreamRange`/`musyxRenderVoiceSamples` SIGBUS @ ~27s). A VI-1024
reach or a different crash signature/timing selects H3a-lowpower; an
identical stall with Low Power Mode confirmed off refutes it — one clean
A/B closes it either way, no third run needed. If it still reads `True`,
stay on the sweep — do not repeat a same-recipe reachability soak with no
new measurement axis (iron rule 8). As of s1897 it still reads `True`
(unchanged since s1892).

Also check the sweep's 15-title REVISIT gate: `grep -n '^## Session '
PORTING-STATE.md | tail -15`. If all 15 titles belong to the sweep
(contain "synchronized" or "confirmed ... symbol"), this iteration is a
REVISIT instead of another census — spend it re-attempting the external
retail-entry boundary or M4 accumulator-origin threads with a genuinely
new angle. As of s1897 this gate does NOT fire (s1888-s1892 are still in
the 15-window, 5 of 15 slots non-sweep) — but the window keeps tightening
toward all-sweep as more census sessions land; check again next iteration.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed, no candidate
  found beyond `rs64_is_hangar_vi()`, already refuted.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed, refuted.
- A same-recipe `s790_postsec2_reachability.sh` run with no new measurement
  axis while Low Power Mode is still ON and unchanged since s1892 — that's
  now 12 confirmations of the 7.2-7.4s stall; a 13th adds nothing.
- Ask (b) from s1891 (disposable clone + `git submodule update` bisect at
  `ef7a0fb9`) is still open and still legitimately human-only per CLAUDE.md's
  hard rule — do not attempt a workaround.
