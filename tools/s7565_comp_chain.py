#!/usr/bin/env python3
"""s7565 compensation-chain audit (Next steps 19c).

Question: which DEFAULT-ON port behaviour levers exist only to repair ANOTHER port deviation (a chain), as s4889 (fires only
because the MusyX gate byte B40 defaults to 0 in the port) and s7476 (repairs s4889's $a1 clobber) do?  A chain is an
owner-facing simplification: choosing the retail setting of the parent would retire the child.

Universe: every ON lever in docs/DEFAULT-ON-LEVERS.md (tools/s7557_gq_census.py --write) plus the s7558 class GR ungated
GUARD/HOSTPLUMB rules (no env switch).  Evidence per lever: the PORTING-STATE entries that name it (first..last session),
their ORIGIN lines, and their titles.  Auto pass: find sentences that name a PARENT (another ON lever by name or by its
session tag, the B40 gate, or a "port's own patch" phrase) next to a causal cue (clobber, repairs, caused by, exposed by,
only because, fallout, regression, side effect ...), or an opt-in FEATURE (dd>1, FPS60, ASPECT/wide) as the trigger.
Then the hand table HAND (read by s7565 against those sentences) gives the verdict:
  CHAIN(parent)    exists because of another DEFAULT-ON port deviation; retail parent would retire it
  FEATURE(parent)  acts only for an opt-in feature (dd>1 / FPS60 / ASPECT ...): inert at retail settings
  RETAIL-GAP       repairs a recompilation / host-runtime / renderer gap against retail hardware behaviour
  DIAG             changes no guest-visible state
  UNKNOWN          evidence too thin to classify (listed, never a zero)
A lever whose auto pass flags a parent but that has no HAND row is UNREVIEWED: --check exits 1.
  python3 tools/s7565_comp_chain.py [--rows] [--write] [--check] [--controls]
"""
import collections, importlib.util, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVERS_MD = os.path.join(REPO, "docs/DEFAULT-ON-LEVERS.md")
OUT_MD = os.path.join(REPO, "docs/COMPENSATION-CHAINS.md")
CAUSE = re.compile(r"clobber|repair|caused by|exposed by|only because|because the port|fallout|regression|side[- ]effect|"
                   r"introduced by|broke|breaks|undo|compensat|works around|workaround for|left by|after s\d{3,4}|"
                   r"our own|the port's|port patch|port's own", re.I)
FEATURE = re.compile(r"\bdd ?> ?1\b|\bdd[2-8]\b|DRAW_DISTANCE|FPS60|ROGUESQ_ASPECT|\bwide(?:win)?\b|21:9|16:9|spill arena|"
                     r"auto-far|\bpx[3-8]\b", re.I)
B40 = re.compile(r"\bB40\b|gate[- ]zero|gate 0\b|0x80130B40", re.I)


def load_levers(path=LEVERS_MD):
    rows = []
    for line in open(path, errors="ignore"):
        m = re.match(r"\| `(ROGUESQ_[A-Z0-9_]+)` \| ([\w-]+) \| (\S+) \|", line)
        if m:
            a, _, b = m.group(3).partition("..")
            rows.append((m.group(1), None if a == "-" else int(a), None if b in ("-", "") else int(b)))
    return rows


def gr_rules():
    spec = importlib.util.spec_from_file_location("gr", os.path.join(REPO, "tools/s7558_gr_census.py"))
    gr = importlib.util.module_from_spec(spec); spec.loader.exec_module(gr)
    return [(t, c, n) for t, c, n in gr.RULES if c in ("GUARD", "HOSTPLUMB")]


def load_sessions():
    ent = {}; cur = None; buf = []
    for line in open(os.path.join(REPO, "PORTING-STATE.md"), errors="ignore"):
        h = re.match(r"## Session (\d+)", line)
        if h:
            if cur is not None:
                ent.setdefault(cur, "".join(buf))
            cur = int(h.group(1)); buf = [line]; continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        ent.setdefault(cur, "".join(buf))
    return ent


