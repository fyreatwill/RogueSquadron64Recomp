#!/usr/bin/env python3
"""s7557 class GQ census: every DEFAULT-ON behaviour change the port makes, read from the code that is actually built.

Question (owner rule: no default flips without the owner): does each env lever that is ACTIVE WHEN UNSET have
 (1) a retail switch (=0 or a documented 0/old value), (2) a row naming it in the docs the owner reads
     (docs/OWNER-OPT-INS.md, docs/CURRENT-TRUTH.md, docs/FPS60-FIXES.md, docs/PROJECT-OVERVIEW.md), and
 (3) a qualifying session in PORTING-STATE.md (a '## Session N' entry that names it)?

Sources = what is compiled: src/, lib/N64ModernRuntime/{librecomp,ultramodern}/src, lib/rt64/src, the GENERATED code
(../N64Recomp/RecompiledFuncs/*.c, build/factor5_ucode/*.c), so dead apply_*.py text is not counted.
Reads: getenv("ROGUESQ_X") with the result bound to a variable, plus the defaulting helpers (s7397_env/s7396_env(n,true),
s6919_mode(n,1), rs64_env_int(n,d!=0), !rs64_s7355_env_is(n,"0")).  Default classes per site:
  ON   - unset evaluates to active (idioms in ON_IDIOMS: !(e && *e=='0'), !e||*e!='0', !(e&&*e)?1:..., helper default true)
  VAL  - unset yields a nonzero number from an ato*/strto* parse (value lever; may be a log cap -> diag rule)
  OFF  - everything else (opt-in); not reported.
Per name: diag (name matches DIAG_RE: logging/dumps/controls/watches; changes no guest-visible state) or lever.
Verdicts for ON levers: H-listed (doc row + session), H-unlisted (no doc row: list for the owner), H-no-session.
An ON lever has its =0 retail switch by construction (the idiom IS the switch), so H-no-switch cannot arise for a read;
VAL-only names are 'param' rows (a feature parameter, inert unless the feature is on; 'param-nosw' = no 0/old mapping
at the read).  --write regenerates docs/DEFAULT-ON-LEVERS.md (every ON lever with its source comment and sessions).
  python3 tools/s7557_gq_census.py [--rows]   # summary (+ every lever row); exit 0 always unless --strict and H-no-switch
  python3 tools/s7557_gq_census.py --controls # planted mutations, each must flip the verdict
"""
import collections, glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.environ.get("RS64_RECOMP_FUNCS", os.path.join(os.path.dirname(REPO), "N64Recomp", "RecompiledFuncs"))
DOCS = ["docs/OWNER-OPT-INS.md", "docs/CURRENT-TRUTH.md", "docs/FPS60-FIXES.md", "docs/PROJECT-OVERVIEW.md"]
G = re.compile(r'getenv\("(ROGUESQ_[A-Z0-9_]+)"\)')
P = r"(?:\*V|V\[0\])"
ON_IDIOMS = [
    r"!\(\s*V\s*&&\s*P\s*==\s*'0'\s*\)",
    r"!\(\s*V\s*&&\s*P\s*&&\s*P\s*!=\s*'0'\s*\)\s*\?\s*(?:[1-9]|true)",
    r"!\(\s*V\s*&&\s*P\s*\)\s*\?\s*(?:[1-9]|true)",
    r"!V\s*\|\|\s*!P\s*\|\|\s*P\s*==\s*'0'\s*\?\s*(?:[1-9]|true)",
    r"\(?!V\s*\|\|\s*!P\s*\|\|\s*P\s*!=\s*'0'\)?\s*\?\s*(?:[1-9]|true)",
    r"!V\s*\|\|\s*P\s*!=\s*'0'",
    r"if\s*\(\s*!\s*\(\s*V\s*&&\s*P\s*==\s*'0'\s*\)\s*\)",
    r"V\s*&&\s*P\s*==\s*'0'\s*\)?\s*\?\s*(?:0|false)\s*:\s*(?:[1-9]|true)",
    r"^\s*;?\s*return\s+V\s*&&\s*P\s*==\s*'0'\s*;",              # inverse 'off' flag: true only when =0
    r"\(\s*!V\s*\|\|\s*!P\s*\)\s*\?\s*[1-9]",                     # (!e || !e[0]) ? 2 : ...
]
VAL_RE = r"\?\s*(?:\([a-z0-9_ ]+\)\s*)?(?:std::)?(?:atoi|atof|atol|atoll|strtoul|strtol|strtod|strtoull)\(V[^)]*\)\s*\)?\s*:\s*\(?(-?(?:0x[0-9A-Fa-f]+|[0-9][0-9.]*)[uUlLfF]*)"
HELPERS = [  # (regex with name group, default-class function of match)
    (re.compile(r'(?:s7397_env|s7396_env)\("(ROGUESQ_[A-Z0-9_]+)",\s*(true|false)\)'), lambda m: "ON" if m.group(2) == "true" else None),
    (re.compile(r's6919_mode\("(ROGUESQ_[A-Z0-9_]+)",\s*(\d+)\)'), lambda m: "ON" if m.group(2) != "0" else None),
    (re.compile(r'rs64_env_int\("(ROGUESQ_[A-Z0-9_]+)",\s*(-?\d+)\)'), lambda m: ("VAL=" + m.group(2)) if m.group(2) != "0" else None),
    (re.compile(r'!\s*rs64_s7355_env_is\("(ROGUESQ_[A-Z0-9_]+)",\s*"0"\)'), lambda m: "ON"),
]
DIAG_RE = re.compile(r"(?:^|_)(LOG|LOGS|DUMP|TRACE|CTL|CHK|CHECK|WATCH|PLANT|CENSUS|PROBE|STAT|STATS|VERBOSE|RING|SAMPLE|"
                     r"QUIET|PRINT|TM|BREADCRUMB|SHEET|STAMP|PROF|PROFILE|AUDIT|TAG|WITNESS|HOLD)(?:_|$)|^ROGUESQ_DIAG_|^ROGUESQ_LOG")
