# Resume checkpoint

This is a close-out of the interrupted s4985 retry. Do not rerun the game in
this iteration. The existing artifact is commit `7f17fcb4`: Debug build
completed after `tools/apply_s4985_voice_lock.py` serialized both complete
functions, and the captured validation log is
`scratch/agent/soak_results/s4985_whole_voice_lock_mission/run.log`.

# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race

Replace s4985's whole-function host mutex with a narrow lock-compatible
handoff: lock only while `allocateSongChannelArray` publishes the base and
count, and lock only while `musyxMixActiveVoices` acquires the paired count and
base. Apply it through the fixup/replay mechanism, build, and run one armed
mission validation soak derived from
`scratch/agent/s4984_atomic_voice_pair_mission.sh`.

Competing hypotheses:

1. H-narrow-lock: a shared lock over only publication/paired observation
   prevents the stale pair while preserving the route. Prediction: title and
   mission controls fire, with `bad=0`, `pidma=0`, `crash=0`.
2. H-lock-too-coarse: even the narrow lock interferes with required runtime
   progress. Prediction: `s4579-A` fires but title does not, as in s4985.
3. H-atomic-insufficient: exclusion is not the missing contract. Prediction:
   title and mission controls fire but `bad>0` or `pidma>0` remains.
4. H-route: the validation route fails before allocator exercise. Prediction:
   `s4579-A=0`; no race conclusion is allowed.

Discriminator: the same run must pass the title and mission controls and show
`s4579-A>0`; then title absence selects coarse-lock interference, while a
mission run separates `bad`/`pidma` zero from atomic insufficiency. ORIGIN:
writer = guest `allocateSongChannelArray` publishing a legitimate count 32 and
base while the mixer runs on another host thread; this is synchronization work,
not a guard or value filter.

Exact checks:

    python3 tools/apply_s4985_voice_lock.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s4984_atomic_voice_pair_mission.sh

Required controls: title origin `0x00790400`, hangar origin `0x006AB400`,
mission onset, `s4579-A`, `ctl_arm`, PCM nonzero rows, `bad`, `pidma`, crash,
and abort. Do not interpret a null unless title and allocator controls fire.