def sentences(text):
    t = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.;])\s+(?=[A-Z(*\[-])", t) if s.strip()]


def evidence(name, sess_list, ent, levers):
    """auto pass -> (parents{parent:sentence}, feature sentence or None)"""
    others = {}
    for n, f, _ in levers:
        if n == name:
            continue
        others[n] = re.compile(re.escape(n) + r"\b")
        t = re.match(r"ROGUESQ_S(\d{4})(?:_|$)", n)
        if t:
            others[n] = re.compile(re.escape(n) + r"\b|\bs" + t.group(1) + r"\b(?! ?-)")
    own = re.match(r"ROGUESQ_S(\d{4})(?:_|$)", name)
    parents, feat = {}, None
    for s in sess_list:
        text = ent.get(s, "")
        if not text:
            continue
        # only sentences that talk about this lever (its name or its own session tag) or the ORIGIN line / title
        tag = re.compile(re.escape(name) + (r"|\bs" + own.group(1) + r"\b" if own else ""))
        for sen in sentences(text):
            about = tag.search(sen) or sen.startswith("## Session") or "ORIGIN" in sen[:12]
            if not about:
                continue
            if CAUSE.search(sen):
                for o, rx in others.items():
                    if rx.search(sen) and o not in parents:
                        parents[o] = (s, sen[:300])
                if B40.search(sen) and "B40" not in parents:
                    parents["B40"] = (s, sen[:300])
            if feat is None and FEATURE.search(sen) and tag.search(sen):
                feat = (s, sen[:300])
    return parents, feat


# Hand verdicts (s7565), keyed by lever; each read against the sentences the auto pass printed (scratch/s7565/rows.txt),
# the lever's first-session title and ORIGIN line.  "(... only)" notes are the session's own reachability claim.
F_DD, F_AS, F_60 = "FEATURE(DRAW_DISTANCE>1)", "FEATURE(ASPECT wide)", "FEATURE(FPS60)"
HAND = {
 # --- CHAIN: a default-on child of another default-on port deviation
 "ROGUESQ_S4889_FIRST_DEREG": ("CHAIN(B40)", "fires only because the port's B40 MusyX gate store defaults to 0 (s4700 why, s7564 A/B: [s4889] gate-0 arms only)"),
 "ROGUESQ_S7476_A1FIX": ("CHAIN(ROGUESQ_S4889_FIRST_DEREG)", "repairs the $a1 clobber of s4889's injected findAndZeroTableSlotMatching call (s7476 ORIGIN)"),
 "ROGUESQ_WRAP_RESTORE": ("CHAIN(ROGUESQ_DPC_WRAP_FLUSH)", "restores lap-1 content the wrap-flush submit found overwritten; s4287: acts only when WRAP_FLUSH and the S4272 shadow are armed (both default-on since s4549)"),
 "ROGUESQ_DPC_KEEP_PIPE": ("CHAIN(dpc_bridge bump-time PIPESYNC drop)", "s4272 ORIGIN: the port's own rsp_dpc_submit PIPESYNC drop on bump-time placeholder words deleted triangle words; keep-pipe undoes it in deferred mode"),
 "ROGUESQ_S4272": ("CHAIN(ROGUESQ_DPC_WRAP_FLUSH)", "bump-time shadow of deferred ranges; the parent WRAP_RESTORE reads it (s4287 caveat)"),
 "ROGUESQ_CUT_LIVE": ("CHAIN(s6418 far-cutoff scaling)", "s6919: our s6418 block overwrote the game's per-scene far cutoff even at dd1; CUT_LIVE confines it to where the dd scale is active"),
 "ROGUESQ_SHADE_ORD_RESET": ("CHAIN(port shade-order diagnostic map)", "s6902: our own never-cleared diagnostic map rehashed on the gfx path (seconds-long freezes); reset fixes our code, not the game"),
 "ROGUESQ_S7376_PQLOCK": ("CHAIN(port present-thread diag/follow-draw code)", "s7376: the port's present-thread code inserted into the shared RT64 targetMap; lock added"),
 "ROGUESQ_S7383_FBPACK": ("CHAIN(ROGUESQ_VI_FOLLOW_DRAW mode 3)", "s7383: last-drawn fb tuple torn when read by follow-draw mode 3 (port default since s23)"),
 "ROGUESQ_S7384_LDGFX": ("CHAIN(ROGUESQ_VI_FOLLOW_DRAW mode 3)", "s7384: the follow-draw last-drawn fb has two writer threads; Gfx-thread write made the single writer"),
 "ROGUESQ_S7478_STALECHK": ("CHAIN(port heap canary)", "s7478: the canary store path itself wrote into dead records; drops stale records (diagnostic machinery fixing itself)"),
 "ROGUESQ_S7335_CLAMP": ("CHAIN(DLPOOLX host arena)", "s7335: DLPOOLX arena (port) could start below the guest top; clamp keeps the port arena off guest memory"),
 "ROGUESQ_RETARGET_RESERVE": ("CHAIN(s6202 G1d framebuffer retarget)", "s7481: the s6202 retarget's frame pool sits inside a FREE main-heap block; reservation repairs our retarget (ASPECT-path reachability not separated)"),
 "ROGUESQ_DD_CINE_GATE": ("CHAIN(dd levers in the boot cinematic)", "s6903: our dd levers ran in the Factor 5 logo cinematic; gated to levels (child of the DD bundle, dd>1 only)"),
 "ROGUESQ_RADAR_GATE_EPOCH": ("CHAIN(s6158 radar-region shift)", "s6730: our ASPECT radar-disc shift outlived flight; epoch gate (wide only)"),
 "ROGUESQ_G1D_SHIFT_SAT": ("CHAIN(s6159 radar-region shift)", "s6851: our radar shift masked 12-bit x after the s6850 clip (wide only)"),
 "ROGUESQ_G1D_REGION_ZGATE": ("CHAIN(s6159 radar-region shift)", "s6852: our radar-region shift also moved world geometry (wide only)"),
 "ROGUESQ_G1D_REGION_CFLIP": ("CHAIN(ROGUESQ_G1D_REGION_ZGATE)", "s6854: stale Z-gate latch of the s6852 region gate; reset on colour flip (wide only)"),
 "ROGUESQ_G1D_640PERSP": ("CHAIN(s6144 footprint x-scale)", "s6719: our s6144 x-scale applied in unwidened states (wide only)"),
 "ROGUESQ_G1D_FPDEPTH": ("CHAIN(s6144 footprint widening)", "s6879: 16:9 flight lost far terrain to our own s6144 footprint widening (wide only)"),
 "ROGUESQ_G1D_EDGE_CONTENT": ("CHAIN(ROGUESQ_G1D_EDGE)", "s6736: the s6726 edge trim now keys on content reach"),
 "ROGUESQ_DD_EDGE": ("CHAIN(s6037 terrain clamp)", "s6874: any dd!=1 deleted retail's off-map border via our s6037 clamp (dd>1 only)"),
 "ROGUESQ_DD_EYEWIN": ("CHAIN(dd terrain window clamp)", "s6899: our window clamp ignored the eye (dd>1 only)"),
 "ROGUESQ_DD_FWDWIN": ("CHAIN(dd terrain window clamp)", "s6901: our window clamp again, placed by heading (dd>1 only)"),
 "ROGUESQ_DD_SKYZ_SEL2": ("CHAIN(ROGUESQ_DD_SKYZ_SEL)", "s6948: SEL missed interleaved modes; SEL2 walks past them (dd>1 only)"),
 "ROGUESQ_SPANSENT_FIX": ("CHAIN(dd frustum-height clamp)", "s6789: our clamp's -128 collided with the 0x80 sentinel (dd>1 only)"),
 "ROGUESQ_S7427_REINIT": ("CHAIN(rs64_g5b_tg_fix static latch)", "s7427: our TriGen fix latched the raw DRAW_DISTANCE before the s7358 sanitiser"),
 "ROGUESQ_PTRMASK": ("CHAIN(dd spill arena at 0x81000000)", "s6992: the game's 0x80000000 pointer test rejects our spill arena (dd>1 only)"),
 "ROGUESQ_SPILL_RESET": ("CHAIN(dd spill arena)", "s7326: spill blocks leak across the retail scene reset (dd>1 only)"),
 "ROGUESQ_DLPOOLX_RECLAIM": ("CHAIN(DLPOOLX host arena)", "s6909 side-effect crash: our DL chunk arena never reset"),
 "ROGUESQ_S7336": ("CHAIN(spill/DLPOOLX host arenas)", "s7336: 3 opt-in arena layout defects of ours (overlap, under guest top, above ram_top)"),
 "ROGUESQ_S7337": ("CHAIN(dd spill arena above 8 MB)", "s7337: stale 8 MB bounds in our ramtop fixups (latent, opt-in)"),
 "ROGUESQ_S7339": ("CHAIN(dd spill arena above 16 MB)", "s7339: wrapper-guard 16 MB bound widened to rs64_ram_top (latent)"),
 "ROGUESQ_G1D_SPANBOUND": ("CHAIN(s6049 span bound)", "s6880: our s6049 bound did not cover wide frames (21:9 crash)"),
 # --- FEATURE: acts for an opt-in feature (inert or no-op at retail settings by its session's claim)
 "ROGUESQ_DD_OFFMAPCULL_EYE": (F_DD, "s7032 off-map cull eye term; s7557 lists it dd>1 only"),
 "ROGUESQ_DD_PNORM_CAP": (F_DD, "s6701: perspNorm cap for our far scaling"),
 "ROGUESQ_DD_PX8_AUTO": (F_DD, "s7293: dd>=8 16:9 bundle"),
 "ROGUESQ_DD_SKYZ_SEL": (F_DD, "s6946 sky-depth selector for dd sky"),
 "ROGUESQ_DD_VARCLAMP": (F_DD, "s6911: map index clamped at dd>1 (off-map coast cells)"),
 "ROGUESQ_DD_WIDEWIN_STACK": (F_DD, "s7258: rides with the dd6 bundle"),
 "ROGUESQ_SPAN_BYPASS": (F_DD, "s6529: default for DRAW_DISTANCE>1"),
 "ROGUESQ_TILEPOOL": (F_DD, "s6893: pools scale by ceil(dd)^2 (K=1 at dd1 4:3)"),
 "ROGUESQ_W_CLAMP": (F_DD, "s6895: W<=0 wedge fix at dd>1"),
 "ROGUESQ_G1E_COAL": (F_DD, "s6944: dd4 Gfx-thread submit coalescing (host perf)"),
 "ROGUESQ_FPS60_DESPAWN": (F_60, "s6820 dt-scaled despawn grace under FPS60"),
 "ROGUESQ_FPS60_FQUANTA": (F_60, "s6826 dt*30 under FPS60"),
 "ROGUESQ_FPS60_INTSTEP": (F_60, "s6831 game-time step under FPS60"),
 "ROGUESQ_FPS60_SCRAPE": (F_60, "s6817 max(dt,1/30) under FPS60"),
 "ROGUESQ_FPS60_SCRAPE_DMG": (F_60, "s6819 dt*30 under FPS60"),
 "ROGUESQ_FPS60_TICKS": (F_60, "s6821 frame-locked timers under FPS60"),
 "ROGUESQ_G1D_340PERSP": (F_AS, "s6927 340-row hangar 3D at wide aspect"),
 "ROGUESQ_G1D_DEBRIEF": (F_AS, "s6724 debrief pillar crop"),
 "ROGUESQ_G1D_EDGE": (F_AS, "s6726 game-over pillar crop; also trims the 4:3 debrief right-edge line (one 4:3 effect)"),
 "ROGUESQ_G1D_INTRO": (F_AS, "s6718 640x340 intro widened"),
 "ROGUESQ_G1D_INTROSHAPE": (F_AS, "s6929 VI_SHAPE faults at wide aspect"),
 "ROGUESQ_G1D_OVL_WRAP": (F_AS, "s6848 emitColorFillRect 10-bit W wrap at 21:9"),
 "ROGUESQ_G1D_RECT_WRAP": (F_AS, "s6844 lr.x 1024 wrap at 21:9"),
 "ROGUESQ_G1D_SHOWROOM": (F_AS, "s6926 512x300 state widened"),
 "ROGUESQ_G1D_SPRITE_WRAP": (F_AS, "s6850 12-bit lr.x clip at 21:9"),
 "ROGUESQ_G1D_TITLE_VI": (F_AS, "s6720 interlaced title VI widened"),
 "ROGUESQ_G1D_W640": (F_AS, "s6929 noise strip below 640 columns"),
 "ROGUESQ_G1D_WIPE_EPS": (F_AS, "s6846 W-scaled wipe epsilon at 21:9"),
 "ROGUESQ_G1F_NOTCH": (F_AS, "s6930 ASPECT=auto notch band"),
 "ROGUESQ_G1F_POSDISP": (F_AS, "s7226 ASPECT=auto on a secondary display"),
 "ROGUESQ_FBW_ALIGN": (F_AS, "s7188 ASPECT=auto odd fb width"),
 "ROGUESQ_PRESENT_SHAPEFIX": (F_AS, "s7213 21:9 mode-switch letterbox flash"),
 "ROGUESQ_RECT_ASPECT": (F_AS, "s7142 RT64 aspectRatioScale on Rectangle draws at 21:9/16:9"),
 "GR:s4700 cbtable": ("FEATURE(ROGUESQ_S4562_PAUSE opt-in)", "skip only while the host pause bit is set; s4562 pause is opt-in -> inert by default"),
 # --- OWNER: deliberate owner-requested change on retail behaviour
 "ROGUESQ_CULL_SPIKE": ("OWNER", "owner 2026-10-31: retail knife-spike wedges culled by default"),
 # --- RETAIL-GAP: repairs a recompilation / host-runtime / renderer gap
 "ROGUESQ_A14_YIELD": ("RETAIL-GAP", "cooperative host scheduler: guest spin never preempted (retail has a preemptive OS); applies at both B40 settings ([a14-yield] in all 6 s7558 arms)"),
 "ROGUESQ_AUDIO_SPIN2_YIELD": ("RETAIL-GAP", "s4765 cooperative-scheduler yield in the second MusyX wait gate"),
 "ROGUESQ_SPIN_YIELD": ("RETAIL-GAP", "s1942 spin starves idle under the cooperative scheduler"),
 "ROGUESQ_AUDIO_WAIT_NOPUMP": ("RETAIL-GAP", "s327 spin-loop pump policy of the host audio wait (auto parent SPIN_YIELD is a cross-mention: both are host-scheduler answers, neither repairs the other)"),
 "ROGUESQ_AUDIO_UCODE": ("RETAIL-GAP", "s300 run the recompiled MusyX ucode (de-stub)"),
 "ROGUESQ_AUDIO_PRIVATE_DMEM": ("RETAIL-GAP", "s4250 host runs gfx+audio RSP concurrently; private DMEM removes the shared-DMEM lock (retail has one RSP)"),
 "ROGUESQ_VI_FULLSYNC": ("RETAIL-GAP", "s11 the game stops emitting FULL_SYNC; RT64 needs it"),
 "ROGUESQ_DPC_WRAP_FLUSH": ("RETAIL-GAP", "s4273 dpc_bridge dropped ring-lap wrap bumps; host bridge gap"),
 "ROGUESQ_FL_HDR_HARD_SKIP": ("RETAIL-GAP", "s659/s4548 RT64 freelist-header writeback policy (renderer copy-back vs guest heap)"),
 "ROGUESQ_EXACT_EDGES": ("RETAIL-GAP", "s6794 RT64 minor-edge rebuild left a column unsampled"),
 "ROGUESQ_MENU_WORKER_FIFO": ("RETAIL-GAP", "s6781 port-only race on the menu worker completion message (host threads)"),
 "ROGUESQ_PE_DEDUPE": ("RETAIL-GAP", "s7208 RT64 static present fired every VI alongside early presents"),
 "ROGUESQ_PE_STALEFIX": ("RETAIL-GAP", "s7206 RT64 resolved the fb one row early"),
 "ROGUESQ_VI_ILACE_ADDR": ("RETAIL-GAP", "s7206 interlaced VI address"),
 "ROGUESQ_VI_BLACK_RETAIL": ("RETAIL-GAP", "s7512 VI register shape vs hardware"),
 "ROGUESQ_VI_RT": ("RETAIL-GAP", "s6967 macOS VI thread priority no-op; Mach RT policy"),
 "ROGUESQ_CF0_DUPDROP": ("RETAIL-GAP", "s7367 duplicate video ack into a full cap-1 queue (host scheduler deadlock)"),
 "ROGUESQ_PREEMPT_POINT": ("RETAIL-GAP", "s6808 cooperative run token held 70-90 ms with no OS call"),
 "ROGUESQ_PI_UNK_COMPLETE": ("RETAIL-GAP", "s7196 PI DMA to an unknown region never posted completion"),
 "ROGUESQ_S7394_HOLDFIX": ("RETAIL-GAP", "s7394 retail re-seed-while-held of the heap mutex"),
 "ROGUESQ_S7396_TQFIX": ("RETAIL-GAP", "s7396 upstream thread_queue_remove walk"),
 "ROGUESQ_S7397_TIMERFIX": ("RETAIL-GAP", "s7397 upstream osSetTimer re-arm"),
 "ROGUESQ_S7398_IOFIX": ("RETAIL-GAP", "s7398 upstream osPiStartDma OSIoMesg"),
 "ROGUESQ_S7400_CONTFIX": ("RETAIL-GAP", "s7400 osContGetReadData err_no / __osDisableInt v0"),
 "ROGUESQ_S7401_FLAGFIX": ("RETAIL-GAP", "s7401 libultra flags divergence"),
 "ROGUESQ_S7402_CLOCKFIX": ("RETAIL-GAP", "s7402 osClockRate unscaled"),
 "ROGUESQ_S7364_WLRESET": ("RETAIL-GAP", "s7364 RT64 stale tileIndex after FULLSYNC"),
 "ROGUESQ_S7377_EARLYLOCK": ("RETAIL-GAP", "s7377 upstream RT64 present thread unlocked lookup"),
 "ROGUESQ_S7378_SHLOCK": ("RETAIL-GAP", "s7378 RT64 SharedQueueResources fields"),
 "ROGUESQ_S7381_BARRIER_CV": ("RETAIL-GAP", "s7381 RT64 workload/present barrier spin -> condvar (auto parent S7381_SPIN is its sibling arm, not a parent)"),
 "ROGUESQ_S7381_SPIN": ("RETAIL-GAP", "s7381 sibling of BARRIER_CV"),
 "ROGUESQ_S7463_PADFIX": ("RETAIL-GAP", "s7463 RT64 padded-struct hash keys"),
 "ROGUESQ_S7528_EVICT": ("RETAIL-GAP", "s7528 librecomp load_overlay func_map gap"),
 "ROGUESQ_S7490_ZHOOK": ("DIAG", "s7490 hooks zmemcpy/PatchesLib bodies into the heap watches (watch visibility)"),
 "ROGUESQ_S7332_CARVE": ("DIAG", "s7332 heap-walk owner classification of the carve block (host census)"),
 "ROGUESQ_S7333_KEEP": ("DIAG", "s7333 carve fallback trusts the guest header (heap-walk classifier)"),
 "ROGUESQ_S7334_CLASS5": ("DIAG", "s7334 host class 5 in the heap-walk classifier"),
 "ROGUESQ_ALTSTACK": ("RETAIL-GAP", "s7355 crash-reporter async-signal safety (host)"),
 "ROGUESQ_AUDIO_HOTPLUG": ("RETAIL-GAP", "s7199 host audio device removal"),
 "ROGUESQ_DISPLAY_HOTPLUG": ("RETAIL-GAP", "s7202 host display removal"),
 "ROGUESQ_PAD_HOTPLUG": ("RETAIL-GAP", "s7201 host pad removal"),
 "ROGUESQ_DLADDR_CACHE": ("RETAIL-GAP", "s7067 host perf: per-call dladdr cached (our helper cost)"),
 "ROGUESQ_FTZ": ("RETAIL-GAP", "s6012 host denormal mode (N64 FPU flushes)"),
 "ROGUESQ_HLE_PATCH_ALPHA": ("RETAIL-GAP", "RT64 F3DFactor5 HLE alpha patch (source comment only, no session; HLE path)"),
 # --- GUARD: acts only on a value retail would fault on
 "ROGUESQ_COPY_GUARD": ("GUARD", "s5037 wild-length / non-RDRAM copies"),
 "ROGUESQ_PIO_GUARD": ("GUARD", "s5062 do_rom_pio range"),
 "ROGUESQ_PI_DMA_GUARD": ("GUARD", "s5061 do_dma range"),
 "ROGUESQ_SPAI_GUARD": ("GUARD", "s5063 SP StartGo / AI SetNextBuffer wrapper"),
 "GR:s1978 drain-base/hdr": ("GUARD", "drain-timeout hang breaker (retail would spin forever)"),
 "GR:musyxKeyOnVoice div-trap": ("GUARD", "teq div-by-zero trap -> early return"),
 "GR:s4984 atomic": ("RETAIL-GAP", "atomic host read of the voice count/base: host audio thread concurrency (retail single CPU)"),
 "GR:s6963 cellidx": ("DIAG", "host memo of the lookup, writes no guest state (s7558 rule)"),
 # --- UNKNOWN
 "ROGUESQ_S6892": ("UNKNOWN", "G5a walker pointer repair; writer never named (H-spill leads, unproven): could be CHAIN(dd spill arena)"),
}


def audit(levers, ent, hand=HAND, sess_index=None):
    out = []
    tag_index = collections.defaultdict(list)
    for k, t in ent.items():
        for g in set(re.findall(r'\bs(\d{4})\b', t)):
            tag_index[g].append(k)
    for name, f, l in levers:
        ss = sorted(sess_index.get(name, [])) if sess_index else []
        if not ss and f:
            ss = [f] + ([l] if l and l != f else [])
        own = re.match(r"ROGUESQ_S(\d{4})(?:_|$)", name)
        if own:  # sessions that cite the lever by its session tag only (s7564 names s4889, never its env name)
            ss = sorted(set(ss) | set(tag_index.get(own.group(1), [])))
        ss = ss[:40]
        parents, feat = evidence(name, ss, ent, levers)
        if name in hand:
            v, note = hand[name]
        elif parents:
            v, note = "UNREVIEWED", "auto: " + ", ".join(parents)
        elif feat:
            v, note = "UNREVIEWED-FEATURE", "auto feature cue"
        else:
            v, note = "UNKNOWN", "no parent or feature cue in its sessions"
        out.append((name, ss, v, note, parents, feat))
    return out


def sess_idx():
    idx = collections.defaultdict(list); cur = None
    for line in open(os.path.join(REPO, "PORTING-STATE.md"), errors="ignore"):
        h = re.match(r"## Session (\d+)", line)
        if h:
            cur = int(h.group(1)); continue
        if cur is not None:
            for n in set(re.findall(r"ROGUESQ_[A-Z0-9_]+", line)):
                if not idx[n] or idx[n][-1] != cur:
                    idx[n].append(cur)
    return idx


def main():
    levers = load_levers()
    for t, c, n in gr_rules():
        m = re.match(r"s(\d+)", t)
        levers.append(("GR:" + t, int(m.group(1)) if m else None, None))
    ent = load_sessions(); si = sess_idx()
    if "--controls" in sys.argv:
        return controls(levers, ent, si)
    rows = audit(levers, ent, sess_index=si)
    cnt = collections.Counter(r[2].split("(")[0] for r in rows)
    if "--rows" in sys.argv:
        for name, ss, v, note, parents, feat in rows:
            print(f"== {name} s={ss} -> {v} | {note}")
            for p, (s, sen) in parents.items():
                print(f"   parent {p} [s{s}]: {sen}")
            if feat:
                print(f"   feature [s{feat[0]}]: {feat[1]}")
    print("[chain] levers=%d " % len(rows) + " ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
    if "--write" in sys.argv:
        write(rows, cnt)
    if "--check" in sys.argv:
        return 1 if any(r[2].startswith("UNREVIEWED") for r in rows) else 0
    return 0


# CHAIN rows whose ROOT deviation is live at retail settings (dd1, 4:3, FPS60 off): the owner-facing simplification list.
# Every other CHAIN row is internal to an opt-in feature (dd>1 / ASPECT wide) and inert at retail settings by its session.
RETAIL_SCOPE = {
    "ROGUESQ_S4889_FIRST_DEREG": "retire by B40=1 (retail store): s7564 6/6 clean at both settings, [s4889] gate-0 only",
    "ROGUESQ_S7476_A1FIX": "retires with its parent s4889",
    "ROGUESQ_WRAP_RESTORE": "s7566 19d H-interlocked: parent WRAP_FLUSH is live (real lap gap; =0 arm noflush drops 17.7G B, 96 B unexplained); restore needs it, keep both",
    "ROGUESQ_S4272": "s7566 19d H-interlocked: shadow WRAP_RESTORE reads; same live parent, keep",
    "ROGUESQ_DPC_KEEP_PIPE": "s7566 19d H-dead-parent: g_defer_active is true at every bump (all DPC_END sites run inside defer_begin/end), so the drop is the =0 path only; L1 dd1 default 0 pipe drops / 8843 tasks vs =0 17.4M B",
    "ROGUESQ_CUT_LIVE": "confines our s6418 far-cutoff block to dd>1; simplification = gate s6418 itself on dd>1",
    "ROGUESQ_SHADE_ORD_RESET": "bounds our own diagnostic map; simplification = drop the map when its log is off",
    "ROGUESQ_S7376_PQLOCK": "locks our present-thread follow-draw code; parent is the port's present policy",
    "ROGUESQ_S7383_FBPACK": "follow-draw mode 3 is the port default since s23; mode 0 would retire it (unmeasured)",
    "ROGUESQ_S7384_LDGFX": "same parent as S7383_FBPACK",
    "ROGUESQ_S7478_STALECHK": "diagnostic canary repairing itself; retire with the canary",
    "ROGUESQ_G1D_EDGE_CONTENT": "refines G1D_EDGE's 4:3 debrief right-edge trim",
}


def roots(rows):
    par = {r[0]: re.match(r"CHAIN\((.*)\)$", r[2]).group(1) for r in rows if r[2].startswith("CHAIN(")}
    out = {}
    for n in par:
        seen, p = [n], par[n]
        while p in par and p not in seen:
            seen.append(p); p = par[p]
        out[n] = (p, len(seen))
    return out


def write(rows, cnt):
    rt = roots(rows)
    L = ["# Compensation chains among default-on port levers (generated by tools/s7565_comp_chain.py --write; do not hand-edit)", "",
         "A CHAIN lever exists only because another port deviation exists (s4889 fires only because the port's B40 MusyX gate store",
         "defaults to 0; s7476 repairs s4889's own $a1 clobber). Universe: every ON lever in docs/DEFAULT-ON-LEVERS.md plus the s7558",
         "class GR ungated GUARD/HOSTPLUMB rules. Verdicts are hand reads (s7565) of each lever's sessions, ORIGIN lines and source",
         "comment, prompted by an auto pass that flags sentences naming a parent next to a causal cue. Owner rule: no default flips",
         "here; this is the list of places where choosing a parent's retail setting or simplifying the parent would retire a child.", "",
         "Counts: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())), "",
         "Runtime cross-check (s7565, single run set): the s7558 B40 A/B logs (6 arms, L1/L4/L12, gate-0 vs B40=1) carry 196 distinct",
         "breadcrumb tags; exactly two fire in every gate-0 arm and in no B40=1 arm: `[s4889` and `[s7476` (the positive control).",
         "No other logged lever is B40-dependent. Coverage caveat: only 18 of the ON levers emit a session-tagged breadcrumb.", "",
         "## Chains whose root is live at retail settings (owner-facing)", "",
         "| lever | parent | root (depth) | what would retire it |", "|---|---|---|---|"]
    for r in rows:
        if r[0] in RETAIL_SCOPE:
            p = r[2][6:-1]; ro, d = rt[r[0]]
            L.append(f"| `{r[0]}` | {p} | {ro} ({d}) | {RETAIL_SCOPE[r[0]]} |")
    L += ["", "## Chains internal to an opt-in feature (inert at dd1 / 4:3 by their sessions)", "",
          "| lever | parent | root (depth) | note |", "|---|---|---|---|"]
    for r in rows:
        if r[2].startswith("CHAIN(") and r[0] not in RETAIL_SCOPE:
            p = r[2][6:-1]; ro, d = rt[r[0]]
            L.append(f"| `{r[0]}` | {p} | {ro} ({d}) | {r[3]} |")
    for cls in ("FEATURE", "RETAIL-GAP", "GUARD", "OWNER", "DIAG", "UNKNOWN"):
        L += ["", f"## {cls}", "", "| lever | verdict | note |", "|---|---|---|"]
        L += [f"| `{r[0]}` | {r[2]} | {r[3]} |" for r in rows if r[2].split("(")[0] == cls]
    open(OUT_MD, "w").write("\n".join(L) + "\n")
    print(f"[chain] wrote {os.path.relpath(OUT_MD, REPO)}")


def controls(levers, ent, si):
    ok = tot = 0
    rows = {r[0]: r for r in audit(levers, ent, sess_index=si, hand={})}   # auto pass alone, no hand verdicts
    for n, want in (("ROGUESQ_S4889_FIRST_DEREG", "B40"), ("ROGUESQ_S7476_A1FIX", "ROGUESQ_S4889_FIRST_DEREG")):
        good = want in rows[n][4]; ok += good; tot += 1
        print(f"[chain-ctl] auto {n} parent {want}: {'ok' if good else 'FAIL'} ({', '.join(rows[n][4])})")
    full = {r[0]: r for r in audit(levers, ent, sess_index=si)}
    for n, want in (("ROGUESQ_S4889_FIRST_DEREG", "CHAIN(B40)"), ("ROGUESQ_S7476_A1FIX", "CHAIN(ROGUESQ_S4889_FIRST_DEREG)")):
        good = full[n][2] == want; ok += good; tot += 1
        print(f"[chain-ctl] hand {n} = {want}: {'ok' if good else 'FAIL'}")
    rt = roots(list(full.values()))
    good = rt["ROGUESQ_S7476_A1FIX"] == ("B40", 2); ok += good; tot += 1
    print(f"[chain-ctl] root of S7476 = B40 depth 2: {'ok' if good else 'FAIL'} {rt['ROGUESQ_S7476_A1FIX']}")
    # planted child (cites a parent lever with a causal cue) and planted bystander (no cue): only the child is flagged
    e2 = dict(ent)
    e2[99001] = "## Session 99001 (x) — planted\nFix: ROGUESQ_CTL_CHILD repairs the clobber left by ROGUESQ_S7402_CLOCKFIX in the timer.\n"
    e2[99002] = "## Session 99002 (x) — planted\nROGUESQ_CTL_BYSTANDER default on. ROGUESQ_S7402_CLOCKFIX is unrelated here.\n"
    lv2 = levers + [("ROGUESQ_CTL_CHILD", 99001, None), ("ROGUESQ_CTL_BYSTANDER", 99002, None)]
    si2 = dict(si); si2["ROGUESQ_CTL_CHILD"] = [99001]; si2["ROGUESQ_CTL_BYSTANDER"] = [99002]
    r2 = {r[0]: r for r in audit(lv2, e2, sess_index=si2)}
    for n, want in (("ROGUESQ_CTL_CHILD", "UNREVIEWED"), ("ROGUESQ_CTL_BYSTANDER", "UNKNOWN")):
        good = r2[n][2] == want and (("ROGUESQ_S7402_CLOCKFIX" in r2[n][4]) == (want == "UNREVIEWED")); ok += good; tot += 1
        print(f"[chain-ctl] planted {n} want={want} got={r2[n][2]} parents={list(r2[n][4])}: {'ok' if good else 'FAIL'}")
    stale = [k for k in HAND if k not in {n for n, _, _ in levers}]
    good = not stale; ok += good; tot += 1
    print(f"[chain-ctl] no stale HAND rows: {'ok' if good else 'FAIL ' + str(stale)}")
    print(f"[chain-ctl] controls {ok}/{tot}")
    return 0 if ok == tot else 1


if __name__ == "__main__":
    sys.exit(main())
