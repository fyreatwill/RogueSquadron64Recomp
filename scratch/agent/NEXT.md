# NEXT work unit (s1015)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Use the landed M4 probe, but first make the phase/input control positive. Run
one short probe with the documented Start schedule and the repository's
current input log enabled, verifying that a Start is observed and that VI
leaves 1024. Then use that verified schedule with
`PROBE_PHASE_WIDTH=512` and `ROGUESQ_LOG_M4_ACCUM=1`; do not rebuild unless
the control check shows the binary lacks the probe.

Competing hypotheses and discriminating measurement:

- `H-accumulator-saturation`: the complete tuple shows signed endpoint output
  created by VMADH saturation.
- `H-v4-v0-arithmetic`: the post-VMADH middle word is already `0x8000` in a
  sign-extending, in-range accumulator result.
- `H-v29-selection`: the post-VGE record selects a `v29` lane equal to
  `0x8000`.

The complete tuple makes the alternatives mutually exclusive; the independent
VMADH control must visibly fire before a null result is meaningful. If input is
positive but 512 still never appears, investigate phase transition/input
mapping rather than interpreting M4 zeros.

Exact commands:

`env ROGUESQ_LOG_INPUT=1 PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/input_control_1015 20 1`

Then, if the control is positive:

`env ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_LOG_INPUT=1 PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=150 zsh tools/probe.sh scratch/agent/accum_probe_1015 30 1`
