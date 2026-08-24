# NEXT work unit (s2281) — qualify the M5 route across C88 arms

HYPOTHESIS-ID: m5-keyon-pointer-branch-discriminator

## Work unit

Run one same-build, concurrent C88=0 versus C88=1 port pair using the
established eleven-Start route, while retaining the oracle whole-RDRAM,
title/hangar, and eight-PC controls. Parameterize the existing driver (or make
one self-contained pair driver) so the two port processes differ only in
`ROGUESQ_M5_C88_VALUE`; do not change the runtime, key-on return, divide
guards, slot stores, audio default, or LLE route gates. Keep the existing
`PROBE_PHASE_WIDTH=1024` / `PROBE_KEYS_FROM_PHASE=1` phase controls and SIGKILL
deadlines. The enlarged oracle binary is already built; rebuild only if the
driver change requires it.

## Competing hypotheses and discriminating measurement

- **H-C88-route:** only one C88 value reaches the target route. If C88=1
  reaches `512 @ 0x006AB400` while C88=0 stalls, the disabled-audio field is a
  route antecedent; if C88=0 reaches and C88=1 stalls, the enabled arm changes
  route behavior. Do not infer key-on fields from the non-qualifying arm.
- **H-RouteLoad:** both C88 arms have the same route outcome (both qualify or
  both stall at the same phase). C88 is not the discriminator at this scope;
  if both qualify, use the C88=0 target window for the retail join, otherwise
  keep the route investigation open.
- **H-CoverageInvalid:** the oracle control, title/hangar gate, or either port
  arm is absent, or the C88=0 arm does not reach the hangar. This outcome
  invalidates the key-on comparison regardless of any nonzero rows.

The single comparison table is keyed by `arm(C88), phase, origin, width` and
contains `title_gate, hangar_gate, last_phase, timeout_or_crash,
keyon_rows_by_PC, b40_route_control, route_state_control`. Accept a key-on
comparison only when the oracle has whole-RDRAM >=10,000 writes and all eight
retail buckets have `overflow=0`, while the C88=0 port arm reaches
`512 @ 0x006AB400`. A C88 route split selects H-C88-route; equal outcomes
select H-RouteLoad; any missing gate selects H-CoverageInvalid.

## Exact commands

1. Use `apply_patch` to parameterize the existing port launch in
   `scratch/agent/run_s2278_m5_keyon_pointer_branch.sh` (replace the literal
   `ROGUESQ_M5_C88_VALUE=0` with a per-arm value), then create one
   `scratch/agent/run_s2281_m5_c88_route_pair.sh` that launches both C88 arms
   concurrently, launches the existing oracle once, enforces the two
   deadlines, SIGKILLs both port processes, and prints the complete comparison
   table. The two port logs must use distinct paths.
2. Run the new pair driver from the repository root:

```sh
zsh scratch/agent/run_s2281_m5_c88_route_pair.sh s2281_m5_c88_route_pair
```

3. Summarize gate counts with `grep -c`/`grep -n` and inspect only tails or
   bounded summaries; do not infer from a missing row without its positive
   controls. If C88=0 reaches hangar, then use the qualified phase-10 rows for
   the next oracle source/state join; otherwise leave the key-on comparison
   unevaluable and make no behavior change.
