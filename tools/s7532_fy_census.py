#!/usr/bin/env python3
"""s7532 class FY census: host buffers holding a COPY of guest RDRAM bytes, the content twin of the
address-latch classes FW/FX (tools/s7530_fw_census.py, tools/s7531_fx_census.py).  If the guest rewrites
the source between the copy and a later read of a PERSISTENT copy, the host acts on stale bytes.

Copy idioms scanned (comments stripped):  memcpy/memmove(dst, src, n), std::copy(first, last, dst),
X.insert(pos, first, last), X.assign(first, last), and element loops `dst[i] = ... RDRAM[...]`.
A site is IN CLASS when the SOURCE expression names guest memory (rdram, RDRAM, g_rdram_for_submit,
g_recomp_rdram*, fromRDRAM) or the site is in EXTRA (indirect: guest bytes passed in by pointer).
Per in-class site the destination's base identifier is resolved:
  guest-write   dst is guest memory itself (a write-back / patch, not a shadow)            -> out of class
  H-local(auto) dst declared without static in the enclosing function (dies in scope)       -> closed
  log(auto)     the statement is a logging / file-dump statement                            -> closed
  rule          explicit RULES row (file suffix, dst identifier) with class + checks (s7530 run_checks:
                verify=<regex in file>, envoff=<VAR absent from owner/loop config>, nocaller=<sym>)
  UNCLASSIFIED  persistent (static / file scope / member) and no rule                        -> FAIL

  python3 tools/s7532_fy_census.py              # non-auto rows + summary, exit 1 on any FAIL
  python3 tools/s7532_fy_census.py --all        # every in-class row
  python3 tools/s7532_fy_census.py --controls   # planted fixtures, mutation control, coverage control
"""
import bisect, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7530_fw_census as fw

ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "src/main", "src/rsp",
         "lib/rt64/src/hle", "lib/rt64/src/gbi", "lib/rt64/src/render"]
GUEST = re.compile(r'\b(rdram|RDRAM|g_rdram_for_submit|g_recomp_rdram\w*|fromRDRAM)\b')
GUEST_DST = re.compile(r'^\s*&?\s*\(?\s*(rdram|RDRAM|g_rdram_for_submit|g_recomp_rdram\w*|state->fromRDRAM)\b')
CALL = re.compile(r'\b(?:std::)?(memcpy|memmove|copy)\s*\(|(\w+(?:(?:\.|->)\w+)*)\s*\.\s*(insert|assign)\s*\(')
LOOP = re.compile(r'([A-Za-z_][\w.\->]*)\s*\[[^;=]*\]\s*=(?!=)([^;]*)')
LOGSTMT = re.compile(r'printf|fputs|fwrite|std::cerr|\bputs\b|dump_file\.write')
EXTRA = [("hle/rt64_framebuffer_storage.cpp", r"memcpy\(rdramData\.data\(\) \+ dstIndex, data, size\)")]


def split_args(t, i):
    """t[i] is just past '('; return (args, end_index)."""
    depth, cur, args = 0, i, []
    j = i
    while j < len(t):
        c = t[j]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                args.append(t[cur:j])
                return args, j
            depth -= 1
        elif c == "," and depth == 0:
            args.append(t[cur:j]); cur = j + 1
        j += 1
    return args, j


def base_ident(expr):
    e = expr.strip()
    e = re.sub(r'^(\(\s*\w[\w\s\*]*\)\s*)', '', e)        # leading C cast
    e = re.sub(r'^reinterpret_cast<[^>]*>\(', '', e)
    e = e.lstrip("&*( ")
    m = re.match(r'([A-Za-z_]\w*)((?:\s*(?:\.|->)\s*\w+)*)', e)
    if not m:
        return None, False
    return m.group(1), bool(m.group(2)) and not re.match(r'\s*(\.|->)\s*(data|begin|end)\b\s*$', m.group(2))


def code_depth_map(t):
    """Per character offset -> number of open braces that are function/lambda/block bodies (namespace, extern "C",
    struct/class/enum/union bodies and brace initialisers after '=' do not count).  Returns list per line (depth at line start)
    plus a function giving depth at any offset."""
    t2 = re.sub(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])\'', lambda m: ' ' * len(m.group(0)), t)
    stack, marks, last = [], [], 0
    depth = 0
    for i, c in enumerate(t2):
        if c == '{':
            head = t2[max(t2.rfind(';', 0, i), t2.rfind('}', 0, i), t2.rfind('{', 0, i)) + 1:i]
            kind = 'ns' if re.search(r'\bnamespace\b|extern\s+"C"|extern\s*$|\b(struct|class|enum|union)\b[^()]*$|=\s*$', head) else 'code'
            stack.append(kind); depth += kind == 'code'
            marks.append((i, depth))
        elif c == '}':
            if stack:
                depth -= stack.pop() == 'code'
            marks.append((i, depth))
    offs = [m[0] for m in marks]
    def at(pos):
        k = bisect.bisect_right(offs, pos) - 1
        return marks[k][1] if k >= 0 else 0
    return at


