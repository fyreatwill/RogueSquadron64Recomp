#!/usr/bin/env python3
"""s7372 AQ runtime half: cross the s7366 static lockset rows with a TSan run's reports.
usage: s7372_aq_runtime_cross.py <rows.tsv> <tsan log files...> [--lines scratch/s7366/lockset_rows.txt] [--cov <llvm-cov export json>]
rows.tsv = tools/s7366_lockset_reviewed.tsv (file, container, function, verdict, reason) or a raw rows_*.tsv / lockset_rows.txt
(file, container, function, unlocked@lines, locks=...).
Per row, from the TSan text:
  RACED   the row's function is in an ACCESS stack of a report whose other side is another thread (a lockset defect if the
          row's static verdict is safe)
  RACED-OTHER  the function is in a racing access stack but not at the row's own unlocked@ line / container: it executed
          and some OTHER location raced (already classified by s7354_tsan_report.py); not a row defect
  SEEN    the row's function appears in some report stack (access or thread-creation): proof it executed, says nothing about
          its own accesses
  UNSEEN  in no report stack. TSan only prints races, so UNSEEN = not executed OR executed clean: NOT a coverage datum.
With --cov-base <json> (export of a profraw copied at the phase start) counts are end minus base = that phase only.
With --cov (llvm-cov export -format=text of a coverage-instrumented run) each row also gets EXEC n = max execution count
over its unlocked@ lines (only raw rows carry them) or the function's entry count: the coverage half TSan cannot give.
Positive control (iron rule 1): a synthetic row for the planted s7354_race_ctl_var race (ROGUESQ_S7354_RACE_CTL=1) is
appended; it must come out RACED or the run's null is void (exit 2). exit 1 if any row with a safe verdict is RACED."""
import re, sys, json, collections
args = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in ("--cov", "--lines", "--cov-base")]
cov_path = sys.argv[sys.argv.index("--cov") + 1] if "--cov" in sys.argv else None
base_path = sys.argv[sys.argv.index("--cov-base") + 1] if "--cov-base" in sys.argv else None  # phase base: counts minus base
rows = []
for l in open(args[0]):
    if l.startswith("#") or l.startswith("TOTAL") or not l.strip(): continue
    p = l.rstrip("\n").split("\t")
    lines = [int(x) for x in re.findall(r"\d+", p[3].split("@", 1)[1])] if len(p) > 3 and p[3].startswith("unlocked@") else []
    verdict = p[3] if len(p) > 3 and not p[3].startswith("unlocked@") else ""
    rows.append({"file": p[0], "cont": p[1], "fn": p[2], "verdict": verdict, "lines": lines})
if "--lines" in sys.argv:  # take unlocked@ lines from a raw census file for reviewed rows that lack them
    raw = {}
    for l in open(sys.argv[sys.argv.index("--lines") + 1]):
        p = l.rstrip("\n").split("\t")
        if len(p) > 3 and p[3].startswith("unlocked@"):
            raw[tuple(p[:3])] = [int(x) for x in re.findall(r"\d+", p[3].split("@", 1)[1])]
    for r in rows: r["lines"] = r["lines"] or raw.get((r["file"], r["cont"], r["fn"]), [])
rows.append({"file": "src/main/main.cpp", "cont": "s7354_race_ctl_var", "fn": "s7354_race_ctl_start", "verdict": "CTL", "lines": []})
FR = re.compile(r"^\s+#\d+\s+(.+?)\s+(\S+?)(?::(\d+))?(?::\d+)?\s+\(")
reports = []  # list of (access stacks [(thread, [frame text])], other stacks [frame text], location)
for f in args[1:]:
    text = open(f, errors="replace").read().splitlines()
    i = 0
    while i < len(text):
        if "WARNING: ThreadSanitizer:" not in text[i]: i += 1; continue
        j = i + 1; acc = []; other = []; loc = ""; cur = None
        while j < len(text) and not text[j].startswith("SUMMARY: ThreadSanitizer"):
            l = text[j]
            m = re.match(r"\s+(?:Previous |Atomic |previous )*(?:atomic )?(?:[Ww]rite|[Rr]ead)\s+of size \d+.*?by (thread T\d+|main thread)", l)
            if m: cur = (m.group(1), []); acc.append(cur)
            elif FR.match(l):
                mm = FR.match(l); fr = f"{mm.group(1)} @{mm.group(2).split('/')[-1]}:{mm.group(3) or 0}"
                (cur[1] if cur is not None else other).append(fr)
            else:
                if "Location is" in l: loc = l.strip()
                cur = None
            j += 1
        reports.append((acc, other, loc)); i = j + 1
