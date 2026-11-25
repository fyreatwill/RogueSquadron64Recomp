# RS64 recomp — autonomous iteration

You are continuing the Rogue Squadron 64 static-recomp investigation. You have
no memory of previous iterations; the docs are your memory.

## Read first, in this order — nothing else
1. docs/CURRENT-TRUTH.md   (state, config, next steps, superseded conclusions)
2. scratch/agent/NEXT.md   (the single next work unit, if it exists)
3. scratch/agent/SOAK-RESULTS.md  (tail -20 — verdicts from queued soaks the
   loop ran between iterations; fold new ones into the ledger like any run)
Do NOT read PORTING-STATE.md except to grep for a specific fact; it is 290+
sessions long and dozens of its conclusions are superseded.

## Step 0 — maintenance check (before choosing a work unit)
Run: `wc -c < docs/CURRENT-TRUTH.md`. If it prints more than 60000, THIS
iteration is a MAINTENANCE iteration: compact docs/CURRENT-TRUTH.md toward its
~35 KB cap — migrate durable material to docs/PROJECT-OVERVIEW.md, prune/merge
superseded and closed Next-steps items, renumber the backlog into ONE monotonic
sequence (it has had three colliding "-1/-2/…" sequences), and refresh the
stale "as of session N" headline. Git history preserves everything you delete.
A net shrink of >=200 lines or >=15000 bytes counts as ADVANCED (the Stop gate knows this). Do
NOT run experiments in a maintenance iteration.

## Strategic priority (user directives: 2026-08-04 items 1-3, 2026-08-15 item 4)
When choosing the work unit, this order overrides Next-steps ordering:
1. Maintenance, when Step 0 triggers it.
2. **M5 audio de-stubbing.** First a design doc (docs/M5-AUDIO-PLAN.md):
   survey every audio stub/trap/gate currently in force, then plan an
   incremental de-stubbing sequence with a validation soak per step. Then
   execute it step by step. Rationale: several recurring crash families
   (waitForAnyAudioSlot boot deaths, voice-array corruption, slot reaping,
   MusyX DMA) are plausibly artifacts of the audio-disabled degenerate paths —
   de-stubbing may dissolve whole classes now being guarded one deref at a time.
3. M3 crash work — ONLY as systematic idiom-class audits (the s282–s288
   `-0x25A4` model: grep-enumerate a whole idiom class, classify every site,
   guard or prove dead, close the class). No reactive single-crash chases.
   Wait-for-recurrence breadcrumbs are passive: enqueue their soaks (see Soak
   queue below) and move on.
3b. **M6 play-through endurance (user directive 2026-10-17).** When items 1-3 are
   exhausted (the current offline indirect-site audit gets at most 2 iterations), do THIS
   instead of writing BLOCKED.md "no discriminator remains". Goal: the first mission plays
   without a crash, hang or frozen frame. Method: queue soaks on the title->mission route
   (s5378 reached mission origin 0x00690400 without the hangar; the hangar route is flaky
   3/5) with a keyed mission hold of >=10 min, >=3 runs, logging every CRASH/abort and every
   stall (VI origin unchanged >30 s). Each DISTINCT failure: capture a backtrace (lldb or an
   ASan arm in a separate build dir), name the writer, and fix the root cause - no more
   guard-one-deref patches. A real MIPS toolchain now exists (mips64-elf-gcc 14.2 +
   binutils; clang kept as mips64-elf-clang), so PatchesLib C patches are allowed; qualify
   them with the same two-arm discipline. Secondary: the ~1/7 title-boot plume SIGSEGV
   (si_addr=0x58) - loop title boots under lldb until it recurs, then read the real
   backtrace instead of waiting on breadcrumbs. Soak hygiene: the macOS screen must be
   unlocked (check CGSSessionScreenIsLocked before key-driven soaks) or nohangar results
   are meaningless. This is engineering, not churn: every iteration must end with either a
   new crash/stall datum or a code/patch change.
