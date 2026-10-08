# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4194 (2026-10-07).

**s4263 (latest):** the s4262 "gated triple" is the scheduler's task-completion fan-out: 0x8011A818 is sent by `spTaskSchedulerThread`, 0x8011A7E8 by `dpInterruptHandlerThread` (host backtrace, 2 arms); queues never full, recv==send each second, counters at 0x8011A894/98 fall with the sends. No flag/queue gate: gap = no task completions (absent submissions, cf. s4258). Next: who stops submitting (blocked-recv table by guest tid/mq at mid-gap; NEXT.md). `scratch/agent/s4263_gate.sh`, ROGUESQ_S4262=1.

**s4262:** audio gap is a tid-0 send gate: in gap seconds tid 0 still sends at full VI rate to 0x8010FF50/0x80110750/0x8011A800/0x80128D10/0x80149990/0x80154650, but sends to 0x8011A818, 0x8011A7E8 and 0x80128CF0 collapse together (30/s -> 1-2/s; 2 arms, `scratch/agent/s4262_send.sh`). H-B (missing thr3 reply) refuted; guest ra unavailable (0). Next: name the gate condition in the tid-0 loop (NEXT.md).

**s4256:** s4255 wave verdict: shared-lock 1/4 vs private-DMEM 0/8 crashed; pooled ~2/13 vs ~4/21 is indistinguishable, so the VI-640 crash family is independent of private audio DMEM. `ROGUESQ_AUDIO_PRIVATE_DMEM` now defaults ON (=0 restores the lock; rsp.cpp + tools/s4250_private_dmem.py + patch exported). Default-unset validation `scratch/agent/s4256_default.sh`: 1/4 crashed (SIGSEGV si_addr=0x1399d8000), single wave. Next: measure the default-arm audio task rate over t=18-28 s with a `=0` positive control, then M5 plan Step 9/10; crash writer still unnamed (M3, parked).
**s4255:** shared-lock vs private-DMEM wave: A 0/4, B 1/4 crashed (B crash = NULL deref at far=0x380000000 inside the VI 640 intro, same family as s4253). Pooled with s4251/s4252 about 4/13 private vs 1/9 shared; under-powered, no mechanism named, private-DMEM default stays OFF. Next steps reordered: (1) read the queued `s4255_ab_wave.sh` verdict (4 A + 8 B) in SOAK-RESULTS.md; (2) if B >> A at N>=12 audit audio-thread shared host state, else drop the flag and take the next step in docs/M5-AUDIO-PLAN.md. No conclusion overturned this session.
**s4253 (latest):** the private-DMEM "t~28s crash" is NOT an audio race: across 24 arms (s4252b/d/e) 12/12 crashed arms never left VI phase 640 (last `[phase]` line = 640 at ~2.8s) and 12/12 surviving arms reached 1024 (~14s). Crash site fillSampleStreamRange+8516 = NULL deref (far=0x380000000 = rdram+0x80000000, i.e. guest address 0) at the sample-block cache's FIRST recycle: `[s4234-ENTRY]` n=15.7k-18.6k, head (0x801499E4) = 0x801FAA90 constant while tail changes every call (append/grow path 0x8008FBxx), then head->next==0 with tail!=head. Survivors leave 640 before n~16k and the 1024 transition re-inits the cache (0x8008F8xx). Open: (a) why ~40% of arms never leave the 640 intro; (b) why head->next==0 at first recycle (guest logic or a node clobber; foreign writers to node heap 0x1F9000-0x1FC000 in crash arms were only 0x80001Cxx). Not yet a mitigation target: fix (a) first. Tool: `tools/apply_s4253_listwatch_retarget.py [LO HI]`; the s4222 store watch prints as `[s4239-ringS]` (per-PC aggregate), not `[s4222-S]`.
**s4251 (latest):** private-DMEM crash is not a fixed 28 s event (s4251 crash at 45 s; 5 private arms passed 28 s). Pooled: private+real audio 3/9 crash, shared 1/5, private+silent 0/2 (under-powered). Crash frames are gfx-side with wild ptr; writer unnamed. Default stays OFF. Tool: `scratch/agent/s4251_ab.sh`. Next: NEXT.md.
**s4258 (latest):** residual t≈22-30 dip is game-side (H3): in default arms zero lock wait, audio tasks ≤5.7 ms, dips are absent submissions; positive control arm4 shows the lock wait. gfx_enter counter unwired (always 0).
**s4257:** default private-DMEM confirmed effective (t=18-30 audio 25-36/s vs 7-8/s with =0, same wave) but a residual dip to 0-17/s at t≈22-30 persists; cause unnamed.
**s4250:** `ROGUESQ_AUDIO_PRIVATE_DMEM=1` (private audio DMEM, no `g_lle_task_mutex`) lifts audio from 7-19 to 48-52 tasks/s at t=18-28 (3 A/B pairs), but 2 of 3 B arms crash at t≈28.2 s (fillSampleStreamRange / RT64 copyToRAM) vs 1 of 3 A crash at 60 s. Default OFF. Crash origin unnamed. Tools: `tools/s4250_private_dmem.py`, `scratch/agent/s4250_ab.sh`. Next: NEXT.md.

**s4230:** fillSampleStreamRange+8136 = `lw $a0,0($v1)` at 0x8008FD60 with allocator list head (0x801499E4) == 0 but tail (0x801499B4) = 0x801F9D10 (probe `[s4230-FD60]`, 1 of 6 stale runs). No watched guest store changed the tail after boot init (14 rows), so the writer is unwatched (host DMA/memcpy or an uninstrumented store). Single-run evidence. Tools: `tools/apply_s4230_listwatch.py`, `apply_s4230_fd60probe.py`, `scratch/agent/s4230_listwatch.sh`. Next: host-side write watch over phys 0x1499B0..0x1499E8 (NEXT.md).

Session 4192: M5 A12 de-stub landed. The countdown wait at `0x8014998A` now defaults to a yielding spin (`ROGUESQ_AUDIO_WAIT_NOPUMP` unset = mode 2): the real producer takes the countdown 16 -> 0 in ~200 x 1 ms yields and title/hangar are reached. The old musyxSynthFrame pump left the countdown at 16 (64-pump ceiling, stall row every wait) - it was a silent skip, so the s327 "only decrementer" justification is superseded. `=0` restores the pump, `=1` the deadlocking blind spin (control). Pre-wait width-320 segfault (`si_addr=0x400128d47`) seen in 2 of 6 arm-runs, unrelated. See PORTING-STATE s4192.

Session 4191: caller continuation `0x8008F4C0` (after `jal 0x8008F858`) matched retail in the hangar on v0/v1/a0/a2/s0/s1/s2; title row lost to oracle hit cap (port-only). initSampleStreamBlockCache object path is register-parity clean entry-to-return; no divergence found, so stop parity qualification and take the next M5 de-stub step.

Session 4190: hangar caller-continuation `0x8008F8A8` (return from `rs_malloc`) matched retail on v0/v1/s0/s1/s2; `ra` differs by native-call convention only. Oracle `--watch-pc` never fires on the `jr` delay slot `0x8008F958` (0 hits despite the matched store), so the retail return is unpaired; next watch the caller continuation `0x8008F4C0`.

## Current state

**s4226 (latest):** 3-arm A/B: stale save reaches title 14.7 s + hangar 24.0 s (control); fresh save reaches title only at 49 s and never hangar (nopump=0 identical, so A12 refuted); cause is the save-dependent flow (single-source). See NEXT.md.