def fn_re(fn):  # bare name as a C symbol, a C++ member (::fn(), or the enclosing function of a lambda (fn()::$_N)
    return re.compile(r"(?:^|[\s:*&])" + re.escape(fn) + r"(?:\(|\s|$|\[abi)")
def load_cov(path):
    cov = {}
    data = json.load(open(path))
    for d in data["data"]:
        for fobj in d["files"]:
            cov[fobj["filename"]] = sorted(s_[:6] for s_ in fobj.get("segments", []))
        for fn in d.get("functions", []):
            cov.setdefault("__fn__", {})[fn["name"]] = max(cov.get("__fn__", {}).get(fn["name"], 0), fn["count"])
    names = list(cov.get("__fn__", {}))
    if names:  # export names are mangled; demangle once so bare row names match members / lambdas
        import subprocess
        dem = subprocess.run(["c++filt"], input="\n".join(n.split(":")[-1] if n.startswith("_Z") is False and ".cpp:" in n else n for n in names),
                             capture_output=True, text=True).stdout.splitlines()
        cov["__fn__"] = {d: cov["__fn__"][n] for n, d in zip(names, dem)} if len(dem) == len(names) else cov["__fn__"]
    return cov
cov = load_cov(cov_path) if cov_path else {}
if base_path:
    base_cov = load_cov(base_path)
import bisect
def line_count(segs, L):  # llvm-cov line rule: the region wrapped into line L plus every region starting on it
    i = bisect.bisect_left(segs, [L])
    cand = [segs[i - 1]] if i else []
    while i < len(segs) and segs[i][0] == L: cand.append(segs[i]); i += 1
    cs = [sg[2] for sg in cand if sg[3] and not sg[5]]
    return max(cs) if cs else 0
def cov_of(r):
    if not cov: return None
    fk = next((k for k in cov if k != "__fn__" and k.endswith(r["file"])), None)
    if r["file"] != "src/main/main.cpp" and fk is None: return "NOTLINKED"
    if fk and r["lines"]:
        c = max(line_count(cov[fk], n) for n in r["lines"])
        if base_path: c -= max(line_count(base_cov.get(fk, []), n) for n in r["lines"])
        return c
    def fnc(cv):
        hits = [c for n, c in cv.get("__fn__", {}).items() if re.search(r"(?:^|:|\b)" + re.escape(r["fn"]) + r"(?:\(|$)", n)]
        return max(hits) if hits else 0
    return fnc(cov) - (fnc(base_cov) if base_path else 0)
res = collections.Counter(); bad = 0; ctl = None
out = []
for r in rows:
    rx0 = fn_re(r["fn"]); base = "@" + r["file"].split("/")[-1] + ":"
    class rx:  # function name AND the row's source file (a lambda's thread_proxy frame carries thread.h instead)
        search = staticmethod(lambda fr: rx0.search(fr) and (base in fr or "__thread_proxy" in fr))
    state = "UNSEEN"; why = ""
    for acc, other, loc in reports:
        thr = {t for t, _ in acc}
        hit_acc = [t for t, st in acc if any(rx.search(fr) for fr in st)]
        own = [t for t, st in acc if st and rx.search(st[0]) and (int(st[0].rsplit(":", 1)[1]) in r["lines"]
               or ("'" + r["cont"] + "'") in loc or not r["lines"])]
        if own and len(thr) >= 2 and (r["lines"] or r["verdict"] == "CTL" or ("'" + r["cont"] + "'") in loc):
            state = "RACED"; why = (loc or "")[:90]; break
        if hit_acc and state != "RACED-OTHER": state = "RACED-OTHER"; why = (loc or "")[:90]
        if state == "UNSEEN" and (hit_acc or any(rx.search(fr) for fr in other)): state = "SEEN"
    c = cov_of(r)
    if c is not None: state += f" EXEC {c}"
    res[state.split()[0]] += 1
    if r["verdict"] == "CTL": ctl = state
    elif state.split()[0] == "RACED" and r["verdict"].startswith("H-safe"): bad += 1
    out.append(f"{state:14s} {r['verdict'][:22]:22s} {r['file'].split('/')[-1]:32s} {r['cont'][:34]:34s} {r['fn'][:40]:40s} {why}")
print(f"reports {len(reports)} rows {len(rows)} (incl. control) {dict(res)} control={ctl}")
for o in sorted(out): print(o)
if not (ctl or "").startswith("RACED"): print("CONTROL FAIL: planted race not RACED -> null void"); sys.exit(2)
sys.exit(1 if bad else 0)