3c. **Standing goal ladder (user directive 2026-10-19).** The backlog never runs
   dry. When Next steps and items 1-3b offer nothing applicable, take the FIRST rung
   below that is not closed, write NEXT.md for it, and continue. "Backlog exhausted",
   "all threads parked", "no discriminator remains" and "need a human-chosen target"
   are NOT blocks — 15+ of the 34 blocks between s5031 and s5604 were exactly this,
   and every one was re-scoped by the unblock tier at the cost of two sessions.
   - G1 **Mission coverage (redefined by the owner 2026-10-22).** A mission is
     VERIFIED when, reached through the forced level-select route
     (ROGUESQ_FORCE_UNLOCK + ROGUESQ_FORCE_SAVE_MISSION + ROGUESQ_NO_SAVE_WRITE,
     s5705-s5720 recipes): (a) it reaches flight, (b) holds >=300 s with 0 crash /
     0 VI stall, (c) a framebuffer capture shows terrain, craft and HUD (compare a
     retail oracle frame when one is obtainable), and (d) its objective logic
     responds: forced hits (the s5841 TELE-style lever) move that level's objective
     counter / end gate. Levels 1-9 have (a)+(b) only (s5708-s5720; lvl7 copyToRAM
     fixed s5712). Order: find the real mission count from the level table, sweep
     every remaining level for (a)+(b), then (c)+(d) for all; every distinct crash,
     stall, softlock or broken render is a datum to root-cause.
     OUT OF SCOPE — owner playtest covers it: making the autopilot aim, steer, hit
     or win (bolt tracking, hit spheres, yaw control laws, ROGUESQ_AIM tuning). The
     s5841-s5930 aim thread is CLOSED as harness work: a blind scripted input
     missing targets is expected, and forced hits already show the game's damage
     -> objective path works. If NEXT.md proposes aim/steer/bolt work, discard it
     and take the next G1 coverage item. Mission-to-mission progression after a
     real win is also the owner's playtest; do not poke wins to test it.
     **(d) PARKED by owner 2026-10-31.** Objective-counter qualification (s6640-s6686:
     per-level counter contracts, spawn paths, lvl7 proximity tanks) is completability
     work and belongs to the owner's playtest. Do not continue it; (a)-(c) stand as done.
   - G1b **Frame pacing (owner report 2026-10-23).** Take this once the G1 per-level
     (a)+(b) sweep is done. Owner watching mission play: ~70% of missions run
     flawlessly, but the whole game intermittently slows as if "buffering" — sometimes
     with many assets on screen, sometimes on plain landscape. Existing logs carry no
     wall-clock time, so the slowdown has never been measured. Competing hypotheses:
     H-host (only 5 P-cores on this Mac; REAPER/Chrome/WindowServer/agent work push
     game threads onto E-cores — fits slowdowns on bare landscape), H-rsp (LLE F5 gfx
     ucode CPU cost per frame rises with scene density — fits busy scenes), H-shader
     (RT64 pipeline/shader creation on first use of new materials), H-log (diagnostic
     logging bursts: 268 MB in one 9-min soak, frames with >1.6 MB). Discriminator,
     ONE instrument / ONE build: per-VI wall-clock frame time, and per frame the gfx
     RSP task host-ms, RT64 present/GPU wait, pipeline-creation count, log bytes, and
     the CPU cluster (P/E) the guest and RSP threads ran on (sample thread CPU or
     QoS). Then same level/recipe in arms: normal logging vs logging off, and quiet
     host vs busy host. Whichever term co-varies with slow frames selects the cause;
     fix the root cause (e.g. thread QoS, async pipeline compile, cheaper logging),
     not the symptom.
   - G1c **Extended draw distance (owner request 2026-10-23).** Take after G1b, and reuse
     its per-frame timing instrument: every gain here costs frame time. Owner sees terrain
     resolve gradually out of the haze in flight and wants more of the landscape drawn than
     the N64 could. RT64 can only draw what the game submits, so the limit lives in game
     code. First find WHICH limit applies, one discriminator per lever, measured as distant
     terrain pixel fraction in a fixed-camera framebuffer (level 1 is the positive control):
     L-fade (a distance fade/haze baked into vertex shade or a combiner blend toward sky
     colour: note PORTING-STATE "Fog contributes nothing" was an early pre-flight scene,
     re-test with ROGUESQ_FORCE_FOG in flight), L-radius (the terrain patch/tile
     visibility radius or far-clip constant in the terrain submit path), L-lod (the
     detail index at 0x80137CE4 that selects per-template LOD slots and
     selectMeshLodAndSubmitForRender / setObjectDetailLevel), L-budget (display-list,
     vertex or streamed-tile buffer caps that would overflow once more is drawn).
     Then expose the winner as an opt-in setting (env ROGUESQ_DRAW_DISTANCE=<multiplier>,
     default 1.0 = retail), raise it in steps (1.5x, 2x, 3x) and record per step: distant
     terrain visible, pop-in, frame time, crashes over a 300 s hold. Done when 2x holds
     300 s on levels 1, 5 and 10 with 0 crashes and no frame-time regression beyond the
     G1b baseline; ask the owner to judge the look. Never change the default away from
     retail without the owner's say.
     **Phase 2 (owner 2026-10-24): push draw distance as far as it will go.** Take right
     after G3b closes. Owner: "everything else seems to be working great"; this is the
     priority after the spike lines. Start from the s6074 state (DRAW_DISTANCE=2 +
     auto-far: tri x2.3, terrain fraction 0.030->0.074, VI 60/s, clean) and find the
     next binding limit at each step up (3x, 4x, beyond the 4.0 clamp if useful):
     guest heap (px3+ exhausts the 8 MB heap, s6062). The 8 MB is NOT a hard limit here:
     librecomp already maps 512 MB read/write behind rdram (addresses.hpp mem_size;
     KSEG0 0x80000000-0x9FFFFFFF), and recomp.cpp:560 just tells the game 8 MB via
     osMemSize. Owner approves expanding it. Cheapest route first: carve the terrain
     pools (or a second rs_malloc arena) from 0x80800000+ rather than raising osMemSize
     globally (the game may branch on 4/8 MB modes). Watch the RSP/RDP side: display-list
     segment addresses are 24-bit, so anything the gfx ucode reads must sit below 16 MB
     physical (0x81000000) unless the ucode/RT64 address masking is widened too, the 64-wide bitmap stride
     and terrain dims (s6035), the ucode iteration cap (ROGUESQ_UCODE_CAP, s6070), RSP
     host cost per frame (G1b instrument; VI must stay 60/s), and distant pop-in.
     Measure every step with the fixed-camera terrain-fraction scorer plus a framebuffer
     contact sheet the owner can eyeball (send per step, same camera, dd1 vs dd-max).
     Bundle the winning combination behind the single ROGUESQ_DRAW_DISTANCE knob (it
     should set far/pool/cap itself) so the owner can flip one setting. Default stays
     retail until the owner chooses.
   - G1d **Widescreen / ultrawide (owner request 2026-10-24).** Take after G1c phase 2.
     Owner plays on a 21:9 ultrawide monitor and a 65" 16:9 TV; today the picture is 4:3
     with black bars. Goal: the 3D view fills whatever aspect the window has (4:3, 16:9,
     21:9), with the extra width drawn (not stretched), the HUD anchored to the real
     screen edges, and menus/hangar still correct. Note the port runs the F5 gfx ucode
     LLE, so RT64 sees only screen-space RDP triangles: its HLE "Expand" aspect mode and
     matrix-based tricks cannot work by themselves. Expect to patch the game side: the
     projection matrix / FOV (the 0x130C50 FOV scalar from s6024 is a lead), viewport and
     scissor, the framebuffer width the game renders into, and the HUD x positions. Pairs
     naturally with G1c: wider view needs the wider terrain footprint. Check the internal
     resolution also follows the window (ROGUESQ_RESMULT exists; a 4K TV should get a
     sharp image). Opt-in setting first (ROGUESQ_ASPECT=auto|4:3|16:9|21:9), owner
     judges via screenshots at 16:9 and 21:9, then the owner decides the default.
   - G1e **Higher frame rate (owner request 2026-10-24).** Take after G1d. VI is 60/s but
     the game probably produces a new frame only every 2-3 VIs. First measure the real
     game frame rate per level (distinct framebuffers per second, G1b instrument). Then
     the levers, cheapest and most faithful first: (1) the game's own frame-pacing/VI
     retrace divisor, if the sim uses a delta time and tolerates a 60 Hz update (verify
     physics, AI, timers, audio sync and mission scripts are not tied to frame count:
     compare mission timer and craft speed per real second at both rates); (2) if the
     sim is frame-locked, run render-only extra frames or decouple sim from render;
     (3) RT64 frame interpolation needs matrix data the LLE path does not provide, so
     only consider it if a way to feed it exists. Opt-in setting, then owner judges feel.
   - G3c **Owner visual report 2026-10-26: take next** (finish the NEXT.md unit in flight,
     then switch; dd3 work resumes after). Owner watched many runs (s6091-s6264 mixed
     dd3/dd4, ASPECT, FPS60) and reports three defects. Each needs: an arm table that
     says which setting(s) produce it (retail control, each opt-in alone, combos), a
     discriminating measurement, a root-cause fix, and owner-viewable before/after frames.
     (a) **Jagged far-terrain edge.** Where fog/haze normally hides the horizon, the edge
     of the drawn terrain is blocky/stair-stepped. Leads: the terrain cell footprint's
     grid-aligned boundary exposed by auto-far at dd>1 (haze/fog distance not scaled with
     the draw distance), or the G1d frustum x-widening (s6144) exposing the side edge.
     Fix candidates: scale the game's distance haze/fog start/end with the dd/aspect
     factor, or fade the outermost ring of cells, so the edge falls inside the haze as in
     retail. Check retail (no opt-ins) first: if retail shows no edge, the opt-ins own it.
     (b) **Knife spikes still visible.** G3b (s6085) called the on-screen wedges
     "retail-identical" from ucode reasoning only; that is single-source and unverified
     (no retail/independent RSP reference was run). Reopen: H-rsp-emu (our LLE RSP
     emulation of the F5 clip path differs from hardware: check VRCP/VRCPH/VRCPL,
     VMULF/VMACF rounding/clamp, VCH/VCL/VCR clip flags against a reference RSP such as
     ares/cen64/parallel-rsp on the exact inputs that produced a logged wedge) vs
     H-retail (run the same level in an accurate emulator and look for wedges). If no
     reference shows them, fix the emulation. If retail truly has them, ask the owner
     about making ROGUESQ_CULL_SPIKE default-on.
     **Owner 2026-10-31: ROGUESQ_CULL_SPIKE is now DEFAULT ON** (src/rsp/dpc_bridge.cpp;
     =0 restores the retail wedges). The cull previously ran only under ROGUESQ_LOG_SPIKE=1,
     so CULL_SPIKE=1 alone was a no-op; it is now independent of logging.
     (c) **Screen shake while turning.** Slight shaking of the whole view whenever the
     ship turns. Leads: H-fps60 (FPS60 camera follow/smoothing is frame-count-based or
     updated on a different cadence from the craft, so camera vs craft alternates),
     H-pacing (presented frames alternate uneven VI spacing, judder), H-aspect (wide
     camera/viewport scale applied on alternate frames), H-retail (retail has it).
     Measure per presented frame: camera yaw/position and craft yaw from guest RAM, plus
     present timestamp, during a scripted steady turn; compute the second difference
     (jerk) of camera yaw per real second. Arms: retail, FPS60, ASPECT, both. Shake =
     sign-alternating jerk that retail lacks.
   - G1f **Window fills the owner's display (owner 2026-10-31): take NOW.** Owner plays on a
     21:9 ultrawide and a 65" 16:9 TV. Today the OS window opens 640x480 (main.cpp
     SDL_CreateWindow, resizable) so ROGUESQ_ASPECT=16:9/21:9 letterboxes inside a 4:3
     window. Goals: (1) the window opens at the chosen aspect (e.g. 21:9 -> 1680x720-class,
     sized to fit the current display); (2) a fullscreen toggle (borderless desktop
     fullscreen, Cmd+Ctrl+F / F11 / Alt+Enter) and ROGUESQ_FULLSCREEN=1 to start in it;
     (3) ROGUESQ_ASPECT=auto derives the game aspect from the window/display (clamped to the
     verified widths, s6142 w<=1024), so fullscreen on either screen fills it with no bars,
     including after a resize or moving between displays if feasible; (4) internal
     resolution follows the window so a 4K TV is sharp. Verify with window screenshots at
     4:3, 16:9 and 21:9 window sizes and a fullscreen capture on the built-in display;
     update docs/OWNER-OPT-INS.md with the one-line command for each screen. Defaults stay
     4:3 retail unless the owner says otherwise.
   - G6 **Owner request 2026-11-18: three features borrowed from upstream, take NOW in this order, ahead of
     NEXT.md and any G5 item that is only waiting for the owner's look.** Upstream (MikeSemicolonD) main is
     fetched as `origin/main`; read it with `git show origin/main:<path>`, never merge or cherry-pick it (it
     is HLE + toml hooks, we are LLE + fixup scripts; see docs/UPSTREAM-COMPARISON-2026-11.md). Every change keeps the owner's current experience as the
     default unless stated, and needs a same-run positive control like any other result.
     G6a **Rumble.** Ours is a stub: `static void set_rumble(int, bool) {}` (src/main/main.cpp ~13219), so
     the game's Rumble Pak motor pulses go nowhere. Port the HOST side of upstream src/input/rumble.cpp
     (446 lines) + rumble.h: a ~60 Hz rumble thread that averages the game's on/off motor pulses into a
     duty cycle and drives SDL_GameControllerRumble (fallbacks SDL_JoystickRumble / SDL_Haptic). Lesson
     from the owner's Starship port (memory): the game strobes the motor like PWM and zero/short-duration
     SDL rumble calls do nothing on DualShock 4 over macOS, so stretch pulses (duty averaging, >=100 ms
     SDL durations) rather than mirroring each edge. First check the game actually sees a Rumble Pak on
     port 0 by default (s7516 ROGUESQ_PAK_SHAPE_CTL=1 is the existing control that reports one); if it
     does not, report one by default so the game sends pulses, without breaking saves (EEPROM, not a
     Controller Pak). Skip upstream's damage-scaling / death-spiral / lightbar layers unless they need
     no guest hooks. Default ON with `ROGUESQ_RUMBLE=0` to turn it off and `ROGUESQ_RUMBLE_SCALE` (0..2).
     Proof: log motor pulses and SDL rumble calls while firing / taking hits on a forced level, with a
     same-run RUMBLE=0 control. Closes on the owner feeling it on a PS4/PS5 pad; add it to OWNER-OPT-INS.
     G6b **Control rebinding tool for OUR scheme.** The owner likes the current controls and does NOT want
     upstream's defaults. Build a way to customise our own mapping: (1) move today's hard-coded pad and
     keyboard map in get_n64_input (main.cpp ~12330-12400, incl. R2 -> C-Left, L3 -> C-Right, left trigger
     -> Z, WASD/ZXC/QE/IJKL/arrows/Enter) into a table whose built-in defaults are EXACTLY today's mapping
     (byte-identical N64 button output for every input with no config file present: prove it with a
     same-run table-vs-old comparison); (2) load overrides from a JSON file in the data folder (e.g.
     `controls.json`, missing = defaults), allowing several bindings per N64 button and the analog
     triggers/stick as sources; (3) an in-game rebinding panel (RT64 already has an ImGui overlay on F1;
     add a Controls panel, e.g. F6: pick an N64 button, press the pad/key to bind, save, reset to
     defaults). Upstream src/input/input_bindings.cpp (1314 lines) and its F6 panel are a reference for
     format and UI only. Do not change any default binding. Document it in README Controls + OWNER-OPT-INS.
     G6c **Far-object stand-ins (owner wants this; biggest job).** Upstream src/game/static_standins.cpp
     (428 lines) draws stand-in models for buildings/turrets/ground units the game has not spawned yet, so
     they stop popping in at higher draw distance (our open issue, G5b/OWNER-OPT-INS). It is renderer-
     independent: it adds models to the game's own visibility bucket, driven by upstream toml hooks on
     runInMissionFrame before 0x800FAC68 and selectMeshLod 0x80058264 (`git show origin/main:rogue_squadron.toml`,
     search "stand-ins"; also src/game/toml_hooks.c and hook_helpers.cpp for what the hook bodies call).
     We have no toml hooks: re-express each hook as a fixup/apply script registered in RS64_REPLAY (docs/
     REGEN-VERIFY.md) so it survives regen. Write a short design doc first (docs/G6C-STANDINS-PLAN.md:
     which guest structures it reads, which addresses differ between upstream's build and ours, and how
     each hook maps onto our generated functions), then implement in steps. Opt-in first
     (`ROGUESQ_STANDINS=1`), active only at draw distance > 1; at dd1 retail must be untouched. Proof:
     same-run on/off frames at dd2 and dd4 on 2+ levels showing objects visible early instead of popping,
     plus crash-free 300 s holds on all 19 levels with it on. Then an owner sheet; closes on the owner's
     look, after which the owner decides whether it becomes the default at dd>1.
   - G5 **Owner playtest 2026-11-04: take NOW, in this order, ahead of NEXT.md and all G1e
     present/latency work.** Owner recipe for every arm unless stated: `ROGUESQ_FPS60=1
     ROGUESQ_DRAW_DISTANCE=4 (or 2) ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1`, no RDP_ASYNC or
     NODRAIN, no logging env, normal boot with the owner's real save read-only.
     G5a **Mission crash, twice on one mission (dd2, FPS60, 16:9).** SIGBUS, write fault, in
     initVec4TripletFromArgs+52, called from cinematicSplineWalkerNpcHandler+10956 via
     cutsceneActorNpcHandler, slotDispatcherIter, runInMissionFrame. Read from the binary:
     the caller does a0 = *(s2+0x18) + 0x28, a1..a3 = *(s2+4). Crash values: a0 = 0x26282B53,
     so *(s2+0x18) = 0x26282B2B (junk, not a guest pointer), a1 = 0x41900000 = 18.0f (sane).
     Last guest PC 0x80022160. **Mission: Liberation of Gerrard V, about half way through, both
     crashes (owner 2026-11-05).** This is LEVEL=4 (0-based: owner save current-mission byte = 4, and owner saw LEVEL=5 play Jade
     Moon), so earlier lvl5 holds were a different mission. A 300 s idle hold does not count, because the mission must be flown past its
     half-way scripted event to reach the actor; drive objectives or force that event. Hypotheses: H-overrun
     (dd/wide span or terrain writes land in the actor object, see s6880/s6883), H-spill (dd>1
     spill arena, s6858), H-fps60 (actor state ticks twice, object freed or reused),
     H-uninit (retail bug exposed). s6892 guard (tools/apply_s6892_walker_guard.py, default on) repairs the pointer
     and logs to build/rs64_s6892.log; positive control fired in a pre-mission scene only. In
     mission at dd2 the object sits in the spill arena (req 0xF14 -> 0x8082C870, LEVEL=4), which
     dd1 never uses, so H-spill leads. A 431 s idle LEVEL=4 hold did NOT reproduce it (0 fires).
     Discriminate with a write watch on s2+0x18 naming the
     writer. Close only on the owner's mission holding past the crash point, repeated.
     G5b **Terrain drops are NOT fixed: G3e is reopened.** Owner at 16:9 dd4: better but still
     significant; dd2 fewer but not gone; dd1 was clean. So the "0 in-flight drops" detector
     misses what the owner sees. First make an instrument that catches it (positive control:
     frames the owner would call a drop, from a screen recording or presented frames at this
     recipe, not from a test build), then find the cause. Measure where drops sit: inside the
     retail dd1 radius, or only in extended cells. That answer decides whether G5e can help.
     G5c **Freezes of a few seconds, then catches up like buffering.** Occasional, in flight.
     Log per-frame wall time in a long owner-recipe run and name what stalls. Candidates:
     shader or pipeline compile, present queue backlog, audio queue, save or file writes,
     the game thread catching up after a stall. Fixed when a long run has no gap over 250 ms
     outside loads, including the catch-up burst.
     G5d **Factor 5 logo in the startup animation is missing most of its frames.** Arm table:
     retail settings, FPS60 alone, 16:9 alone, ROGUESQ_WIDE_EARLY=0 (s6885 changed present
     logic for the >=1024-wide phase, and whether the logo uses it is unverified),
     ROGUESQ_CULL_SPIKE=0, and git bisect if none explain it. Compare the frame count with
     angrylion. Check the LucasArts logo and other startup cinematics for the same loss.
     G5e **Owner request: fog on the extended draw distance.** Fade or haze the extended
     terrain so its unreliable far pieces melt away rather than pop. Opt-in or tied to dd>1,
     dd1 stays retail. Use G3c(a)'s leads: scale the game's fog start and end with dd, or fade
     the outermost cell ring. Note PORTING-STATE "Fog contributes nothing" was an early scene.
     Fix G5b's cause first where it is fixable; fog is not a substitute for it. Owner sheet
     with before and after at dd2 and dd4 on 3 levels.
     G5f **Knife spikes still annoy the owner on stable frames.** G3c closed them as retail;
     the owner wants them gone anyway, so retail matching is not the bar here. CULL_SPIKE is
     already on and they still show at the owner recipe, so find which wedges escape it.
     Close on spike count at this recipe with no new missing geometry, plus an owner sheet.
     G5g **Owner request 2026-11-05: get rid of the fish-eye lens effect, after G5f.** Owner
     thinks it was tuned for the TVs of the time. Retail matching is not the bar, and "G3f closed
     as retail" does not close this. G3f found the hangar look comes from the craft-select camera:
     sideways slide, yaw lagging ~3 s, fixed 45 degree projection; it shows while scrolling ships
     and settles after a second or two. ROGUESQ_HANGAR_FOV=38 only narrows the lens and is
     opt-in. Fix the look itself, for example keep the camera aimed at the craft during the slide
     or correct the lens, and make it the default, with =0 restoring retail. Judge at 4:3, 16:9
     and 21:9 with FPS60 on, on frames taken mid-scroll. Then check whether the owner's recipe
     shows the same stretching elsewhere (flight edges, cutscenes, level select) and report it
     with an owner sheet before changing those views. Close on the owner's look.
     G5i **OWNER PRIORITY 2026-11-08, do this BEFORE anything else (ahead of the L15 21:9 crash, which the
     owner does not hit at 16:9): the G5g hangar fix fails after an aborted mission.** Owner playtest: the
     fish-eye was gone and looked good on first entry to SELECT YOUR CRAFT, but after aborting a mission and
     going back to the hangar to reload it, the fish-eye came back and was worse than retail. Reproduce
     it: hangar, start a mission, abort, back to the hangar, scroll ships, with ROGUESQ_G5G_CAM logging,
     against the first-entry scrolls in the same run. First suspects: rs64_s6907_aim's function statics
     (ps, act, fade, li, sc, t0, te, ds, lo) carrying stale scroll state over the hangar re-init; or the
     state byte 0x800CC3E4, cursor 0x800CD6E8, table 0x800CC404 or list 0x800CDA5C meaning something
     else after the re-entry, so the view aims at the wrong craft. Fix it so every hangar entry behaves
     like the first one. Same-run proof: first entry and re-entry off-axis numbers match, with an owner
     sheet of re-entry scroll frames. Closes on the owner's look.
     G5h **Owner request 2026-11-05: cutscenes are missing the most background, after G5g.** Owner
     playtest: of everything still dropping, cutscenes lose the most. Flight checks do not cover
     this; s6899 fixed one Gerrard V cutscene only. Go through the mission intro and outro
     cutscenes at dd2 and dd4, 16:9, against dd1 of the same frames, and count missing ground, water
     and background per cutscene. Find why (cutscene camera position and heading vs the terrain
     window is the first suspect). Fix what is ours, and give the owner a sheet of before and after
     frames. Closes on the owner's look.
   - G3e (REOPENED as G5b, 2026-11-04) **Terrain drops out for single frames (owner playtest 2026-11-02): take NOW, before
     any further retail-match sweep work.** Owner: "Landscape/terrain missing frames
     intermittently, but consistently." Owner's run was `ROGUESQ_FPS60=1
     ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1` (no ASPECT). Boring-first
     discriminator: the same recipe with ASYNC/NODRAIN off, then FPS60 off, then dd1, counting
     frames whose terrain pixel fraction collapses vs neighbours (phase-gated, same-run control).
     If ASYNC/NODRAIN is the cause, fix it or demote them from OWNER-OPT-INS until fixed. Close
     with a per-arm dropout count over >=120 s of flight.
     UPDATE owner 2026-11-02 (second run): drops are still frequent with ONLY `ROGUESQ_FPS60=1
     ROGUESQ_DRAW_DISTANCE=4` (no ASYNC/NODRAIN) -> those two are refuted as the sole cause.
     Next arms: FPS60 off at dd4, and dd1 with FPS60, to split H-dd (far terrain window / ucode
     cap / buffer limits at dd4) from H-fps60 (terrain stream or LOD state stepped at 60 Hz).
     UPDATE owner 2026-11-02 (third run): with NO draw-distance arg (dd1) there were no real
     dropouts -> H-dd selected by owner observation. Find which dd level starts dropping (dd2,
     dd3, dd4) and the mechanism (terrain window/LOD, ucode cap, RDP/display-list buffer,
     far-plane), fix it; until fixed, OWNER-OPT-INS must not recommend the failing dd levels.
   - G2b **Choppy audio on the Chapter II opening text crawl (owner playtest 2026-11-02): after
     G3e.** Owner heard choppy audio during the chapter II title scroll (run likely FPS60, dd1).
     Discriminate FPS60 on/off on the same crawl (AI underrun/[ai] cadence log, host frame
     times during the crawl), against retail as the control. G2 was closed for in-flight
     dialogue only; crawls were not covered.
   - G3f **Hangar "fish-eye lens" look (owner playtest 2026-11-02): after G2b.** Owner saw the
     hangar 3D view look fish-eye distorted (run: FPS60 only, no ASPECT/DD, default window).
     Boring-first order: (1) is it retail? compare the same hangar frame against the angrylion/
     retail oracle at native 4:3 (s6785 already matched SELECT LEVEL at RDP level, so check the
     PRESENTED image, not just RDP input); (2) presentation: non-uniform window scaling or
     aspect correction from G1f WINDOW_FIT / RT64 (measure presented width:height vs 4:3);
     (3) projection: FP_XSCALE/widescreen FOV or our far-plane/perspNorm changes leaking into the
     hangar camera at dd1. Close with presented-frame geometry numbers vs retail; if retail
     itself is wide-FOV, report that and offer an opt-in FOV knob rather than changing default.
     UPDATE owner detail: it appears ONLY while scrolling between ships (camera moving between
     craft) and disappears 1-2 s after the camera settles on a ship. So it is a transition
     effect: capture the whole pan, phase-gated on the scroll press, in retail and port. Extra
     hypotheses: (4) retail does a deliberate FOV/zoom swing during the pan (then it's retail);
     (5) FPS60 steps the pan's FOV/camera interpolation at the wrong rate or overshoots (test
     FPS60 off on the same pan); (6) a per-frame projection value (guPerspective fovy/perspNorm)
     lags or is reused across the 60 Hz split. Log the hangar camera fovy per frame across the pan.
   - G3d **Turning shake follow-up (owner 2026-10-31): after G1f.** G3c(c) was closed as
     retail judder, but its own data contradicts that reading: s6458 VI stamps arrive in
     bursts (3-4 VIs within 0.1 ms, then ~66 ms gaps) and lvl1 ran ~18 gfx tasks/s, not
     the ~30/s retail rate measured by s6452 (0x8011A890). Uneven, slow presentation
     would look like shake. Hypotheses: H-log (G1B/G3C logging in the soak recipe slows
     the game thread and bunches VI delivery; normal play is fine), H-thread (VI events
     are delivered to a game thread busy for ~66 ms, i.e. real ~15-18 fps in normal play
     too), H-present (presents bunch even when game frames are even). Discriminator, one
     build: stamp game-frame submit and RT64 present wall times (cheap ring buffer, dumped
     at exit, no per-frame stderr) in a minimal-logging arm vs the usual soak logging,
     lvl1 steady turn, retail and FPS60. Report game fps and present-interval
     distribution per arm. If normal play is below ~30 or bursty, root-cause and fix
     (thread priority/QoS, VI delivery, present pacing). Owner judges the feel after.
   - G2 **Audio fidelity: CLOSED** (owner live listen 2026-10-22: dialogue clean, no
     fuzz; agrees with s5669-s5674 PCM evidence). Reopen only on a new owner report.
   - G3 **Render fidelity.** Hangar artifacts (CURRENT-TRUTH list) and in-flight frame
     diffs against retail framebuffers.
   - G3b **In-flight spike lines (owner report 2026-10-24).** Take this next (G4 is
     parked; queued G4 soaks were cancelled). Owner watching
     plain retail-settings flight (s6081 lvl2, no draw-distance flags): mostly smooth, but
     occasional single-frame flashes of thin lines, one or two at a time, shooting in
     from random points on the screen border. Classic spike-triangle signature: a vertex
     at or behind the eye plane (w~0) or with garbage coords, unclipped, stretched past
     the viewport. Same class as the hangar "holo spikes" fixed ~s4518.
     Hypotheses: H-rsp (LLE F5 gfx ucode emulation edge case: VRCP/VRCPH/VRSQ precision,
     clamp/saturation, or near-plane clip path emits a bad vertex), H-rt64 (renderer
     treats extreme/out-of-guard-band RDP coords differently from hardware, which
     clamps), H-retail (retail does it too, masked by RDP coordinate clamping).
     Instrument, one build: per frame, log every RDP triangle with any vertex beyond a
     guard band (e.g. |x| or |y| > 2x viewport) or with a near-zero/negative w where
     visible, with frame number, vertex coords and the display-list/ucode task it came
     from; dump the framebuffer on those frames. Positive control: count must be > 0
     on a frame where a flash is visible in the dump. Discriminator: if the bad vertex
     is already in the RSP output (RDP command stream) -> H-rsp, bisect against the
     reference RSP behaviour of the offending vector op; if the RDP command is sane
     but RT64 draws a spike -> H-rt64, clamp/cull like hardware; if retail (emulator,
     same level and frame region) shows the same lines -> H-retail, optional
     host-side cull behind an env flag. Done when a 300 s lvl2 hold shows 0 logged
     spike triangles (or only retail-matching ones) with no new missing geometry.
   - G4 **Crash/stall hunting: PARKED by owner 2026-10-24.** s5999-s6082: all 19 levels
     (0-18) held 660 s clean, hangar route 9/9 clean, 0 retail-settings crashes found;
     repeat holds stopped paying. Do NOT queue crash/stall-hunt or repeat-hold soaks.
     Reopen only on an owner-reported crash/stall in play, or a crash that a soak
     run for another goal hits as a side effect (fix that one, don't start a sweep).
   - G5 The renaming sweep (item 4), last.
4. **Generated-symbol renaming sweep** (HYPOTHESIS-ID:
   generated-symbol-renaming-sweep), once 1-3 are inapplicable (M5 closed;
   M3 parked pending a new discriminator). Real, bounded work — ~1,548
   functions still carried placeholder `func_0x...` names when measured at
   s1487 — but it is open-ended by address, not by session count, and it
   stays perpetually actionable while the retail-entry boundary and M4
   accumulator-origin threads sit parked awaiting a new idea that will not
   arrive on its own. Before starting a sweep session, run
   `grep -n '^## Session ' PORTING-STATE.md | tail -15`: if all 15 titles
   belong to the sweep (contain "synchronized", "confirmed ... symbol", or
   are a sweep-scoped census that selected H2/H3), this iteration is a
   REVISIT instead — spend it re-attempting CURRENT-TRUTH's "external
   retail-entry boundary" (Next steps #2) or its "M4 accumulator boundary"
   (Durable boundaries) with a genuinely new angle, not another sweep step.
   Otherwise resume the sweep.

## Do exactly one work unit
A work unit is ONE experiment or ONE bounded change, chosen from the top of
CURRENT-TRUTH "Next steps" (or NEXT.md if present). Before building anything:
- Write down (in NEXT.md) the 2-4 competing hypotheses and the DISCRIMINATING
  measurement — the one whose outcome splits them. If you cannot name what
  each possible outcome would prove, redesign before running.
- Batch instrumentation: one build carrying every counter you will want, one
  run collecting all of them. Never spend a build-run cycle per counter.
- Batch your reads too (owner 2026-10-31, token cost). Every tool call re-reads the
  whole conversation from cache, so a session of 50 small calls costs far more than one
  of 15 larger ones. Decide up front what you need, then fetch it in ONE Bash call
  (several sed/grep/tail joined with `;` and short `echo ---` separators). Print only
  the lines you need: grep -n with tight patterns, sed ranges under ~60 lines, `| head`.
  Never cat large files or dump whole logs; summarise them with a short python/awk pass.

## Iron rules (each one bought with multiple lost sessions)
0. CPU budget (owner, 2026-11-19): the owner's fan was running flat out from
   parallel sweeps. Run at most 2 CPU-heavy jobs at once (s7651_gate_sweep.py
   defaults to --jobs 2). Do not raise --jobs or add wider fan-outs.
1. A null result is WORTHLESS until the instrument passes a positive control
   in the same run ("mark everything" must visibly fire). A counter proving
   the branch ran is NOT a control.
2. No cross-run A/B on animating scenes. Phase-gate on VI transitions
   (PROBE_PHASE_WIDTH / PROBE_KEYS_FROM_PHASE=1), never a stopwatch. Toggle
   within a single run where possible.
3. Scope every counter and log budget to the phase. Run-lifetime budgets read
   as false zeros in later phases.
4. Two independent lines of evidence before any conclusion enters
   CURRENT-TRUTH. One source = label it "single-source" explicitly.
5. Check the boring thing first: build flags, env vars, stale schedules,
   "working as designed" — before instrumenting the exotic thing.
6. Regeneration order: make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
   cmake. New diagnostics in build/factor5_ucode/*.c or RecompiledFuncs/ go
   into the fixup scripts or they die at the next regen.
7. Kill runs with SIGKILL, never SIGTERM. Capture paths must not start with
   "." in the final component. Run the game from build/ with the ROM present.
8. Budget rule: if this is the 3rd consecutive iteration on the same
   hypothesis with no discriminating result, STOP experimenting. Write the
   hypothesis/evidence table into NEXT.md, pick the highest-information-value
   next probe, or go BLOCKED with a specific question.
9. NEVER run `git submodule update`, `git checkout -- lib/...`, `git clean`,
   or `git reset --hard` (all denied in .claude/settings.json). lib/ carries
   uncommitted patches. If you edit anything under lib/, run
   `./submodule-patches/export.sh` and commit the refreshed patches in the
   same iteration, or the work is lost at the next reset.
10. Headless permission matching is a PREFIX match on the command string, so
   a leading env assignment breaks it: `PROBE_MODE=1 zsh run.sh` does not
   match the `zsh` allow rule and gets DENIED. Write env-prefixed commands
   as `env PROBE_MODE=1 zsh run.sh` (`env` is allowlisted). Exception:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake ...` is
   allowlisted verbatim and works either way.

