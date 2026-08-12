# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. 28 passes so far
   (git log has per-pass targets; PROJECT-OVERVIEW §16-§27 hold the most recent arcs) kept the file
   oscillating around the cap as new session detail accrues. 35 KB remains a stretch target, not a
   hard floor -- the "Current truth" env-var/timeline prose and the Regeneration section's Standing
   warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (PROJECT-OVERVIEW §10-§12). Next
   M5 work needs a genuinely new lead (rechecked s582 SOAK-RESULTS: no new audio-family
   crash leads since s487; due again s585+).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket from
   the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW §18-§19). The
   `DL_LIST_APPEND_GUARD`→`HEAPLISTDEQ_ATTR_WRITE_GUARD` lineage (items -312..-348, s481-569) is all
   fully CLOSED — PROJECT-OVERVIEW §20-§25; see individual items below for closure notes.

## Current truth (reviewed through s682; compacted in maintenance s679)

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- `ROGUESQ_LOG_FL_ZERO_WATCH=1` (s640+): soft poller on freelist header phys
  `0x1F3CC0` **plus** s646/s647 mprotect page-fault watch (`[fl-zero-fault]`).
  Arms PROT_READ while header is zeros (boot `want=1`) or freelist-shaped
  `0x2/0x60` (`want=2`); write SIGSEGV/SIGBUS logs host PC via local-symtab +
  guest sticky, re-enables RW. 16KB Apple pages → filter `in_hdr=1`. s647:
  freelist window uses busy re-arm spinner (20µs hold-off after fault; poller
  10µs) + `to_zero_correlate`. **ARM64 SS via `thread_set_state` from SEGV
  REFUTED** (nested SIGTRAP → CRASH). **s648:** freelist-window fault lines/BT
  **rate-limited** (first 32/16, all in_hdr, every 256th). **s649:** recover
  watch-page faults even when `armed==0` (concurrent/stale-TLB race; s648
  att4 SIGBUS in `buildModelViewerTextPage` at fa on page after peer disarm
  fell through to `[CRASH]`). Count `late=1` recovers. Posctrl LIVE s649
  (fault_n LIVE, `late=` field, CRASH=0). **s650 freeroll Outcome B**
  (recovery-active): arm_fl + freelist `0x2/0x60`→0 + `fault_hdr=0`;
  ~15s quiet while `armed=1` then silent zero → **H-busy-rearm REFUTED**
  freelist-class. **s651 freeroll:** same shape + **adlb_tgt=0** →
  **H-adlb-writer REFUTED**; rate-limit hole → **fault_ring** +
  **near_hdr** (-405). **s652 freeroll consume:** ring LIVE near=9;
  **H-ssnr380-writer REFUTED** (payload of LIVE alloc). **s653 freeroll
  Outcome B CONFIRMED:** freelist to_zero 0x2/0x60@165665ms immediately
  after `[fb-fl-writeback] HIT` `addrStart=0x1F0D74` range covers phys
  `0x1F3CC0` (w=1161); ssnr_tgt=0 → **H-ssnr-zero-stores REFUTED**;
  **H-fb-writeback-stomp CONFIRMED**. Product: `SKIP_WILD_W` allowlist +
  `SKIP_FL_HDR` + HIT early-return (-407). **s654 freeroll Outcome A
  CONFIRMED dual-source:** SKIP_WILD_W of exact killer CIMG
  (`addr=0x1F0D74 w=1161`) mid freelist-window + freelist 0x2/0x60
  survived post-arm; **H-fb-skip-stops-stomp CONFIRMED**; wild CIMG also
  fires on silent → H-recov-co-gate-stomp partly recharacterized.
  **s655 Outcome C:** post-SKIP freeroll 0/7 recovery-active engaged
  (s654 soak 2 silent + s655 in-session 5 silent); freelist 0x2/0x60
  survival reconfirmed 5/5; **H-fl-survive-unblocks-thr11d UNEVALUABLE**.
  **s656 Outcome B:** `ROGUESQ_ALLOW_WILD_W=1` A/B **0/6 recovery-active
  engaged** → **H-skip-suppresses-recov REFUTED** for SKIP_WILD_W alone;
  freelist still protected by SKIP_FL_HDR. Landed `ROGUESQ_ALLOW_FL_HDR=1`.
  **s656 soak Outcome C:** ALLOW both still HIT_SKIP in
  `copyNativeToRAM` last-line (not gated) — freelist never stomped.
  **s657:** gate last-line on ALLOW_FL_HDR → **HIT_WRITE LIVE**; freelist
  to_zero 0x2/0x60 returned; complete-ALLOW freeroll **1/3 recovery-active**
  (att3 recov768=7948 thr11d_new=1 fail136c=1) →
  **H-fl-survive-suppresses-recov SUPPORTED** (under permanent stomp).
  **s658 Outcome A CONFIRMED triple-source:** `ROGUESQ_FL_HDR_RESTORE=1`
  (ALLOW path) snapshots 16B @ phys 0x1F3CC0 around HIT writeback;
  `HIT_WRITE_RESTORE` classic killer + `[fb-fl-hdr-restore] match=1`
  pre=0x2/0x60 mid=0/0 post=0x2/0x60; freelist heartbeats survive past 170s;
  recovery-active **3/5 engaged** (att2/4/6; thr11d_new=0 fail136c=0) →
  **H-wb-complete-not-stomp SUPPORTED**. Product SKIP drought recharacterized
  as **writeback-skip** of freelist-range wild CIMG, not freelist integrity.
  **s659 productize LIVE (Outcome A):** freelist-range writeback
  snapshot/write/restore default ON. Policy A: wild freelist-range →
  `ALLOW_WILD_FL` + restore; non-freelist wild still `SKIP_WILD_W`. s659
  freeroll: recov 3/3 thr11d 3/3 fail136c 2/3. **s660:** offline zero_node
  next=`node+size+0x10` → **H-body-stomp STRUCTURAL**; full-body 64KB →
  next_ok=1 but recov drought 0/3 → body bytes co-gate recovery. **Product
  mode=headers:** restore only 16B freelist headers along chain; leave body
  writeback intact. A/B: `FL_RESTORE_MODE=body` / `FL_RESTORE_BYTES=N`.
  Opt-out: `FL_HDR_HARD_SKIP=1` / `FL_HDR_RESTORE=0`.
  **s662–s663 cimg-origin-desync CLOSED for class:** hangar wild SETCIMG
  **and** the exact freelist killer (`w=1161`/`0x1F0D74`) are **garbage
  ring content** after wrap. Length-respecting RDP walker lands SETCIMG
  after garbage prev (hangar: TRI op 0x09; killer: zeros+op 0x3F).
  Hangar **104/104 in_wrap=1** ring start=0x781800; killer **in_wrap=1**
  ring start=0x766000 (same class, different ring). Submit sticky
  contains killer task → not a deferred-merge sticky bug. **ORIGIN:**
  freelist stomp host writer = RT64 color writeback of that garbage
  SETCIMG (range covers phys 0x1F3CC0); operands not legitimate (w=1161
  never used). Instruments: `ROGUESQ_LOG_CIMG_RAW`, `ROGUESQ_LOG_DL_SYNC2`.
  **s664 Outcome B:** env-gated `ROGUESQ_DROP_WRAP_RDP=1` (default OFF)
  drops any submit with `lo ∈ [last_wrap_start,seen)` — **too coarse**:
  sticky never expires, so legitimate ring reuse after wrap is starved
  (~30k drops on early ring `0x4B7800`); cinematic SIGBUS; hangar never
  reached (A+B dual-source). Control C filter OFF + restore OFF still
  hits exact KILLER + freelist `0x2/0x60`→0. **s665 Outcome A:**
  `ROGUESQ_DROP_GARBAGE_CIMG=1` (default OFF) at processRDPLists —
  drop wild SETCIMG when prev ring garbage OR operands addr=0/w=1161.
  **H-prev-garbage-kills-killer CONFIRMED** dual-source: B drop ON +
  restore OFF → exact 1F0D74=0, freelist to_zero freelist-shaped=0;
  C control exact KILLER + HIT_WRITE + to_zero. Hangar craft_stable
  content LIVE both arms → false-drop REFUTED for hangar. v1 last-4
  hole fixed same-iter (full 8-deep + operand gate).
  **s666 productize REJECTED:** default-ON freeroll A+B (restore ON/OFF)
  freelist+content OK (kill_applied=0 flz=0 OK×8) but **recov 0/4 eng
  both arms** vs s659 restore 3/3 under drop OFF →
  **H-drop-suppresses-recov SUPPORTED** (writeback-prevent = skip-class
  drought; H-wb-complete-not-stomp). Reverted default OFF; product path
  remains multi-header restore. Drop stays opt-in experiment only (-418
  CLOSED).
  **s667 freeroll SCORE (headers product, drop OFF, BUDGET=1200):**
  posctrl LIVE mode=headers nhdr=45 next_ok=1; fail136c=0 both
  recovery-fired → **H-headers-fail136 SUPPORTED**. thr11d_new=0/2
  UNEVALUABLE (ship n≤2; holds truncated/silent shape).
  **s668 thr11d multi-hold freeroll (BUDGET=1800, product headers):**
  recov_full=2/3 eng thr11d_hit=**2/2** dual-source →
  **H-headers-thr11d CONFIRMED**; ship n=3 + mv-b8=27 both →
  **H-headers-shipn3 CONFIRMED**; fail136c=0; next_ok=1.
  **Pipeline LIVE:** thr11d → ok136c (rs_malloc 0x136C succeeds) →
  thr12 create (ltexmg=0) → **section 2** mission overlay → thr12
  recreate; crash=0 packTlut=0 both holds. s667 thr11d=0 recharacterized
  as ship-n3-miss (holds never reached B8 gate), not headers regression.
  **s669 offline post-sec2 SCORE (s668 att2+att3 dual-source):**
  **H-sec2-mission-live CONFIRMED** — ~195–200s outdoor VI 512
  origins 0x620000↔0x690000 continuous present FIRE swap pairs=4,
  ~5900 GFX tasks tris=42; thr12 id=13 long-lived then menu sec3 return.
  **H-thr12-churn-normal CONFIRMED** (not immediate death).
  **H-postsec2-fs-plateau CONFIRMED** — thr13 life rdpFs delta 0/+2 while
  synth +~5864–5892; runner syncs=0 ~5866–5894 vs syncs>0 only 3;
  fs_b0=E9=6 vs F7~11.7k. packTlut=0 crash=0. Residual → -421
  (post-sec2 FS plateau / menu return / packTlut never).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  per-pixel (s24→s26), `ROGUESQ_FIX_ZERO_SHADE` (s20), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15),
  `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough + forceAdvance +
  `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10), **s78 wild/OOB FB refuse** in `FramebufferManager::get`
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present),
  **s182 `[fbsync-oob-skip]` guard** in `State::fullSync`'s color/depth read-into-`fbStorage`
  blocks (`rt64_state.cpp`) — s78's refuse gate returns a `refuseFb` that still carries the wild
  width/height, and this downstream RDRAM read had no bounds check of its own; same family as
  s72/s78. **s653 `rs64_writeback_sane`:** `SKIP_WILD_W` (allowlist 320/512/640/1024,
  matches s82) + freelist-range allow. **s659–s660 product (default ON):**
  freelist-range writeback + surgical multi-header restore @ phys 0x1F3CC0
  (`mode=headers`, walk_cap 64KB); wild freelist-range `ALLOW_WILD_FL`.
  `SKIP_WILD_W` still ON for non-freelist wild. A/B: `FL_HDR_HARD_SKIP=1`,
  `FL_HDR_RESTORE=0`, `FL_RESTORE_MODE=body`, `FL_RESTORE_BYTES=N`,
  `ALLOW_WILD_W=1`.
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30, pad-only), `ROGUESQ_SHADE_WRAP=3` (s31), `ROGUESQ_SHADOW2`,
  `ROGUESQ_RING_RESYNC`, **`ROGUESQ_DROP_WRAP_RDP`** (s664 Outcome B — too coarse; experiment
  only), **`ROGUESQ_DROP_GARBAGE_CIMG`** (s665 Outcome A / s666 REJECTED
  productize — decode-site wild+garbage SETCIMG drop; default OFF forever
  under current recovery co-gate; opt-in freelist-origin experiments only).
  Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1` (s47, lib-side) dumps every skipped
  IMEM DMA to `build/imem_dma_dump.bin` (`scratch/s47_parse_imemdump.py` decodes).
  `ROGUESQ_LOG_RUNNER=1` prints a per-task RDP-opcode histogram (1-in-32 sampled by default --
  `ROGUESQ_LOG_RUNNER_ALL=1`, s64, prints every task unsampled; the sampled mode misattributes
  31 tasks' counts onto whichever task is next sampled). `ROGUESQ_LOG_SEQ=1` dumps a task's raw
  pre-translation DL bytes -- not valid for "does this task emit SYNC_FULL" (needs the
  post-translation histogram above, s64).
- Deleted from the code (s44): `ROGUESQ_DPC_WRAP` / `ROGUESQ_WRAP_DEDUP` (s11), `ROGUESQ_FORCE_PAL15`
  (s14), `ROGUESQ_FORCE_SHADE_WHITE` (s19). `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times
  since s11 but is KEPT deliberately -- OOM insurance for future FULL_SYNC-less phases (M3
  missions), turns a 22 GB Metal abort into a capped workload (s44).

