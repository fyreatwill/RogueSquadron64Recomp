# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Implement the lock-compatible handoff variant for `musyxMixActiveVoices` and
`allocateSongChannelArray` through the fixup/replay mechanism, rather than a
generated-file-only edit. Preserve the diagnostic controls, build the runtime,
and run one armed mission validation soak derived from
`scratch/agent/s4984_atomic_voice_pair_mission.sh`.

Competing hypotheses:

1. H-lock-required: a shared lock-compatible handoff prevents the pair from
   being observed across publication. Prediction: controls and mission fire,
   with `bad=0`, `pidma=0`, `crash=0`.
2. H-atomic-insufficient: explicit guest-memory acquire/release atomics are
   insufficient without exclusion. Prediction: controls and mission fire but
   `bad>0` or `pidma>0` remains.
3. H-route: the validation route fails to exercise the allocator. Prediction:
   `ctl_arm=0` or `s4579A=0`; no race conclusion is allowed.

Discriminator: the same run must pass both allocator controls and mission onset;
then `bad`/`pidma` separates a lock handoff from atomic insufficiency. ORIGIN:
writer = guest `allocateSongChannelArray` publishing a legitimate count 32 and
base while the mixer runs on another host thread; this is synchronization work,
not a guard or value filter.