**s4225:** with the fresh 7F save the real audio ucode produces NONZERO PCM at title (`[ai-output]` nz~759/768 on 107 of 107 rows; `[pcm-sanity]` callbacks non-silent after title); the `nz=0` / `FNV=0xF59C39C5` zero-payload boundary (s4164-s4224) was a stale-save artifact. Hangar (512) was NOT reached in 200 s with the fresh save (also absent in s4224) - cause unmeasured. Next: NEXT.md.

**s4224 (closes the s4219-s4223 zero-volume chain):** the zero volume was a stale persisted port save (build/saves had 00 00 00 at 0x48; retail/fresh/default is 7f7f7f). With a good or fresh save the cmd 0x15 a0 is 0x7F. The "unrecompiled gap" 0x8002A120..0x8002B18F is libultra EEPROM/controller code natively replaced by librecomp (writer 0x8002A518 = retail osEepromRead). Reset build/saves before any audio A/B; `RS64_EEP_TRACE=1` prints save_read. Next: re-validate M5 audio output with the fresh save (NEXT.md). Superseded: s4222/s4223 "port misses code that fills the source block".

**s4223 (latest, supersedes the s4222 "save-loaded bytes" framing):** the zero volume is a copy chain, not
EEPROM: settings source block 0x80194FC8 (+0x10..0x12 = 7F in retail, 0 in port) -> memcpy to 0x8013A5C0 ->
0x8006E0C8 -> live 0x80130B60..62 -> saved/restored via stack (0x800A5DF4 / 0x800A6528). Retail fills the
source block at PC 0x8002A518 (1 s boot), an address in an unrecompiled gap 0x8002A120..0x8002B18F of the
generated C. 0x800AF60C does not touch the buffer in either build. Next: NEXT.md (name that code, find the
port's writer). Single-run per side.

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and
hangar VI 512 (`0x006AB400`) on the qualified real-audio/LLE/ungated/solo/
spin-yield route. Hangar geometry and color artifacts remain. The real audio
path is not production-complete; `ROGUESQ_AUDIO_UCODE=0` is the silent control.

The active M5 boundary is the source payload and its producer context, not
rendering. Qualified retail and port hangar source spans are zero on the port
(`FNV=0x762B22A5`) but nonzero in retail. The port's exact target-span guest
scalar/non-scalar observations show the legitimate later `rs_memset` clear at
`0x800078E0/0x800078EC`; the earlier nonzero state is written by the host ROM
asset path (`pi_rom_to_rdram`) before the clear. No mitigation or guest
behavior change is authorized from this boundary.

Session 4164 independently requalified M5 Step 3. Declared-size staging
(`0x800`, the OSTask-declared span) and legacy staging (`0xF80`) both reached
title and hangar with matching task/SP/route, zero-payload, and downstream
signatures. The declared arm is sufficient at this boundary; legacy staging
adds DMEM writes without a measured downstream benefit. ORIGIN: `rsp.cpp`
staging DMA is the writer and the OSTask declaration is legitimate.

Session 4167 completed a clean canonical same-build real-image/silent port
pair after two route-invalid attempts caused by missing route flags and stale
game child processes. Both clean arms passed the positive controls, reached
title VI 1024 and hangar VI 512, and had live gate/task/SP/PCM instrumentation.
The gate was `0x01` in both arms; hangar PCM source and consumer rows were
present but zero-valued in both (`384` samples, `FNV=0xF59C39C5`, `nz=0`).
The real image completed its DMEM/DMA path (`break_pc=0x1328`, `dma_count=3`)
while the silent arm had `dma_count=0`. No downstream real-versus-silent
divergence was measured, so H-upstream-zero-payload remains selected and no
gate change is authorized.

Session 4168 reproduced the same boundary with a self-cleaning concurrent pair.
Both arms fired the positive control and reached title VI 1024 and hangar VI
512. In hangar, real-image and silent PCM source/consumer rows were both zero
(`384` samples, `FNV=0xF59C39C5`, `nz=0`); the real arm logged 3,846 audio-stage
rows and 3,890 image-queue rows, while the silent arm logged no image-queue
rows. The silent arm later bus-crashed after the target phases, so that crash
does not invalidate the phase result. This independently requalifies
H-upstream-zero-payload and rules out route invalidity for this clean pair; no
gate or consumer change is authorized.

Session 4169 qualified the port-side gate writer contract in a fresh concurrent
real-image/silent pair. Both arms fired the positive control and reached title
VI 1024 and hangar VI 512. Both recorded the same four gate-writer rows,
including `0x8008EC88` storing `0x01` in hangar after the `0x8008ED48` and
`0x8008EB7C` zero stores. Gate consumers saw `0x01` in 1,021 real and 1,022
silent hangar rows. Real and silent task/SP completion routes were live; real
had image DMA while silent had none. PCM source/consumer rows remained zero in
both arms (`384` samples, `FNV=0xF59C39C5`, `nz=0`). This selects
H-port-writer-parity and moves the open boundary to the upstream producer
context; no writer or gate change is authorized.

Session 4170 qualified that upstream boundary with the independent retail
oracle and the port in one phase-gated run. Both arms fired the whole-RDRAM
positive control and reached title VI 1024 and hangar VI 512. Retail recorded
664 nonzero post-store bytes in the target source span, with writers including
`0x800078EC` and the `0x8008F*`–`0x800910*` producer family. Port source-span
writer/DMA rows remained `FNV=0x762B22A5`, `nz=0`, and its source-context rows
were zero-valued. This selects a producer-context/source-writer mismatch over
producer parity; no writer or payload mitigation is authorized.

Session 4171 qualified the first matched source-span writer family in the
same phase-gated oracle/port run. Retail scalar stores at `0x80090268`,
`0x80090278`, and `0x8008FF04/0C/14` were observed with zero store-sample
mismatches; the port emitted the same PCs in hangar with matching target-span
destinations and nonzero values. Both arms fired the positive control and
reached title VI 1024 and hangar VI 512. Port image DMA and PCM rows remained
zero-valued (`0x762B22A5` source span and `0xF59C39C5` PCM), so this selects
writer-counterpart parity and moves the boundary to caller/object context.
No behavior change is authorized.

Session 4172 landed and built an M5 task-contract guard in the runtime. The
declared audio `ucode_data_size` is now rejected before DMEM staging when it
is zero or exceeds the `0xFC0` DMEM limit; the explicit legacy `0xF80` arm is
unchanged. This protects the task/SP contract but does not explain the
qualified zero PCM payload: the valid `0x800` task remains on the same image
path. ORIGIN: the guest OSTask producer owns `ucode_data` and
`ucode_data_size`; invalid span metadata is not legitimate audio input.

Session 4173 qualified the matched-writer context join with independent retail
and port arms. Both fired the whole-RDRAM positive control and reached title VI
1024 and hangar VI 512. Retail field dumps at all five watched PCs fired in
hangar and showed per-object source words `0x00C0006F/C6/D7/DE`, branch state,
and changing object bases. The port source-context rows remained on the
matched `0x800AB694 -> 0x800078EC` path with target-span bytes zero and the
source-producer rows carrying their existing destination/value records. The
contexts are not equivalent at the measured object/field boundary, selecting
H-context-mismatch; the first divergent object-field input is now the open
boundary. Port image input and PCM remained zero (`0x762B22A5` /
`0xF59C39C5`, `nz=0`). No behavior change is authorized.

Session 4174 added a regeneration-safe port witness for the same five
object/field producer PCs and qualified it against the independent retail
oracle. The whole-RDRAM control fired; the port phase trace reached title 1024
and hangar 512, and the witness control fired once per target phase with 512
capped rows covering all five PCs. After correcting an initial raw-byte endian
mistake, port rows still did not reconcile with retail: object bases/layouts
differed and the port `s0+0x60`, `s0+0x22`, and `s1+0x22` values diverged from
the retail field table. This selects H-legitimate-field-mismatch over an
instrumentation alias; the wrapper's exact-origin verdict was false only
because it missed the observed phase-origin spelling, so raw phase lines are
the route evidence. The first divergent object-field input remains open; no
audio, gate, writer, or payload behavior changed.

Session 4175 tested the first static candidate for the open object-field
boundary, `recycleSampleStreamBlock` at `0x8008F9C8`, with a
regeneration-safe entry snapshot joined to the five target-PC rows. The first
phase-gated version was unevaluable because the entry occurs before the target
VI; the fixed version latched the entry snapshot and emitted it at
target-phase field rows. Both matched runs fired the whole-RDRAM control and
reached retail/port title 1024 and hangar 512, while the oracle reported zero
executions at `0x8008F9C8` (`0x80090268`/`0x80090278` each 73,352 hits;
`0x8008FF04`/`0x8008FF0C` 67,918 hits). Port target-field controls fired in
both phases but produced zero entry joins. This rules out `0x8008F9C8` as the
executed entry boundary; it does not move the object-field mismatch or
authorize behavior changes.

Session 4176 qualified the next independent retail predecessor range. The
whole-RDRAM control and both title/hangar phase gates fired; the range
`0x8008F900:0x8008FB00` executed 4,480,806 times, while exact
`0x8008F9C8` remained at zero. The earliest executed range entry was
`0x8008F900`, entered from `0x8008F8FC` (142 executions). This selects
H-earlier-executed-entry over H-static-entry-unexecuted-at-range and
H-route-invalid, making `0x8008F900` the next port witness boundary. No
audio, gate, writer, payload, or mitigation behavior changed.

Session 4177 independently requalified that retail predecessor boundary with
the exact target-PC joins. The whole-RDRAM control and both title/hangar phase
gates fired; the range `0x8008F900:0x8008FB00` executed, and exact
`0x8008F900` executed 71 times with `PREVIOUS_PC=0x8008F8FC`. This selects
H-entry-executed and makes `0x8008F900` the next port witness boundary. The
retail result is ground truth only; no port, audio, gate, writer, payload, or
mitigation behavior changed.

**s4261:** audio producer into 0x8010FEE0 = guest tid 3 only (ok=7391 fail=2, no refusals); in every t>=20 gap tid 3 waits on 0x8011A818 whose sole sender is tid 0 (~6 sends/s vs ~800/s healthy) while tid 0 wakes every ~10 ms on VI posts but does not send. osSetTimer never called (n=0). Game-side gating in the main loop, not runtime delivery (4 arms agree; single run-set).
**s4260:** per-mq post ages at t>=19.5 audio gaps: VI retrace (mq 0x80114388) delivered within 1-14 ms and main-thread queue 0x80149670 tracks it, but audio/sched queues 0x8010FEE0/0x80128D10/0x80149990 are 90-120 ms stale and thr3 queue 0x8011A818 340-910 ms. Only Vi/Pi host posts exist (no Timer/Ai/Sp/Dp), so s4259's "host message late" is REFUTED; the stall is a guest-internal producer. Single-source. Outlier: arm1 had a 3.5 s total delivery stall with fresh VI enqueues (unexplained).
**s4259:** residual t≈19-28 audio dips are guest-idle: with ROGUESQ_S4259=1 every dip dump shows all 6 guest threads blocked in osRecvMesg (spin refuted; single-source). Next: timestamp host posts per mq to name the late message source (scratch/agent/NEXT.md).

## Next steps

> s4254 correction: VI phase 640 is the ~52-56 s intro (all 22 survivors leave it then), not a "stuck" state; the private-DMEM ~28 s crash lands inside it at varying sites. The free-list chain was intact (len 256) at the crash, so the s4253 head->next / cache-recycle mechanism is unsupported. Probe: tools/apply_s4254_chainprobe.py.
0b. (s4248) **Audio stall mechanism measured: the slow run_task is ~98% waiting on `g_lle_task_mutex` (main.cpp:4806), held by the gfx LLE runner for a whole display list.** Per-task lockwait_us/wall_us: 5.8/6.0 ms pre-stall, 47.9/48.1 ms at t18-21, 103/104 ms at t21-24, max 755 ms; thread CPU only 0.1-0.3 ms (2/2 runs, run21 wall-vs-cpu, run22 lockwait). Not ucode work (c1 refuted), not preemption. Next: design a separate audio DMEM/RSP-state so audio tasks need not serialize with gfx (M5 de-stub step), or measure the gfx hold time per DL to confirm the holder (tools/s4248_summarize.py, ROGUESQ_S4245=1).
0a. (s4249) **Lock holder CONFIRMED (h1): the gfx LLE path holds `g_lle_task_mutex` for whole DLs; audio holds it <1 ms.** Per-3 s windows (run31, ROGUESQ_S4245=1): audio holds n=86-181, max 0.2-0.8 ms every window; `rs64_run_lle_gfx` holds n=6-104, each >=1 ms, max 14-31 ms in t<15, 146 ms at t18, 873 ms at t21, 534-628 ms at t25-28; gfx duty cycle 40% at t15 rising to ~93% at t22-28, which is exactly when audio task count falls 180 -> 22/3 s. factor5_gfx_runner never an outermost holder (always nested inside run_lle_gfx). h3 (fairness starvation by many short holds) refuted: gfx holds are few and long. Single run, but consistent with s4248 lockwait numbers (two lines of evidence). Next: give audio its own DMEM so run_task need not take the gfx mutex (NEXT.md). Instrument: tools/s4249_patch.py (idempotent installer; already applied in main.cpp).
0a. (s4247) Stall mechanism localised: host audio run_task goes from 6-11 ms to 60-860 ms per task for t~19-26 s (2/2 runs), so the audio thread is busy in the ucode, not blocked; gfx tasks never pass run_task. Next: split work vs contention by counting RSP instructions/DMA bytes per audio task alongside wall time. See NEXT.md.
0. (s4246) The s4245 stall recurs at ~t=18.5 s in 2 of 2 runs, no Metal crash (artefact refuted); tasks drop to ~0-30/s until t~25 then resume 60/s, right after a heavy pak-combiner/flush burst. Next: add gfx-task enter/ok and audio-thread block site to [s4245] (NEXT.md).
0. (s4245) Audio producer stalls (task_enter stops ~t=18.5 / task 1061 while AI set-next+VI continue at 60/s) -> stale-ring replay. Find what the guest audio thread/scheduler is blocked on; repeat run (scratch/agent/s4245_rates.sh, ROGUESQ_S4245=1) to see if the stall recurs. Steady-state task rate is 1:1 with AI (60/s); "half rate" hypothesis refuted (single-source).

- s4244: **16-buffer audible periodicity = stale AI-ring re-DMA, not music.** Queued buffers join 343/346 to ucode writes; 62 duplicated queue hashes each map to ONE ucode write; ucode-out has 0 repeats; n-k offset steps by 16 (consumer replays the ring whenever the producer pauses; ~171 writes served ~345 queues). Open: why the audio task makes ~1 buffer per 2 AI periods. Next: audio-task submit/complete/osAiSetNextBuffer counts per phase (NEXT.md). Two lines of evidence.
- s4243: audible-PCM "repeated RMS" was sampling aliasing; no consecutive-buffer repeats (0/1660); 16-buffer periodic hashes remain (loop vs stale ring) — see scratch/agent/NEXT.md.
0. (s4242) **The audible path had the s4239 byte-order bug too**: `main.cpp queue_samples` fed SDL byte-swapped PCM (old-order RMS ~18.5k noise vs correct fade-in 1->520 on the same buffers, same-run control). Fixed with `^3`. ai.cpp/audio.cpp audited; no other s16 readers. Single run, not yet confirmed by ear. Open: identical RMS at consecutive buffers n=1616/1632.
0. (s4241) Retail oracle (s4238_clip/oracle.log) ALSO emits constant rms=33 AI buffers at title (n=1..7) and hangar (n=1..8) entry, then zeros, audible by n=128: the port's -33 x19 entry transient is BENIGN prefill (hypothesis b not supported; stretch 19 vs 8 buffers is single-run/unaligned). Remaining: ^3 audit of other TO_PTR audio readers; RMS 4.7k vs 1.4k phase alignment.
0. (s4240) With the FIXED reader the hangar entry is still a real transient: hangar AI buffers n=1..19 are constant L==R==-33 (distinct=1), n=20 all zeros, wide-band (distinct ~190, peak 2-19k) from n=128; title n=1..3 are also constant but ramping (-213,-208,-203). So the s4239 'hangar must be re-measured' item is DONE: transient real (not a logger artifact), small amplitude, not hangar-specific. Single run (run1, VI 512 at 72.2s). NEXT: does retail title entry also emit constant buffers for its first N AI buffers (oracle per-buffer distinct counts n=1..40) -- benign prefill vs late voice start; plus ^3 audit of other audio rdram readers. See NEXT.md.

0. (s4239) **SUPERSEDES s4235-s4238 AI-output statistics: they were a host byte-order instrument artifact.** `ai.cpp` read the AI buffer with `TO_PTR` bytes in host (word-swapped) order, so every s16 pair was byte-swapped: small samples read as loud wide-band noise (the 'clipping', '13x hot', 'hangar constant DC ramp +0x100/buffer', 'identical 19/25 buffers' were that). Fixed (`p[i ^ 3]`); with it 876 of 894 title AI buffers FNV-match a ucode `0x6F0/0x300` DMA output exactly (independent join; before the fix 10/826), and AI RMS ~4.7k tracks ucode RMS ~4.7k with no guest store into the ring after init (store watch control fired: memset PC 0x800078EC). So the ucode->AI path is intact and NO over-gain stage was found. Residual: port title RMS ~4.7k vs retail oracle 1.4k (oracle used raw physical bytes = correct order) is ~3x, but phases are not sample-aligned (single run each). The hangar DC ramp (s4235-s4237) must be re-measured with the fixed reader before any hangar conclusion. Next: NEXT.md. Tools: `scratch/agent/s4239_stage.sh`, `tools/apply_s4239_ringwatch.py`, `ROGUESQ_S4239=1` (`[s4239-dma|out|ai]`).

0. (s4237) SUPERSEDES s4236: hangar AI output is a DC ramp (+256/buffer, distinct=1) only for the first ~19 buffers after hangar entry (then one zero buffer); from n=128 it is wide-band (distinct ~188, +-32.7k) like title; hangar phase-5 ucode mix buses are populated. The 'constant DC hangar' conclusion was a window artifact. Open: (a) writer of the 19-buffer entry transient (low value), (b) title and hangar both reach +-32.7k - quantify clipping fraction vs retail oracle title AI buffers. Hangar claim single-source (one run, title control in same run).


- **s4231 note:** allocator-list head==0/tail!=0 (s4230) NOT reproduced in 6 stale runs with host DMA watch + 200us poll (dmaHIT 0/6, controls fired, head/tail always written together by guest). Treat s4230 as single-source/possible probe artifact. New dominant crash PCs: last-guest-pc 0x8000b650 (3/6), 0x80001b08 (2/6) - classify next.
0000. (s4229) The s4228 'early crash at spTaskSchedulerThread+9632 / 0x8000834c' and the rs64_s3308_stage_adv crash were OUR diagnostic probes using `MEM_x(..., 0x8…u)` (zero-extended base -> rdram+0x1_00xx_xxxx, unmapped). Fixed by `S32(0x8…u)` as the reg arg with a SIGNED offset (unsigned offset re-zero-extends). Class-closed by grep in generated code + fixup/apply scripts (4 sites). Remaining real audio crash: fillSampleStreamRange+8136/+932 (fault rdram+0x80000000 = null guest ptr, last-guest 0x8000b650/0x834c). Supersedes the s4228 line below.
0000. (s4228) Audio crashes at 0x8000834c (spTaskSchedulerThread+9632, SEGV, ~1-3 s) and 0x8000b650 (SIGABRT) occur under BOTH fresh (0x7F) and stale (zero-volume) saves: 1/5 fresh, 1/2 stale in 100 s (small n, tally only) -> not caused by nonzero volume. Fresh save + shifted keys reaches hangar (VI 512) at ~72 s (2/5). Next: classify the 0x8000834c early crash (writer of bad pointer, x19=0xffffffff8011a89c in stale2) before any guard.
000. (s4222) ZERO-VOLUME ROOT NARROWED TO SAVED SETTINGS. Port's applyMusicOrSfxVolume cmds 0x15/0x16 carry a0=0 (retail 0x7F) because volume-settings bytes 0x80130B60..62 are zeroed by 0x800A6528/6530/653C (copy from stack buf sp+0x88.. filled by jal 0x800AF60C save/EEPROM load); retail runs the same PCs and ends 0x7F. Evidence: retail write-watch (`run_s4222_retail_v.sh`), retail cmd twin (`run_s4222_retail_c.sh`), port `[s4222-S/V/C]` (`s4222_chain.sh`). Single-source for the save-load link. Next: see NEXT.md.
00. (s4221) WRITER CHAIN NAMED, H-writer-runs-zero-input SELECTED (H-writer-never-runs, H-overwritten refuted). Retail oracle write-watch: record gain words +0x00..+0x0C are stored only by musyxKeyOnVoice 0x80090CA4/B0/BC/C8 (11092 hits each), from voice-state halfwords +0x6E..+0x74 <<16, which musyxRenderVoiceSamples copies from trunc(s1[0x44..0x4A] * float s1[0x5C]) (0x80090948..0x800909DC). Retail writers of voice-object +0x44..+0x4A (objects 0x801714D0 + k*0x88, same addresses as port) are only computeVoiceVolumePanCoefficients 0x80094198/942BC/942C0/94338. Port hooks (`tools/apply_s4221_{gain_writer,pan,coef}.py`, ROGUESQ_LOG_S4221=1, `scratch/agent/s4221_gain.sh`): key-on writer runs every voice (4205/4948 calls) but gain_src is 0 in phase 4 (0/4948 nonzero; phase 3 3745/4205 = control); h44..4A zero with float s1[0x5C] valid (0x3F800000); computeVoiceVolumePanCoefficients runs (424 sampled rows) with volume arg (sp+0) = 0 and pan arg (sp+0x14) = 0 while its tables at 0x800A4BD8/4DD8/4DE8 are nonzero. Its only caller is setVoiceModulationParams (0x800923E4), called from 0x8008D710/0x8009818C/0x80098264; s4079 already showed the port's 0x8008D710 call carries a1=0/a3=0 where retail carries nonzero (e.g. 0x004A79E0). Next: trace those call inputs back (scratch/agent/NEXT.md). Caveat: coef hook has no phase-3 positive control (phase-3 voices got their h44.. nonzero by another route or the phase label lags the first rows); retail side relies on watched PCs, not a value comparison at 0x80094198.
0. (s4220) SELECTED H-param-zero: port voice records have zero per-bus gain words (+0x00..+0x0C) in phases 4/5 (0/181 rows nonzero) vs retail 14/16 nonzero; ucode mix buses 0x3F0/0x570 never written (s4220 DMEM snaps, three views agree). The ucode is exonerated. Next: find the guest writer of record +0x00..+0x0C (port store-watch with PC + oracle write-watch), then why it writes 0 (scratch/agent/NEXT.md). Retail side single-source (voice 0).
1. (s4219, now superseded as lead by item 0) Retail output buffers are ~98% nonzero at title-1024 n>=256 while the port's are all-zero, and the voice records are equal (s4218): the defect is the port's RSP/ucode consumption. Find the first zero-producing ucode command for one voice (scratch/agent/NEXT.md). Single-source (oracle).

Session 4218: port voice records (active=15, state 0x80178C80, block 0x171CE0, output ring) MATCH retail at end-state -> H-records-equal; producer side exonerated, divergence is in ucode consumption of identical input. Next: retail post-task contents of the +0x7C output buffers (nonzero?) vs port zeros (s4208) to pin it to RSP execution; if retail is nonzero, diff DMEM/command execution on one voice.

Session 4217: retail data_ptr block ALSO has ASCII names (+0x40 'ltext_cache_3') early, real records (p801~100) from task n~256 -> s4214's "not audio records / builder-wrong-target" inference is void (retail identical in kind); block content is not the divergence. Next: field-by-field retail/port voice-record (+0x10, stride 0x50) compare at equal phase/ordinal.

Session 4215: raw guest OSTask words (struct at RDRAM 0x149470) equal host-read fields -> H-task-struct-stale refuted; data_ptr alternates 0x8016BD50/0x80169F10 in phase 2. Next: guest writer PC of 0x1494A0 (check M5-S3482-TASK-WRITER-JOIN.md first). Session 4216: writer already named (PC 0x8009177C, s3482-s3486); retail stores same 7728 B blocks -> H-builder-wrong-target refuted; next: retail content dump of 0x171CE0 (docs/M5-S4216-DATAPTR-RECONCILE.md).

Session 4214: audio data_ptr block (menu heap) holds ASCII filenames + 0x28-stride pointer structs that change per task, not audio records -> H-cmdbuf-never-built refuted, H-builder-wrong-target selected (s4212 ownership + s4214 content). Next: writer of OSTask.data_ptr (NEXT.md).

Session 4201 (single join, s4200 log): AI source and `queue_samples` consumer PCM agree 124/124 by FNV; hangar buffers are 81/81 all-zero at source (guest silence -> M5 Step 9, voice/MORT gap); title has 19 fully-nonzero buffers (every byte nonzero, atypical for real PCM; content unverified). `tools/pcm_join.py <log>` reproduces it. Next: dump title buffer samples + hangar voice-slot state.
Session 4204: at the key-on tail every voice's source bytes are NONZERO in all three phases (`[m5-voice-src]`: src_nz=n, src_zero=0, src_bad=0, positive control ctl_nz=n; phases 3/4/5 n=4096/4864/139520 floors; p28/p2c/p40 each 55-64 of 64 bytes nonzero, p30=length/flag word, p34=0) -> H-voice-no-decode REFUTED at the guest-bytes edge (single-source, port only; what p28/p2c/p40 ARE — sample vs codebook vs envelope — is not yet identified). Zero PCM therefore arises in the guest-built audio command list or the ucode: H-mix-drop selected, see NEXT.md. **REGEN WARNING (s4204): the documented `N64Recomp -> fixup_game_funcs.py` full flow is BROKEN (aborts at s3290 entry E088 after fixing the s2173/s3341/s3530/s4079 anchors; likely more). A regen clobbers the live patched RecompiledFuncs, which is gitignored-by-practice and uncommitted. Never regen; patch the live tree with `tools/apply_s*.py`. s4204 clobbered it once and rebuilt it as `RecompiledFuncs.s4082.before` + apply_s4140..s4199 + A13 gate + apply_s4204 (backup `RecompiledFuncs.s4204-reconstructed`); the s4083-s4087 voice-modulation probes were NOT replayed (now opt-in `RS64_S4079_PROBES=1`).** The pre-title `spTaskSchedulerThread+9632` crash is flaky, not a reconstruction artifact (hit once, absent on identical rerun).
Session 4205: guest-built command-list records at the render jal (0x80090F00) are nonzero 100% of the time (phase 3/4/5 n=4096/4608/138752, rec_zero=0, positive control ctl_nz==n; `[m5-cmdlist]`, `tools/apply_s4205_m5_cmdlist.py`, `scratch/agent/s4205_cmdlist.sh`) -> H-list-silent weakened (volume field not yet identified; single-source, port only); H-ucode-drop leads. Next: hash buffers referenced by the records around audio-task completion (NEXT.md).
Session 4203: voices ARE keyed on in title+hangar (key-on entry>=22, normal_tail>=21, slot 01->02->00; `scratch/agent/s4203_keyon_census.sh`, single-source, counts are floors) -> H-no-voices refuted; open: H-voice-no-decode vs H-mix-drop, see NEXT.md.
Session 4202 (`[pcm-samples]` in main.cpp consumer): the 19 title nonzero buffers are an exact 2-value L/R alternation decaying ~3%/buffer (424/148 -> 411/143 ...) = released DC, not audio; 535 others (all 296 hangar) are min=max=0. Both arms identical in shape. So no real PCM content on title or hangar; next: MusyX active-voice count / first voice-start (Step 9).

Session 4178 qualified the regeneration-safe port witness at `0x8008F900` in
a paired oracle/port run. The whole-RDRAM positive control, both retail target
phases, and both port target phases fired. The port witness joined to the
existing object-field witness in title and hangar, proving the predecessor
executes on the qualified port route. The oracle emitted no phase-gated field
rows for `0x8008F900` because its observed retail origins were
`0x00790800`/`0x006AB800`, while the recipe gated `0x00790400`/`0x006AB400`;
entry-context parity remains unevaluable. This rejects H-route-invalid but
does not select H-entry-context-match or H-earlier-producer-mismatch. No
audio, gate, writer, payload, or mitigation behavior changed.

Session 4180 reran the paired predecessor measurement with isolated output and
the stable retail phase origins. The whole-RDRAM positive control, both retail
phases, both port phases, and both port predecessor joins fired. Retail's
`0x8008F8FC` and `0x8008F900` rows each had 71 hits and showed
`s0=0x48`, `s1=0x1B000`, `source_word=0`, `branch_selector=1`,
`branch_state=0x1100`. Port predecessor joins matched `s0=0x48` and
`s1=0x1B000`, but its helper reported pointed fields as `0xFFFFFFFF` because
it rejects those low raw register values as non-KSEG pointers. This selects
H-predecessor-register-parity and identifies the source/branch comparison as a
measurement-alias defect; the earlier s4179 divergence conclusion is
superseded. No audio, gate, writer, payload, or mitigation behavior changed.

Session 4181 repaired the port predecessor witness to use raw physical-address
semantics for low `s0`/`s1` values, then reran the paired measurement. The
whole-RDRAM control, both target phases, 71 retail hangar predecessor hits,
and two port joins all fired. At the shared hangar phase, retail and port
matched `s0=0x48`, `s1=0x1B000`, `source_word=0`, `source_byte=0`,
`branch_selector=1`, and `branch_state=0x1100`. The first attempt was
unevaluable because the recipe used stale retail origin `0x006AB400`; the
corrected rerun used observed retail origin `0x006AB800`. This selects
H-entry-body-mismatch: the predecessor context is parity and the next boundary
is inside `0x8008F900`. No audio, gate, writer, payload, or mitigation
behavior changed.

Session 4182 added a regeneration-safe witness at the pre-instruction body
boundary `0x8008F900`, recording raw registers and first derived store
addresses/values. The body begins with arithmetic and stores rather than a
guest load, so the witness does not invent one. The retail oracle arm passed
the whole-RDRAM control, reached title/hangar, and recorded 71 phase-gated
`0x8008F900` executions using both observed title/hangar origin variants. The
real-audio port arm crashed before title at `spTaskSchedulerThread+9772` (last
guest PC `0x8000834c`); the silent port control stopped at width 640. Neither
port arm qualified a target phase, so zero port body rows are route-invalid and
do not select body mismatch or parity. The body boundary remains open; no
audio, gate, writer, payload, or mitigation behavior changed.

Session 4183 reran the body discriminator after correcting its port arm from
silent to real audio. The retail positive control and both title/hangar phases
qualified, but the silent attempt crashed at VI width 320 with SIGSEGV and the
real-audio attempt stopped at the same width with SIGBUS; both reported
`spTaskSchedulerThread+9772`, last guest PC `0x8000834c`. Neither port arm
reached a target phase or emitted body rows. This independently requalifies
H-body-route-invalid; body mismatch versus parity remains unevaluable. The
recipe still lacks the canonical autopilot/stop-width settings used by the
earlier qualified route, so no body, audio, gate, writer, payload, or
mitigation conclusion is authorized.

Session 4184 restored the canonical autopilot schedule and
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512` in the existing body-witness recipe. The
whole-RDRAM positive control, both retail phases, both port phases, and 130
port body rows qualified (59 title, 71 hangar). At the shared hangar body
entry, port rows matched the independent retail execution tuple for
`a0/a1/a2`, `s0/s1`, and the first derived store value; the retail field tuple
also matched (`s0=0x48`, `s1=0x1B000`, zero source word/byte, selector `1`,
state `0x1100`). This selects H-body-entry-parity and moves the open boundary
after the first body stores. No audio, gate, writer, payload, or mitigation
behavior changed.

Session 4185 extended that canonical paired run with an independent oracle
physical watch for the body-store range and exact `0x8008F90C`/`0x8008F910`
store PCs, including post-store scalar controls. The whole-RDRAM control,
both retail phases, both port phases, and 130 port body rows qualified. At the
shared hangar tuple, retail and port matched the body store/link addresses
(`0x8017D9E0`/`0x8017D9F8` and `0x8017D9FC`) and both exact retail store PCs
had nonzero, mismatch-free post-store samples. This selects
H-next-store-parity and moves the open boundary after the second body
store/link tuple. The oracle GPR callback does not expose a stable written
value field, so the conclusion is limited to the independently matched
address/link and scalar-write contract; no audio, gate, writer, payload, or
mitigation behavior changed.

Session 4186 extended the same canonical paired run to the loop-control tuple
at `0x8008F914`/`0x8008F918`. The whole-RDRAM positive control, both retail
phases, both port phases, and 130 port body rows qualified; port emitted 260
loop rows. At the shared hangar phase, port showed `a2=0x47` then `0x48`,
`s0=0x48`, and compare `1` then `0`. Independent retail execution watches
recorded 71 hits at each exact PC with the same `s0=0x48`, `s1=0x1B000`, and
the expected predecessor relation. This selects H-loop-control-parity and
moves the open boundary to the `0x8008F91C` loop branch. No audio, gate,
writer, payload, or mitigation behavior changed.

Session 4187 extended the canonical paired run to the `0x8008F91C` branch.
The whole-RDRAM positive control, both retail phases, both port phases, and
130 port branch rows qualified. Port took the branch for `a2=0x02..0x47` and
fell through at `a2=s0=0x48` in both title and hangar. Independent retail
recorded 71 branch hits with the same `v0=1` for 70 iterations and `v0=0` at
the terminal iteration. The oracle's `0x8008F920` watch had zero hits because
its debugger accounts for the delay-slot execution under the branch PC; this
is a measurement limitation, not a route failure. This selects
H-branch-parity and moves the open boundary after the delay-slot increment,
at the loop exit successor. No audio, gate, writer, payload, or mitigation
behavior changed.

Session 4188 extended the canonical paired run to the loop-exit successor at
`0x8008F924`. The positive control, both retail phases, both port phases, and
two port successor rows qualified. At the terminal hangar iteration, port and
independent retail matched `v0=0`, `a2=s0=0x48`, and the unchanged predecessor
context; the oracle recorded the same successor PC. The first post-loop load
is `0x801499C8`, and the port witness read `0xE0D91780` there. This selects
H-successor-parity and moves the open boundary into the first post-loop loaded
state. No audio, gate, writer, payload, or mitigation behavior changed.

Session 4189 extended the canonical paired run to the first post-loop load/use
at `0x8008F928`, `0x8008F938`, and `0x8008F93C`. The first attempt was
route-invalid because the port crashed at `spTaskSchedulerThread+9772` before
VI 320; the fixed rerun qualified the whole-RDRAM control, both retail phases,
and both port phases. At the shared hangar phase, the independent retail oracle
and port matched the loaded word at `0x801499C8` (`0xE0D91780`), the loaded
`v1` (`0x8017D9E0`), the derived `v0` (`0x8017E0A0`), and the resulting store
address (`0x8017E088`). Title tuples also matched (`0x402C1980`,
`0x80192C40`, `0x801931E0`, and `0x801931C8`). This selects
H-load-use-parity and moves the open boundary to the post-loop store/caller.
No audio, gate, writer, payload, or mitigation behavior changed.

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 audio de-stubbing:** (s4200: A13 drain-tick gate was NEVER in generated code (reader only in incremental fixup mode); now in full fixup flow, applied and rebuilt; drainAudioAndFinalizeSpeechBuffer not entered on title+hangar in either arm (0 drain-tick/exit logs, single-source) -> A13 dormant there, closed like A14/A15; next = Step 9/10, see NEXT.md. s4199: A15 ROGUESQ_SPIN_YIELD now default-on (=0 off); 0 spin-yield fires in both arms, both reach hangar -> A15 dormant on title+hangar once A11 yields, closed; next = Step 6/A13 drain-tick validation. s4197: ROGUESQ_WAITFORSLOT_YIELD=2000 removes the A11 cap fire 1->0, single-run; REPEATED s4198 and now DEFAULT (unset=2000; =0 restores old behaviour; =0 control stalled pre-title). s4196: A11 pre-title slot-0 stall = tick-starved non-yielding spin, producer live, cap 5M also fires; next = yield in waitForAnyAudioSlot spin) A12 countdown wait de-stubbed (s4192); A12 second spin at `0x8014974C` CLOSED as never-stuck (s4193: entered once, flag already 0, no spin; nothing to de-stub). A14 status-03 shutdown wait CLOSED as never-entered (s4194: 4/4 entries status 0x00, call 2 only; tools/audit_a14_shutdown_wait.py). M5 Step 8 voice-base (A9, 12 sites) and song-tick-table (A10, 43 sites) guards CLOSED as never-firing on title+hangar (s4195: all fire-logs armed, 0 fires; control = A11 `waitforslot-guard-fire`, so single-source for the other classes). That A11 500k cap fired once PRE-TITLE (phase 3 width 640, slot-0 byte stuck 0x02): next lead, see NEXT.md (m5-a11-pretitle-slot-stall). Object-path parity qualification is closed (s4187-s4191); do not add witnesses there.
2. **M3 pre-publication guard runtime qualification** remains blocked on a host
   with `mips64-elf-gcc`/`mips64-elf-ld` and a configured `PatchesLib` target;
   do not spend another host-only iteration.
3. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
   writer, or audio work. Keep slug `generated-symbol-renaming-sweep` if it
   resumes; mapping-only edits do not reset the engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 producer absent | Hangar source-span census is closed as retail parity at the measured boundary. The missing port nonzero payload is upstream/earlier provenance, not an established missing guest store. |
| M5 pre-clear provenance | H-host-ROM-writer selected at s4163: `pi_rom_to_rdram` writes legitimate nonzero target bytes before the later guest clear; generated guest scalar and non-scalar target rows are zero-valued at the clear. |
| M5 source setup state | H-shared-source-state selected at s4150: independent retail and port setup tuples match for the title clear and dominant hangar source-construction calls. The setup boundary is not the measured explanation for the later zero producer payload. |
| M5 producer caller state | H-caller-state-split selected at s4152, with s4153 selecting H-entry-body-shared: retail preserves producer object/state into `0x800078EC`, while port context differs earlier. Generated port `ra=0` is an instrument limitation, not guest evidence. |
| M5 Step 3 declared audio staging | H-step3-equivalent independently requalified at s4164: declared `0x800` and legacy `0xF80` arms match at the measured downstream contract. Semantic irrelevance outside that contract is unproven. |
| M5 Step 4 retail gate ground truth | H-retail-gate-writers selected at s4166: the independent oracle whole-RDRAM control fired in both target phases; `0x800A0F50` was written 14 times by five PCs, with `0x8008EC88` producing the observed nonzero value. The watched `0x80094648`, `0x80090AAC`, and `0x80090BA4` words had zero writes in this retail route. This selects the port parity measurement, not a gate change. |
| M5 Step 4 port parity | H-upstream-zero-payload selected at s4167: the clean canonical pair reached title/hangar and live gate/task/PCM controls. Both arms had gate `0x01` and zero-valued hangar PCM source/consumer rows; only the real image's DMEM/DMA activity differed. The initial route-invalid attempts are excluded because they stopped at VI 640 or crashed with stale game children present. |
| M5 Step 4 producer context | H-writer-counterpart-parity selected at s4171: retail and port both exercised `0x80090268`, `0x80090278`, and `0x8008FF04/0C/14` in hangar; port target-span rows carried matching nonzero values and destinations. The downstream port DMA/PCM remained zero-valued, so caller/object context is the next boundary. |
| M5 writer object context | H-context-mismatch selected at s4173: retail field dumps fired for all five PCs and showed changing per-object source words/branch fields, while the port matched source-context path retained zero target-span values and did not expose equivalent object-field state. The first divergent object-field input is open; no behavior change is authorized. |
| M5 object-field witness | H-legitimate-field-mismatch selected at s4174: the corrected port witness fired in both target phases and recorded all five producer PCs. Its runtime-memory field values and object records did not reconcile with the independent retail field table after using `MEM_W/MEM_BU/MEM_HU` semantics. The earlier raw-byte result is superseded as an endian instrumentation defect. |
| M5 object-entry boundary | H-entry-body-mismatch selected at s4181: after repairing the port witness to raw physical-address semantics, retail and port matched `s0=0x48`, `s1=0x1B000`, source word/byte, selector, and branch state at the shared hangar phase. The open boundary is inside `0x8008F900`. |
| M5 object-body witness | H-successor-parity selected at s4188: the canonical route qualified both target phases and two port successor rows; independent retail and port rows matched terminal `v0=0`, `a2=s0=0x48`, and the successor PC. The first post-loop load is `0x801499C8`; the open boundary is its loaded state/use. |
| M5 object load/use witness | H-load-use-parity selected at s4189: the qualified paired route matched the independent retail loaded word, loaded `v1`, derived `v0`, and post-store address in both title and hangar target phases. The open boundary is the post-loop store return/caller. |
| M5 task contract | H-contract-gap selected at s4128: image task handoff/completion is live, but image and silent controls both have zero measured PCM payload at the tested scope. |
| M5 consumer disconnected | Selected at the measured task/output scope; upstream zero payload remains open. |
| M5 title host sink | H-play selected at s4065: device 2 opens, host queue calls are positive, and drain depth advances. Native device callback/output behavior remains open. |
| M5 image zero boundary | H-guest-zero-producer selected at s4112: qualified port arms recorded zero-valued `0x800078EC` stores into the source span before zero image reads; host writeback is downstream zero data. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| M5 descriptor selector writer | H-port-writer-live selected at s4100: port witness rows fire and `0x80090AAC` has retail-matching selector values; `0x80090BA4` has no port rows. |
| M5 key-on early returns | H-returns-dead/H-guard-valid selected at s4101: valid divisors, normal tails, and slot transitions; no guard relaxation authorized. |
| M5 drain-tick policy | H-Drain-Changes-Ordering remains qualified at s4103/s4114. Tick-required behavior is not established because the reverse-order arm was route-invalid. |
| M5 status-03 reaping | H-status03-after-return selected by qualified port ordering at s4136: service entry, read, `03 -> 00` store, and exit are ordered after the observed shutdown return. No force-clear or wait change is authorized. |
| M5 A10/A9/A8 guards | A10 and A9 guards are not suppressing measured valid work; A8 trap PCs are live but do not fire on qualified retail/port routes. No relaxation is authorized. |
| M5 A11 wait terminal transition | H-target-phase-absent-both selected at s4145: target-phase wait/post-wait terminal rows were absent in both qualified arms. This is not a safety proof. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime remains unqualified because this macOS graph lacks the MIPS toolchain and `PatchesLib` target. |
| Generated symbols | Parked until higher-priority M5/M3 work is inapplicable. |

## Durable evidence boundary

Retail reaches title/hangar and can attribute relevant writer PCs. The paired
port can reach image-DMA joins when its arm completes. The port task
`0x80171E70`, size 1, joins the exact input DMA at matching generations, but
payloads are zero; separate writeback joins are real. The task and output edges
therefore execute, but zero payload does not identify the missing upstream
writer.

The qualified consumer comparison used same-build declared/real,
declared/silent, and legacy/real arms. It found matching phase-5 zero-payload
signatures. A route failure invalidates a null; it never proves absence.

Session 4166 supplied the independent retail line for Step 4. The oracle's
whole-RDRAM watch reached its 10,000-callback positive-control threshold and
the driven route reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`. Its narrow gate watch recorded 14 writes: the writer set was
`0x8008EA34`, `0x8008EB40`, `0x8008ED48`, `0x8008EB7C`, and `0x8008EC88`;
post-store samples were zero for the `ED48`/`EB7C` rows and nonzero for the
`EC88` row. The three candidate consumer/selector watches had no writes.
This is independent retail evidence only; port parity and downstream joins
remain open.

The title playback/drain capture is independently controlled by retail
whole-RDRAM and title/hangar AI-output witnesses. On the paired port,
declared-real reaches both phase gates and host enqueue/raw drain rows are
positive in both phases. This closes immediate queue-drain starvation at the
measured SDL queue boundary, not device delivery to audible output.

## Superseded conclusions

- (s4240 narrowing of s4237) 'Hangar entry DC ramp +256/buffer' was believable from the byte-swapped logger; with the fixed reader it is a constant -33 fill for 19 buffers (no ramp), then one zero buffer. Entry transient is real, ramp magnitude was artifact.

The s4179 H-earlier-producer-mismatch conclusion at `0x8008F8FC` is
superseded by s4180. Its retail row was valid, but the port helper's
`0xFFFFFFFF` fields came from a KSEG-only guard while the shared predecessor
registers were low raw values (`0x48` and `0x1B000`), so those fields were not a
like-for-like comparison.

The s4180 H-predecessor-register-parity conclusion is refined by s4181: the
shared register values were correct, but the pointed-field reads were not yet
like-for-like. The corrected raw-address witness and independent retail rows
now establish parity at the shared hangar phase; the open boundary is the
`0x8008F900` body.

The overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input
and wait-return explanations, global-zero image-DMA theory, route-wide PCM-gap
theory, and force-zero default policy are superseded at their measured scopes.
They were plausible before qualified routes, same-build controls, or
independent retail attribution existed.

The early staging-based route explanation is superseded by same-build route
tables: launch order and timing affect qualification, but neither staging size
nor real-audio mode alone explains the measured boundary. The s3579–s3584
stored-value inference is unsupported because a retail byte store was compared
with an aligned word containing neighboring bytes.

The s4075 missing-store inference is superseded by the source audit: the
generated source contained the store and the fixup had silently omitted its
witness. The s4088 detail-hook conclusion is superseded by s4089, where a
corrected callsite fired the positive control. The s4149 setup/state
route-invalid conclusion is superseded by s4150's route-stable retail match.

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
MusyX/MORT audio remains partially stubbed; MusyX data must not be sent to
stock `aspMain`.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions and batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Evidence index

See [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md),
[M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md), and
[M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md).
Detailed counts and session-specific notes remain in `PORTING-STATE.md`.
- s4206 (m5): rec volume (+0x58) and source buffers nonzero in 100% of 139264 hangar records; H-list-zero-volume refuted, H-ucode-drop leads (see PORTING-STATE Session 4206).
- s4207 (m5): after audio task returns (exit=1), +0x7C output buffers are zero in 100% of phase 4/5 records (hangar 0/138065, src 137561 nonzero; phase 3 control out_nz 3348/3973); H-downstream refuted, H-ucode-drop selected, H-wrong-ptr open. Next: AudioDmaProbe ranges vs +0x7C addresses (PORTING-STATE Session 4207).

- s4208: audio ucode DMA writes into +0x7C buffers are all-zero after early phase 4 (15.0 MB written, nz bytes frozen at 264405; phase-3 control nonzero). H-writes-zeros selected; next is Step 9g in scratch/agent/NEXT.md.
- s4209: RDRAM->DMEM reads to the audio ucode are nonzero and copied exactly in phases 4/5 (59.2 MB nz of 77.8 MB; nzsrc_but_zero_dmem=0) while output writes stay zero. H-src-dma-zero refuted; H-state-zero vs H-cmd-skip open (Step 9h).
- s4210: audio ucode processes ONE 0x50-byte record per task in all phases (H-cmd-skip refuted); phase 3 record valid + nonzero writes (control), phase 4/5 record at data_ptr 0x80171CE0/0x80171E70 is ASCII filename text ("expl","mat_11","tie_") and writes are zero => H-cmdbuf-aliased selected (single-run). Next (Step 9i): guest-store watch with PC on that cmd buffer range.
- s4211: audio task data_ptr buffers get 0 PI-DMA overlaps (9 dp, ring complete) but change every task (9212/9212 phase 5) => written by guest stores; text there (mat_11, ltex_cache_329) is a second heap owner. H-cmdbuf-aliased refined to H-heap-ownership; next Step 9j = guest malloc/free/memcpy overlap log (NEXT.md).
- s4212: the s4211 data_ptr pairs are plain rs_malloc blocks (7728 B x2 + a 2040/2448 B header, allocated at phase entry, freed at phase exit; 0x80171CE0/0x80173B20 phase 4, 0x80171E70/0x80173CB0 phase 5). Not double-owned: either the task classified as audio is mis-classified or its data_ptr is stale. Next: NEXT.md Step 9k.

### s4227 addendum
Fresh 7F save: intro->title at ~48 s; Start leads to the first-run SELECT GAME / pilot-create menu (not hangar); s4226 "no hangar" = input mismatch. Fresh-save runs crash at varying audio sites (fillSampleStreamRange+8136; 0x80001b08) - next: tally (NEXT.md).


## s4232 addendum
The s4231 crash PC 0x80001b08 was OUR rs64_log_ai_output probe (zero-extended TO_PTR; fixed). last-guest-pc is not the fault site: use the host pc-symbol. Remaining real faults: fillSampleStreamRange (+8292 NULL deref, +932 garbage ptr 0x10CF300D); one MetalFramebuffer null-ctor. Next: re-run the 6-run listwatch with the fix, and map fillSampleStreamRange+932/+8292 to the guest source loads.

## s4233 addendum
fillSampleStreamRange+8292 = unlink at 0x8008FD60 `lw $a0,0($v1)` with v1==0 (probe confirmed head=0, pool=0, tail=801F9E00, ra=0); +932 = list-walk `lw $v0,0xC($t0)` at 0x8008FADC with t0=0x10CF3001 (asm-map only). Host-offset mapping recipe: cmake --build build --target Users/<...>/funcs_N.s then scratch/agent/s4233/map.py (direct cc/otool/nm are denied). Next: who zeroes head+pool (0x8015-0x661C/-0x6634), and why ra==0 at the call.

## s4234 addendum
fillSampleStreamRange entry probe (4 runs, ~80k entries): ra==0 on every entry (host-called; NOT evidence of a zeroed context). Allocator-list stores occur only in init, before the first call. head==0 appears only with tail==0 (empty list/re-init with new pool). The s4233 state head==0/tail!=0 did NOT recur (1 sighting in ~10 runs): PARK as wait-for-recurrence; the probe stays in tools/apply_s4234_entryprobe.py. Next: resume the M5 de-stub sequence (docs/M5-AUDIO-PLAN.md), not another allocator chase.

- s4252: private-DMEM crash rate is B 3/6 vs silent-ucode C 3/6 (ucode-independent; c1 refuted). Crashes cluster ~28s fillSampleStreamRange; one RT64 copyToRAM at 15s. Next: name the wild-pointer writer (see NEXT.md).

- s4264: in audio-gap seconds the scheduler thread (tid 3) waits on 0x8011A7E8 with ~1 completion/s (healthy 30/s); main thread not blocked and keeps submitting; tid 2/5 starve behind tid 3. Next: per-task start/done timestamps on host SP-complete path (NEXT.md).