Unattended timeline (VI width, ±1 s over 9 runs, s18; content counts s9/s20/s22/s23):

| t | VI | scene |
|---|---|---|
| 0.0 s | 0 → 320 | boot |
| 1.7 s | 640 | attribution → N64 logo → cinematic geometry → star flare → **Factor 5 logo**, all correct (content in 24/60 frames over ~2–44 s) |
| ~46.5 s | 1024 | **title screen** — logo, pilot, X-wing, START/OPTIONS; 5/5 content frames, ~20.9k colours |
| ~72 s | 640 | transition |
| ~90 s | 512, origin 0x690400 | **outdoor scene** — sky, clouds, horizon, sand; 6/6 content frames |

**s39/`-O2` harness note:** the game now progresses further per unit time, so the old
`PROBE_KEYS="3:start 7:start 11:a 15:a 19:a"` schedule overshoots the hangar into a later exterior
scene that shares VI origin **0x6AB400** — origin alone no longer identifies the hangar. Use
`"3:start 7:start"`. The phase timeline below is unchanged (transitions are not render-rate bound).

Driven from the title with `PROBE_KEYS_FROM_PHASE=1` (s23, scene names corrected s48):

| t | VI | scene |
|---|---|---|
| 46.7 s | 1024 | clean title |
| ~50 s | 1024 | **SELECT GAME** (photographic hangar backdrop, AAA save, ERASE GAME) — waits for input indefinitely |
| +1 press | 512, origin 0x6AB400, colour 0x656000/0x6AB000 | **level-select war room → SELECT LEVEL — "AMBUSH AT MOS EISLEY"** with X-wing hologram (the scene s12–s47 called the "main-menu hangar"; see s48 below) |
| ~93 s | 640 | transition — process died here in the undriven-era observation and in every crashing run of the post-s86 family; on later crash-free runs the process instead survives past here |
| leave SELECT YOUR CRAFT (1 Start press) | 512→640, origin 0x6AB400→0x6A2900ish | **s162: a Chapter-1 mission-intro cutscene** — gold "STAR WARS" logo bumper → "Chapter 1"/"THE RED…" crawl text → black → desert-planet horizon widening into a fast dive toward a hangar structure (establishing shot, not gameplay). The s75/s76/s161 "hangar-flight" label for this window was an unverified inference from title-yellow color decay, not from the picture itself — **see the s150 overturned-conclusion entry below: it is the SAME craft-select scene under a corrupting camera move, not gameplay.** |
| ~+90-115s post-leave | varies | **graphics-task-submission stall** — `[vi-fs-decision]` reports `stalled=1 pairs=0` continuously, RDP `fs` counter frozen. Not a crash; a staggered subsystem shutdown (s178). Open, unresolved as of s183 (last dedicated session). Full detail: `PORTING-STATE` Sessions 176-183. Note s579: post-exit `rdpFs` plateau with live GFX is a *different* class (FULL_SYNC starvation, item -349) — do not merge. |