def decl_kind(lines, lno, ident, depth_at=None, starts=None):
    """Nearest preceding declaration of ident (0-based line lno, searched to file start):
    'local' | 'persistent' | 'param' | None.  Only the text after the last '{' or ';' before the
    identifier counts, so `static T f() { uint32_t v;` is a local and `{ static T x;` is persistent."""
    TYPE = r'(?:unsigned\s+\w+|auto|bool|char|int|float|double|size_t|u?int\d+_t|uintptr_t|std::[\w:]+(?:<[^;]*>)?|[A-Z]\w*(?:<[^;]*>)?|[a-z]\w*_t)'
    decl = re.compile(r'(?:^\s*|[;{(,]\s*)((?:static\s+|thread_local\s+|const\s+|constexpr\s+|alignas\(\w+\)\s+)*)' + TYPE +
                      r'(?:\s*[\*&]+\s*|\s+)(?:\w+\s*(?:\[[^\]]*\])?\s*(?:=[^,;{]*)?,\s*\**\s*)*' + re.escape(ident) + r'\s*(\[|=|;|,|\{|\)|\()')
    for k in range(lno, -1, -1):
        l = lines[k]
        if ident not in l:
            continue
        for m in decl.finditer(l):
            pre = l[:m.start(1)]
            seg = re.split(r'[{;]', pre)[-1]
            if pre.count('(') > pre.count(')') and not re.search(r'\bfor\s*\(\s*$', pre):
                return 'param'
            if re.search(r'\bstatic\b|\bthread_local\b', m.group(1) + seg):
                return 'persistent'
            if depth_at is not None:
                return 'local' if depth_at(starts[k] + m.start(1)) >= 1 else 'persistent'
            if l == l.lstrip() and '{' not in pre:
                return 'persistent'
            return 'local'
    return None


def in_class_sites(path):
    try:
        raw = open(path, errors="replace").read()
    except OSError:
        return
    t = fw.strip_comments(raw)
    lines = t.split("\n")
    starts = [0]
    for ln in lines[:-1]:
        starts.append(starts[-1] + len(ln) + 1)
    lno_of = lambda pos: bisect.bisect_right(starts, pos) - 1
    depth_at = code_depth_map(t)
    seen = set()
    for m in CALL.finditer(t):
        args, end = split_args(t, m.end())
        if m.group(1) in ("memcpy", "memmove"):
            if len(args) != 3: continue
            dst, src = args[0], args[1]
        elif m.group(1) == "copy":
            if len(args) != 3: continue
            dst, src = args[2], args[0]
        else:
            if m.group(3) == "insert":
                if len(args) != 3: continue
                src = args[1]
            else:
                if len(args) != 2: continue
                src = args[0]
            dst = m.group(2)
        k = lno_of(m.start())
        forced = any(path.endswith(e[0]) and re.search(e[1], t[m.start():end + 1]) for e in EXTRA)
        if not (GUEST.search(src) or forced):
            continue
        a = max(t.rfind(';', 0, m.start()), t.rfind('{', 0, m.start()), t.rfind('}', 0, m.start())) + 1
        yield k + 1, dst.strip(), src.strip(), t[a:t.find(';', end) + 1], lines, raw, k, depth_at, starts
        seen.add(k)
    for k, l in enumerate(lines):
        for mm in LOOP.finditer(l):
            if not GUEST.search(mm.group(2)) or GUEST_DST.match(mm.group(1)):
                continue
            if re.search(r'\b(rdram|RDRAM)\w*\s*$', mm.group(1)):
                continue
            yield k + 1, mm.group(1), mm.group(2).strip(), l, lines, raw, k, depth_at, starts


