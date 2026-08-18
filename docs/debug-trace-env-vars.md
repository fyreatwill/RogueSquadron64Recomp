# Debug Trace Environment Variables

The recompile accumulates many `fprintf(stderr, "[tag] ...")` trace points
during bug investigation. Most fire dozens or hundreds of lines per second
and are silent on a healthy run. To keep the terminal usable they are
gated behind environment-variable flags. This file lists every flag, what
trace tags it controls, where the code lives, and when you'd want to turn
it on.

## How to enable

Set the env var to a non-zero value before launching the executable:

**PowerShell / cmd**
```
set ROGUESQ_LOG_DPC=1
build\Debug\RogueSquadron64Recomp.exe
```

**bash / git-bash**
```
ROGUESQ_LOG_DPC=1 ./build/Debug/RogueSquadron64Recomp.exe
```

**Catch-all**: `ROGUESQ_LOG_ALL=1` enables every category at once.

To disable: unset, set to `0`, or leave undefined.

## Categories

| Env Var | Default | Tags Enabled | When To Enable |
|---|---|---|---|
| `ROGUESQ_LOG_ALL` | off | everything below | Quick "show me everything" — heavy output, OK for one-shot diagnostic. |
| `ROGUESQ_LOG_THREADS` | off | `[NAME] set_native_thread_name`, `[NAME] wstring`, `[NAME] SetThreadDescription`, `[RT64] Thread::setCurrentThreadName begin/done`, `[RT64] wstring ok` | Thread-name registration crashed (utf-8/utf-16 conversion, COM init). Useful only when investigating thread-naming code. |
| `ROGUESQ_LOG_THREAD_LIFECYCLE` | off | `[DEBUG] osCreateThread/osStartThread`, `[DEBUG] thread N starting`, `[Thread] _thread_func`, `[Thread] about to set name` | Thread-system bring-up, scheduler-deadlock, or "which thread is doing X" investigations. Fires ~30 lines at startup. |
| `ROGUESQ_LOG_INIT` | off | `[DEBUG] init_heap done`, `[DEBUG] calling init_saving`, `[DEBUG] init_saving done`, `[DEBUG] calling entrypoint`, `[DEBUG] entrypoint returned` | Game hangs before reaching the entrypoint — these breadcrumbs tell you whether heap setup or save-system init was the last thing to run. |
| `ROGUESQ_LOG_DPC` | off | `[task-brief]`, `[task]`, `[task#N gfx]`, `[task#N gfx-FULL]`, `[task#N setcombine]`, `[task#N movemem-idx]`, `[task#N hist]`, `[dpc] FULL_SYNC byte sent`, `[dpc] G_SETPRIM/ENV_COLOR`, `[dpc] PRIM override`, `[dpc] SET_COLOR/DEPTH/TEXTURE_IMAGE`, `[dpc-pak] *`, `[dpc-cine] ENTER`, `[dpc-64tri] ENTER`, `[trace] cinematic_drv ENTRY/BEFORE/AFTER` | Tracing what GFX commands the Factor5 LLE ucode emits. **Highest-volume category** — easily 1000+ lines/sec during cinematic. Use when investigating combiner muxes, texture loads, task pacing, or per-task tri/texrect counts. |
| `ROGUESQ_LOG_RDP_STATE` | off | `[trace] setCombine #N mux=...`, `[trace] setOtherMode #N cycleType=...`, `[texfilt] tf=...`, `[particle-mux] otherMode...` | RDP-state diagnosis — which combiner/cycleType is active when a specific draw fires. Useful when correlating "what mux runs at frame X" or "did texfilt change between expected and actual". |
| `ROGUESQ_LOG_TRI_COPY` | off | `[tri-copy]`, `[tri-copy-assert]` | Phase-scoped `drawIndexedTri` caller breadcrumb: active GBI/opcode, command words, RSP/RDP other-mode values, and copy-cycle assertion context. |
| `ROGUESQ_LOG_TRI_WRITER` | off | `[tri-source-join]` | Bounded F5 VTXCOLOR-to-RT64 triangle join: task-local F5 state, RT64 DL/shade ordinal, and accepted submit serial/range. |
| `ROGUESQ_LOG_PRESENT` | off | `[trace] RT64::Present #N swapIdx=...`, `[trace] PresentQueue::frame #N`, `[trace] Present::lookup`, `[trace] PresentQ::regfb/scratch`, `[trace] fbReg`, `[vi-status] word=...` | VI presentation / framebuffer routing investigations. The buffer-arbiter bug was diagnosed via these traces. Fires ~60 lines/sec. |
| `ROGUESQ_LOG_VI_SELECTOR` | off | `[vi-selector-positive]`, `[vi-selector-callsite]`, `[vi-selector-control]`, `[vi-selector-selected]`, `[vi-predecessor-entry]`, `[vi-predecessor-edge]` | s802/s1149 diagnostic for the game-side VI mode selector, its generated caller, and the caller's exact predecessor edge; includes an independent host-path positive control. |
| `ROGUESQ_LOG_VI_CALLERS` | off | `[vi-gate]`, `[avf-gate]` | Direct `osViSetMode` caller sites (`initVideoSubsystem` / `applyPendingViChanges` / `swapBufferWithViMode`) plus the s1920 `advanceVideoFrame` swap-gate table (`site=loop\|B0\|swap`, `n`, `byte` at `0x80128EAD`, `$s0`, `took_B0`, `took_swap`), the s1921 `site=entry\|exit` counts (`entryn`/`exitn`), the s1922 `runVideoFrameTick` table (`site=tick-entry\|tick-jal\|tick-exit`, `tickn`/`jaln`/`exitn`), the s1923 caller table (`site=mgl-entry\|mgl-jal-a\|mgl-jal-b\|mission-entry\|mission-jal\|menu-entry\|menu-jal`, `tickn`/`jaln`/`siten`), the s1924 `menuOverlayInit` spin/exit table (`site=menu-spin\|menu-exit`; spin rate-limit is first 8 then every 1000000, tightened s1926), the s1925 `anyAudioSlotActive` return table (`site=slot-ret`, `gate` at `0x800A0F50`, pre-sltiu `s1`, return `v0`, `path=gate0\|stub\|walk`; first 8 then every 1000000), the s1926 `isAudioSlotActive` load table (`site=slot-byte`, `idx`/`byte`/`base` at `0x801496F8`/`ch` at `0x80141AD0`; first 8, every 1000000, and first 8 `byte!=0`), and the s1927 writer table (`site=slot-alloc` after `sw` `0x8008F0EC` with `old`/`new`/`count`; `site=slot-sb` on every table-using `sb` to slot+0 in `allocateSongChannelArray` / `musyxRenderVoiceSamples` / `musyxInitVoiceFromSample` / `musyxTriggerVoiceAttack` / `stopVoiceMarkRetrigger` / `deactivateVoice`, first 32 then every 1000 and every `new==2`), the s1928 end/rekey table (`site=render-stage` n2/n0; `site=render-end` every fire; `site=rekey` when TriggerVoiceAttack `old!=0`), and the s1929 cursor/attacker table (`site=cursor` at `L_80090150` sltu with `cur`/`pos`/`step`/`cross`, first 8 then every 1000000 plus every `cross=1`; `site=attack-jal` on both `jal 0x8009231C` sites with `caller=tick|stream` and slot+0 `old`, first 32 then every 1000 plus every `old==0`). Also enabled by `ROGUESQ_LOG_ALL`. |
| `ROGUESQ_LOG_VI_TRANSITION` | off | `[vi-transition-producer]` | Phase-scoped `osViSetMode` producer calls after the committed VI width reaches 640; distinguishes continued producer activity from a stable pre-1024 loop with no mode-selection calls. |
| (unconditional) | always | `[osViSetMode #N] ... ra=... site=` | Every `osViSetMode_recomp` submit. `site=` is `dladdr` of the host caller (the five jal sites). Guest `$ra` is `0` under this recomp (N64Recomp does not write `$ra` on `jal`). Added s1919. |
| `ROGUESQ_LOG_SP_TASKS` | off | `[sp] osSpTaskStartGo #N kind=GFX...` | Task-scheduling rate (cinematic ~30/s, normal play 1-2/frame). Useful when tracking how often the game submits GFX tasks to the RSP. |
| `ROGUESQ_LOG_EVENT_WIRING` | off | `[event-wiring] register/complete` | Bounded SP/DP event registration and completion target rows. Compare guest queue/message identities across both sides when a blocking SP/DP receive has no obvious producer. Also enabled by `ROGUESQ_LOG_ALL`. |
| `ROGUESQ_LOG_AUDIOTICK_TRACE` | off | `[vi-cb-loop]`, `[vi-cb-recv1]`, `[vi-cb-recv2]`, `[vi-cb-walk]`, `[vi-cb-slot]`, `[vi-cb-after]`, `[synth-entry]`, `[synth-exit]`, `[vi-set-event]`, `[vi-enq]`, `[vi-mq]`, `[vi-deq]`, `[vi-wait]` | s1940: `[vi-deq]` on `dequeue_external_messages` for `mq=0x80114388` (`site=ok\|full`, pre-send `validCount`/`msgCount`); `[vi-wait]` enter/exit/timeout on `wait_for_external_message` (`mq`/`sent`/`timed`). s1939: host `osViSetEvent` register (`mq`/`msg`/`retrace`) and VI-thread enqueue (`mq`/`msg`/`retrace`/`total_vis`); host `osSendMesg`/`osRecvMesg`/`osJamMesg` on `0x80114388` as `[vi-mq] site=send\|recv\|jam`. Guest retrace-handler sites stay always-on when this flag is set. Also enabled by `ROGUESQ_LOG_ALL`. |
| `ROGUESQ_HWBP` | off | `[hwbp] watching VA ...`, `[hwbp-hit #N] tid=... stack trace` | Hardware-breakpoint watchdog on `rdram + ROGUESQ_HWBP_ADDR` (default 0x3CBC4) — fires a symbolicated stack trace on every write to that address. Use when tracking memory corruption to find the writer. Heavy: kernel-mode debug-register churn. |
| `ROGUESQ_HWBP_ADDR` | `0x3CBC4` | (companion to `ROGUESQ_HWBP`) | Hex address (offset into RDRAM) to watch. Set both to enable a custom watchpoint, e.g. `ROGUESQ_HWBP=1 ROGUESQ_HWBP_ADDR=0x4B7848`. |
| `ROGUESQ_LOG_FRAME_RATE` | off | `[rate] swap=N/s sample=M/s fb=...` | Once-per-second telemetry of `osViSwapBuffer` and VI-tick rates. Useful when investigating producer/consumer imbalance during cinematic. |
| `ROGUESQ_LOG_PIPELINE` | off | `[pipe-1]`, `[pipe-2]`, `[pipe-3]` stage counters in RT64 framebuffer renderer | Per-stage TEXRECT pipeline counters (push → GPU draw). Used to verify the pipeline isn't dropping cinematic content between submission and rasterization. |
| `ROGUESQ_LOG_PROBES` | off | `[wp@*]` watchpoint probes in `funcs_*.c` | Per-call value-change watchpoint probes inserted during the iter-810 freeze investigation. Volume is naturally bounded (only fire on transitions) but useful to gate if you want a quieter run. Same flag is checked from `src/main/debug_logs.h`. |
| `ROGUESQ_LOG_RT64_ALLOC` | off | `[rt64-alloc] interpolatedColorTargets/nativeSwappedRAM/rdramData/BufferPair/RT::setupColor/setupDepth` | RT64 allocation hotspots — emit `[rt64-alloc]` log lines whenever an allocator commits ≥ 1 MB. Used to find allocation spikes. Lives in 5 sites across `lib/rt64/src/{hle,render}/`. |
| `ROGUESQ_LOG_TEXBYTES` | off | `[trace] tex bytes ...` | First 32 bytes of texture data at SETTIMG addresses, for diagnosing wrong/missing assets. |
| `ROGUESQ_LOG_DL_SYNC` | off | `[dl-sync-probe] task=#N syncs=… e9_a=… e9_b=… lin_e9=… fs_addr=…` | Guest F3D walk vs post-LLE runner `syncs` (RDP hist `0x29`). **e9_a** = B5=ENDDL (false-neg on complex); **e9_b** = B5=no-op (authoritative presence); **lin_e9** = linear scan; **fs_b0** = byte at last FULL_SYNC submit. **s581:** late hangar control GREEN via e9_b (30/30). Pass via `GAME_EXTRA_ENV`. Rate-limited. |
| `ROGUESQ_LOG_RDP_FULLSYNC` | off | `[rdp-fullsync] n=… kind=head\|single addr=… b0=… size=…` | Per-submit RDP FULL_SYNC (op family `b0&0x3F==0x29`). **head** = first byte of a submit range (= runner `syncs` hist); **single** = 8-byte submit that also refreshes `g_last_fullsync_addr`. Not in `LOG_ALL`. Use with `LOG_DL_SYNC` for H-sync4 (item -352): cutscene dual-DL had sticky `fs_addr=0x76DF60` / `fs_b0=E9` with `e9_b=0`. Pass via `GAME_EXTRA_ENV`. Logs every submit once `cum_fs>=4000`. |
| `ROGUESQ_LOG_E9_UNIFIED` | off | `[e9-unified] task=… guest_dl=… aligned=… fetched=… handler=… state_fullsync=…` | One task-identity row joining the inline-aware aligned E9 count with authoritative fetch, handler, and State/fullSync counts. Also enabled by `ROGUESQ_LOG_RDP_ADVANCE` or `ROGUESQ_LOG_ALL`. |
| `ROGUESQ_LOG_FS_SLOT` | off | `[fs-slot] event=arm\|write\|heartbeat\|submit\|task_end\|task_delta\|intertask_delta\|slot_op_change` | H-sync4 / H7 writer (item -353/-355): poll 16 B at fixed FULL_SYNC side-slot (default phys `0x76DF60`, override `ROGUESQ_FS_SLOT_ADDR`); LLE pre/post task_delta (src=rsp_lle) vs intertask_delta (src=outside_lle); write lines stamp `lle_depth`/`lle_task`/`guest_pc`/`dpc_*`; dpc_bridge slot submits + slot_op_change on E7/E9 head flips. Pass via `GAME_EXTRA_ENV`. |
| `ROGUESQ_LOG_SLOT_DISPATCH` | off | `[slot-dispatch] kind=entry\|pre\|post` | s857 behavior-neutral `slotDispatcherIter` input/update trace; phase-gated with `ROGUESQ_SLOT_DISPATCH_PHASE_MIN` (uses the host VI phase ordinal), bounded to 512 entry and 256 pre/post rows. |
| `ROGUESQ_LOG_SLOT_LINK` | off | `[slot-link]` | s860 behavior-neutral `getNextSlotNpcTypeId` selector/table/link/context/type trace; phase-gated with `ROGUESQ_SLOT_LINK_PHASE_MIN`, bounded to 4096 rows per host phase. |
| `ROGUESQ_LOG_INLINE_ADVANCE` | off | `[inline-advance]`, `[inline-route]`, `[inline-overlay]`, `[inline-advance-summary]` | Factor 5 live inline-data audit: logs DMA table words, `r17` advances, and the TriGen indirect route/overlay selector. TriGen routes have their own phase-scoped 96-row budget; other detail rows share a separate 96-row budget. |
| `ROGUESQ_LOG_BEGINFRAME_S0_GUARD` | off | `[beginframe-s0-guard] site=0x8000AFA0 n=… bad_s0=… ra=…` | Item -338 / -365: range-check on stack-slot node ptr (`$s0`/`ctx->r16`) before `lw $v0,0x8($s0)` in `beginFrameDLChunk`. Fire = same-run positive control for the guard. Pass via `GAME_EXTRA_ENV`. |
| `ROGUESQ_LOG_M4_Y8000` | on | `[m4-y8000]` | s1856: phase-gated L_17F0 / L_112C census of vertex `+0x1A == 0x8000` vs flushed `0xD60` YL/YM/YH. Default on; set `0` to silence. Pair with `ROGUESQ_M4_Y8000_WIDTH` (default 640). Width 512 also requires hangar origin `0x006ab400` / `0x006ab800` so attract 512 is not counted. |

