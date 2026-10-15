# Next work unit

HYPOTHESIS-ID: m5-route-qualification-hle

Run one production image arm with the verified window-controlled Rice/HLE
driver and qualify the positive route before repeating the deferred A1
image/silent auxiliary-store A/B. Use the existing single-arm recipe:

`env ROGUESQ_LOG_S4938_AUX_JOIN=1 zsh scratch/agent/s4923_mission_longevity.sh`

Competing hypotheses and discriminator:

1. H-driver-mismatch: the local build/driver combination is what prevents
   title/hangar; the single arm will stop at VI-640 again.
2. H-image-route: the production image reaches title `1024 @ 0x00790400`
   and hangar `512 @ 0x006AB400`, establishing the positive control needed for
   the deferred A1 A/B.
3. H-image-failure: the image arm reaches neither target and records a crash,
   abort, or task/SP failure that identifies a route-independent blocker.

The discriminating measurement is the phase sequence plus task/SP completion,
PCM source/consumer, and crash/abort markers in that one run. Do not interpret
the s4938 auxiliary-store nulls until both title and hangar controls fire.