Menu state machine (s48, extended through s75; hold/crash triage s76-s114): title --start--> SELECT
GAME --start--> war room / SELECT LEVEL --start--> **AVAILABLE CRAFT** (war-room craft holograms; `a`
does **not** show a level description card, s61-s69). With process alive 65s+ post-`a` (s72/s73):
black ~5s -> capital-ship flash -> stable **SELECT YOUR CRAFT** (hangar pad + full X-wing; `a`
no-ops, s74; camera orbits). A single Start leaves the menu, but what it leaves INTO is unresolved
(s75's "hangar-flight" claim was **OVERTURNED s150**, see Overturned conclusions -- same craft-select
scene under a corrupting camera move, not a new environment). VI stays on the 0x6AB400/0x656400 pair
throughout -- **origin cannot identify these menu scenes**, only phases. ~20 crash classes closed
getting through this chase (mechanisms/tags: `docs/PROJECT-OVERVIEW.md` §3/§7/§9).

Remaining visual defects, all parked as M4 except where noted: outdoor 512 zero-shade masked not
fixed (`baseFixed = −32768` root cause unknown, s19/s20); S=0 triangles in the 640 attribution phase,
uninvestigated (s18); `[dpc-behind]` ring-wrap drops with `DPC_WRAP` off (not a black-screen cause,
s11). Hangar floor multi-hue band, hangar dimness, and the post-leave black/SIGBUS chain are all
FIXED (M1 closed s48; `SHADE_WRAP` s25; ImemOverrun s69 + depth-writeback SIGBUS s72) — mechanisms in
`docs/PROJECT-OVERVIEW.md` §3.

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep. 0
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. The `[missing-func]` saga
(s49's original 3 addresses plus ~801-803 further phantom `main_overlay.txt` entries found while
fixing them) is fully **CLOSED** (items -6/-249) — every clean live-verify should show 0
`[missing-func]` lines. Post-`a` process now soaks well past 65s without death.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism: `docs/PROJECT-OVERVIEW.md` §3.