U, S, B = "src/main/upstream_compat.cpp", "hle/rt64_state.cpp", "src/rsp/dpc_bridge.cpp"
RULES = [
    # --- functional persistent copies: the copy IS the semantic (snapshot taken at the event the consumer models) ---------------
    (B, "g_s4272_shadow", "H-canon",
     "bump-time shadow of every deferred RDP range = the bytes the RDP would have consumed at the bump (s4286/s4287 3/3: feeding "
     "it removes the ODD cimgs the ring-lap overwrite caused); cleared at every stream/wrap flush and task commit",
     {"verify": r"g_deferred_ranges\.clear\(\); g_s4272_sh\.clear\(\); g_s4272_shadow\.clear\(\);"}),
    (B, "wm_live", "H-canon",
     "undo snapshot of the live bytes under each restored range, written back after RT64 read the run. Gfx tasks send "
     "sp_complete BEFORE send_dl, so the guest CPU runs during the restore..undo window: a guest store into an undo range there "
     "would be lost. Measured s7532 ROGUESQ_S7532_UNDO_CHK (control 1/1 both arms): 0 foreign bytes; ring is RSP-only output",
     {"verify": r"ROGUESQ_S7532_UNDO_CHK"}),
    (S, "present", "H-canon",
     "VI present snapshot: present.storage is resized and re-copied from the VI origin on every VI present; the async present "
     "thread shows that VI's scanout (what the VI read at that retrace), cleared on reset",
     {"verify": r"present\.storage\.resize\(screenFbBytes\);"}),
    ("hle/rt64_framebuffer_storage.cpp", "rdramData", "H-canon",
     "upstream RT64: FramebufferManager::storeRAM copies each tracked framebuffer's RDRAM at workload end (rt64_state.cpp "
     "storeRAM call) for that workload's fb ops; rdramUsed is reset per workload (clear)", {"verify": r"rdramUsed = 0;"}),
    ("hle/rt64_rdp.cpp", "TMEM", "H-canon",
     "TMEM model: hardware LoadTile/LoadBlock copy RDRAM into TMEM and later draws read TMEM, so a 'stale' TMEM is the "
     "hardware semantics, not a host artifact", {}),
    ("gbi/rt64_gbi_s2dex.cpp", "state", "H-canon",
     "upstream RT64 S2DEX: readS2DStruct DMAs the obj struct into the S2D buffer right before the command that consumes it "
     "(models the ucode's DMEM struct load)", {"verify": r"readS2DStruct\(state,"}),
    # --- diagnostics: env-gated, default off, consumers are logs / compare counters ---------------------------------------------
    (B, "uc_post", "H-instrument-only", "s7532 undo-window check itself, ROGUESQ_S7532_UNDO_CHK only",
     {"verify": r"ROGUESQ_S7532_UNDO_CHK", "envoff": "ROGUESQ_S7532_UNDO_CHK"}),
    ("hle/rt64_rdp.cpp", "g_s4280_ev", "H-instrument-only",
     "s4280 SetColorImage event ring (host offset + cimg address, not a byte copy; RDRAM appears only in pointer arithmetic); "
     "read only by the bridge's ROGUESQ_G1E_CDIAG attribution (counters/fprintf), reset each commit otherwise",
     {"verify": r"g_s4280_n < 256", "envoff": "ROGUESQ_G1E_CDIAG"}),
    (B, "g_bc_shadow", "H-instrument-only", "s6955 batch reference list, only when ROGUESQ_G1E_BATCH_CHECK (bc_check compare)",
     {"verify": r"ROGUESQ_G1E_BATCH_CHECK", "envoff": "ROGUESQ_G1E_BATCH_CHECK"}),
    (B, "wm_chk", "H-instrument-only", "s6933 merge check, ROGUESQ_WRAP_MERGE_CHECK only",
     {"verify": r"ROGUESQ_WRAP_MERGE_CHECK", "envoff": "ROGUESQ_WRAP_MERGE_CHECK"}),
    (B, "cc_pre", "H-instrument-only", "s6945 coalesce check, ROGUESQ_G1E_COAL_CHECK only",
     {"verify": r"ROGUESQ_G1E_COAL_CHECK", "envoff": "ROGUESQ_G1E_COAL_CHECK"}),
    (B, "cc_exp", "H-instrument-only", "see cc_pre", {"envoff": "ROGUESQ_G1E_COAL_CHECK"}),
    (B, "q", "H-instrument-only", "G5b frame-trigger dump ring (ROGUESQ_G5B_FRAME file), written to disk only",
     {"verify": r"ROGUESQ_G5B_FRAME", "envoff": "ROGUESQ_G5B_FRAME"}),
    (B, "g_f5_hosttgt_pending", "H-instrument-only", "F5 store shadow (rs64_f5_shadow_on: ROGUESQ_LOG_F5_STORE_SHADOW/LOG_ALL)",
     {"verify": r"if \(!rs64_f5_shadow_on\(\)", "envoff": "ROGUESQ_LOG_F5_STORE_SHADOW"}),
    (B, "g_f5_host_order_pending", "H-instrument-only", "see g_f5_hosttgt_pending", {"envoff": "ROGUESQ_LOG_F5_STORE_SHADOW"}),
    (B, "row", "H-instrument-only", "F5 store-shadow registration row (same gate)", {"envoff": "ROGUESQ_LOG_F5_STORE_SHADOW"}),
    (S, "ctx_out", "H-instrument-only", "ost_wb diagnostic reader; destinations are the caller's locals (&ctx, &pri)", {}),
    (S, "pri_out", "H-instrument-only", "see ctx_out", {}),
    ("src/main/s7391_spwm.cpp", "t_snap", "H-instrument-only", "s7391 stack watermark snapshot, ROGUESQ_S7391_SPWM",
     {"envoff": "ROGUESQ_S7391_SPWM"}),
    (U, "s6883_win", "H-instrument-only", "s6883 span log, after `if (!s6883_log()) return;` (ROGUESQ_G1D_SPANLOG)",
     {"verify": r"if \(!s6883_log\(\)\) return;", "envoff": "ROGUESQ_G1D_SPANLOG"}),
    (U, "s6883_snap", "H-instrument-only", "see s6883_win (snapshot hashed and fwritten)", {"envoff": "ROGUESQ_G1D_SPANLOG"}),
    # s7653: post-closure diagnostics (s7535/s7539-s7541/s7644); callers read by hand: events.cpp:1719 + rsp.hpp:345 behind
    # rs64_s7535_on, rt64_render_context gb::at_exit/job_end/compare behind gb::on, s7644 pre hooks return on !g_on / !g_gon.
    ("src/main/rt64_render_context.cpp", "snap", "H-instrument-only", "s7539/s7541 16 MB post-task snapshot, ROGUESQ_S7539_GB_CHK only",
     {"verify": r'getenv\("ROGUESQ_S7539_GB_CHK"\)', "envoff": "ROGUESQ_S7539_GB_CHK"}),
    ("src/main/rt64_render_context.cpp", "gb", "H-instrument-only", "s7541 kind-3 snapshot refresh after `if (!gb::on || !rdram ...) return;`",
     {"verify": r"if \(!gb::on \|\| !rdram \|\| !bytes", "envoff": "ROGUESQ_S7539_GB_CHK"}),
    ("src/rsp/s7535_ga_chk.cpp", "g_sh", "H-instrument-only", "s7535 gfx RSP-input window snapshot, ROGUESQ_S7535_GA_CHK only",
     {"verify": r'getenv\("ROGUESQ_S7535_GA_CHK"\)', "envoff": "ROGUESQ_S7535_GA_CHK"}),
    ("src/rsp/s7535_ga_chk.cpp", "g_row", "H-instrument-only", "s7535 diff rows (dumped to stderr), same gate", {"envoff": "ROGUESQ_S7535_GA_CHK"}),
    ("src/rsp/s7644_rspdma.cpp", "t_snap", "H-instrument-only", "s7644 audio PI-vs-RSP snapshot, after `if (!g_on ...) return;`",
     {"verify": r"if \(!g_on \|\| g_tasks\.load\(\) == 0\) return;", "envoff": "ROGUESQ_S7644_RSPDMA"}),
    ("src/rsp/s7644_rspdma.cpp", "t_g", "H-instrument-only", "s7644 gfx PI span snapshot, after `if (!g_gon) return;`",
     {"verify": r"if \(!g_gon\) return;", "envoff": "ROGUESQ_S7644_RSPDMA"}),
    ("src/rsp/s7751_task_snap.cpp", "s", "H-instrument-only", "s7751 gfx task snapshot (16 MB RSP window), after `if (!dir() ...) return;`",
     {"verify": r"if \(!dir\(\) \|\| !rdram \|\| !dmem\) return;", "envoff": "ROGUESQ_S7751_SNAP"}),
    ("librecomp/src/sp.cpp", "ram_unswapped", "H-dead", "ramdump under dump_frame, which nothing sets true",
     {"verify": r"bool dump_frame = false;"}),
]