11. A MITIGATION IS NOT AN EXPLANATION. Before landing a skip / allow /
   guard / restore for a corruption or wild-value defect, name the WRITER and
   say whether the value is legitimate. s640-s659 landed four layers of
   freelist mitigation without once asking why a colour image is set at
   0x1F0D74 with width 1161 - a width this game never uses - and every one of
   those iterations passed the ADVANCED contract. The Stop gate now requires
   an `ORIGIN:` line in the session entry when the diff adds mitigation-shaped
   machinery.
12. ASK GROUND TRUTH BEFORE BUILDING AN INSTRUMENT. See the section below.
   Our runtime is the thing under test; it cannot be its own witness.
13. BUILD EVERY ARM OF AN A/B IN ONE ITERATION. A three-hypothesis work unit
   that measures one arm per iteration costs three iterations to learn what a
   single iteration could have shown. Build the arms, run them concurrently
   (one game instance uses ~50% of one core), report the comparison in this
   session's entry.
14. A DIAGNOSTIC FIELD IS NOT A WORK UNIT. Threading one join key / counter /
   ordinal per iteration - and concluding "still X-shaped, the individual
   source remains open" - is churn, not a sweep: the discriminator never
   moves (s1003-s1006 burned six iterations this way). Design the WHOLE
   discriminating table (all keys) in ONE instrument, ONE build, ONE run. A
   diagnostic-only iteration that selects nothing is not ADVANCED-worthy; the
   Stop gate flags it. If the measurement cannot discriminate, stop adding
   fields and re-read docs/F5-UCODE-REFERENCE.md or the oracle.
   ENFORCED BEYOND ONE SLUG (2026-08-26, tightened 2026-08-29): the loop counts
   consecutive ADVANCED iterations that land NO engineering change -- no changed
   code/tool/patch, no NEW non-scratch file, and not a >=200-line CURRENT-TRUTH
   compaction. At 6 it forces a bounded-work pivot; at 12 it blocks the loop.
   This is slug-INDEPENDENT: renaming the HYPOTHESIS-ID does not reset it, only
   real work does. A generated-symbol-renaming sweep NO LONGER resets it: a
   tools/rename* mapping edit commits no build/runtime artifact (its regen output
   is gitignored), so it reads as churn, not engineering. If you are re-running
   an instrument that keeps returning "absent / unresolved / unevaluable", stop
   -- land an M5 de-stub (docs/M5-AUDIO-PLAN.md) or an M3 guard-class audit that
   commits a guard, or go BLOCKED with a specific question. Do not fall back on
   the rename sweep to stay fed; it will trip the pivot at 6 and block at 12.