**M2 — post-clip-fix regression sweep: DONE (s49).** Stability baseline: 1138 tasks, fanjal=9448,
0 cull-census-identity violations. The 3 `[missing-func]` addresses **DONE/CLOSED s399** (item -6).

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT reachable
and stable; ~20 crash classes closed s50-s294. Leave-key "hangar-flight" OVERTURNED s150; **s577
REAL hangar exit CONFIRMED** (case 3→5→6→8). Post-exit FULL_SYNC starvation product-fixed via
`ROGUESQ_FS_PIPE_INJECT` (default OFF; items -354..-358). Pipeline status as of **s671**:
- thr11 (`saveServiceWorker` `0x8006F2CC`) → sec4 → thr12 (`hudDisplayUpdateWorker` via
  `loadLevelTextureCache`) → **sec2 LIVE** under product multi-header restore.
  **s668 dual-source:** thr11d→ok136c→thr12→sec2. **s669 dual-source offline:**
  post-sec2 outdoor content LIVE ~195–200s (VI 512 0x620000/0x690000, present
  swap FIRE) then **menu sec3 return**; thr12 long-lived; **rdpFs plateau**
  (syncs=0 / E9 starved) entire thr13 window; packTlut=0. **s670 split:**
  menu-return/thr12-teardown is **input-gated** (-422). **s671: -422
  CONFIRMED dual-source and CLOSED** (2/2 pulsed attempts: thr12 alive
  >1000s, 0 sec3 return, 0 packTlut) while the **rdpFs plateau itself is
  untouched by both inject (Arm A) and input (Arm B)** — stays open as -421,
    **s675 confirms command-boundary E9 is abundant** in two independent
  post-sec2 samples (4,444/12,924 and 9,549/13,135 tasks) while runner
    FULL_SYNC appears in only 3 tasks per sample. Walker misalignment is
    refuted as the sole explanation. **s676 dispatch discriminator:** one
    recovery-active post-sec2 run had aligned walker E9 sum **32,150** in
    **6,719** positive task probes, while the authoritative RDP parser's
    cumulative E9 count advanced by only **2**. Every authoritative E9 seen
    reached `GBI_RDP::fullSync` and `State::fullSync`. Thus the dominant loss
    is before authoritative dispatch; map/handler and State accounting are
    ruled out for those commands. Residual rank: (1) **-421 authoritative
    parser advance/control-flow mismatch** then rdpFs
  starvation mechanism / packTlut (-373), (2) B8
  co-gate -393, (3) -387 **5×**. Do **not** productize DROP_GARBAGE_CIMG; do
  **not** re-soak thr11d rate (-419 CLOSED) or re-run the -422 input pulse
  (CLOSED, no residual).