def classify(path, row, rules):
    ln, dst, src, stmt, lines, raw, k, depth_at, starts = row
    if GUEST_DST.match(dst):
        return "guest-write", "dst is guest memory"
    ident, member = base_ident(dst)
    rule = next((r for r in rules if path.endswith(r[0]) and r[1] == (ident or dst)), None)
    if rule:
        err = fw.run_checks(path, raw, rule[4], fw.BINARY)
        return ("FAIL-check", err) if err else (rule[2], rule[3])
    if LOGSTMT.search(stmt):
        return "log(auto)", "logging / dump statement"
    if ident is None:
        return "UNCLASSIFIED", "unparsed dst %r" % dst
    kind = decl_kind(lines, k, ident, depth_at, starts)
    if kind in ("local",) and not member:
        return "H-local(auto)", "dst %s declared local in scope" % ident
    return "UNCLASSIFIED", "dst %s (%s%s), no rule" % (ident, kind, ", member" if member else "")


def census(files, rules=None):
    rules = RULES if rules is None else rules
    rows, fails = [], 0
    for p in files:
        for row in in_class_sites(p):
            cls, why = classify(p, row, rules)
            if cls in ("UNCLASSIFIED", "FAIL-check"):
                fails += 1
            rows.append((p, row[0], row[1][:40], cls, why))
    return rows, fails