**Owner save rule (2026-11-04).** build/saves holds the owner's real save (profile "ASS"). Never
delete, swap or overwrite it, and never clear ROGUESQ_NO_SAVE_WRITE, which runner.sh exports.
A test needing another save copies the game to its own working folder. tools/g3_port_capture.sh
SAVE_FROM does exactly that since s7819 (private OUTDIR/game dir, build/saves untouched).

## Ground truth that is not our runtime
- `tools/oracle/README.md` - runs the RETAIL ROM under mupen64plus with memory
  read/write watches, so "is this address ours or the game's?" gets an
  independent answer with a PC attribution. Watches are PHYSICAL addresses;
  always arm a positive control first (a whole-RDRAM watch must fire ~1.6M
  times in 8 emulated seconds). Currently undriven: it reaches boot and
  attract only, so a null says nothing about the hangar or a mission.
- `docs/F5-UCODE-REFERENCE.md` - the Factor 5 microcode's real command table,
  its six inline-data pointer advances, and what it can and cannot emit, taken
  from GLideN64's shipped HLE implementation of this exact ucode. Read it
  before reasoning about any DL or RDP stream anomaly. It also corrects our
  own long-standing mislabelling of ops 0x01/0x02/0x03.

## Soak queue — never spend a session babysitting a repeat soak
A soak that only re-runs an existing recipe belongs to the loop, not to you.
- Enqueue: write a SELF-CONTAINED script to scratch/agent/soak_queue/<name>.sh.
  It runs from the repo root, must launch the game itself, watchdog itself,
  SIGKILL the game, and exit nonzero on a crash. Arm ALL passive
  breadcrumb/instrument env vars in every recipe unless the experiment needs
  isolation — passive instruments are free, and rotating one per soak wasted
  10 sessions (s272–s281, 0/20 hits).
