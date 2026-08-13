# NEXT work unit (bounded post-sec2 FULL_SYNC persistence capture)

HYPOTHESIS-ID: m3-postsec2-authoritative-e9

Run one bounded, phase-gated capture using `scratch/agent/s790_postsec2_reachability.sh`.
Keep `ROGUESQ_LOG_VI_ARGS=1`, the provenance positive controls, `[rdp-fullsync]`
logging, and the phase-relative key schedule. Do not change game logic or add
a mitigation. The capture is valid only if VI reaches 1024 and the control
record has `emit=1 raw=1 dispatch=1 match=1`.

Competing hypotheses:

- H-authoritative-persistent: after VI-1024, aligned E9 provenance and
  authoritative `rdpFs`/FULL_SYNC advances recur; this confirms s820's parser
  result is not a one-run artifact.
- H-pre-authoritative-loss: aligned E9 provenance recurs, but authoritative
  advancement remains absent or flat after the gate; this restores the parser
  loss hypothesis.
- H-prechain-transient: the run fails before a valid post-gate parser sample;
  the persistence question remains unevaluable.

Discriminating measurement: in the same run after the VI-1024 transition,
compare aligned `e9_b` and authoritative `rdpFs`/`[rdp-fullsync]` records.
Positive advancement selects H-authoritative-persistent; positive provenance
with flat authoritative state selects H-pre-authoritative-loss; no valid
post-gate sample selects H-prechain-transient.

Exact command:

    zsh scratch/agent/s790_postsec2_reachability.sh

Run one arm only. Record the capture path and classify the result from the
captured log, including any later crash family.
