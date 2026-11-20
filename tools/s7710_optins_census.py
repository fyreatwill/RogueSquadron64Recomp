#!/usr/bin/env python3
"""s7710 owner-setting census: every ROGUESQ_* name the owner is told to type must be read by the code.

Sources of names the owner sees:
  docs/OWNER-OPT-INS.md, README.md          (every ROGUESQ_ token)
  src/main/rs64_settings.cpp presets()       (the --preset tv|ultrawide|window env pairs)
  build/settings.txt                         (the owner's own file, read-only, if present)
A name counts as READ when it appears as a quoted string "ROGUESQ_X" in host/runtime/RT64 sources or in a
fixup/apply script (they inject C into generated code), excluding rs64_settings.cpp for the preset names (the table
itself would otherwise be its own witness), or as a CMake option(ROGUESQ_X ...) in CMakeLists.txt.
ALLOW: names that are documentation placeholders, not settings.

A name that only matches as a longer extension of a read prefix (e.g. "ROGUESQ_" + suffix built at run time) is
reported PREFIX and counts as MISSING unless allow-listed: the census cannot prove a run-time-built name is read.

Exit 0 = every name read; 1 = MISSING rows; 2 = control failure.
--controls: plant a fake doc name (must be MISSING), a fake preset name (must be MISSING), drop a real name's only
reader (must flip it MISSING), and check a known-read name stays READ, before the real run.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = ["docs/OWNER-OPT-INS.md", "README.md"]
SETTINGS_CPP = "src/main/rs64_settings.cpp"
OWNER_FILE = "build/settings.txt"
ROOTS = ["src", "lib/rt64/src", "lib/N64ModernRuntime"]
EXTS = (".c", ".cpp", ".h", ".hpp", ".mm", ".m")
ALLOW = {"ROGUESQ_NAME": "placeholder in 'ROGUESQ_NAME=value' (settings file syntax)"}
TOK = re.compile(r"ROGUESQ_[A-Z0-9_]*[A-Z0-9]")
QUOTED = re.compile(r'"(ROGUESQ_[A-Z0-9_]*)')


def doc_names(texts):
    out = {}
    for path, text in texts:
        for i, line in enumerate(text.split("\n"), 1):
            for m in TOK.findall(line):
                out.setdefault(m, []).append(f"{path}:{i}")
    return out


def preset_names(cpp_text):
    m = re.search(r"presets\(\)\s*\{(.*?)\n\}", cpp_text, re.S)
    if not m:
        return None
    return sorted(set(re.findall(r'\{"(ROGUESQ_[A-Z0-9_]+)"', m.group(1))))


def owner_file_names(text):
    return sorted({l.split("=", 1)[0].strip() for l in text.split("\n")
                   if l.strip().startswith("ROGUESQ_") and "=" in l})


def source_files():
    files = []
    for r in ROOTS:
        for dp, dn, fn in os.walk(os.path.join(ROOT, r)):
            dn.sort()
            for f in sorted(fn):
                if f.endswith(EXTS):
                    files.append(os.path.join(dp, f))
    tools = os.path.join(ROOT, "tools")
    for f in sorted(os.listdir(tools)):
        if (f.startswith("fixup_") or f.startswith("apply_")) and f.endswith(".py"):
            files.append(os.path.join(tools, f))
    return files


def readers(files_text):
    """name -> set of relative files quoting it."""
    rd = {}
    for path, text in files_text:
        for n in set(QUOTED.findall(text)):
            rd.setdefault(n, set()).add(path)
    return rd


def classify(name, rd, cmake_opts, exclude=None):
    if name in ALLOW:
        return "ALLOW", ALLOW[name]
    if name in cmake_opts:
        return "READ", "CMakeLists.txt option()"
    who = {p for p in rd.get(name, ()) if p != exclude}
    if who:
        return "READ", sorted(who)[0]
    pre = sorted(q for q in rd if q != name and name.startswith(q) and len(q) > len("ROGUESQ_"))
    if pre:
        return "PREFIX", pre[0]
    return "MISSING", "-"


def census(docs_text, cpp_text, owner_text, files_text, cmake_text, quiet=False):
    rd = readers(files_text)
    cmake_opts = set(re.findall(r"option\((ROGUESQ_[A-Z0-9_]+)", cmake_text))
    rows = []
    for n, where in sorted(doc_names(docs_text).items()):
        rows.append(("doc", n, where[0]) + classify(n, rd, cmake_opts))
    pn = preset_names(cpp_text)
    if pn is None:
        rows.append(("preset", "<presets() table not found>", SETTINGS_CPP, "MISSING", "-"))
        pn = []
    for n in pn:
        rows.append(("preset", n, SETTINGS_CPP) + classify(n, rd, cmake_opts, exclude=SETTINGS_CPP))
    for n in owner_file_names(owner_text or ""):
        rows.append(("owner-file", n, OWNER_FILE) + classify(n, rd, cmake_opts))
    bad = [r for r in rows if r[3] in ("MISSING", "PREFIX")]
    if not quiet:
        for r in rows:
            if r[3] != "READ":
                print(f"{r[3]:8s} {r[0]:10s} {r[1]:32s} {r[2]}  ({r[4]})")
        kinds = {}
        for r in rows:
            kinds.setdefault(r[0], [0, 0])[0] += 1
            kinds[r[0]][1] += r[3] in ("READ", "ALLOW")
        print("summary " + " ".join(f"{k}={v[1]}/{v[0]}" for k, v in sorted(kinds.items())) + f" bad={len(bad)}")
    return rows, bad


def load():
    rel = lambda p: os.path.relpath(p, ROOT)
    docs_text = [(d, open(os.path.join(ROOT, d), errors="replace").read()) for d in DOCS]
    cpp_text = open(os.path.join(ROOT, SETTINGS_CPP), errors="replace").read()
    of = os.path.join(ROOT, OWNER_FILE)
    owner_text = open(of, errors="replace").read() if os.path.exists(of) else ""
    files_text = [(rel(f), open(f, errors="replace").read()) for f in source_files()]
    cmake_text = open(os.path.join(ROOT, "CMakeLists.txt"), errors="replace").read()
    return docs_text, cpp_text, owner_text, files_text, cmake_text


def controls(base):
    docs_text, cpp_text, owner_text, files_text, cmake_text = base
    ok = True

    def status(rows, name, kind):
        return next((r[3] for r in rows if r[1] == name and r[0] == kind), None)

    # C1 planted doc name nobody reads
    d = docs_text + [("PLANT.md", "set `ROGUESQ_S7710_PLANTED_NOBODY=1`")]
    rows, _ = census(d, cpp_text, owner_text, files_text, cmake_text, quiet=True)
    c1 = status(rows, "ROGUESQ_S7710_PLANTED_NOBODY", "doc") == "MISSING"
    # C2 planted preset pair nobody reads (and the table's own quote must not be its witness)
    cpp2 = cpp_text.replace('{{"ROGUESQ_FPS60", "1"}, {"ROGUESQ_DRAW_DISTANCE", "2"}}',
                            '{{"ROGUESQ_FPS60", "1"}, {"ROGUESQ_DRAW_DISTANCE", "2"}, {"ROGUESQ_S7710_PLANTED_PRESET", "1"}}', 1)
    planted = cpp2 != cpp_text
    f2 = [(p, cpp2 if p == SETTINGS_CPP else t) for p, t in files_text]
    rows, _ = census(docs_text, cpp2, owner_text, f2, cmake_text, quiet=True)
    c2 = planted and status(rows, "ROGUESQ_S7710_PLANTED_PRESET", "preset") == "MISSING"
    # C3 drop every reader of a real documented name -> MISSING
    victim = "ROGUESQ_RUMBLE_SCALE"
    f3 = [(p, t.replace(f'"{victim}"', '"ROGUESQ_S7710_GONE"')) for p, t in files_text]
    rows, _ = census(docs_text, cpp_text, owner_text, f3, cmake_text, quiet=True)
    c3 = status(rows, victim, "doc") in ("MISSING", "PREFIX")
    # C4 the same real name is READ on the untouched tree, and so is every preset name
    rows, _ = census(docs_text, cpp_text, owner_text, files_text, cmake_text, quiet=True)
    c4 = status(rows, victim, "doc") == "READ" and all(r[3] == "READ" for r in rows if r[0] == "preset") \
        and sum(1 for r in rows if r[0] == "preset") >= 4
    # C5 owner-file parsing: a planted settings line nobody reads -> MISSING
    rows, _ = census(docs_text, cpp_text, "# c\nROGUESQ_FPS60=1\nROGUESQ_S7710_OWNER_PLANT=1\npreset=tv\n",
                     files_text, cmake_text, quiet=True)
    c5 = status(rows, "ROGUESQ_S7710_OWNER_PLANT", "owner-file") == "MISSING" \
        and status(rows, "ROGUESQ_FPS60", "owner-file") == "READ"
    for n, c in (("C1 planted doc", c1), ("C2 planted preset", c2), ("C3 dropped reader", c3),
                 ("C4 real names read", c4), ("C5 owner file", c5)):
        print(f"control {n}: {'PASS' if c else 'FAIL'}")
        ok &= c
    return ok


def main():
    base = load()
    if "--controls" in sys.argv[1:]:
        if not controls(base):
            print("CONTROL FAIL")
            return 2
        print("CONTROL PASS 5/5")
    _, bad = census(*base)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
