# NEXT: RUN — post-vd clamp replay on corrected FD57 ring
HYPOTHESIS-ID: g3c-owner-visual-b

The route audit is complete. Do not rebuild or rerun the game before this
offline replay.

Use the corrected route witness:

- `scratch/agent/m6/g1_lvl2s6380long/run.log`
- `scratch/agent/m6/g1_lvl2s6380long/keys.log`
- `scratch/agent/m6/g1_lvl2s6380long/mc_ctl.txt`
- reference: `scratch/agent/m6/g1_lvl2s6378/run.log`

Run `python3 tools/agent/rsp_vu_replay.py <run.log> <first-spike-vu8-line>`
for s6380long and the reference ring. Record rows, accumulator mismatches,
result mismatches, and saturated-result matches. The route audit already passed
the positive control: s6380long has 155 FD57 `[spike-st]` rows and 546 FD57
`[spike-vu8]` rows, with `att=1 mission` and the same VI origins as s6378.

Competing hypotheses:

- H-rsp-emu-clamp: replayed post-`vd` results disagree with the logged lane
  values at the FD57 ring, indicating clamp/ACC semantics are wrong.
- H-clip: replayed values match and show legitimate saturation from near-zero w;
  the wedge is a valid clip-path output.
- H-retail: replay matches, but an independent retail/reference RSP run is
  still required before calling the visible spike retail-identical.

DISCRIMINATING MEASUREMENT: FD57-ring post-`vd` result replay. Mismatched
logged results select H-rsp-emu-clamp; matching results with saturated lanes
select H-clip, while H-retail remains open pending an independent reference.