### Cinematic-loop checkpoints

These were added during the iter-810 freeze investigation and live in
`E:/Projects/N64Recomp/RecompiledFuncs/funcs_27.c`. They get clobbered on
N64Recomp regeneration — see [audit-changes.md](audit-changes.md) for the
preservation strategy.

| Env Var | Default | Tags Enabled | When To Enable |
|---|---|---|---|
| `ROGUESQ_LOG_CINE_CP` | off | `[cp] iter=N cpNN-...` | Per-call-site checkpoints inside `func_800A5D80`'s cinematic loop body. The last `[cp]` line before silence identifies which call hangs. ~30 sites. |
| `ROGUESQ_LOG_CINE_CP_FROM` | `800` | (companion to `ROGUESQ_LOG_CINE_CP`) | Iter at which to start verbose logging. Each site prints once before the cutoff for sanity, then prints every iter from this point on. Set lower for full traces, higher to focus on the freeze window. |

## Workaround / experiment env vars (separate from logging)

These control *behavior*, not just logging. Listed here for convenience —
they're orthogonal to the log gates above but commonly co-used.

| Env Var | Default | Effect |
|---|---|---|
| `ROGUESQ_SHADE_FIX` | `10` | Per-vertex SHADE attribute transform. `0` = disabled. `4-10` = various transforms (see [rt64_gbi_rdp.cpp:563-707](../../../Projects/RogueSquadron64Recomp/lib/rt64/src/gbi/rt64_gbi_rdp.cpp#L563-L707)). Mode 10 broadcasts SHADE = 1.0 (TEXEL passthrough) and is the current default that lets the cinematic render. |
| `ROGUESQ_PARTICLE_FIX` | on | Surgically rewrites alpha-D in mux `0xFC11FE23` (cinematic-particle TEXRECT setup variant) from ZERO to TEXEL0_ALPHA. See [rt64_rdp.cpp:360+](../../../Projects/RogueSquadron64Recomp/lib/rt64/src/hle/rt64_rdp.cpp#L360). Found redundant in practice — actual rendering uses a different mux. |
| `ROGUESQ_PARTICLE_DEBUG` | off | Forces alpha-D = ONE (opaque blocks) in mux `0xFC11FE23`. High-visibility diagnostic — particle rectangles render as solid colored squares. Found ineffective (mux mismatch). |
| `ROGUESQ_TEXRECT_ALPHA_FIX` | on | Rewrites alpha-A from SHADE → ONE in mux `0xFC119623` (the actual cinematic-particle render mux). Confirmed firing 10000+ times during cinematic. Whether visually effective is still being investigated. |
| `ROGUESQ_VI_FOLLOW_DRAW` | `1` | VI-presentation override picker. `0` = original VI/0x66A000 lookup. `1` (default) = override only when VI's fb is stale (not in recently-written set). `2` = aggressive — always pick most-recent color fb. `3` = freshness mode — pick whichever Framebuffer in the manager has the highest `lastWriteTimestamp`, decoupled from `colorImageAddressVector` (use when modes 1/2 don't keep VI on a fresh fb because the workload's pairs aren't `interpolationCandidate` and so the vector stays empty). Workaround for the cinematic buffer-arbiter bug. |
| `ROGUESQ_LOG_VI_FRESH` | off | Diagnostic. At each VI present, log the chosen fb's `lastWriteTimestamp` vs the freshest color fb in the manager (positive `lag` = VI is presenting a stale fb while a newer one exists). Also logs `colorImageAddressVector` size to confirm whether VI-follow modes 1/2 even have candidates to pick. Throttled to first 20 + every 60th. |
| `ROGUESQ_PRIM_FF` | off | Force PRIM_COLOR RGB to (FF,FF,FF) keeping alpha. Tests whether the warm off-white tint accounts for "less saturated reds" gap from ideal. |
| `ROGUESQ_NO_SYNTH_FULLSYNC` | off | Disables the synthetic-fullsync injection in dpc_bridge.cpp. |
| `ROGUESQ_FS_PIPE_INJECT` | off | Product response to H-sync4 sticky-cell FULL_SYNC starvation (items -356/-357). `1` = when a size-8 submit hits **both** `g_last_fullsync_addr` **and** `ROGUESQ_FS_SLOT_ADDR` (default `0x76DF60`) and the cell is no longer E9, queue a synthetic FULL_SYNC from host scratch phys `0x7FFF80` and **drop** the size-8 (E7 PIPE + residual F3/FD/F5; s588 H9d drop-return). Forwarding residual correlated with UJ 0xA8A9 (s588 r2). `2` = last_fs-only (H8c flood). Logs `[fs-pipe-inject]` with `b0=`. Hangar mode-1: no inject (hangar FS at `0x7778C8`). Default OFF until post-dual empty characterized. |
| `ROGUESQ_SHADE_FALLOFF` / `ROGUESQ_SHADE_AMBIENT` / `ROGUESQ_SHADE_SLOPE` | various | Tuning knobs for SHADE_FIX modes 8-9 (env-mapped magnitude). |
| `ROGUESQ_FILLCOLOR_DEBUG` | off | Forces every FILL_COLOR write to a fixed value. `1` = red (`0xF801F801`, two 5551 reds). Pass an arbitrary 32-bit hex (`0xAABBCCDD`) for any color. Reveals where FILL-mode draws land — the cinematic uses FILL-mode for its background, so setting red shows the whole cutscene bg as red with geometry on top. Doubles as a useful sanity check that the rasterizer reaches the displayed fb. |
| `ROGUESQ_PARTICLE_VISIBLE_DEBUG` | off | Diagnostic. Rewrites the cinematic-pass mux family (low-half `0xFC127FFF` or `0xFC11FE23`) so it outputs PRIM color at alpha=1.0 unconditionally. If sprites turn into PRIM-colored blocks, the pipeline reaches the displayed fb; if no change, sprites land in a non-displayed fb or aren't being rasterized. |
| `ROGUESQ_VI_FORCE_FB` | off | Diagnostic. Forces VI to present a specific RDRAM fb regardless of VI_ORIGIN. Use as `ROGUESQ_VI_FORCE_FB=0x80695C00`. Bypasses the cinematic buffer-arbiter bug to test "explosion sprites land in fb X but VI never shows X" hypotheses. Strips upper-half virtual prefix automatically. |
| `ROGUESQ_NO_FULLSCREEN_FILLRECT` | off | Diagnostic. Suppresses full-screen FillRect (rect covers entire color target). Modes: `1`/`all` = skip every full-screen FillRect (causes Memory Pak attribution to ghost-trail since clears are needed there); `cinematic` = skip only when target is cinematic color fb 0x0062B800 / 0x00695C00 (preserves attribution clears, exposes cinematic content). Tests sub-frame-overwrite hypothesis for cinematic explosions. Partial FillRects always execute. |
| `ROGUESQ_VI_FOLLOW_INCLUDE_FILLS` | off | Restores legacy VI-follow behavior. By default, fillOnly fbpairs are excluded from the VI-follow candidate list (so VI doesn't pick a just-cleared cinematic buffer when the actual content is in a sprite-rendering fbpair earlier in the workload). Set to `1` to include fillOnly pairs again. |
| `ROGUESQ_FILLRECT_DEBUG` | off | Forces every FillRect to a fixed magenta. Visual sanity check: any cinematic frame with FillRect activity glows magenta. Lives in `rt64_framebuffer_renderer.cpp`. |
| `ROGUESQ_DISABLE_Z_CMP` | off | Forces Z_CMP and Z_UPD bits OFF in `setOtherModeL`. Diagnostic for "is geometry being z-killed" hypotheses. |
| `ROGUESQ_FULL_DUMP` | off | When a crash dump is written (SEH handler, SIGABRT, F12), `=1` produces a full-memory minidump (~5 GB) instead of the default lite dump. Use only when you need RDRAM contents for postmortem. |
| `ROGUESQ_SUPPRESS_OOB_CIMG` | off | When set, drops Factor 5 ucode emissions of bogus SET_COLOR_IMAGE commands at HIGH (≥ 0x800000) and LOW (< 0x100000) addresses before they reach RT64. Reduces the iter-810 memory spike but causes a visual regression — the 3D Factor 5 logo no longer renders, since some legitimate Factor 5 lowmem CIMGs are dropped along with the garbage. |
| `ROGUESQ_SWAP_SHADE` | off | **Legacy alias** for `ROGUESQ_SHADE_FIX=1`. Prefer setting `SHADE_FIX` directly. Kept because old logs reference it. |

## How to add a new debug trace

1. Pick the right category from the table above (or invent a new one and add it here).
2. At the call site, gate the `fprintf(stderr, ...)` behind a static-cached env-var check:

   **C++ (lambda + static)**
   ```cpp
   static const bool log_x = []{
       const char *a = std::getenv("ROGUESQ_LOG_ALL");
       if (a && *a && *a != '0') return true;
       const char *e = std::getenv("ROGUESQ_LOG_DPC");  // your category
       return e && *e && *e != '0';
   }();
   if (log_x) {
       fprintf(stderr, "[your-tag] ...\n");
       fflush(stderr);
   }
   ```

   **C (manual init flag)**
   ```c
   static int log_x_init = 0, log_x = 0;
   if (!log_x_init) {
       const char *a = getenv("ROGUESQ_LOG_ALL");
       const char *e = getenv("ROGUESQ_LOG_DPC");
       log_x = ((a && *a && *a != '0') || (e && *e && *e != '0')) ? 1 : 0;
       log_x_init = 1;
   }
   if (log_x) { fprintf(stderr, "[your-tag] ...\n"); fflush(stderr); }
   ```

3. Add a comment above the gate stating *what* the trace shows and *when* to enable it.
4. If you introduce a new env-var category (rare — prefer reusing existing ones), update both this file and `src/main/debug_logs.h`.

## What is NOT gated (intentional)

These always print regardless of env vars — don't gate them:

- **`[CRASH]`, `[ABORT]`** — crash handler / SIGABRT path. Always need these for postmortem.
- **`[CRT_REPORT]`, `[INVALID_PARAM]`** — CRT debug-report hooks; rare and serious.
- **`[Audio] SDL_OpenAudioDevice failed`, `[ROM] Imported`, `[F12] manual minidump requested`** — one-shot user-facing events.
- **`[exp mode=N]`, `[particle-fix]`, `[texrect-alpha-fix]`, `[vi-follow-draw mode=N]`** — workaround/experiment confirmation messages, throttled to first 3-5 hits. Telemetry that an opt-in workaround actually fired.
- **`[RT64] setCurrentThreadName threw`** — exception that the gated success path was supposed to avoid; you want to see this.
| `ROGUESQ_LOG_FL_ZERO_WATCH` | off | `[fl-zero-poll]` / `[fl-hdr-write]` / `[fl-zero-watch]` | s639 freelist zero-node writer audit. Host soft-watch phys 0x1F3CC0 (override `ROGUESQ_FL_ZERO_ADDR`); free/split header logs; E8 exit scan for size==0 nodes. |
