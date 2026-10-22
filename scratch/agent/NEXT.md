# NEXT (s5903): derive collider-owner shape -> NPC/objective join

HYPOTHESIS-ID: g1-mission-progression

The s5902 same-run table proved that `rs5841_cand` is not a stable collider owner: candidate id 0x52 maps to multiple `obj` shape pointers. Candidate-derived `did` is `dead` throughout, and c1f disagrees across RET controls (0x52=0, 0x66=1), so neither field is a valid objective join alone.

Competing hypotheses:

- H-owner: `obj` has an owner pointer or adjacent shape/descriptor link; reading it will map RET ids 0x52/0x66 to the class-1 objective set.
- H-slot: the owner is reached through the active slot table using the shape's position/transform, not through `obj` fields; an obj-word census will be all non-pointers while a slot/position join resolves controls.
- H-class: c1f=1 is only an update-function subset and RET id 0x52 is a legitimate non-class-1 collision; owner resolution will show distinct object classes for the two RET controls.

Discriminator: one static field census plus one runtime field dump at the existing sphere hook, all in one build/run. For every distinct RET control owner (`obj`), dump the first 0x100 bytes and pointer-looking words, then test each pointer for descriptor +0x70 and for an active NPC/slot record. Outcome H-owner = a stable pointer/descriptor relation for both controls; H-slot = no local owner but a reproducible slot/position relation; H-class = stable owners resolve to different legitimate classes. Positive controls are same-run `[s5856] RET` for 0x52 and 0x66, plus the existing NPC-bolt hit stream.

Commands:

1. Add the bounded owner census to `tools/apply_s5835_sphere_probe.py` and live `N64Recomp/RecompiledFuncs/funcs_16.c`; update the analyzer.
2. `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run `env zsh scratch/agent/s5902_life.sh`; capture `scratch/agent/m6/s5902_life/run.log` and kill the explicit game/wrapper PIDs with SIGKILL at the cap.
4. Run `python3 -I tools/s5901_nn.py scratch/agent/m6/s5902_life/run.log` and require both RET controls before interpreting nulls.