- Co-gates: recovery (-374/-413/-414/-418), mat3inv (-375), ship (-376/-377/-392/-393),
  class-D (-378), FORCE_STATE6 (-381 CLOSED), freeroll (-382..-384), thr12 path
  LIVE under headers (-385 dissolved), sinfApprox (-386 1×), do_rom_read
  (-387 **5×**). thr11d metric = post-hsel destroy of `0x8006F2CC` only (s618).
  Tools default OFF: `FORCE_STATE6_AFTER`, `FORCE_CASE6_START`, `FS_PIPE_INJECT`,
  `ALLOW_WILD_W`, `FL_HDR_HARD_SKIP`, `FL_HDR_RESTORE=0`, `FL_RESTORE_MODE=body`,
  `DROP_WRAP_RDP`, `DROP_GARBAGE_CIMG`. Product ON: freelist multi-header restore.
  Diagnostics: `ROGUESQ_LOG_CIMG_RAW`, `ROGUESQ_LOG_DL_SYNC2`.
- Full durable arc: **`docs/PROJECT-OVERVIEW.md` §27**; items -349..-422; Sessions 577-675.
DoD = **cutscene→in-mission** + craft input.
*Done when:* 60s in-mission render, craft responds to synthetic input, stability 0, phase timeline
covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it. The 3 `[missing-func]` addresses, the `main_overlay.txt` phantom-overlay-function
family, and its `0x800290d4` clustering are all **DONE/CLOSED** (items -6/-249/-259).

