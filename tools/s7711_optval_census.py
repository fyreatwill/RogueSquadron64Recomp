#!/usr/bin/env python3
"""s7711 owner-setting VALUE census: every documented `ROGUESQ_X=V` must reach a parser that can read V.

s7710 proved every documented NAME is read. This checks the VALUE side, statically, per reader site:
  pairs : every `ROGUESQ_X=V` token in docs/OWNER-OPT-INS.md + README.md, and every preset pair in rs64_settings.cpp.
  sites : every `getenv("ROGUESQ_X")` in src/, lib/rt64/src, lib/N64ModernRuntime and tools/fixup_*/apply_* (they inject
          C), with a window = that line + the next 3 lines, cut at the next getenv( of another name.
Per (pair, site) the window's parse idioms decide:
  SYNTAX   V has a fraction (1.6, 0.4) and the site parses with an integer parser only (atoi/strtol/...): V is truncated.
  SYNTAX   V is not numeric (16:9, auto, mouse) and the site has only numeric parsers, no string/char compare.
  PRESENCE V is 0/OFF-style and the site only tests the pointer (no deref, no parser): "=0" may switch it ON.
           PRESENCE rows are hand-reviewed (a "user has not set it" guard before an auto-default is legitimate) and
           the reviewed ones go into REVIEWED with the reason.
  OK       otherwise.
Sites that only print / setenv / pass the name through (no getenv of it) are not sites.
CMake option() names (ROGUESQ_SRC_OPT) are build flags, not env, and are skipped.

Exit 0 = no unreviewed SYNTAX/PRESENCE row; 1 = defects; 2 = control failure.
--controls: plant an atoi site for a fractional doc value (must be SYNTAX), a presence-only site for a doc =0 (must be
PRESENCE), an atof site for a fractional value (must be OK), a numeric-only site for a ':' value (must be SYNTAX), and drop
a REVIEWED entry (its row must flip back to PRESENCE), before the real run.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = ["docs/OWNER-OPT-INS.md", "README.md"]
SETTINGS_CPP = "src/main/rs64_settings.cpp"
ROOTS = ["src", "lib/rt64/src", "lib/N64ModernRuntime"]
EXTS = (".c", ".cpp", ".h", ".hpp", ".mm", ".m")
PAIR = re.compile(r"(ROGUESQ_[A-Z0-9_]*[A-Z0-9])=([^\s`|);\"'\]]+)")  # commas kept: lists like 95,80
INTP = re.compile(r"\b(atoi|atol|atoll|strtol|strtoul|strtoll|strtoull|rs64_env_int|stoi|stol)\s*\(")
FLTP = re.compile(r"\b(atof|strtof|strtod|stof|stod|sscanf)\s*\(")
STRP = re.compile(r"\b(sscanf|strcmp|strncmp|strcasecmp|strncasecmp|strstr|strchr|std::string|rs64_stick_gate_parse|env_is)\b|==\s*'|!=\s*'|\[0\]|\*\s*[a-z_][a-z0-9_]*\s*(==|!=)|==\s*\"")
DEREF = re.compile(r"\[0\]|\*\s*[a-z_][a-z0-9_]*\b|\[[0-9]\]")
NUM = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")
ZEROISH = {"0", "OFF", "off", "false"}

# A value that only takes effect with a companion setting: (name, predicate, companion) -> the doc line must carry it.
# apply_s6036_dd.py caps the terrain multiplier at 4.0 unless ROGUESQ_DD_UNSAFE is on (cap 8.0, s7426 value test).
COUPLED = [("ROGUESQ_DRAW_DISTANCE", lambda v: NUM.match(v) and float(v) > 4.0, "ROGUESQ_DD_UNSAFE=1",
            "above the 4.0 cap without DD_UNSAFE=1 (apply_s6036_dd.py)")]

# (name, value, file) -> reason. Each entry was read by hand at s7711.
REVIEWED = {}


def coupled_rows(texts):
    rows = []
    for path, text in texts:
        for i, line in enumerate(text.split("\n"), 1):
            for n, v in PAIR.findall(line):
                for cn, pred, comp, why in COUPLED:
                    if n == cn and pred(v.rstrip(".:,")) and comp not in line:
                        rows.append((n, v, f"{path}:{i}", "-", "CAPPED", why))
    return rows


def doc_pairs(texts):
    out = {}
    for path, text in texts:
        for i, line in enumerate(text.split("\n"), 1):
            for n, v in PAIR.findall(line):
                v = v.rstrip(".:,")
                if n == "ROGUESQ_NAME" or not v or v.startswith("<"):
                    continue  # placeholder syntax (ROGUESQ_NAME=value, =<s>)
                for vv in (v.split("..") if ".." in v else [v]):  # a range a..b documents both ends
                    out.setdefault((n, vv), f"{path}:{i}")
    return out


def preset_pairs(cpp_text):
    m = re.search(r"presets\(\)\s*\{(.*?)\n\}", cpp_text, re.S)
    return {(n, v): SETTINGS_CPP for n, v in re.findall(r'\{"(ROGUESQ_[A-Z0-9_]+)",\s*"([^"]*)"\}', m.group(1))} if m else {}


def source_files():
    files = []
    for r in ROOTS:
        for dp, dn, fn in os.walk(os.path.join(ROOT, r)):
            dn.sort()
            files += [os.path.join(dp, f) for f in sorted(fn) if f.endswith(EXTS)]
    tools = os.path.join(ROOT, "tools")
    files += [os.path.join(tools, f) for f in sorted(os.listdir(tools))
              if (f.startswith("fixup_") or f.startswith("apply_")) and f.endswith(".py")]
    return files


HELPERS = {  # helper(name, ...) readers and the parse they apply (read by hand, s7711)
    "rs64_env_int": "atoi(e)",                       # main.cpp: (e && *e) ? atoi(e) : d
    "s6919_mode": "e[0] == 't' ? 2 : e[0] != '0'",   # upstream_compat.cpp
    "rs64_bind_flag": "*e != '0'",                   # main.cpp
    "env_on": "*e != '0'",                           # s7644_rspdma.cpp
    "env_flag": "*e == '0' strcmp(e, \"false\")",     # debug_logs.h
    "rs64_s7355_env_is": "strcmp(e, v)",             # main.cpp
}
CALL = re.compile(r'\b(getenv|' + "|".join(HELPERS) + r')\(\s*\\?"(ROGUESQ_[A-Z0-9_]+)\\?"')
PRINT = re.compile(r"\b(f?printf|snprintf|fputs|puts)\s*\(")


def segment(line, pos):
    """The statement around pos: from the last ';' '{' '}' before it to the next ';' after it."""
    a = max(line.rfind(c, 0, pos) for c in ";{}") + 1
    b = line.find(";", pos)
    return line[a:] if b < 0 else line[a:b + 1]


def sites(files_text):
    """name -> list of (file:line, window text). Print-only arguments are not sites."""
    out = {}
    for path, text in files_text:
        if "ROGUESQ_" not in text:
            continue
        lines = text.split("\n")
        rel = os.path.relpath(path, ROOT)
        for i, l in enumerate(lines):
            for m in CALL.finditer(l):
                fn, name = m.group(1), m.group(2)
                seg = segment(l, m.start())
                pre = l[:m.start()]
                if PRINT.search(pre[max(pre.rfind(c) for c in ";{}") + 1:]):
                    continue  # an argument of a printf
                if fn != "getenv":
                    out.setdefault(name, []).append((f"{rel}:{i + 1}", HELPERS[fn]))
                    continue
                w = re.search(r"(\w+)\s*\(\s*(\(const char\s*\*\)\s*)?(std::)?$", pre)
                win = (w.group(1) + "(" if w else pre[-2:]) + m.group(0) + ")"  # only the call that wraps the getenv
                v = re.search(r"(\w+)\s*=\s*(\(const char\s*\*\)\s*)?(std::)?$", pre)
                if v:  # follow the receiving variable through the rest of the line and the next 3 lines
                    var = v.group(1)
                    rest = l[m.end():] + "\n" + "\n".join(lines[i + 1:i + 4])
                    stop = re.search(r"\b" + var + r"\s*=\s*(std::)?getenv", rest)
                    if stop:
                        rest = rest[:stop.start()]
                    win = l[m.end():].split(";")[0] + "\n" + "\n".join(st for st in (PRINT.split(x, 1)[0] for x in re.split(r"[;\n]", rest))
                                                if re.search(r"\b" + var + r"\b", st))  # printf args cut off
                out.setdefault(name, []).append((f"{rel}:{i + 1}", win))
    return out


def judge(value, win):
    ip, fp, sp = bool(INTP.search(win)), bool(FLTP.search(win)), bool(STRP.search(win))
    if NUM.match(value):
        if "." in value and ip and not fp:
            return "SYNTAX", "fractional value, integer-only parser"
        if value in ZEROISH and not (ip or fp or sp or DEREF.search(win)):
            return "PRESENCE", "pointer test only"
        return "OK", ""
    if (ip or fp) and not sp:
        return "SYNTAX", "non-numeric value, numeric-only parser"
    if value in ZEROISH and not (ip or fp or sp or DEREF.search(win)):
        return "PRESENCE", "pointer test only"
    return "OK", ""


def census(pairs, site_map, cmake_opts, reviewed, quiet=False, docs_text=()):
    rows = coupled_rows(docs_text)
    for (n, v), where in sorted(pairs.items()):
        if n in cmake_opts:
            rows.append((n, v, where, "-", "CMAKE", "build option"))
            continue
        ss = site_map.get(n, [])
        if not ss:
            rows.append((n, v, where, "-", "NOSITE", "no getenv site (s7710 covers names)"))
            continue
        for loc, win in ss:
            k, why = judge(v, win)
            f = loc.rsplit(":", 1)[0]
            if k != "OK" and (n, v, f) in reviewed:
                k, why = "REVIEWED", reviewed[(n, v, f)]
            rows.append((n, v, where, loc, k, why))
    bad = [r for r in rows if r[4] in ("SYNTAX", "PRESENCE", "CAPPED")]
    if not quiet:
        for r in rows:
            if r[4] not in ("OK",):
                print(f"{r[4]:8s} {r[0]}={r[1]:10s} {r[3]}  ({r[5]})")
        pairs_ok = {(r[0], r[1]) for r in rows} - {(r[0], r[1]) for r in bad}
        print(f"summary pairs={len(pairs)} sites={sum(1 for r in rows if r[3] != '-')} "
              f"pairs_clean={len(pairs_ok)}/{len(pairs)} bad={len(bad)}")
    return rows, bad


def load():
    docs_text = [(d, open(os.path.join(ROOT, d), errors="replace").read()) for d in DOCS]
    cpp = open(os.path.join(ROOT, SETTINGS_CPP), errors="replace").read()
    pairs = doc_pairs(docs_text)
    for k, w in preset_pairs(cpp).items():
        pairs.setdefault(k, w)
    files_text = [(f, open(f, errors="replace").read()) for f in source_files()]
    cmake = open(os.path.join(ROOT, "CMakeLists.txt"), errors="replace").read()
    return pairs, sites(files_text), set(re.findall(r"option\((ROGUESQ_[A-Z0-9_]+)", cmake)), docs_text


def controls(pairs, site_map, cmake_opts, docs_text):
    def kinds(p, s, rv):
        rows, _ = census(p, s, cmake_opts, rv, quiet=True)
        return {(r[0], r[1]): r[4] for r in rows}
    ok = True
    plant_p = dict(pairs)
    plant_p.update({("ROGUESQ_PLANT_F", "0.5"): "x", ("ROGUESQ_PLANT_P", "0"): "x",
                    ("ROGUESQ_PLANT_G", "1.6"): "x", ("ROGUESQ_PLANT_A", "16:9"): "x"})
    plant_s = dict(site_map)
    plant_s.update({
        "ROGUESQ_PLANT_F": [("P.c:1", 'getenv("ROGUESQ_PLANT_F"); int v = e ? atoi(e) : 1;')],
        "ROGUESQ_PLANT_P": [("P.c:2", 'getenv("ROGUESQ_PLANT_P")) on = 1;')],
        "ROGUESQ_PLANT_G": [("P.c:3", 'getenv("ROGUESQ_PLANT_G"); float k = e ? (float)atof(e) : 1.f;')],
        "ROGUESQ_PLANT_A": [("P.c:4", 'getenv("ROGUESQ_PLANT_A"); int a = e ? atoi(e) : 0;')]})
    k = kinds(plant_p, plant_s, REVIEWED)
    for name, v, want in (("ROGUESQ_PLANT_F", "0.5", "SYNTAX"), ("ROGUESQ_PLANT_P", "0", "PRESENCE"),
                          ("ROGUESQ_PLANT_G", "1.6", "OK"), ("ROGUESQ_PLANT_A", "16:9", "SYNTAX")):
        got = k.get((name, v))
        print(f"control {name}={v} want {want} got {got} {'PASS' if got == want else 'FAIL'}")
        ok &= got == want
    rows, _ = census(pairs, site_map, cmake_opts, REVIEWED, quiet=True,
                     docs_text=list(docs_text) + [("PLANT.md", "`ROGUESQ_DRAW_DISTANCE=6 ROGUESQ_FPS60=1`")])
    got = [r[4] for r in rows if r[2] == "PLANT.md:1"]
    print(f"control dd6 without DD_UNSAFE want CAPPED got {got} {'PASS' if got == ['CAPPED'] else 'FAIL'}")
    ok &= got == ["CAPPED"]
    if REVIEWED:
        key = next(iter(REVIEWED))
        rv = dict(REVIEWED); del rv[key]
        rows, _ = census(pairs, site_map, cmake_opts, rv, quiet=True)
        got = {r[4] for r in rows if (r[0], r[1], r[3].rsplit(":", 1)[0]) == key}
        print(f"control drop-REVIEWED {key[0]}={key[1]} want PRESENCE/SYNTAX got {sorted(got)} "
              f"{'PASS' if got & {'PRESENCE', 'SYNTAX'} else 'FAIL'}")
        ok &= bool(got & {"PRESENCE", "SYNTAX"})
    return ok


def main():
    pairs, site_map, cmake_opts, docs_text = load()
    if "--controls" in sys.argv and not controls(pairs, site_map, cmake_opts, docs_text):
        return 2
    _, bad = census(pairs, site_map, cmake_opts, REVIEWED, docs_text=docs_text)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