def files_under(roots=ROOTS):
    return fw.files_under(roots)


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    rows, fails = census(files_under())
    from collections import Counter
    cnt = Counter(r[3] for r in rows)
    for r in rows:
        if "--all" in sys.argv or not r[3].endswith("(auto)") and r[3] != "guest-write":
            print("%-46s %5d %-30s %-18s %s" % (r[0].replace("lib/N64ModernRuntime/", "").replace("lib/rt64/src/", "rt64/"),
                                                 r[1], r[2], r[3], r[4][:110]))
    print("summary: sites=%d %s fails=%d" % (len(rows), dict(sorted(cnt.items())), fails))
    sys.exit(1 if fails else 0)


def controls():
    res = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture_fy.cpp")
        open(p, "w").write("static uint8_t g_planted_copy[64];\nvoid snap(uint8_t* rdram){ memcpy(g_planted_copy, rdram + 0x100, 64); }\n"
                           "int use(){ return g_planted_copy[3]; }\n"
                           "void loc(uint8_t* rdram){ uint8_t tmp[16]; memcpy(tmp, rdram + 8, 16); (void)tmp; }\n"
                           "void wr(uint8_t* rdram){ memcpy(rdram + 4, rdram + 64, 4); }\n")
        rows, fails = census([p])
        cls = {r[2]: r[3] for r in rows}
        res.append(("planted persistent copy -> UNCLASSIFIED", cls.get("g_planted_copy") == "UNCLASSIFIED", rows))
        res.append(("local copy -> H-local(auto)", cls.get("tmp") == "H-local(auto)", rows))
        res.append(("guest write-back -> guest-write", cls.get("rdram + 4") == "guest-write", rows))
        res.append(("fixture fails == 1", fails == 1, fails))
        # mutation: delete the per-flush shadow clear from a copy of dpc_bridge.cpp -> the H-canon g_s4272_shadow row must FAIL
        src = B
        mut = os.path.join(d, "src", "rsp", "dpc_bridge.cpp"); os.makedirs(os.path.dirname(mut))
        txt = open(src, errors="replace").read()
        txt2 = txt.replace("g_deferred_ranges.clear(); g_s4272_sh.clear(); g_s4272_shadow.clear();", "g_deferred_ranges.clear(); g_s4272_sh.clear();")
        open(mut, "w").write(txt2)
        rows, fails = census([mut])
        bad = [r for r in rows if r[2] == "g_s4272_shadow"]
        res.append(("mutation: shadow clear removed -> FAIL-check", txt2 != txt and bad and all(r[3] == "FAIL-check" for r in bad), bad[:1]))
    rows, fails = census(files_under(), rules=[])
    res.append(("coverage: rule-less census sees >=25 UNCLASSIFIED", fails >= 25, "fails=%d" % fails))
    rows, fails = census(files_under())
    res.append(("live census 0 fails", fails == 0, [r for r in rows if r[3] in ("UNCLASSIFIED", "FAIL-check")]))
    ok = True
    for name, good, detail in res:
        print("control %-52s %s %s" % (name, "PASS" if good else "FAIL", "" if good else detail))
        ok &= bool(good)
    print("controls: %d/%d PASS" % (sum(1 for r in res if r[1]), len(res)))
    return 0 if ok else 1


if __name__ == "__main__":
    main()
