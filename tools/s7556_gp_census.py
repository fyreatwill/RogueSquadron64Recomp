#!/usr/bin/env python3
"""s7556 class GP census: every guest consumer of TIME (osGetTime, osClockRate, the VI-count frame-dt terms) and whether it
uses the same unit and clock the host provides, in default config and under ROGUESQ_FPS60=1 (frame limiter 0x80128EAF 2 -> 1).

Builds on s7514 FK (time base canon at runtime: 46875.0 ticks/ms, monotone; consumer map) and s7402 BL (osClockRate rescale
fix, runtime dt histograms); this tool turns those into checked rows and adds the FPS60 / 64-bit-word angles.

 (A) SITES: every guest `osGetTime_recomp` call in the generated code (coverage: EXPECT_SITES, 14 at s7555), with the use of
     each word of the 64-bit result: $v0 = hi, $v1 = lo.  s7555's GO census tracked only $v0, so it read 'kill' at sites that
     consume $v1.  Every site must have a rule for its enclosing function; the rule names the consumer class and the hi-word
     verdict is checked: a site that READS $v0 consumes the full 64-bit time, which no rule allows -> OPEN.
 (B) GLOBALS: every function touching a time-derived global (lui/addiu/off(reg) resolver over asm comments, the s7514 idiom)
     must be in that global's allowed reader/writer set.  A new reader of a write-only duration -> OPEN.
 (C) CLOCK: host osGetTime rate (timer.cpp counter_per_ms == 46875, speed_multiplier == 1), osClockRate fix default-on writing
     46875000 over the ROM value 62500000 (checked in the ROM image), and every guest divisor of an osGetTime delta reads the
     osClockRate word (no hardcoded 46.875/62.5 MHz constant in a time path).
 (D) FRAME DT: timeSnapshotFiller's +0x20 field (the sim dt consumed by runInMissionFrame / cinematicComputeDt /
     advanceWrappingPhaseAccumulator) = dstamp/osClockRate + getViModePeriod() * K * N, N = VIs per frame (limiter byte
     0x80128EAF - 0x80128EAE) when >= 2, else K' * period.  Linear in VI count iff K == K' (ROM floats 0x80000568/56C) and the
     N >= 2 arm multiplies by N; then a FPS60 single-VI frame gets exactly one VI period (H-unit-ok), else H-mixed.
     The flags-clear arm is [0x8011A904]/osClockRate = measured ticks / count rate (no frame count).

Classes: H-sim-dt, H-stamp, H-profiler (gated: FK runtime ctl), H-write-only, H-dead-fn (0 callers), OPEN / FAIL / UNCLASSIFIED.
  python3 tools/s7556_gp_census.py              # rows + summary; exit 1 on any OPEN / FAIL / UNCLASSIFIED
  python3 tools/s7556_gp_census.py --controls   # planted mutations, each must flip the verdict
"""
import collections, glob, os, re, struct, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.environ.get("RS64_RECOMP_FUNCS", os.path.join(os.path.dirname(REPO), "N64Recomp", "RecompiledFuncs"))
ROM = os.path.join(REPO, "rs64.n64.us.1.0.z64")
TIMER = "lib/N64ModernRuntime/ultramodern/src/timer.cpp"
ULTRA = "lib/N64ModernRuntime/librecomp/src/ultra_translation.cpp"
EVENTS = "lib/N64ModernRuntime/ultramodern/src/events.cpp"

EXPECT_SITES = {"computeElapsedMillis": 1, "musyxSynthFrame_s4562_impl": 2, "serviceVoicePoolFrame": 2, "timeSnapshotFiller": 1,
                "viRetraceHandlerThread": 3, "spTaskSchedulerThread": 1, "dpInterruptHandlerThread": 1,
                "recordFrameTimestamp": 1, "getTimeLow32": 1, "getTimeSinceLastFrame": 1}
