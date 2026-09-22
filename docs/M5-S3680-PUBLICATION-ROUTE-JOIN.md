# M5 s3680 — publication-boundary route join

The work unit tested stale task publication versus route sequencing after the
s3678 generation/route mismatch. The first implementation sampled the latest
route at `M_AUDTASK` handoff. That was the wrong boundary: route identity is
published by `rs64_audio_route_prepare` before the stage callback.

The fixed run added a monotonic route-publication sequence and latest route
ordinal/row at `rs64_audio_route_prepare`, and emitted those fields in the
existing source and stage rows. It used one build and the qualified concurrent
55-second oracle/port capture:

    env zsh scratch/agent/run_s3680_m5_publication_route_join.sh

Controls passed: oracle whole-RDRAM and descriptor/task watches reached title
and hangar; the port emitted phase, source-hook, ABI, DMA, source, and stage
controls. The port emitted 1,024 source rows and 3,836 stage rows.

| Rows | Generation current | Route current | Count |
|---|---:|---:|---:|
| Stage rows | yes | yes | 3,836 |
| Source rows | yes | yes | 246 |
| Source rows | yes | no | 778 |

Every stage row therefore observed the current generation and current route
publication. The source split shows that source reads can occur before the
route publication becomes current, but that lag does not persist into the
stage callback. This selects `H-StageCurrentPublication` and
`H-SourceBeforePublication`, and refutes stale stage publication and stage
route sequencing as explanations of s3678. The s3678 mismatch was a
handoff-boundary measurement artifact, not a runtime ownership result.

Remaining work is to join source-read ordering and exact input-DMA ownership
to the selected task object; no mitigation or guest-state change was made.