- A recipe that drives the game window/keys or needs a quiet host adds a header line
  `# SOAK_NEEDS_IDLE=<secs>`: the loop leaves it queued while HID idle is below that or the
  screen is locked, and re-queues it on exit 2 (the recipe's own human/lock/sleep void), up
  to SOAK_MAX_VOIDS=5 times (s7234; test: tools/agent/test_soak_idle_gate.sh). When nothing ran and only gated
  recipes are waiting, the loop polls up to SOAK_IDLE_WAIT=1800 s for idle before the next iteration (s7254; 0 = off).
- The loop runs up to 2 queued recipes between iterations (600 s hard cap
  each, then SIGKILL of the whole process group), appends one verdict line per
  run to scratch/agent/SOAK-RESULTS.md, and moves the recipe to
  soak_queue/done/. Full logs land in scratch/agent/soak_results/.
- Score summary fields with `sh tools/agent/summary_field.sh $D/summary <key> eq|ne|le|ge|lt|gt|is <value>`
  (exact key, numeric compare, missing key fails), never `grep -q 'key=N'` or `[[ $S == *key=N* ]]`: those pass
  inits=12 for `inits=1`, exitrc=134 for `exitrc=1`, mission_restarts=3 for `restarts=3` (s7455, test_summary_field.sh).
- Since s7456 each verdict line ends `arms=<k> alive=<a>/<k> crash_arms= stall_arms= fatal=` from the recipe's own `tag=`
  summary lines (tools/agent/soak_verdict_fields.sh); fold from those, not rc. arms=0 means the recipe printed no summary. Since s7457 it also ends `stall_na=<k>`: arms
  with no stall measure (vi_stalls30s=na/missing, no frozen=), whose stall_arms=0 is not a zero. Since s7924 it also ends `freeze_arms=<n> freeze_na=<m>`: arms with a frozen VI hold or present gap >= 1 s (G5c freezes; vi_stalls30s misses them). Since s7458 g1e_owner_quiet_arms arms score
  vi_stalls30s from their present ring (tools/agent/ring_stalls.py; a held VI origin counts even when presents keep flowing). Every live launcher prints a tag= line.
- Consume: read the new SOAK-RESULTS.md lines at session start (read list #3)
  and fold them into the ledger like any other run evidence.

## Declare your outcome honestly (the Stop hook checks this)
Write ONE of these words to `scratch/agent/OUTCOME`:

- `ADVANCED` — you ran the planned work unit and it produced a result, or you
  landed a real change (code, instrument, script, patch, or a NEW document).
  Editing existing docs is not advancing — with ONE exception: in a triggered
  MAINTENANCE iteration (Step 0), compacting CURRENT-TRUTH by >=200 net lines (or >=15000 net bytes)
  IS advancing.
- `SUBSTITUTED` — the planned work unit could NOT be run, so you did something
  else. This is legitimate ONCE. It is not a way to keep the loop fed.
- `BLOCKED` — you need something only the human can do. Write
  `scratch/agent/BLOCKED.md` and give it a line `NEEDS-HUMAN: <category>` where
  category is one of: `install` (software from the internet), `money` (spend,
  quota, billing), `system-settings` (TCC, permissions, keychain), `physical`
  (unlock the screen, plug in a controller, quit an app the human is using),
  `credentials`, or `gate-defect` (the loop/stop gate itself is wrong). The Stop
  gate rejects a BLOCKED.md without one. These are NEVER blocks — handle them
  yourself: backlog exhausted (take the next ladder rung, item 3c); waiting on an
  in-flight or queued soak (do other work; the loop folds results between
  iterations); a tool or command denied (find another route, or SUBSTITUTED);
  host load too high (queue the run as a soak, do offline work); loop.sh edited
  (the loop now re-executes itself when its script changes).

If you write `SUBSTITUTED` you must also write `scratch/agent/SUBSTITUTION.md`
containing three things:
1. What specifically stopped the planned unit from running.
2. The evidence, THIS ITERATION, that it was actually stopped — a measurement,
   not a precedent. "Confirmed N times before" is not evidence; it is a
   citation of an unrefuted claim, and an unrefuted claim is not a fact.
3. The single experiment that would REFUTE your blocking explanation. If you
   cannot name one, your explanation is not falsifiable and you should treat it
   as unproven and attempt the work unit anyway.

**The loop stops itself after 2 consecutive SUBSTITUTED iterations.** That is
deliberate. If the environment will not let the work proceed, the correct move
is to surface it to the human, not to generate documentation work to stay busy.
A doc-housekeeping iteration is not a cheap iteration — it costs the same as a
real one.

## Exit contract (the Stop hook enforces this)
Before you may stop, ALL of:
1. Append a dated session entry to PORTING-STATE.md: what ran, what it
   showed, what it rules out. Include failed experiments — a documented dead
   end is a result. The heading MUST match this shape EXACTLY, because the
   Stop gate greps for it verbatim (`^+## Session `):
   `## Session N (date) — title`
   e.g. `## Session 983 (2026-08-13) — audited r4300_pc wrapper contract`.
   N is the next integer after the previous entry's number. No other shape
   satisfies the gate — not `## sNNN`, not a leading date, not a missing
   "Session" word. Sessions 877-926 drifted into these variants and every one
   of them failed this check.
2. Update docs/CURRENT-TRUTH.md: next-steps reordered; any overturned
   conclusion moved to the superseded section WITH why it was believable.
3. Rewrite scratch/agent/NEXT.md for the next iteration: the single next work
   unit, exact commands, expected discriminating outcomes — and a line
   `HYPOTHESIS-ID: <slug>` naming the active investigation thread. Keep the
   slug while pursuing the same hypothesis; change it when you pivot or close
   it. A long systematic sweep (one ranked list, one lead per session) keeps
   ONE slug for the whole campaign — do not rename it per lead. The loop
   enforces iron rule 8 with it: an ADVANCED iteration resets the counter, so
   only stalled runs count — 3 consecutive non-ADVANCED iterations on one slug
   force a pivot preamble, a 4th blocks the loop.
4. git add -A && git commit (message: "iter: <one-line finding>"). ALWAYS a new
   commit. Never `git commit --amend`, rebase, or reset onto a commit from a
   previous iteration — that deletes another session's entry from the ledger,
   and the ledger is the only memory. The gate checks this by ancestry, so an
   amend of a commit you made THIS iteration is fine and a rewrite below your
   own starting point is blocked. When in doubt, add a commit.
5. Write scratch/agent/STATUS: DONE (work unit finished), or BLOCKED (also
   write scratch/agent/BLOCKED.md: what you need, from whom, and what you
   already tried — specific enough that a human can act in 2 minutes).
6. Write scratch/agent/OUTCOME: ADVANCED, SUBSTITUTED (plus SUBSTITUTION.md),
   or BLOCKED — per the section above.
Never end on a plan or a promise. If the experiment failed, run the fixed
version now, in this iteration.
