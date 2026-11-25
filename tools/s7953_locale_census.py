#!/usr/bin/env python3
"""s7953 class LC census: nothing that runs in the game process may change the C locale.

Why: every float parse in our tree (env knobs such as ROGUESQ_DRAW_DISTANCE, settings.txt, stand-in tuning, RT64 config
text) goes through strtod/atof/sscanf/printf, which follow LC_NUMERIC. If anything called setlocale(LC_ALL, "") under a
comma locale, "1.5" would parse as 1 and print as "1,50" (measured, s7953 plant arm). The process starts in "C" and stays
there only because no linked code changes it; this gate turns RED the moment that stops being true.

Sources (two lines):
 1. static source scan of src/, lib/N64ModernRuntime/{librecomp,ultramodern}, lib/rt64/src (minus contrib) for
    setlocale / uselocale / newlocale / std::locale::global / .imbue( ; query-only calls (setlocale(X, nullptr|NULL|0)) are
    'query'; reviewed setters are listed in REVIEWED; anything else is OPEN.
 2. undefined-symbol imports (nm -u) of build/RogueSquadron64Recomp and every non-system dylib it loads (followed through
    @loader_path/@executable_path/@rpath, e.g. sdl2-compat -> libSDL3): a locale-setter import in a third-party dylib is
    OPEN; in our binary it is OPEN unless every source setter is reviewed.
--witness DIR: also score the runtime witness extracts DIR/{base,stress,plant}.s7953.txt (ROGUESQ_S7953_LOCALE=1 logs,
    scratch/s7953/run.zsh): base and stress (LC_ALL=de_DE.UTF-8 launch) must stay C with '.' throughout, plant
    (ROGUESQ_S7953_PLANT=de_DE.UTF-8) must show the CHANGED line with dp=',' (positive control for the witness itself).
Controls (always): planted setlocale(LC_ALL, "") source line -> OPEN; planted _uselocale import in a third-party dylib -> OPEN;
dropping the REVIEWED row -> the s7953 plant setter turns OPEN. Exit 1 on any open row or failed control.
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = ["src", "lib/N64ModernRuntime/librecomp", "lib/N64ModernRuntime/ultramodern", "lib/rt64/src"]
EXTS = (".c", ".cc", ".cpp", ".h", ".hpp", ".mm", ".m", ".inl")
CALL = re.compile(r"\b(setlocale|uselocale|newlocale|_create_locale)\s*\(|\blocale::global\s*\(|\.imbue\s*\(")
QUERY = re.compile(r"\bsetlocale\s*\(\s*LC_[A-Z]+\s*,\s*(nullptr|NULL|0)\s*\)")
# (file, substring) -> reason. Keep tiny: a reviewed setter must be env-gated and off in normal play.
REVIEWED = {("src/main/main.cpp", "setlocale(LC_ALL, pl)"): "s7953 positive-control plant, only with ROGUESQ_S7953_LOCALE=1 + ROGUESQ_S7953_PLANT"}
SETTER_SYMS = ("_setlocale", "_uselocale", "_newlocale", "__ZNSt3__16locale6globalERKS0_")
DLOPEN_SDL3 = ("/opt/homebrew/opt/sdl3/lib/libSDL3.0.dylib", "/opt/homebrew/lib/libSDL3.0.dylib", "/usr/local/lib/libSDL3.0.dylib")
BIN = os.path.join(ROOT, "build", "RogueSquadron64Recomp")


STR = re.compile(r'"(?:[^"\\]|\\.)*"')


def strip_comment(line):
    line = STR.sub('""', line)  # string literals ("[s7953] plant setlocale(...)" log text) are not calls
    i = line.find("//")
    return line if i < 0 else line[:i]


def scan_sources(extra=()):
    rows = []
    files = []
    for d in SCAN:
        for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
            dn[:] = [x for x in dn if x != "contrib"]
            files += [os.path.join(dp, f) for f in fn if f.endswith(EXTS)]
    items = []
    for f in sorted(files):
        try:
            txt = open(f, errors="replace").read()
        except OSError:
            continue
        items.append((os.path.relpath(f, ROOT), txt))
    items += list(extra)
    for rel, txt in items:
        for n, line in enumerate(txt.split("\n"), 1):
            code = strip_comment(line)
            for m in CALL.finditer(code):
                seg = code[m.start():m.start() + 120]
                rows.append((rel, n, seg.strip()))
    return rows, len(items)


def classify(rows, reviewed):
    out = []
    for rel, n, seg in rows:
        if QUERY.match(seg):
            v = "query"
        elif any(rel == f and s in seg for (f, s) in reviewed):
            v = "reviewed"
        else:
            v = "OPEN"
        out.append((v, rel, n, seg[:80]))
    return out


def deps(path, seen):
    try:
        o = subprocess.run(["otool", "-L", path], capture_output=True, text=True).stdout.split("\n")[1:]
    except OSError:
        return
    base = os.path.dirname(path)
    for l in o:
        l = l.strip().split(" (")[0]
        if not l or l.startswith(("/System/", "/usr/lib/")):
            continue
        cands = [l]
        for tok in ("@loader_path", "@rpath", "@executable_path"):
            if l.startswith(tok):
                cands = [l.replace(tok, base, 1), l.replace(tok, os.path.dirname(BIN), 1)]
        for c in cands:
            c = os.path.realpath(c)
            if os.path.isfile(c) and c not in seen and c != os.path.realpath(path):
                seen.add(c)
                deps(c, seen)
                break


def imports(path):
    o = subprocess.run(["nm", "-u", path], capture_output=True, text=True).stdout.split()
    return sorted(s for s in o if s in SETTER_SYMS)


def score_imports(imp, all_reviewed):
    open_rows = []
    for path, syms in imp.items():
        ours = os.path.realpath(path) == os.path.realpath(BIN)
        for s in syms:
            if ours and s == "_setlocale" and all_reviewed:
                continue
            open_rows.append((path, s))
    return open_rows


def witness(d):
    res = {}
    for a in ("base", "stress", "plant"):
        p = os.path.join(d, a + ".s7953.txt")
        if not os.path.isfile(p):
            return False, "missing " + p
        L = [l for l in open(p).read().split("\n") if l.startswith("[s7953] frame=")]
        c = [l for l in L if "LC_ALL=C LC_NUMERIC=C dp=. strtod(1.5)=1.5 printf=1.50" in l]
        ch = [l for l in L if "CHANGED" in l and "dp=, " in l and "strtod(1.5)=1 " in l]
        res[a] = (len(L), len(c), len(ch))
    ok = (res["base"][0] > 0 and res["base"][0] == res["base"][1] and res["stress"][0] > 0 and res["stress"][0] == res["stress"][1]
          and res["base"][2] == 0 and res["stress"][2] == 0 and res["plant"][2] == 1 and res["plant"][1] >= 1)
    return ok, " ".join("%s samples=%d C=%d changed_comma=%d" % (a, *res[a]) for a in ("base", "stress", "plant"))


def main():
    wdir = sys.argv[sys.argv.index("--witness") + 1] if "--witness" in sys.argv else None
    rows, nfiles = scan_sources()
    cl = classify(rows, REVIEWED)
    for r in cl:
        print("row %-8s %s:%d %s" % r)
    src_open = [r for r in cl if r[0] == "OPEN"]
    all_rev = not src_open
    seen = set()
    deps(BIN, seen)
    # sdl2-compat dlopen()s SDL3 at runtime (no LC_LOAD_DYLIB, so otool -L misses it): add it by its install names.
    if any("sdl2-compat" in x for x in seen):
        for c in DLOPEN_SDL3:
            if os.path.isfile(c):
                seen.add(os.path.realpath(c))
                deps(os.path.realpath(c), seen)
                break
        else:
            print("OPEN dlopen target libSDL3 not found (sdl2-compat present)")
            return 1
    imp = {BIN: imports(BIN)}
    for d in sorted(seen):
        imp[d] = imports(d)
    for p, s in imp.items():
        print("imports %s %s" % (os.path.relpath(p, ROOT) if p.startswith(ROOT) else p, ",".join(s) or "-"))
    imp_open = score_imports(imp, all_rev)
    for p, s in imp_open:
        print("OPEN import %s %s" % (p, s))
    # controls
    c1 = [r for r in classify(scan_sources([("planted/x.cpp", 'int f(){ setlocale(LC_ALL, ""); return 0; }')])[0], REVIEWED) if r[0] == "OPEN" and r[1] == "planted/x.cpp"]
    fake = dict(imp)
    fake["/planted/libSDL3.dylib"] = ["_uselocale"]
    c2 = [x for x in score_imports(fake, all_rev) if x[0] == "/planted/libSDL3.dylib"]
    c3 = [r for r in classify(rows, {}) if r[0] == "OPEN" and r[1] == "src/main/main.cpp"]
    c3b = score_imports({BIN: ["_setlocale"]}, False)
    ctl = bool(c1) and bool(c2) and bool(c3) and bool(c3b)
    print("CONTROL planted_source=%s planted_dylib_import=%s drop_reviewed=%s/%s %s" % (
        "FIRED" if c1 else "MISSED", "FIRED" if c2 else "MISSED", "FIRED" if c3 else "MISSED", "FIRED" if c3b else "MISSED",
        "PASS" if ctl else "FAIL"))
    wok = True
    if wdir:
        wok, msg = witness(wdir)
        print("WITNESS %s %s" % (msg, "PASS" if wok else "FAIL"))
    nq = sum(1 for r in cl if r[0] == "query")
    nr = sum(1 for r in cl if r[0] == "reviewed")
    print("s7953 LC census files=%d rows=%d query=%d reviewed=%d open=%d dylibs=%d import_open=%d" % (
        nfiles, len(cl), nq, nr, len(src_open), len(seen), len(imp_open)))
    return 0 if (not src_open and not imp_open and ctl and wok) else 1


if __name__ == "__main__":
    sys.exit(main())