# Names whose tokens look diagnostic but that change guest-visible behaviour, or the reverse (checked by hand, s7557).
DIAG_OVERRIDE = {"ROGUESQ_WAITTAB": True,   # s7191 wait-table instrument (timing only, no guest-visible change)
                 "ROGUESQ_STALL_DUMP": True, "ROGUESQ_STALL_SAMPLE": True}
SWITCH_RE = re.compile(r"(?:=\s*0\b|\b0\s*=|\b0\s*(?:->|restores|keeps|=)\s*(?:old|retail|off)|\bold\b|\bretail\b|disable)", re.I)


def sources():
    out = []
    for d in ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]:
        for r, _, fs in os.walk(os.path.join(REPO, d)):
            out += [os.path.join(r, f) for f in fs if f.endswith((".cpp", ".c", ".h", ".hpp", ".mm"))]
    out += sorted(glob.glob(os.path.join(GEN, "*.c"))) + sorted(glob.glob(os.path.join(REPO, "build/factor5_ucode/*.c")))
    return out


def classify_text(t):
    """yield (name, cls, line_text) for every default-active read in text t."""
    for m in G.finditer(t):
        pre = t[max(0, m.start() - 80):m.start()].replace("std::", "")
        b = re.search(r"([a-z_][a-z_0-9]*)\s*=\s*$", pre)
        if not b:
            continue
        v = re.escape(b.group(1))
        w = re.sub(r"\s+", " ", t[m.end():m.end() + 400])
        ls = t.rfind("\n", 0, m.start()) + 1
        le = t.find("\n", m.end()); le = len(t) if le < 0 else le
        line = t[ls:le]
        above = t[max(0, ls - 600):ls].split("\n")[-4:-1] if ls else []
        below = t[le + 1:le + 400].split("\n")[:2]
        line = " ".join([line] + [x for x in reversed(above)] + below)  # comment_of takes the first comment found
        cls = None
        for idi in ON_IDIOMS:
            # s7565: generated-code fixups spell the char as 48 (e[0] == 48), not '0' -- missed S4889/S7476/S4875
            if re.search(idi.replace("P", P).replace("V", v).replace("'0'", "(?:'0'|48)"), w):
                cls = "ON"; break
        if not cls:
            vm = re.search(VAL_RE.replace("V", v), w[:200])
            if vm and not re.fullmatch(r"-?0(?:x0+)?(?:\.0*)?[uUlLfF]*", vm.group(1)):
                cls = "VAL=" + vm.group(1)
                if not SWITCH_RE.search(line + " " + w[:200]):
                    cls += "!nosw"
        if cls:
            yield m.group(1), cls, line.strip()[:200]
    for rx, f in HELPERS:
        for m in rx.finditer(t):
            c = f(m)
            if c:
                yield m.group(1), c, m.group(0)


