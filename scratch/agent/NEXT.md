# Next work unit: positive-control the title->hangar route (soak s5373 is queued)
HYPOTHESIS-ID: patcheslib-shadowed
s5371 soak: nohangar t=200 (title reached, hangar never). s5099 (01:28) reached hangar 3/3 with the same key recipe, but build/RogueSquadron64Recomp was rebuilt 18:30, after it. Queued scratch/agent/soak_queue/s5373_hangar_control_s5099_recipe.sh = s5099 recipe verbatim on the current binary (PASS = >=2 hangar arrivals, 0 CRASH).
Read the verdict in SOAK-RESULTS.md / soak_results/s5373_*/keys.log:
- PASS: route and focus are fine; the s5371 failure comes from its env delta (s5371 adds LOG_ALLOC_TAIL_GUARD2/3, drops LOG_SCENE_NODE_CACHE_GUARD) or its 150s title wait. Bisect by adding the two GUARD flags to the s5099 recipe.
- FAIL (title reached, no hangar): the 18:30 rebuild regressed the title->hangar path (H2); but a FAIL also fits host focus/key timing, so rerun once to separate it before bisecting the build delta.
