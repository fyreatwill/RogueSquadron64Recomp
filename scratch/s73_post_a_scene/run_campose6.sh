#!/bin/zsh
# s231: campose6, 2nd of the 2 budgeted reduced-I/O attempts. campose5
# (this session, attempt 1) crashed again at ~73.8s (memcpy_recomp+288),
# a 3rd distinct crash PC vs campose4's two attempts -- this run confirms
# or refutes that as a repeatable pattern before concluding I/O overhead
# is ruled out (iron rule 4: two independent lines of evidence).
# Copied from campose4 (s230) per NEXT.md instructions --
# same schedulepush2-derived schedule, all env vars kept armed as
# regression checks (including ROGUESQ_LOG_RENDER_CACHE_EPOCH=1). Only
# change vs campose4: the epoch diagnostic's fixup_game_funcs.py patch
# (site A/B) had its heartbeat modulus raised 500->5000 and its
# transition-log threshold raised run>=50->run>=2000, to cut fprintf
# syscall volume, since campose4 crashed 2/2 near the SELECT-CRAFT->
# mission VI transition (~73s) while a diagnostic-present-but-disabled
# control on the same binary ran clean -- isolating the cause to the
# diagnostic's I/O overhead, not its C logic or mere presence. This soak
# tests whether reduced I/O lets the run reach the freeze window
# (n=15360+) clean; if it still crashes at ~73s, I/O overhead is ruled
# out and the SELECT-CRAFT->mission transition itself is independently
# fragile. Launched as a single SYNCHRONOUS (foreground) Bash call, per
# longstanding instruction (needs to send scheduled keypresses and
# SIGKILL the process itself at the end).
set -e
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene

export ROGUESQ_LOG_CAMPOSE=1
export ROGUESQ_LOG_MAT3INV=1
export ROGUESQ_LOG_UNLIT_MESH_TRACER=1
export ROGUESQ_LOG_RENDERUNLIT_GUARD=1
export ROGUESQ_LOG_HEAPWALKER_GUARD=1
export ROGUESQ_LOG_HEAPWALKER_GUARD3=1
export ROGUESQ_LOG_HEAPWALKER_GUARD4=1
export ROGUESQ_LOG_MESGQUEUE_GUARD=1
export ROGUESQ_LOG_HEAPLISTDEQ_GUARD=1
export ROGUESQ_LOG_EMIT_DL_GUARD2=1
export ROGUESQ_LOG_EMIT_DL_GUARD3=1
export ROGUESQ_LOG_RENDER_CACHE_EPOCH=1

export PROBE_MODE=start_only
export HOLD_S=350
export CAPTURE_TICK_S=0.2
export HOLD_TICK_S=1
export STICK_SCHEDULE="20:start 40:start 60:start 70:su 78:sr 86:sd 94:sl 102:su 110:sr 118:sd 126:sl 134:su 142:sr 150:sd 158:sl 166:su 174:sr 182:sd 190:sl 198:su 206:sr 214:sd 222:sl 230:su 238:sr 246:sd 254:sl 262:su 270:sr 278:sd 286:sl 294:su 302:sr 310:sd 318:sl 326:su 334:sr 342:sd"

zsh run_mission_keys.sh campose6 5 12
