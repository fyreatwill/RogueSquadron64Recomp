# Next work unit

HYPOTHESIS-ID: m5-aux-store-ab

Run the same-build image vs `musyx_stub` auxiliary-store A/B (recipe:
`scratch/agent/s4942_m5_aux_ab.sh`, built in s4942), both arms concurrently,
using the s4923-style driver that qualified title+mission in s4943. Controls:
title `0x00790400` and mission `0x00690400` must fire in BOTH arms; relaunch an
arm that stalls at VI-640 (intermittent), do not read it as a null.

Hypotheses: H-contract-gap (silent arm diverges in aux-store rows/task cadence),
H-route-only (rows identical across arms), H-rollback-specific (silent arm
changes route progress). Discriminator: per-phase `s4938-aux-store` row
counts/values, image vs silent.
