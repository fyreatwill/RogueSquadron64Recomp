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

## Current truth (reviewed through s715; compacted in maintenance s679)

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
   plateau mechanism. **s683 added that join and fixed its pending-command-path hole in the same
   iteration:** boot controls were visibly complete (`emit=submit=raw=match=1`, four individual
   `match=1` fetch marks); corrected section-2 capture had all 64 rows and `emit=submit=43` but
   `raw=match=3`, with the other 40 emitted E9s absent from both direct and pending-command raw
   fetch paths. **s684 span join REFUTED parser advance/control-flow mismatch:** two independent
   section-2 windows, each with four exact boot controls (`emit=submit=raw=match=1`, `gap=0`),
   showed every sampled non-fetch E9 byte strictly inside an executed raw `0xCE` 20-word span
   (`pending=0`). The bridge's fixed-8-byte emission scan was counting inline triangle payload as
   E9 commands. Thus there is no submitted-command loss in this population and the apparent 40-E9
   deficit is a scanner false positive, not the plateau mechanism. The three genuine raw E9s still
   dispatch normally. **s685 parser→State discriminator:** one recovery-active, phase-latched
   64-task section-2 window passed four visible boot controls
   (`guest=emit=submit=raw=dispatch=match=1`, each). The target total was
   `guest=3 raw=3 dispatch=3`, while legacy fixed-stride `emit=submit=37`.
   Therefore **H-dispatch-loss is REFUTED**: every real parser E9 invoked
   `State::fullSync`, and the apparent other 34 E9s are triangle inline data.
   **H-rsp-starvation is SUPPORTED** at the RT64 boundary; the next question is
   whether the source-side three-E9 total is legitimate game/RSP input or an LLE
   control-flow defect. **s686 source-stream completion audit:** the same-run
   four boot controls visibly completed naturally (`src_fetch=42 src_e9=1
   src_end=1 src_kind=1`) and preserved their exact E9→dispatch chain. The
   phase-latched 64-row section-2 window had exactly three matching natural
   rows (`src_fetch=42 src_e9=1`), followed by **61** rows that each made
   `src_fetch=8192`, `src_e9=0`, and returned only through synthetic
   `src_kind=2` (iter cap); target totals are `guest=src_e9=raw=dispatch=3`.
   The all-fetch marker and independently anchored exit marker agree, with
   the boot controls proving both live. This is **single-run, dual-marker
   support for H-lle-control-flow**: after the three real boundaries the LLE
   does not reach a natural display-list completion. It does not yet establish
   whether that cap loop is an expected SP_STATUS-stub artifact or a stale
   stream reset; next trace the real EndDL/unwind path. **s687 EndDL audit:**
   all four boot controls and the three natural section-2 rows show
   `unwind=3 unwind_natural=1`, while all 61 cap rows show 106–122 EndDL
   visits but `unwind_natural=0` (and their last depth is exactly zero).
   **H-unwind-missed is REFUTED; H-unwind-corrupt is SUPPORTED**
   single-run with live controls: EndDL executes repeatedly but never takes
   the root `L_10E8` exit. **s688 saved-frame audit:** controls and all three
   natural section-2 rows have balanced `push=pop=resume=2`, `mis=0`, and
   `slot=0`; each of the 61 cap rows has coherent pop→resume (`mis=0`) but
   `push-pop=8`, `slot=0..8`, and 102–115 zero-slot resumes. Thus
   **H-stale-resume is REFUTED for the observed pop/resume pairs** and
   **H-unbalanced-frame is SUPPORTED** (single-run, controls live). **s689
   caller/payload capture:** controls stayed balanced and complete. All 61 cap
   rows had only slot-0/slot-8 first pushes; the initial slot-0 push was
   caller `0x1090`, while every slot-8 push was caller `0x1088`; representative
   cap task 8820 kept the saved target stable while saved PC advanced
   `0x180..0x1F8`. This is single-run support for a repeated dispatcher return
   path, but `r31` alone does not identify the decoded command. Next join the
   push with the current fetched opcode/operands and guest address. **s690
   command-word capture is built and regeneration-safe:** `L_12A0` now passes
   `r17/r19/r20` as `pc/w0/w1`; `[e9-prov-frame]` prints them and retains
   first/last re-entry slot-0 (`caller=0x1088`) in addition to slot 8. The
   main/ovl4 regeneration exposed stale fixup anchors; updated fixups accept
   the current whitespace and absent out-of-range `L_1650` jump. Build passed.
   Two phase-gated starts reached the post-craft pulse window with all four
   boot controls live, but neither reached the section-2 latch before the
   bounded run was stopped (`sec2=0`, `latch=0`, `CRASH=0`): **no conclusion**
   from their command words. **s691 completed the bounded reroll:** 9/9
   hangar-selection-engaged attempts were recovery-silent (`0x0076B768`
   absent), one pre-engagement exit was discarded, and no pulse, section-2
   latch, or target row occurred. This fails the required recovery positive
   control, so it is not evidence for any command-path hypothesis. Do not
   repeat unchanged: first audit why the formerly recovery-active recipe now
   produces only silent rows, then retry only after the control is restored.
   **s692 recovery-latch readiness audit:** the s689 historical and current
   launcher/runner scripts have identical SHA-1s and identical effective
   `GAME_EXTRA_ENV` (no inherited `ROGUESQ_*` setting), refuting
   **H-config-drift**. The saved s689 log passed the new common scorer
   (`literal=7936`, authoritative `rdp-fullsync=3968`, independent
   `fs-slot=1984`, boot E9 controls=4). In the new current arm, boot controls
   passed and recovery became live (`literal=96`, `rdp-fullsync=48`,
   `fs-slot=24`), refuting **H-wrapper-observer-loss**. The simultaneous
   historical arm never reached `hangar-sel` because the two GUI instances
   competed for focus, so it is invalid as an A/B outcome. This supports
   **H-stochastic-route** only provisionally; the recovery control is now
   restored for one ordinary, single-instance provenance-capture reroll.
   **s693 qualified single-instance command capture:** attempt 5 reached
   recovery (`rdp-fullsync=2662`, `fs-slot=7984`), section 2, and fired both
   scheduled Start pulses. Of 1,381 post-recovery frame rows, all 547
   `caller=0x1088` rows were `kind=P` with `w0=0x06000000` and KSEG0 display
   list operands (`w1=0x8058...`--`0x805A...`); none had a zero/data-shaped
   `w0`. The independent F5 command table identifies `0x06` as `F3DSWRS_DL`.
   Therefore **H-inline-data-dispatch is REFUTED for the captured cap frames**
   and **H-legitimate-open-chain is SUPPORTED** (runtime capture + independent
   reference). Target/PC families are coherent, so this run provides no
   support for H-state-corrupt. **s694** landed regeneration-safe paired-frame
   IDs (push→pop→resume) and `dl06=push/complete/open` phase summaries. Its
   same-run boot positive controls passed in tasks 1--4 (each valid `0x06`
   pair completed, `open=0`), but attempt 1 returned to section 3 before the
   section-2 latch. **s695 consumed that 600-second reroll:** attempts 1--3
   again passed the tasks-1--4 paired-frame controls; attempts 1 and 3 were
   recovery-silent, while attempt 2 aborted before any section-2 latch. There
   are no `scope=sec2` or target cap rows in any attempt, so this is an
   **unqualified null**, not evidence for H-extra-push, H-missing-return, or
   H-game-open-chain. **s696 consumed both follow-up 600-second rerolls:** all
   five engaged attempts passed all four boot paired-frame controls
   (`dl06=push:2,complete:2,open:0`; P/O/R counts 20/16/16), but every one was
   recovery-silent and none latched section 2. This is a third consecutive
   unqualified provenance reroll (s694--s696); do not enqueue another
   unchanged reroll. **s697 retail-oracle readiness audit:** the first
   concurrent two-arm attempt was invalid because the oracle's combined hit
   total hid the narrow watch; it also never left VI width 320. The oracle now
   prints per-watch totals. Its fixed single-instance arm carried a whole-RDRAM
   positive control (11,785,811 writes), a narrow physical
   `0x0076B768:0x0076B76C` watch (0 writes), `--pif-trace`, and the documented
   6..56-second Start schedule. Every injected Start was observed in PIF RAM,
   but VI remained 320 through 4,199 frames/70.0 emulated seconds, never
   reaching the documented 640/1024/hangar phases. The target zero is therefore
   **unqualified**: it cannot distinguish H-game-route, H-observer, or
   H-runtime-divergence. The next unit is an oracle boot-reachability audit
   (RSP/plugin versus debugger/watch arms) before another target watch or any
   new runtime instrument.
   The remaining question is whether the valid `0x06` chain is pushed with
   incorrect control-flow semantics or lacks its eventual root return. The
   pulse/section-3 outcomes remain incidental to this provenance result, not
   a new input conclusion.
   Durable evidence and probe mechanics: PROJECT-OVERVIEW §27 and Sessions
   669–698. **s698 retail A/B:** both current-RSP no-watch and whole-RDRAM
   control arms stayed at 320 through 70s despite all eleven PIF-observed
   Starts; the control counted 11,785,883 writes. H-watch-perturbation is
   refuted. **s704 found the local arm missed by the earlier narrow inventory:**
   `~/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/`
   contains an arm64 `mupen64plus-rsp-cxd4.dylib`. The concurrent current-HLE
   and CXD4 arms used identical ROM/core/input schedule, VI/PIF traces, and
   whole-RDRAM controls; both received all eleven Starts, remained 320 through
   4,193 VI/~69.9 emulated seconds, and counted exactly 11,769,059 writes.
   **H-rsp-hle-route is REFUTED; H-core-environment-route is SUPPORTED.** This
   is still not a phase-qualified target-watch witness; next audit the oracle
   debugger/pure-interpreter launch mode before another recovery-cell watch or
   provenance reroll. **s699 source-backed
   launch audit:** both candidate ROM files have identical SHA-256
   `9c32d0087fa2b83c5ee6f19ee86683907653ed8f30e7d4680a0adac334559dd7`
   and identical 64-byte N64 headers (U v1.0 CRC `66A24BEC 2EADD94F`);
   Homebrew's `mupen64plus.ini` has the matching U v1.0 per-ROM entry
   (`SaveType=Eeprom 4KB`). The oracle passes that data directory to
   `CoreStartup`, explicitly enables the debugger and pure interpreter, and
   attaches input then RSP in the documented order. Thus **H-rom-identity and
   H-core-launch-config are REFUTED** for the checked launch path. Installed
   plugins are audio-sdl, input-sdl, rsp-hle, video-glide64mk2, and video-rice:
   there is only one RSP arm. **H-single-rsp-limitation is SUPPORTED.** The
   oracle remains an unqualified phase witness; obtain an alternate compatible
   RSP plugin before another oracle target-watch or provenance reroll. **s700
   blocker check:** maintenance did not trigger (41,577 bytes) and no alternate
   compatible RSP plugin has been supplied since s699. The required two-arm
   discriminator therefore cannot be run; this is a dependency blocker, not a
   new runtime result. **s701 recheck:** the file is 41,888 bytes and a fresh
   `/opt/homebrew` plus `/usr/local` dylib inventory still finds only the
   already-tested `mupen64plus-rsp-hle.dylib`. Keep the target watch and E9
   tracer unchanged pending a human-provided alternate compatible RSP plugin.
   **s702 fresh dependency audit:** the full local dynamic-library inventory again
   found exactly one RSP dylib, the already-tested Homebrew
   `mupen64plus-rsp-hle.dylib`; the remaining dylibs are audio, input, and
   video plugins. The alternate/current two-arm measurement remains impossible
   to assemble locally, so no one-arm rerun, target watch, or tracer change is
   informative. **s703 recheck:** `docs/CURRENT-TRUTH.md` remains below the
   maintenance threshold (42,516 bytes), and a fresh `/opt/homebrew` plus
   `/usr/local` RSP-dylib inventory still yields only that same HLE plugin.
   The two-arm discriminator remains externally blocked; a compatible alternate
   macOS RSP dylib is required before another oracle run can be evidence.
   **SUPERSEDED s704:** that conclusion was believable because the inventories
   searched only `/opt/homebrew` and `/usr/local`; they omitted the local
   `rs64-oracle` source tree. CXD4 is compatible enough to load and complete
   the control run, but did not change the 320 stall. **s705 launch-mode A/B:**
   exposed `--oracle-debugger` and `--oracle-emulator`. Default
   (debugger=1/emulator=0) and emulator=1 each observed all eleven Starts in
   PIF, ran 4,199/4,200 VI (~70s), recorded 11,786,166/11,788,933 whole-RDRAM
   writes, and never transitioned from 320. **H-interpreter-route is
   REFUTED** with two controlled arms. Debugger=0 ran all presses but reports
   `0 VI/0 hits` by design because the oracle's VI/PIF/watch mechanisms are
   debugger callbacks; that is an absent instrument, not evidence for or
   against **H-debugger-route**. **s706 direct VI poll A/B:** added
   `--vi-poll`, which calls exported `DebugMemRead32` from a frontend thread
   outside debugger callbacks. The first version read before the core powered
   its device and SIGSEGVed in all three arms; after a 100ms post-execute gate,
   default, debugger=0, and emulator=1 all produced the same live control:
   `WIDTH 0 -> 320` at 0.2--0.3s followed only by the boot-origin change.
   The debugger-on callback independently reported `WIDTH 0 -> 320`, all
   eleven presses reached PIF, and both whole-RDRAM controls counted 11,785,945
   writes over 4,199 VI/~70s. Thus **H-debugger-route is REFUTED** and
   **H-core-environment-route is SUPPORTED**: the debugger-off core itself
   remains 320, not merely its callbacks. This does not phase-qualify a target
   watch. **SUPERSEDED s707:** H-core-environment-route was believable because
   dummy video plus debugger/RSP/emulator variants all stayed at 320; Rice
   differs only at the GFX plugin and reaches the documented driven phases.
   **s707 video-plugin A/B:** three concurrent 70-second retail arms,
   each with separate config, eleven PIF-observed Starts, callback + direct
   VI controls, and a whole-RDRAM write watch, cleanly initialized. Dummy
   (4,195 VI; 11,774,568 writes) and Glide64MK2 (4,177 VI; 11,725,357 writes)
   each stayed at 320, but Rice (4,182 VI; 111,727,025 writes) transitioned
   320→640 at VI 99, 640→1024 at VI 1,014, then 1024→512 / `0x006AB400` at
   VI 2,279. Thus **H-dummy-video-route is CONFIRMED**: a real GFX plugin can
   phase-qualify the retail oracle; Glide's live 320-only outcome is plugin-
   specific, not an initialization failure. The oracle recovery-cell watch is
   now qualified under Rice. **s708 Rice recovery-cell watch:** one 70-second
   retail arm with the exact established schedule reached 320→640 at VI 99,
   640→1024 at VI 998, and 1024→512 / `0x006AB400` at VI 2265. All eleven
   Starts were injected, and the simultaneous whole-RDRAM positive control
   recorded 111,111,067 writes; the narrow physical
   `0x0076B768:0x0076B76C` watch recorded **0**. This is a qualified null and
   **single-source support for H-cell-is-runtime-only**, not a final ownership
   conclusion: the next unit adds a same-run surrounding-page write control to
   distinguish a target-specific zero from an otherwise quiescent region.
   **s709 surrounding-page control:** the same 70-second Rice-qualified arm
   again reached 320→640→1024→512 / `0x006AB400`, observed all eleven PIF
   Starts, and recorded 111,080,684 whole-RDRAM writes. The surrounding physical
   page `0x0076B000:0x0076C000` recorded **126** writes while the exact
   `0x0076B768:0x0076B76C` cell remained **0**. This rejects
   H-region-quiescent and gives a second qualified, but still single-source,
   result for **H-cell-is-runtime-only**: retail does not write the exact
   recovery cell during the driven hangar path. It is not permission to remove
   the recomp recovery instrumentation or to claim final ownership; the next
   -421 unit is a static audit of the LLE cap-return path, not another
   unchanged recovery reroll. **s710 static cap-return audit:** complete
   repository enumeration found exactly one `src_kind=2` producer: fixup 10's
   synthetic cap return at `L_1090`. Static table/edge tracing independently
   maps `0x06` to `L_12A0` (save already-advanced parent PC, load child),
   child EndDL to `L_12C4`/`L_12DC` (restore that parent PC), and root EndDL
   directly to `L_10E8`. The command meanings are independently documented in
   `F5-UCODE-REFERENCE.md`. Thus **H-cap-misses-06-return**,
   **H-cap-misses-enddl-exit**, and **H-probe-misattribution are REFUTED**;
   `src_kind=2` is exactly the cap marker. **s711 root-loader state-field
   audit:** all three generated instruction accesses to `0x54($18)` are
   `L_1494` store, paired `L_14B8` renderer-state load, and `L_1E80` root
   fetch-pointer load. The latter has exactly one direct producer:
   `L_1E70` DMA-loads DMEM `[0,0xFFF]` from `DMEM[0x38]`, returns via
   `r31=0x1E80`, then seeds `r17` from DMEM `0x154` and enters `L_1090`.
   Thus the root pointer is loader-DMA data, not the `L_1494` store, and no
   synthetic-cap edge can reach `L_1E80` (it returns directly). This refutes
   **H-root-stale-or-unwritten** for the root-loader path and selects
   **H-cap-never-enters-root-reload**. **s712 fetch-pointer lifecycle audit:**
   all 16 executable generated `r17 =` sites classify as ordinary command or
   inline-data advances, scratch-DMEM DMA setup, a paired `0x06`/EndDL frame
   restore, or the s711 root-loader seed. The only `L_1090` entries are the
   root seed, `L_10D8` normal boundary continuation, and `L_1088`'s DMA-helper
   return (`r31=0x1090` has one producer). Thus **H-r17-stale-reload** and
   **H-r17-unmodelled-dispatch are REFUTED**; H-r17-command-advance is
   supported only statically. **s713 dispatch/advance audit:** the universal
   dispatcher `r17 += 8` and `0x03 → L_14D4 → +16` exactly match MoveMem's
   24-byte total. But the two dispatch tables have zero generated stores and
   are DMA/overlay-populated; `0x05` selects overlay `0x0C` through `L_15AC`
   / `L_1268`, while most reference inline-op table words are not materialized
   in generated C. Thus **H-advance-conformant** and
   **H-advance-mismatch are UNEVALUABLE**; **H-dispatch-table-opaque has
   single-source static support** from table-load and overlay-selection code.
   **s714 live phase-6 table probe:** the positive control is LIVE
   (`0x03→table1:0x14D4`, `0xB4→table2:0x1484`, `0xBF→table2:0x146C`,
   `0xBE→table2:0x12E4`). MoveMem is 0/720--743 and OtherMode-H 0/186--202
   mismatch per phase-6 task. TriGen (15/15 in the first dense task) and Tri
   (1,245--1,372/task) differ when measured from dispatch to the *next fetch*,
   but the observed `+8/+24` totals conflate Tri's documented run continuation
   with one command. This is a qualified instrument result, not a
   generated-advance verdict. Next: reconstruct `r17` at internal Tri/TriGen
   advances, with the same live table control. **s715 internal Tri probe:**
   phase-6 table control again LIVE; `0xB4→0x1484` and `0xBF→0x146C` reached
   `L_13A8`'s exact `+8` non-textured and `+16` textured branches. This agrees
   with the independent reference's conditional Tri steps, so the next-fetch
   mismatch is **not evidence of an individual Tri increment defect** and
   H-tri-run-conformant is supported. TriGen had 9--15 live samples/task but
   never reached the static `L_15AC` marker: its live overlay continuation is
   still opaque. Next: locate that continuation from its live table word and
   instrument its actual `r17` steps; preserve the table control.

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
