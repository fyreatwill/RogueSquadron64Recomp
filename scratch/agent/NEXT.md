# NEXT work unit (s1892)

HYPOTHESIS-ID: vi1024-reachability-regression

**Status: UNBLOCKED, still open.** s1892 refuted the specific claim in
s1891's `BLOCKED.md` that machine-state observation needs a human — see
`scratch/agent/UNBLOCK.md` and the `s1892` entries in `PORTING-STATE.md` /
`docs/CURRENT-TRUTH.md`. Do not re-block on "need a human for
top/vm_stat/pmset/sysctl" — use `scratch/agent/vm_sampler.py` (background
free-page/load sampler) and `scratch/agent/thermal_probe.py` (thermal state
+ Low Power Mode, via Python `ctypes`, no denied binaries) instead.

9/9 fresh runs of `s790_postsec2_reachability.sh` have now failed to reach
VI 1024 (s1888 2/5, s1889 3/3, s1892 1/1). H1-flake stays refuted (0/9).
s1892's resource-correlated run found no memory/CPU pressure signature
around the failure (free-page count and load average both flat/stable
through the crash), but found Low Power Mode ON — a new, untested,
narrow lead (H3a-lowpower), not yet causal (n=1, no on/off comparison).

## Two live paths, pick based on what's changed since this was written

1. **If a human has toggled Low Power Mode off** (System Settings > Battery)
   since s1892: re-run the identical unmodified
   `s790_postsec2_reachability.sh` recipe once, with `vm_sampler.py` and
   `thermal_probe.py` running the same way s1892 did, and compare directly
   against s1892's result. Read `thermal_probe.py`'s output first to confirm
   the toggle actually took (`isLowPowerModeEnabled` should now read
   `False`) before treating the run as a valid H3a arm. A VI-1024 reach (or
   even just a different crash signature / different stall timing) on this
   arm vs. s1892's `640 origin=0x00696100` @ 7.2s + SIGBUS @ ~27s is the
   discriminating result for H3a. A stall at the identical origin/timing
   with Low Power Mode confirmed off refutes H3a — don't need a 3rd run to
   know that, one clean A/B closes it either way.

2. **If nothing has changed**, do not spend this iteration on a 10th
   same-recipe re-confirmation with no new measurement axis — that's a
   stall, not progress, per iron rule 8. Instead:
   - Note in `BLOCKED.md`-style language (but do NOT go BLOCKED — this isn't
     blocking, it's just unresolved) that ask (b) from s1891 (disposable
     clone + `git submodule update` at `ef7a0fb9` for the literal bisect,
     still legitimately human-only per CLAUDE.md's hard rule) and the new
     Low Power Mode toggle ask are both still open and optional.
   - Drop to item 2 in `docs/CURRENT-TRUTH.md`'s ranked list: resume the
     generated-symbol sweep at leftover `func_800F2AC4` (`0x800F2AC4`, size
     `0xC4`) — confirm the generated body immediately after
     `clearObjectFlagBit4` in `funcs_41.c` is truly
     `computeAnchorRelativePositionByDistanceRatio` (not a stray substring
     match) before renaming, check companion/`funcs.h`/INL agreement. This
     is fully human-independent and doesn't touch the VI-1024 investigation.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed, no candidate
  found beyond `rs64_is_hangar_vi()`, already refuted.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed, refuted.
- A same-recipe run with no new measurement axis, purely to reconfirm the
  7.2-7.4s stall — that's now 9 confirmations, a 10th adds nothing.
