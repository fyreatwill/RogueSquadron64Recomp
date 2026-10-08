# Next work unit: why does guest tid 0 not send to 0x8011A818 on gap-time VI wakes? (s4262)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4261: tid 3 (audio) produces 0x8010FEE0, then blocks on 0x8011A818; only sender is tid 0 (~6/s in gap vs ~800/s healthy). Tid 0 wakes on each VI post on 0x80149670 but skips the send.
Hypotheses: (A) tid 0 loop gates the send on a game-state flag/counter (e.g. an audio-request-pending bit set by a callback that never runs); (B) tid 0 branches differently because a reply from thr3 (on 0x80128D10/0x80149990) is missing; (C) tid 0 sends via osJamMesg, which is not counted in on_result.
Discriminator: record guest ra of osSendMesg/osJamMesg to 0x8011A818 (add osJamMesg to on_result) and, per tid-0 osRecvMesg wake on 0x80149670 in a GAP window, the next mq tid 0 touches. Healthy (CONTROL) vs gap in one run. Positive control: ra table non-empty for a healthy-period send to 0x8011A818.
Reuse scratch/agent/s4259_gap.sh.