# enclosing function -> (class, why).  hi word must never be READ (no consumer uses the 64-bit value).
SITE_RULES = {
    "timeSnapshotFiller": ("H-sim-dt", "lo -> stamp 0x8011A8F0 (+0x24 = dlo/osClockRate); +0x20 sim dt is part (D)"),
    "viRetraceHandlerThread": ("H-stamp", "lo -> VI stamp 0x80128ED8 and per-VI record deltas (s7514 FK consumer map)"),
    "spTaskSchedulerThread": ("H-stamp", "lo -> gfx task start 0x80128D30; duration 0x80128D34 feeds the gated profiler only"),
    "dpInterruptHandlerThread": ("H-profiler", "lo - 0x80128D30 -> 0x80128D34 gfx duration; then getTimeSinceLastFrame -> 0x80128EDC"),
    "recordFrameTimestamp": ("H-stamp", "lo -> 0x80128F10, the base getTimeSinceLastFrame subtracts"),
    "getTimeLow32": ("H-stamp", "returns lo in $v0 (spTaskSchedulerThread task stamps)"),
    "getTimeSinceLastFrame": ("H-profiler", "returns lo - [0x80128F10]; callers store to profiler-only globals (part B)"),
    "musyxSynthFrame_s4562_impl": ("H-write-only", "lo -> synth duration 0x801499E8, write-only (part B)"),
    "serviceVoicePoolFrame": ("H-write-only", "lo -> 0x8015466C / 0x80154680 and deltas 0x80154678, write-only (part B)"),
    "computeElapsedMillis": ("H-dead-fn", "dlo*1e9/osClockRate/1000; 0 jal callers in the generated code (checked)"),
}
# global range -> (allowed functions touching it, why).  Ranges are [lo, hi).
GLOBALS = {
    (0x80039100, 0x80039108): ({"computeElapsedMillis", "emitProfilerBarSegment", "timeSnapshotFiller"},
                               "osClockRate: the only guest divisors of time deltas"),
    (0x80128EDC, 0x80128EE4): ({"dpInterruptHandlerThread", "drawFrameProfilerBars", "musyxSynthFrame_s4562_impl",
                                "submitGfxFrame", "spTaskSchedulerThread"},
                               "getTimeSinceLastFrame results / task low32 (sw by spTaskSchedulerThread 0x80019F18): profiler-only reader"),
    (0x801499E8, 0x801499EC): ({"musyxSynthFrame_s4562_impl"}, "musyx synth duration: write-only"),
    (0x80154678, 0x8015467C): ({"serviceVoicePoolFrame"}, "voice-pool service delta: write-only"),
    (0x80154680, 0x80154684): ({"serviceVoicePoolFrame"}, "voice-pool stamp: written only"),
    (0x8011A900, 0x8011A908): ({"buildAndRegisterDefaultMaterial", "computeFrameDeltaTime", "submitGfxFrame", "timeSnapshotFiller"},
                               "frame stamp / measured frame ticks feeding the +0x20 arms"),
}
# resolver artifacts: an address-only hit (no load/store through it) the linear lui tracker produces across a branch.
# 0x8001BBBC / 0x8001BAEC: `beql $v0,$zero; addiu $v1,$v1,0xF0` where $v1 holds a VI-mode table pointer on the taken path,
# not the earlier lui 0x8013 the tracker kept; the next ops copy 0x50 bytes from $v1 into 0x80128C90 (VI mode). Read s7556.
ADDR_ARTIFACTS = {(0x80128EDC, 0x80128EE4): {"selectAndApplyViMode", "swapBufferWithViMode"}}
ROM_K = (0x80000568, 0x8000056C)            # 0.001 per-VI and single-VI scale of getViModePeriod (ms -> s)
ROM_PERIOD = (0x80000450, 0x80000454)       # getViModePeriod: NTSC 16.667 ms / PAL 20 ms
ROM_CLOCK = 0x80039100


def rom_word(rom, va):
    o = va - 0x80000400 + 0x1000
    return rom[o:o + 4]


