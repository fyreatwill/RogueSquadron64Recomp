# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Implement the reader-side ordering fix for `musyxMixActiveVoices`: make the
count/base pair observation acquire the publication from
`allocateSongChannelArray`, using the existing fixup/replay mechanism rather
than a generated-file-only edit. Preserve the diagnostic controls, build the
runtime, and run one armed mission validation soak derived from
`s4981_armed_mission_fix.sh`.

Competing hypotheses:

1. H-reader-order: an acquire/order barrier at the mixer reader prevents the
   stale base. Prediction with `ctl_arm>=1` and `s4579A>=1`: `bad=0`,
   `pidma=0`, `crash=0`, mission onset present.
2. H-lock-required: acquire alone is insufficient because the pointer/count
   pair is not published atomically with respect to the host-thread schedule.
   Prediction: controls and mission fire but `bad>0` or `pidma>0` remains.
3. H-route: the validation route fails to exercise the allocator. Prediction:
   `ctl_arm=0` or `s4579A=0`; no race conclusion is allowed.

Discriminator: the same run must pass both allocator controls and mission onset;
then `bad`/`pidma` separates reader ordering from a remaining synchronization
defect. ORIGIN: the writer publishes legitimate count 32 and the reader sees a
stale base; this is synchronization work, not a guard or value filter.
