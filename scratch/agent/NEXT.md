# Next work unit (s4332): C88C descriptor-to-D740 join

HYPOTHESIS-ID: m5-step9-c88c-descriptor-join

The s4331 corrected witness showed that `0x8009D740` is an inner edge of
`decodeAndFillVoiceBlock` (`0x8009C904` entry), not an edge of
`updateVoiceChannelParamsLarge` (`0x8009C5BC`). The image arm had shared
entry/post-helper/direct sequence ids; the silent arm had no target-phase
sequence/direct rows. The next unit must identify the descriptor class at the
actual C88C helper boundary.

Competing hypotheses:

- H-post-descriptor: C88C entry arguments and descriptor words are stable
  across silent/image arms; the divergence is after descriptor selection or in
  filter/output handling.
- H-pre-filter-route: C88C arguments or descriptor words differ or are invalid
  between arms; the divergence is before the D740 filter input.
- H-join-boundary: C88C state cannot be joined to the D740 sequence despite
  shared execution, leaving a generated/host state boundary unresolved.

Discriminator: extend the existing sequence witness at the C88C helper call to
retain its arguments and read a bounded set of candidate words (`a0`, `a1`,
and the first three words at each valid RDRAM-segment argument). Emit those
values with the sequence id and join them to the first 256 D740 direct rows.
Stable descriptor/type across both arms selects H-post-descriptor; differing
or invalid values selects H-pre-filter-route; zero C88C-to-D740 joins selects
H-join-boundary. Do not add decoder, RSP, AI, or game-path behavior.

Before building, verify the independent oracle controls in the same recipe.
Then edit the existing probe, build once, and run both arms concurrently with:

`zsh scratch/agent/run_s4320_m5_callsite_trace.sh`

Required controls: oracle whole-RDRAM positive control, oracle title VI 1024,
oracle hangar VI 512, both port VI controls, and the existing filter audit
positive control. Phase-gate all comparison rows on VI 512; use SIGKILL only.