def load_gen(gen):
    return {os.path.basename(f): open(f, errors="replace").read().split("\n") for f in sorted(glob.glob(gen + "/*.c"))}


def text(path, over):
    return over[path] if path in over else open(os.path.join(REPO, path), errors="replace").read()


R = {r: re.compile(r'ctx->%s(?!\d)' % r) for r in ("r2", "r3")}
CALL = re.compile(r'\b(\w+?)(?:_recomp)?\(rdram, ctx\);')


def word_use(lines, i, reg, killers):
    """first use of reg after line i on the straight-line text: read | kill | unknown (a call or jump first)"""
    rx = R[reg]
    for l in lines[i:i + 80]:
        s = l.strip()
        if not s or s.startswith("//") or re.match(r'(goto after_\d+;|after_\d+:|L_[0-9A-F]+:)$', s):
            continue
        if s.startswith("if (__builtin_expect(g_rs64_store_diag") or s.startswith("rs64_m5_lowfield_store") or "PATCH:" in s and not rx.search(s.split("PATCH:")[0]):
            continue
        c = CALL.search(s)
        if c and c.group(1) in killers:
            return "kill"
        if "RECOMP_FUNC" in s or s == "return;" or c or re.search(r'\bgoto L_', s):
            return "return" if s == "return;" else "unknown"
        if not rx.search(s):
            continue
        w = re.search(r'ctx->%s(?!\d)\s*=(?!=)\s*(.*)' % reg, s)
        before = s[:w.start()] if w else s
        if w and not rx.search(before) and not rx.search(w.group(1)):
            return "kill"
        return "read"
    return "unknown"


def sites(gen_lines):
    out = []
    for f, lines in gen_lines.items():
        fn = None
        for i, l in enumerate(lines):
            m = re.match(r'RECOMP_FUNC void (\w+)\(', l)
            if m:
                fn = m.group(1)
                continue
            if re.search(r'\bosGetTime_recomp\(rdram, ctx\);', l):
                out.append((fn, f, i + 1))
    return out


# hi-word ($v0) killers: the call that follows osGetTime at these sites returns its own $v0 (host bodies assign ctx->r2).
HI_KILLERS = {"__osDisableInt", "applyPendingViChanges", "osRecvMesg", "getTimeSinceLastFrame", "getTimeLow32"}


def refs(gen_lines, ranges):
    """s7514 FK resolver: (addr, op) -> set of fn@pc for lui/addiu/off(reg) references into ranges"""
    fn_re = re.compile(r'^RECOMP_FUNC void (\w+)\(')
    op_re = re.compile(r'^\s*// (0x8[0-9A-F]+): (\w+)\s+(.*)$')
    num = lambda s: int(s, 16) if s.lstrip('-').startswith('0x') else int(s)
    hits = collections.defaultdict(set)
    for f, lines in gen_lines.items():
        fn, regs = None, {}
        for line in lines:
            m = fn_re.match(line)
            if m:
                fn, regs = m.group(1), {}
                continue
            m = op_re.match(line)
            if not m or not fn:
                continue
            pc, op, args = m.groups()
            a = [x.strip() for x in args.split(',')]
            if op == 'lui':
                regs[a[0]] = (num(a[1]) << 16) & 0xFFFFFFFF
                continue
            addr = None
            if op in ('addiu', 'ori') and len(a) == 3 and a[1] in regs:
                v = num(a[2])
                addr = (regs[a[1]] + v) & 0xFFFFFFFF if op == 'addiu' else regs[a[1]] | v
                regs[a[0]] = addr
            else:
                mm = re.match(r'(-?0x[0-9A-Fa-f]+|-?\d+)\((\$\w+)\)', a[-1]) if a else None
                if mm and mm.group(2) in regs:
                    addr = (regs[mm.group(2)] + num(mm.group(1))) & 0xFFFFFFFF
                if a and a[0].startswith('$') and op not in ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'beq', 'bne'):
                    regs.pop(a[0], None)
            if addr is not None:
                for lo, hi in ranges:
                    if lo <= addr < hi:
                        hits[(lo, hi)].add((fn, "addr" if op in ("addiu", "ori") else op))
    return hits


