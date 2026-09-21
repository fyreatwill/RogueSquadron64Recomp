# Next: task-generation join at audio-task handoff

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3677 showed that task data pointers are reused: the corrected shared
record produced 0 exact task-pointer/route matches and mostly same-pointer,
different-route fallbacks. The next bounded unit is to carry one monotonic
audio-task generation from the actual `get_rsp_microcode`/task handoff into
both the source-reader and image-stage witnesses. This is one shared key, not
another pointer-only join.

Competing hypotheses:

- H-HandoffGeneration: source and stage rows share the same task generation;
  route-ordinal drift is only publication timing.
- H-CrossThreadTask: source and stage rows have different generations despite
  matching task pointers; the current thread-local task is not ownership-safe.
- H-RoutePublicationLag: generations match but route ordinals still drift;
  the route identity is published at a different callback boundary.

Discriminating measurement: emit the generation in every bounded source and
stage row and classify exact generation/route, same-generation/different-route,
and different-generation matches. Exact generation/route hits select
H-HandoffGeneration; same-generation/different-route hits select
H-RoutePublicationLag; different-generation hits select H-CrossThreadTask.
Require oracle whole-RDRAM, descriptor, title, hangar, and type-2 controls plus
port source-hook, source, phase, ABI, and stage controls.

Commands:

    cmake --build build -j8
    zsh scratch/agent/run_s3674_m5_stage_task_join.sh

Preserve the qualified route and SIGKILL cleanup in the existing recipe. Do not
alter guest state or add a mitigation. If the generation instrument does not
emit its positive control in the same run, discard the result.