def doc_index():
    idx = collections.defaultdict(set)
    for d in DOCS:
        p = os.path.join(REPO, d)
        if os.path.exists(p):
            for n in set(re.findall(r"ROGUESQ_[A-Z0-9_]+", open(p, errors="ignore").read())):
                idx[n].add(os.path.basename(d))
    sess = collections.defaultdict(list); cur = None
    for line in open(os.path.join(REPO, "PORTING-STATE.md"), errors="ignore"):
        h = re.match(r"## Session (\d+)", line)
        if h:
            cur = int(h.group(1)); continue
        if cur is not None and "ROGUESQ_" in line:
            for n in set(re.findall(r"ROGUESQ_[A-Z0-9_]+", line)):
                if not sess[n] or sess[n][-1] != cur:
                    sess[n].append(cur)
    return idx, sess


def census(texts, idx, sess):
    reads = collections.defaultdict(lambda: {"cls": set(), "files": set(), "line": ""})
    for fn, t in texts:
        for n, c, line in classify_text(t):
            r = reads[n]; r["cls"].add(c); r["files"].add(os.path.basename(fn)); r["line"] = r["line"] or line
    rows = []
    for n, r in sorted(reads.items()):
        diag = DIAG_OVERRIDE.get(n, bool(DIAG_RE.search(n)))
        if diag:
            rows.append((n, r, "diag", "diag-only")); continue
        if not any(c == "ON" for c in r["cls"]):
            # value default only: a parameter of some feature; inert unless that feature is on. '!nosw' = no 0/old
            # mapping visible at the read (informational: a parameter needs none when its feature has the switch).
            rows.append((n, r, "param", "param-nosw" if any(c.endswith("!nosw") for c in r["cls"]) else "param")); continue
        if not idx.get(n):
            v = "H-unlisted"
        elif not sess.get(n):
            v = "H-no-session"
        else:
            v = "H-listed"
        rows.append((n, r, "lever", v))
    return rows