def fn_asm(gen_lines, name):
    for f, lines in gen_lines.items():
        for i, l in enumerate(lines):
            if l.startswith("RECOMP_FUNC void %s(" % name):
                out = []
                for l2 in lines[i + 1:]:
                    if l2.startswith("RECOMP_FUNC"):
                        break
                    m = re.match(r'^\s*// (0x8[0-9A-F]+): (.*)$', l2)
                    if m and (not out or out[-1][0] != m.group(1)):
                        out.append((m.group(1), re.sub(r'\s+', ' ', m.group(2).strip())))
                return out
    return []


def census(gen_lines, rom, over=None, quiet=False):
    over = over or {}
    rows, bad = [], 0
    # (A) sites
    ss = sites(gen_lines)
    cnt = collections.Counter(fn for fn, _, _ in ss)
    for fn, f, ln in ss:
        L = gen_lines[f]
        hi, lo = word_use(L, ln, "r2", HI_KILLERS), word_use(L, ln, "r3", ())
        rule = SITE_RULES.get(fn)
        if rule is None:
            cls, why = "UNCLASSIFIED", "osGetTime site in a function with no rule"
        elif hi == "read":
            cls, why = "OPEN", "reads $v0 (hi word): 64-bit time consumer not covered by any rule"
        elif lo not in ("read", "return"):
            cls, why = "OPEN", "lo word ($v1) use not found on the straight line (lo=%s)" % lo
        else:
            cls, why = rule
        rows.append(("A", "%s %s:%d" % (fn, f, ln), cls, "hi=%s lo=%s; %s" % (hi, lo, why)))
    for fn, n in EXPECT_SITES.items():
        if cnt.get(fn, 0) != n:
            rows.append(("A", "coverage " + fn, "FAIL", "expected %d osGetTime sites, found %d" % (n, cnt.get(fn, 0))))
    if sum(cnt.values()) != sum(EXPECT_SITES.values()):
        rows.append(("A", "coverage total", "FAIL", "expected %d sites, found %d" % (sum(EXPECT_SITES.values()), sum(cnt.values()))))
    # computeElapsedMillis callers
    callers = [(f, i) for f, L in gen_lines.items() for i, l in enumerate(L) if re.search(r'^\s*computeElapsedMillis\(rdram, ctx\);', l)]
    rows.append(("A", "computeElapsedMillis callers", "H-dead-fn" if not callers else "OPEN", "%d jal callers" % len(callers)))
    # (B) globals
    hits = refs(gen_lines, list(GLOBALS))
    for rg, (allowed, why) in GLOBALS.items():
        got = hits.get(rg, set())
        art = ADDR_ARTIFACTS.get(rg, set())
        extra = sorted({fn for fn, op in got if fn not in allowed and not (fn in art and op == "addr")})
        got = {fn for fn, op in got}
        rows.append(("B", "%08X-%08X" % rg, "OPEN" if extra else "OK",
                     "%s; touched by %d fns%s" % (why, len(got), "; NEW: " + ",".join(extra) if extra else "")))
    # (C) clock
    t = text(TIMER, over)
    cpm = re.search(r"constexpr uint32_t counter_per_ms = ([\d']+) \* speed_multiplier;", t)
    spm = re.search(r"constexpr uint32_t speed_multiplier = (\d+);", t)
    ok = cpm and int(cpm.group(1).replace("'", "")) == 46875 and spm and spm.group(1) == "1"
    rows.append(("C", "host osGetTime rate", "OK" if ok else "OPEN",
                 "counter_per_ms=%s speed_multiplier=%s (hardware count rate 46875/ms)" % (cpm and cpm.group(1), spm and spm.group(1))))
    u = text(ULTRA, over)
    romclk = struct.unpack(">Q", rom_word(rom, ROM_CLOCK) + rom_word(rom, ROM_CLOCK + 4))[0]
    fix = (re.search(r'return !\(e && e\[0\] == \'0\'\);', u) and re.search(r'lo == 62500000u\) \{\s*MEM_W\(0, \(int32_t\)0x80039104u\) = 46875000u;', u))
    rows.append(("C", "osClockRate", "OK" if fix and romclk == 62500000 else "OPEN",
                 "ROM %d, osInitialize_recomp default-on writes 46875000 = 62500000*3/4 (retail osInitialize)" % romclk))
    hard = []
    for f, L in gen_lines.items():
        for i, l in enumerate(L):
            if re.search(r'// 0x8[0-9A-F]+: (?:lui|ori|addiu)\s+\$\w+, (?:\$\w+, )?(0x2CB|0x3B9|0x2CB4178|0x3B9ACA0|0x4178|0xACA0)$', l):
                hard.append("%s:%d" % (f, i + 1))
    # 46875000 = 0x02CB4178, 62500000 = 0x03B9ACA0 (lui 0x2CB / 0x3B9); 1e9 = 0x3B9ACA00 is lui 0x3B9A (not matched)
    rows.append(("C", "hardcoded count-rate constants", "OPEN" if hard else "OK",
                 "%d lui/ori of 46875000/62500000 halves%s" % (len(hard), (": " + ",".join(hard[:4])) if hard else "")))
    # (D) frame dt
    k1, k2 = (struct.unpack(">f", rom_word(rom, a))[0] for a in ROM_K)
    p1, p2 = (struct.unpack(">f", rom_word(rom, a))[0] for a in ROM_PERIOD)
    asm = fn_asm(gen_lines, "timeSnapshotFiller")
    seq = [x[1] for x in asm]
    j = "\n".join(seq)
    lin = (re.search(r"lbu \$v0, -0x7151\(\$v0\)\nlui \$v1, 0x8013\nlbu \$v1, -0x7152\(\$v1\)\ncvt\.s\.d \$f0, \$f4\nsubu \$v0, \$v0, \$v1\n"
                     r"slti \$v0, \$v0, 0x2", j) and
           re.search(r"jal 0x80002710\nnop\nlui \$at, 0x8000\nlwc1 \$f2, 0x568\(\$at\)\nmul\.s \$f0, \$f0, \$f2\n(?:.*\n){6}"
                     r"cvt\.s\.w \$f2, \$f2\nmul\.s \$f0, \$f0, \$f2", j) and
           re.search(r"jal 0x80002710\nnop\nlui \$at, 0x8000\nlwc1 \$f2, 0x56C\(\$at\)\nmul\.s \$f0, \$f0, \$f2", j) and
           re.search(r"swc1 \$f0, 0x20\(\$s0\)", j))
    rows.append(("D", "+0x20 formula shape", "OK" if lin else "FAIL",
                 "N>=2: period*K*N, N<2: period*K' (asm pattern in timeSnapshotFiller, %d insns)" % len(seq)))
    good = abs(k1 - 0.001) < 1e-9 and k1 == k2 and abs(p1 - 1000 / 60) < 1e-3 and p2 == 20.0
    rows.append(("D", "per-VI linearity", "H-unit-ok" if good and lin else "H-mixed",
                 "K=%.7g K'=%.7g period NTSC=%.5g PAL=%.5g ms: one VI -> %.5g s, two -> %.5g s" %
                 (k1, k2, p1, p2, p1 * k2, 2 * p1 * k1)))
    e = text(EVENTS, over)
    fps = re.search(r'ROGUESQ_FPS60=1 \(opt-in, default retail 30 game fps\): clamp the arbiter limit byte 2 -> 1', e)
    rows.append(("D", "FPS60 lever", "OK" if fps else "FAIL",
                 "FPS60 changes only limiter byte 0x80128EAF 2->1 (N=1 arm); dt then = %.5g s per frame" % (p1 * k2)))
    st = collections.Counter(r[2] for r in rows)
    bad = sum(n for c, n in st.items() if c in ("OPEN", "FAIL", "UNCLASSIFIED", "H-mixed"))
    if not quiet:
        for r in rows:
            print("%s | %-58s | %-12s | %s" % r)
        print("summary: sites=%d rows=%d %s bad=%d" % (len(ss), len(rows), dict(st), bad))
    return rows, bad