**M5 — audio de-stubbing: DONE and fully CLOSED (s297-376).** No outstanding thread; next M5 work
needs a genuinely new lead (rechecked s570: zero new leads, intentionally-left stubs still C88
force-zero + default `real_ucode=0`; due again s573+). Full arc: `docs/PROJECT-OVERVIEW.md` §9-§12.

## Backlog — one monotonic sequence (reviewed s679)

Legacy negative identifiers remain searchable in `PORTING-STATE.md` and
`docs/PROJECT-OVERVIEW.md`; this active backlog is intentionally renumbered from 1 on each
maintenance pass. Closed lineages are not backlog items.

1. **M3 / legacy -421 — post-sec2 FULL_SYNC plateau: OPEN.** Post-sec2 outdoor rendering is
   live, but `rdpFs` stays flat while GFX continues. Two independent s675 samples show aligned
   guest E9s in 4,444/12,924 and 9,549/13,135 target tasks, with runner FULL_SYNC in only three
   each. s676 confirms the dominant loss is before authoritative dispatch: all authoritative E9s
   reach both `GBI_RDP::fullSync` and `State::fullSync`. s677 rules out parser-length and
   boundary-carry loss: guest and authoritative address domains are distinct. The current,
   generated-code provenance probe joins guest L_1090 E9 fetches, raw DPC E9 emissions, and
   deferred-submit coverage. **s680 corrected its target gate from 6500 to 8200–8263:** the
   former 64-record window was recovery traffic, exhausted before the s677 divergent population.
   **s681's shortened recovery-active rerun passed all task-1..4 controls but falsified that
   static gate:** section 2 began at task 8800, after the complete 8200–8263 capture. Those 64
   earlier records were `guest=1 emit=0 submit=0` while their matching walker counts were
   `e9_aligned=0`; they are recovery traffic, not the divergent population. No E9-loss mechanism
   is established. Next, replace the absolute task window with a section-2 phase latch and count
   E9 at every output-ring command (the current `emit` field only sees a submit-range head).
   **s682 completed the real phase-latched capture:** section 2 at task 8754 triggered the latch;
   all 64 post-latch records and all four boot controls printed. Controls were complete
   `guest=emit=submit=1`; the target had guest=3, emit=submit=62, including 57 emitted E9s
   with no L_1090 fetch and nine walker>guest rows. Thus DPC-submit loss is refuted for all
   62 captured output E9s, and walker/guest divergence supports a non-executed walker path.
   The capture lacks per-address authoritative-parser attribution, so it does not establish the
   plateau mechanism. Next: join every emitted E9 address to RT64's raw parser fetch. Durable
   evidence and probe mechanics: PROJECT-OVERVIEW §27 and Sessions 669–682.