def main():
    idx, sess = doc_index()
    if "--controls" in sys.argv:
        return controls(idx, sess)
    texts = [(f, open(f, errors="ignore").read()) for f in sources()]
    rows = census(texts, idx, sess)
    cnt = collections.Counter(v for _, _, _, v in rows)
    nsites = sum(len(G.findall(t)) for _, t in texts)
    print(f"[gq] sources={len(texts)} getenv_sites={nsites} default_active_names={len(rows)} " + " ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
    for n in ("ROGUESQ_CULL_SPIKE", "ROGUESQ_S7402_CLOCKFIX", "ROGUESQ_S7476_A1FIX"):
        hit = [v for m, _, _, v in rows if m == n]
        print(f"[gq] coverage {n}: {hit[0] if hit else 'MISSING'}")
    show = "--rows" in sys.argv
    for n, r, k, v in rows:
        if (k == "lever" and (show or v != "H-listed")) or (k == "param" and "--params" in sys.argv):
            ss = sess.get(n, [])
            print(f"  {v:13s} {n:34s} {'/'.join(sorted(r['cls'])):14s} docs={','.join(sorted(idx.get(n, []))) or '-'} "
                  f"s={ss[0] if ss else '-'}..{ss[-1] if ss else '-'} in={','.join(sorted(r['files']))[:60]}")
    cov = all(any(m == n for m, *_ in rows) for n in ("ROGUESQ_CULL_SPIKE", "ROGUESQ_S7402_CLOCKFIX"))
    if "--write" in sys.argv:
        write_doc(rows, idx, sess)
    bad = cnt.get("H-unlisted", 0) + cnt.get("H-no-session", 0)
    return 1 if (not cov or ("--strict" in sys.argv and bad)) else 0


def comment_of(line):
    m = re.search(r"(//|/\*)\s*(.*?)(\*/|$)", line)
    return (m.group(2).strip() if m else "").replace("|", "/")[:150]


def write_doc(rows, idx, sess):
    out = ["# Default-on port levers (generated by tools/s7557_gq_census.py --write; do not hand-edit)", "",
           "Every env lever the built code treats as ACTIVE WHEN UNSET, i.e. a behaviour change from the plain recompiled game",
           "that the owner gets without asking. Each one is switched back to the old/retail path with `ROGUESQ_<NAME>=0`.",
           "Owner rule: none of these defaults changes without the owner. Diagnostic-only names (logs, dumps, controls) and",
           "feature parameters (value defaults, inert unless their feature is on) are excluded; counts are in the census summary.",
           "`docs` = which of OWNER-OPT-INS / CURRENT-TRUTH / FPS60-FIXES / PROJECT-OVERVIEW names it; `sessions` = first..last",
           "PORTING-STATE session that names it. `H-unlisted` rows had no doc row before s7557: this file is now their row.", "",
           "| lever | verdict | sessions | docs | read in | source comment at the read |", "|---|---|---|---|---|---|"]
    for n, r, k, v in rows:
        if k != "lever":
            continue
        ss = sess.get(n, [])
        out.append(f"| `{n}` | {v} | {ss[0] if ss else '-'}..{ss[-1] if ss else '-'} | "
                   f"{', '.join(sorted(d.replace('.md', '') for d in idx.get(n, []))) or '-'} | "
                   f"{', '.join(sorted(r['files']))[:50]} | {comment_of(r['line'])} |")
    open(os.path.join(REPO, "docs/DEFAULT-ON-LEVERS.md"), "w").write("\n".join(out) + "\n")
    print(f"[gq] wrote docs/DEFAULT-ON-LEVERS.md ({sum(1 for *_, k, _ in rows if k == 'lever')} levers)")


def controls(idx, sess):
    idx = dict(idx); sess = dict(sess)
    idx["ROGUESQ_GQCTL_LISTED"] = {"OWNER-OPT-INS.md"}; sess["ROGUESQ_GQCTL_LISTED"] = [9999]
    T = [
        ("ROGUESQ_GQCTL_UNLISTED", 'static const bool a = [] { const char* e = std::getenv("ROGUESQ_GQCTL_UNLISTED"); return !(e && *e == \'0\'); }();', "H-unlisted"),
        ("ROGUESQ_GQCTL_LISTED", 'static const bool a = [] { const char* e = std::getenv("ROGUESQ_GQCTL_LISTED"); return !(e && *e == \'0\'); }();', "H-listed"),
        ("ROGUESQ_GQCTL_LOG_X", 'static const bool a = [] { const char* e = std::getenv("ROGUESQ_GQCTL_LOG_X"); return !(e && *e == \'0\'); }();', "diag-only"),
        ("ROGUESQ_GQCTL_NOSW", 'static const int a = [] { const char* e = std::getenv("ROGUESQ_GQCTL_NOSW"); return e ? atoi(e) : 7; }();', "param-nosw"),
        ("ROGUESQ_GQCTL_SW", 'static const int a = [] { const char* e = std::getenv("ROGUESQ_GQCTL_SW"); return e ? atoi(e) : 7; }(); // =0 old', "param"),
        ("ROGUESQ_GQCTL_OPTIN", 'static const bool a = [] { const char* e = std::getenv("ROGUESQ_GQCTL_OPTIN"); return e && *e && *e != \'0\'; }();', None),
        ("ROGUESQ_GQCTL_HELPER", 'static bool f = s7396_env("ROGUESQ_GQCTL_HELPER", true);', "H-unlisted"),
        ("ROGUESQ_GQCTL_INVOFF", 'static const bool off = [] { const char* e = std::getenv("ROGUESQ_GQCTL_INVOFF"); return e && e[0] == \'0\'; }();', "H-unlisted"),
        ("ROGUESQ_GQCTL_HELPER_OFF", 'static bool f = s7396_env("ROGUESQ_GQCTL_HELPER_OFF", false);', None),
        ("ROGUESQ_GQCTL_CHR48", 'if (s_on < 0) { const char* e = getenv("ROGUESQ_GQCTL_CHR48"); s_on = !(e && e[0] == 48); }', "H-unlisted"),
    ]
    ok = 0
    for n, src, want in T:
        rows = census([("ctl.cpp", src)], idx, sess)
        got = next((v for m, _, _, v in rows if m == n), None)
        good = got == want; ok += good
        print(f"[gq-ctl] {n:28s} want={want} got={got} {'ok' if good else 'FAIL'}")
    texts = [(f, open(f, errors="ignore").read()) for f in sources()]
    rows = census(texts, *doc_index())
    for n in ("ROGUESQ_CULL_SPIKE", "ROGUESQ_S7402_CLOCKFIX", "ROGUESQ_S7476_A1FIX"):
        got = next((v for m, _, _, v in rows if m == n), None); good = got == "H-listed"; ok += good
        print(f"[gq-ctl] coverage {n:19s} want=H-listed got={got} {'ok' if good else 'FAIL'}")
    tot = len(T) + 3
    print(f"[gq-ctl] controls {ok}/{tot}")
    return 0 if ok == tot else 1


if __name__ == "__main__":
    sys.exit(main())
