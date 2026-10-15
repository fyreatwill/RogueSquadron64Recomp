# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Implement the next reader-side synchronization variant for
`musyxMixActiveVoices`: replace the ordinary count/base pair observation with
an explicit atomic snapshot or lock-compatible handoff from
`allocateSongChannelArray`, using the existing fixup/replay mechanism rather
than a generated-file-only edit. Preserve the diagnostic controls, build the
runtime, and run one armed mission validation soak derived from
`s4982_reader_acquire_mission.sh`.

Competing hypotheses:

1. H-atomic-observation: explicit atomic acquire loads/snapshot of the count
   and base prevents the stale pair. Prediction with `ctl_arm>=1` and
   `s4579A>=1`: `bad=0`, `pidma=0`, `crash=0`, mission onset present.
2. H-lock-required: only a lock-compatible handoff prevents the pair from
   being observed across publication. Prediction: controls and mission fire
   but `bad>0` or `pidma>0` remains after atomic loads.
3. H-route: the validation route fails to exercise the allocator. Prediction:
   `ctl_arm=0` or `s4579A=0`; no race conclusion is allowed.

Discriminator: the same run must pass both allocator controls and mission onset;
then `bad`/`pidma` separates an atomic-observation fix from a remaining lock
requirement. ORIGIN: writer = guest `allocateSongChannelArray` publishing a
legitimate count 32 and base while the mixer runs on another host thread; this
is synchronization work, not a guard or value filter.