2. **M3 co-gates / legacy -374, -375, -378, -382..-384, -387, -393.** These are passive
   recurrence breadcrumbs, not reactive work: recovery-cell silence, one-off math/scene crashes,
   craft-shadow, `do_rom_read+608`, and the B8 ship gate. Enqueue self-contained soaks when a
   recipe adds information; pursue only a systematic idiom-class audit after recurrence.

3. **M4 correctness.** Outdoor `baseFixed=-32768` zero-shade, attribution S=0 triangles, then
   I4 `sample=64x128`; each needs an independently controlled experiment.

4. **Tooling / legacy -20.** Intermittent regeneration omission: delete generated `funcs_*.c`
   before regen and audit `fixup_game_funcs.py` counts. Escalate only with a reproducible case.

## Closed lineages — do not reopen

- **M5 audio (legacy -160..-230): CLOSED.** A new audio lead is required; see
  PROJECT-OVERVIEW §9–§12 and `docs/M5-AUDIO-PLAN.md`.
- **Hangar-exit → sec2 pipeline (legacy -349..-422): CLOSED except backlog item 1.** Product
  multi-header freelist restore is ON. `DROP_WRAP_RDP` and `DROP_GARBAGE_CIMG` remain OFF:
  suppressing the garbage SETCIMG writeback also suppresses recovery. The exact w=1161 CIMG was
  proven garbage after ring wrap, not a legitimate game command. Detail: PROJECT-OVERVIEW §27.
- **Idiom-class audits (legacy -231..-348): CLOSED.** The duplicate-symbol, frequency-scan,
  `DL_LIST_APPEND_GUARD`, and sibling/freelist campaigns are archived in PROJECT-OVERVIEW §13–§26.
  Do not revive an individual crash without a new class-level enumeration.

### Standing / open non-pipeline items

-20. **Regen-pipeline reliability bug (s120, intermittent).** `N64Recomp` skips rewriting existing
    `funcs_*.c`; delete all before every regen is mandatory but residual intermittency unknown.
    **Standing rule**: audit patch report for unexpected counts after every `fixup_game_funcs.py`.
    PORTING-STATE 120/121/126.

-11. **`advancePlayerAnimationPhase` SIGBUS: PARKED s89, RECURRED s424, GUARDED s425** (see -261).

-10/-9. **Metal-shader-compiler SIGSEGV** (s83, one data point). **s83 spline div0 guard**: 0/5
    fires; real fix by inspection, no same-run positive control yet.

-8. **`frameStartReset` SIGBUS** — 3 occurrences (s85/s108/s156); no located faulting insn.

-7. **M3 DoD gate.** Mission-entry pipeline is live through sec2; the only active blocker is
    backlog item 1. Product settings and the durable causal chain are in PROJECT-OVERVIEW §27.

-6. **(s53→s399) M4 `[missing-func]` addresses: DONE, CLOSED s399.** PORTING-STATE 399.

-5. Past first sustained mission hold: expect new failure classes (mission overlay DMA,
    missing-func/UJ, new VI phase, overlays 12/44, texture corruption). Each is its own unit.