def controls(gen_lines, rom):
    res = []

    def flip(name, gl=None, rm=None, over=None, want="bad"):
        rows, bad = census(gl or gen_lines, rm or rom, over, quiet=True)
        ok = (bad > 0) if want == "bad" else (bad == 0)
        res.append((name, ok, bad))

    flip("baseline clean", want="clean")
    # 1 K' = 0.002: a single-VI frame would be charged two VIs -> H-mixed
    o = ROM_K[1] - 0x80000400 + 0x1000
    flip("rom K' 0.002 -> H-mixed", rm=rom[:o] + struct.pack(">f", 0.002) + rom[o + 4:])
    # 2 host rate 62500/ms -> OPEN
    flip("host counter_per_ms 62'500 -> OPEN", over={TIMER: text(TIMER, {}).replace("46'875 * speed", "62'500 * speed")})
    # 3 drop one site -> coverage FAIL
    fn, f, ln = sites(gen_lines)[0]
    g = dict(gen_lines); g[f] = list(g[f]); g[f][ln - 1] = g[f][ln - 1].replace("osGetTime_recomp", "osGetTimeX_recomp")
    flip("dropped site -> coverage FAIL", gl=g)
    # 4 planted site in an unruled function, reading $v0 -> UNCLASSIFIED/OPEN
    g = dict(gen_lines)
    g["zz_plant.c"] = ["RECOMP_FUNC void plantedTimeUser(uint8_t* rdram, recomp_context* ctx) {",
                       "    osGetTime_recomp(rdram, ctx);", "    ctx->r4 = ADD32(ctx->r2, 0);", "}"]
    flip("planted unruled site -> UNCLASSIFIED", gl=g)
    # 5 hi-word read at a ruled site -> OPEN
    g = dict(gen_lines); g[f] = list(g[f]); g[f].insert(ln, "    ctx->r9 = ADD32(ctx->r2, 0);")
    rows, _ = census(g, rom, quiet=True)
    res.append(("hi read at ruled site -> OPEN", any(r[2] == "OPEN" and "reads $v0" in r[3] for r in rows), 1))
    # 6 new reader of a write-only duration -> OPEN
    g = dict(gen_lines)
    g["zz_plant2.c"] = ["RECOMP_FUNC void plantedDurReader(uint8_t* rdram, recomp_context* ctx) {",
                        "    // 0x80FF0000: lui         $v0, 0x8015", "    // 0x80FF0004: lw          $v0, -0x6618($v0)", "}"]
    flip("planted reader of 0x801499E8 -> OPEN", gl=g)
    # 7 hardcoded count rate constant in game code -> OPEN
    g = dict(gen_lines)
    g["zz_plant3.c"] = ["RECOMP_FUNC void plantedRate(uint8_t* rdram, recomp_context* ctx) {",
                        "    // 0x80FF0010: lui         $a2, 0x2CB", "}"]
    flip("planted lui 0x2CB (46.875 MHz) -> OPEN", gl=g)
    # 8 FPS60 lever text changed -> FAIL
    flip("FPS60 lever drift -> FAIL", over={EVENTS: text(EVENTS, {}).replace("clamp the arbiter limit byte 2 -> 1", "x")})
    for n, ok, b in res:
        print("%-44s %s (bad=%d)" % (n, "PASS" if ok else "FAIL", b))
    npass = sum(1 for r in res if r[1])
    print("controls %d/%d" % (npass, len(res)))
    return npass == len(res)


def main():
    gl = load_gen(GEN)
    rom = open(ROM, "rb").read()
    if "--controls" in sys.argv:
        return 0 if controls(gl, rom) else 1
    _, bad = census(gl, rom)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
