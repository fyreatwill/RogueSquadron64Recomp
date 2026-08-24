# NEXT work unit (s2275) — M5 Step 1 route requalification

HYPOTHESIS-ID: m5-step1-task-output-contract

## Work unit

Run one single silent-arm control using the reduced Step 1 probes and the
phase-origin watcher. Enumerate every VI phase, process-death timing, crash
symbol, guest PC, and route-control count. Do not launch the image arm and do
not interpret audio/output nulls. Only `512 @ 0x006AB400` is the hangar gate;
the `512 @ 0x00690400` phase seen in s2274 is off-target.

## Competing hypotheses and discriminating measurement

- **H-RouteStable:** the silent arm reaches `1024 @ 0x00790400` and then
  `512 @ 0x006AB400`, remains alive through the post-hangar window, and has
  the positive route controls. A new staggered pair is permitted.
- **H-RouteDeathRace:** the expected hangar phase is emitted, but the process
  dies before the watcher sees it or immediately after it. The phase log and
  crash/death ordering select a driver/route-gate race, not an audio contract.
- **H-RouteLoadCrash:** the run reaches only off-target 512/640 phases or dies
  with a renderer/game crash before `0x006AB400`. This keeps the pair
  unevaluable and identifies the crash boundary for route-stability work.
- **H-RouteStall:** the process stays alive until the 180-second pre-hangar
  deadline without the target origin. This selects a stall/load-sensitivity
  result and does not authorize a guard or route change.

The single discriminating table is:
`phase_index,width,origin,phase_time,process_alive,death_time,pc_symbol,
last_guest_pc,audtask_dispatch,audio_return,pcm_source/consumer,
m5_b40_route,m5_route_state,missing_func,crash,hangar_gate`.
`1024 @ 0x00790400` and `512 @ 0x006AB400` are positive route controls;
`512 @ 0x00690400`, any other 640 phase, and the startup `[phase]` rows are
not target controls. Each outcome above is selected by the target phase plus
the process/death/crash relation, not by an audio counter.

## Ground-truth prerequisite

No new runtime instrument is being added. The existing retail whole-RDRAM
watch and writer controls remain the independent ground truth. This is a
port-side route-validity run only; a null is not evidence about audio.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
zsh scratch/agent/run_s2275_m5_step1_route_requal.sh s2275_m5_step1_route_requal
```

The script launches one silent arm from `build/`, self-watchdogs, SIGKILLs on
timeout, and writes bounded summaries under
`scratch/agent/s2275_m5_step1_route_requal/`. If the target phase is
qualified, the next iteration may construct the staggered image comparison;
otherwise keep the Step 1 pair unevaluable and pivot to the selected route
boundary after the third stalled attempt.