-3. **Sibling-repo housekeeping (not autonomous):** `~/Documents/Tools/rogue_squadron64`
    carries uncommitted symbol-file edits. Ask user before committing there.

-2/-1. **Band-row coverage history** (settled s41-49). **GPU->CPU present PNG** via
    `NativeTarget::copyToRAM` — convenience, not a blocker.

**Done, do not redo:** optimising the ucode vector path (s38: `-O0`→`-O2` gave 41x); the
ucode-performance→DL-submission-collapse→RDP-census→draw-loss chain (s33-s37); coverage
attribution/format-mismatch (`LOG_BBOX`/`LOG_UPLOAD`); the s27-s31 I4-decode line.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, re-applies hand-edits
   idempotently: `$zero` writes commented (~2700); `fake_func_*` → `__builtin_trap()`; cross-
   function branch traps; audio-engine gate stores → 0 in `funcs_23.c` for
   `setDisplayMode`/`reapplyDisplayMode` only (`initMusyXEngine` site reversed s302); `jr $t9`
   in `convertMat3x4ToN64Mtx` → plain `return`; `musyxKeyOnVoice` break 6/7 → early return;
   `evalCubicSplineAtTime` div0 guard (`[spline-div0]`).
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. **s47: before the fixup, also run
`python3 tools/make_clip_composite.py` + RSPRecomp on `factor5_rsp_ovl4.toml`**. `factor5b_rsp.toml`
is the **MusyX audio** ucode; stays in the build as a never-called artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches** — never
  `git submodule update --force`. Mirror via `submodule-patches/export.sh`.
- ROM must sit next to the executable in `build/`; otherwise silent "place your ROM" dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` / `RecompiledFuncs` die on regen — put them
  in fixup scripts.
- settings.json Bash allowlist matches FIRST WORD: prefix env assignments with `env` (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill with SIGKILL, not SIGTERM (s9).
  Python decoders: `scratch/venv/bin/python` (s18).
- `regress.sh` must not write probe images as `.*` hidden names (s26).
- ~~Screen Recording permission intermittent~~ — overturned s32: wrong window id, not permission.
- `winctl activate` ignored while another app holds focus — use `probe.sh`/`regress.sh`
  `raise_game()` (System Events `set frontmost`) instead (s45).

## Overturned conclusions — do not act on these

Full list (11+ entries spanning s2-s422, each with why it was believable and what refuted it),
plus the early-era dead-ends list: `docs/PROJECT-OVERVIEW.md` §26. Load-bearing for active work:
- **(s400-421→s422)** `0x800290d4` "six independent triggers" is `inflate_fast`'s clean return.
- **(M5-AUDIO-PLAN.md §4→s371)** host audio `queue_samples`→`SDL_QueueAudio` unit-mismatch, fixed s371.
- **(s578→s579)** post-exit `rdpFs` plateau is **not** the s178 graphics-task-submission stall —
  s178 is `stalled=1 pairs=0` + producer stop; s577 post-exit keeps submitting GFX with present
  FIRE pairs=4 while only FULL_SYNC dies (item -349).

### Dead ends — labelled as such in the log, do not retry

Full list (early ucode/DMA/overlay hacks, s2b-s91) migrated to `docs/PROJECT-OVERVIEW.md` §26.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here:
- §4.1 instruments-that-lie; §4.2 attribution errors; §4.3 cross-run comparison on animating
  scenes (gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`); §4.6 missing protocol events.
- Other instrument traps: PROJECT-OVERVIEW §8.
- **crash-signature blindness (s344)**: soak "any `[CRASH]`" is not evidence for a SPECIFIC target
  unless `last-guest-pc`/`pc-symbol` matches — ~20+ independent crash families. Also: grepping
  game `run.log` for driver `[keys]` is wrong (launcher log only). Item -200.
- **repeated-`last-guest-pc` is not repeated-bug proof outside the audited set (s595)**: only
  ~52/2499 functions track `g_rs64_last_guest_pc`. N identical addresses can be N different
  crashes sharing one instrumented caller. Check audited set before "Nth occurrence" escalation.
  Item -347.
