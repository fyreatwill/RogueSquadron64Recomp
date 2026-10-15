# Next work unit

HYPOTHESIS-ID: m5-audio-route-reinit

Explain the selected mission route reinitialization. First perform a bounded
source census of every writer/prepare path that changes the M5 route identity
ordinal or row, then classify whether the `0x00690400` -> `0x00620400` reset
is a legitimate new audio publication or a port-only discontinuity. If more
than one live candidate remains, add one phase-gated capture that logs those
candidate writers in the existing transition window. Do not add a guard or
skip.

Competing hypotheses and discriminator:

1. H-legitimate-publication: the census finds one intentional writer/prepare
   path whose new ordinal is paired with a new source/task generation and
   valid PCM publication at both origins.
2. H-port-discontinuity: the reset is caused by a port-only writer or missing
   retail-equivalent state transition; the candidate has no legitimate new
   publication or diverges from the expected route state.
3. H-unresolved: multiple candidate writers remain live, or the capture lacks
   the first-512, both-origin, advancing-counter, or PCM controls. This selects
   no behavior change and requires a narrower discriminator.

Positive controls: the static census must enumerate all route-identity writes;
if a capture is required, phase output at `0x00690400`, the following
`0x00620400`, advancing `update_screen`, nonzero global task/PCM rows, and zero
crash/abort markers. The writer-to-publication table is the discriminator.

Exact baseline/source commands:

`rg -n "g_rs64_audio_identity|route_ordinal|route_row|rs64_audio_route_prepare|rs64_audio_join_m5_event" src lib`

If the census leaves multiple live candidates, use:

`cmake --build build --config Debug --target RogueSquadron64Recomp && zsh scratch/agent/s4923_mission_longevity.sh`

Inspect only bounded source windows plus
`scratch/agent/s4923_mission_longevity/summary.txt` and bounded `grep -a`
matches from `run.log`; kill any manual process with SIGKILL.
