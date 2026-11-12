# Host completion-delivery census (s7197)

Question: does any host path that owes the guest a completion message return without posting it, when hardware
would have posted? s7196 showed that one such path (PI DMA to an unknown region) freezes the game 3/3. This table
covers every producer of an external message in ultramodern, librecomp and src/main.

Classes: **DEAD** = cannot happen in this game. **SAFE** = hardware also posts nothing, or the failure is loud
(QUICK_EXIT / throw / assert), not a silent freeze. **HAZARD** = hardware completes, we do not.

## Delivery layer (ultramodern/src/mesgqueue.cpp)

| Path | Behaviour | Class |
|---|---|---|
| dequeue, queue full, source has requeue off (VI, AI, PI) | message dropped | SAFE: libultra's exception handler and `__osDevMgrMain` post with NOBLOCK and drop on full too |
| dequeue, queue full, requeue on (SP, DP, SI, Timer) | requeued | SAFE (stronger than hardware) |
| guard-refused mq (s7194) | dropped, logged once per mq | SAFE: undeliverable |
| mq == NULL (event never registered) | refused by do_send | SAFE: hardware with no registered event posts nothing |

## Producers

| Producer | File | Skip paths | Class |
|---|---|---|---|
| SP done, non-gfx task | events.cpp task_thread_func | `run_task` false -> QUICK_EXIT | SAFE (loud) |
| SP + DP done, gfx task | events.cpp gfx_thread_func | none; both posted unconditionally; only `exited` stops the loop | DEAD |
| osSpTaskStartGo override | src/main/upstream_compat.cpp | invalid OSTask pointer -> return, no SP/DP post | DEAD in practice (static scheduler task structs); now logs `[s7197-sp-drop]` so a recurrence names it |
| librecomp weak osSpTaskStartGo | librecomp/src/sp.cpp | spai guard -> return | DEAD (overridden by src/main) |
| DL extension events | ultramodern/src/extensions.cpp | posts only on a registered match | DEAD (game registers none) |
| VI retrace | events.cpp vi_thread_func | mq NULL; before game start | SAFE |
| AI, legacy per-VI (`ROGUESQ_AI_EVENT_DRAIN=0`) | events.cpp vi_thread_func | none (time driven) | SAFE |
| AI, `ROGUESQ_AI_EVENT_HZ` thread | events.cpp | none (time driven) | SAFE |
| **AI, drain thread (default since s5672)** | events.cpp | posts only when SDL's queue holds <= thr bytes. A device that stops pulling (paused; SDL2 disconnected output: the queue callback stops) never drains, so AI is never posted again | **HAZARD -> fixed s7197** |
| Timer expiry | ultramodern/src/timer.cpp | none; mq NULL refused | SAFE |
| SI: osContStartReadData / osContStartQuery | ultramodern/src/input.cpp | none; posted synchronously to the registered SI mq (hardware posts to the OS_EVENT_SI queue as well) | SAFE |
| osContReset | input.cpp | `assert(false)` | SAFE (loud) |
| EEPROM read/write/probe | librecomp/src/eep.cpp | synchronous; libultra consumes its own SI messages internally, so none is owed | SAFE |
| PI do_dma: ROM read, SRAM read/write, guard path | librecomp/src/pi.cpp | all post | DEAD |
| PI do_dma: unknown region read/write | pi.cpp | posted since s7196 | fixed s7196 |
| PI do_dma: ROM write | pi.cpp | throws | SAFE (loud) |
| Flash write/read array | librecomp/src/flash.cpp | post; wrong save type QUICK_EXITs | SAFE |
| Flash erase / status | flash.cpp | synchronous, no message owed | SAFE |

## The AI hazard (s7197)

Hardware raises the AI interrupt from the DAC clock, so a buffer always completes. The default drain thread
substitutes "SDL queue drained" for that clock. Close/reopen is fine: `audio_device == 0` reports 0 bytes and a
fresh device is empty. A device that exists but does not pull is the hole: SDL2 stops calling the queue callback
while a device is paused or after its output disconnects (an HDMI TV or Bluetooth headset going away).

Fix, default on: after `ROGUESQ_AI_STALL_POST_MS` (100) with no AI post, the drain thread posts anyway and logs
`[s7197-ai-stall] fallback post`. `=0` restores the drain-only path.
Forced arm: `ROGUESQ_AI_STALL_TEST=<sec>` pauses the SDL device from `<sec>` on (re-paused after a reopen).
Qualification arms and results: PORTING-STATE session 7197.
