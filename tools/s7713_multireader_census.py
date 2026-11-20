#!/usr/bin/env python3
"""s7713 multi-reader clamp census: one ROGUESQ_X read at several sites where one site clamps / range-resets the parsed
number and another site compares the RAW number against a threshold the clamp makes unreachable (or reachable).

s7712's defect: apply_s6036 capped ROGUESQ_DRAW_DISTANCE at 4 (no DD_UNSAFE) while the dd bundle tested the raw value
(dd >= 6 off-map cull, dd >= 8 px8): dd6 drew at 4x but sized for 6. This closes the CLASS statically.

Model (per name, sites from tools/s7711_optval_census.py's finder):
  clamp site  a numeric parse whose result is clamped:  if (v < A) v = A;  if (v > B) v = B;  if (v > capX) v = capX with
              capX = (opt-in) ? X : Y  (Y, the no-companion default, is the cap);  if (v < A || v > B) v = D (range reset);
              std::min/max/clamp.
  raw site    a numeric parse (atoi/atof/strto*) whose result (or the parse call itself) is compared against literals
              (>, >=, <, <=, ==, !=; "8.0 - 1e-3" is evaluated) with no clamp; the result variable is followed to the end
              of its block (brace depth), at most 60 lines.
  sanitizer   rs64_s7358_sanitize_env (main.cpp) runs before every reader: each setenv(X, "L", 1) under a "v > B" /
              "v < A || v > B" condition is a clamp applied to the value EVERY reader sees.
SPLIT: some probe value V (each clamp bound +-1, x2, each threshold +-eps) reaches a clamp site as f(V) and a raw site as V
(both after the sanitizer), and some raw-site threshold T orders f(V) and V differently. MASKED = split only without the
sanitizer. REVIEWED = hand-classified harmless, with the reason.

Exit 0 = no unreviewed SPLIT; 1 = splits; 2 = control failure.
--controls: (1) drop the s7712 DRAW_DISTANCE cap line from the sanitizer -> DRAW_DISTANCE must SPLIT (s6036 cap 4 vs the
bundle's dd >= 6 / dd >= 8); (2) drop the s7713 OSMEM_MB range line -> OSMEM_MB must SPLIT (recomp 4..16 -> 8 vs the
bundle's atoi > 8); (3) recomp.cpp vs upstream_compat.cpp OSMEM readers alone (both 4..16 -> 8) must AGREE;
(4) a planted clamp-at-2 + raw "> 3" pair must SPLIT and a planted clamp-at-2 + raw "> 1" pair must AGREE.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7711_optval_census as c7711

ROOT = c7711.ROOT
MAIN = "src/main/main.cpp"
PARSE = r"(?:\(\w+\)\s*)?(?:std::)?(?:atoi|atol|atof|strtol|strtoul|strtod|strtof)\s*\(\s*(\w+)[^()]*\)"
NUM = r"-?[0-9]+(?:\.[0-9]*)?(?:[eE]-?[0-9]+)?f?"
EXPR = r"(" + NUM + r")(?:\s*([+-])\s*(" + NUM + r"))?(?![0-9.eE])"
CMP = r"(>=|<=|==|!=|>|<)"

REVIEWED = {  # name -> reason (hand-read, s7713)
}


def num(s):
    return float(s.rstrip("fF"))


def ev(m, a, b, cc):
    v = num(m.group(a))
    if m.group(b):
        v = v + num(m.group(cc)) if m.group(b) == "+" else v - num(m.group(cc))
    return v


def block(lines, i, maxn=60):
    """Lines i.. until the brace depth drops below the depth at the start of line i (or maxn lines)."""
    out, d = [], 0
    for l in lines[i:i + maxn]:
        out.append(l)
        for ch in l:
            d += ch == "{"
            d -= ch == "}"
            if d < 0:
                return "\n".join(out)
    return "\n".join(out)


def site_model(text_lines, lineno, name):
    """(kind, clamp, thresholds): kind clamp/raw/none; clamp = (lo, hi, reset) with reset=None for saturate."""
    body = block(text_lines, lineno - 1)
    first = text_lines[lineno - 1]
    g = re.search(r"(\w+)\s*=\s*(?:\(const char\s*\*\)\s*)?(?:std::)?getenv\(\s*\\?\"" + name + r"\\?\"", first)
    gv = g.group(1) if g else None
    if gv:  # stop where the same variable receives another getenv / value
        r = re.search(r"(?<![\w.>])" + gv + r"\s*=(?!=)", body[len(first):])
        if r:
            body = body[:len(first) + r.start()]
    # the parse result variable: X = ... atof(gv) ...  (or a direct parse of getenv(...))
    pv, direct = None, []
    if gv:
        # the value itself, not a latch: X = atof(gv)  /  X = (gv && *gv) ? atof(gv) : D  (casts allowed)
        pm = re.search(r"(\w+)\s*=\s*(?:[^;?=]*\?\s*)?(?:\(\w+\)\s*)?(?:std::)?(?:atoi|atol|atof|strtol|strtoul|strtod|strtof)\s*\(\s*" + gv + r"\b", body)
        if pm:
            pv = pm.group(1)
        direct = [m for m in re.finditer(PARSE + r"\s*" + CMP + r"\s*" + EXPR, body) if m.group(1) == gv]
    if not pv and not direct:
        return "none", None, []
    lo = hi = reset = None
    if pv:
        V = re.escape(pv)
        m = re.search(r"if\s*\(\s*" + V + r"\s*<\s*" + EXPR + r"\s*\|\|\s*" + V + r"\s*>\s*" + EXPR + r"\s*\)\s*" + V + r"\s*=\s*(" + NUM + r")", body)
        if m:
            lo, hi, reset = ev(m, 1, 2, 3), ev(m, 4, 5, 6), num(m.group(7))
        for m in re.finditer(r"if\s*\(\s*" + V + r"\s*<\s*" + EXPR + r"\s*\)\s*" + V + r"\s*=", body):
            lo = ev(m, 1, 2, 3)
        for m in re.finditer(r"if\s*\(\s*" + V + r"\s*>\s*(\w+(?:\.\w+)?)\s*\)\s*" + V + r"\s*=", body):
            t = m.group(1)
            if re.fullmatch(NUM, t):
                hi = num(t)
            else:  # a cap variable: capX = (cond) ? X : Y  -> Y
                cm = re.search(re.escape(t) + r"\s*=\s*\([^;]*\)\s*\?\s*(" + NUM + r")\s*:\s*(" + NUM + r")", body)
                if cm:
                    hi = num(cm.group(2))
        for m in re.finditer(r"std::(min|max)\s*\(\s*" + V + r"\s*,\s*(" + NUM + r")\s*\)|std::clamp\s*\(\s*" + V + r"\s*,\s*(" + NUM + r")\s*,\s*(" + NUM + r")\s*\)", body):
            if m.group(1) == "min": hi = num(m.group(2))
            elif m.group(1) == "max": lo = num(m.group(2))
            else: lo, hi = num(m.group(3)), num(m.group(4))
    th = []
    if pv:
        for m in re.finditer(r"(?<![\w.])" + re.escape(pv) + r"\s*" + CMP + r"\s*" + EXPR + r"(?!\s*\)\s*" + re.escape(pv) + r"\s*=)", body):
            th.append((m.group(1), ev(m, 2, 3, 4)))
    for m in direct:
        th.append((m.group(2), ev(m, 3, 4, 5)))
    if lo is not None or hi is not None:
        th = [t for t in th if t[1] not in (lo, hi)]  # the clamp's own compares are not thresholds
        return "clamp", (lo, hi, reset), th
    return "raw", None, th


def sanitizer_clamps(main_text):
    """name -> (lo, hi, reset) applied by rs64_s7358_sanitize_env to the value every reader sees."""
    a = main_text.find("static void rs64_s7358_sanitize_env() {")
    if a < 0:
        return {}
    body = block(main_text[a:].split("\n"), 0, 200)
    out = {}
    for m in re.finditer(r"setenv\(\"(ROGUESQ_\w+)\",\s*\"(" + NUM + r")\",\s*1\)", body):
        name, val = m.group(1), num(m.group(2))
        pre = body[:m.start()]
        cond = pre[pre.rfind("if (") if "if (" in pre else 0:]
        lo, hi, reset = out.get(name, (None, None, None))
        r = re.search(r"v\s*<\s*(" + NUM + r")\s*\|\|\s*v\s*>\s*(" + NUM + r")", cond)
        u = re.findall(r"v\s*>\s*(" + NUM + r")", cond)
        if r:
            lo, hi, reset = num(r.group(1)), num(r.group(2)), val
        elif u:
            hi = val if hi is None else min(hi, val)
        out[name] = (lo, hi, reset)
    return out


def apply_clamp(cl, v):
    if cl is None:
        return v
    lo, hi, reset = cl
    if reset is not None:
        return reset if (lo is not None and v < lo) or (hi is not None and v > hi) else v
    if lo is not None and v < lo: v = lo
    if hi is not None and v > hi: v = hi
    return v


def holds(op, a, b):
    return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b, "==": a == b, "!=": a != b}[op]


def judge(models, san):
    """models: [(site, kind, clamp, th)] -> list of (V, clamp site, raw site, op, T) witnesses."""
    clamps = [m for m in models if m[1] == "clamp"]
    raws = [m for m in models if m[1] == "raw" and m[3]]
    wit = []
    for cs in clamps:
        lo, hi, _ = cs[2]
        probes = set()
        for b in (lo, hi):
            if b is not None:
                probes |= {b - 1, b + 1, b * 2 + 1, b - 0.5, b + 0.5}
        for rs in raws:
            for _, t in rs[3]:
                probes |= {t - 0.5, t, t + 0.5}
        for V in sorted(probes):
            v = apply_clamp(san, V)
            fc = apply_clamp(cs[2], v)
            for rs in raws:
                for op, t in rs[3]:
                    if holds(op, fc, t) != holds(op, v, t):
                        wit.append((V, cs[0], rs[0], op, t))
    return wit


def load_models(files_override=None):
    pairs, site_map, cmake_opts, docs_text = c7711.load()
    texts = {}
    models = {}
    ml = open(os.path.join(ROOT, MAIN), errors="replace").read().split("\n")
    san_lo = next((i + 1 for i, l in enumerate(ml) if l.startswith("static void rs64_s7358_sanitize_env() {")), 0)
    san_hi, d = san_lo, 0
    for i in range(san_lo - 1, len(ml)) if san_lo else ():  # the function's own closing brace
        d += ml[i].count("{") - ml[i].count("}")
        if d <= 0:
            san_hi = i + 1
            break
    for name, sl in site_map.items():
        if len(sl) < 2:
            continue
        ms = []
        for site, _w in sl:
            rel, ln = site.rsplit(":", 1)
            if rel == MAIN and san_lo <= int(ln) <= san_hi:
                continue  # the sanitizer is modelled separately (sanitizer_clamps), not as a reader
            if rel not in texts:
                texts[rel] = (files_override or {}).get(rel) or open(os.path.join(ROOT, rel), errors="replace").read().split("\n")
            ms.append((site,) + site_model(texts[rel], int(ln), name))
        models[name] = ms
    return models, set(n for n, _ in pairs)


def census(models, owner, san, quiet=False):
    bad = []
    for name in sorted(models):
        ms = models[name]
        if not any(m[1] == "clamp" for m in ms) or not any(m[1] == "raw" and m[3] for m in ms):
            continue
        w = judge(ms, san.get(name))
        w0 = judge(ms, None)
        verdict = "SPLIT" if w else ("MASKED" if w0 else "AGREE")
        if verdict == "SPLIT" and name in REVIEWED:
            verdict = "REVIEWED"
        if not quiet:
            print(f"{verdict:8s} {name}{' (owner)' if name in owner else ''} sanitizer={san.get(name)}")
            for m in ms:
                if m[1] != "none":
                    print(f"         {m[1]:5s} {m[0]} clamp={m[2]} th={m[3]}")
            for x in (w or w0)[:3]:
                print(f"         witness V={x[0]:g}: {x[1]} clamps, {x[2]} raw '{x[3]} {x[4]:g}' disagrees")
            if verdict == "REVIEWED":
                print(f"         reviewed: {REVIEWED[name]}")
        if verdict == "SPLIT":
            bad.append(name)
    return bad


def main():
    main_text = open(os.path.join(ROOT, MAIN), errors="replace").read()
    models, owner = load_models()
    san = sanitizer_clamps(main_text)
    ok = True
    if "--controls" in sys.argv:
        dd_line = 'setenv("ROGUESQ_DRAW_DISTANCE", "4", 1);'
        os_line = 'setenv("ROGUESQ_OSMEM_MB", "8", 1);'
        for nm, line in (("ROGUESQ_DRAW_DISTANCE", dd_line), ("ROGUESQ_OSMEM_MB", os_line)):
            if line not in main_text:
                print(f"control drop-sanitizer {nm}: line missing FAIL"); ok = False; continue
            s2 = sanitizer_clamps(main_text.replace(line, ""))
            got = judge(models[nm], s2.get(nm))
            print(f"control drop-sanitizer {nm} want SPLIT got {'SPLIT' if got else 'AGREE'} {'PASS' if got else 'FAIL'}")
            ok &= bool(got)
        pair = [m for m in models["ROGUESQ_OSMEM_MB"] if m[0].startswith(("lib/N64ModernRuntime/librecomp/src/recomp.cpp",
                                                                          "src/main/upstream_compat.cpp"))]
        kinds = sorted(m[1] for m in pair)
        got = judge(pair, None)
        good = kinds == ["clamp", "clamp"] and not got
        print(f"control OSMEM recomp vs upstream_compat kinds={kinds} want AGREE got {'SPLIT' if got else 'AGREE'} {'PASS' if good else 'FAIL'}")
        ok &= good
        plant = ["double v = atof(e);", "if (v > 2.0) v = 2.0;", "double w = atof(f);", "if (w > 3.0) go();", "if (w > 1.0) go();"]
        a = site_model(['const char* e = getenv("ROGUESQ_PLANT"); double v = e ? atof(e) : 1.0; if (v > 2.0) v = 2.0;'], 1, "ROGUESQ_PLANT")
        b = site_model(['const char* f = getenv("ROGUESQ_PLANT"); double w = f ? atof(f) : 1.0; if (w > 3.0) go();'], 1, "ROGUESQ_PLANT")
        d = site_model(['const char* f = getenv("ROGUESQ_PLANT"); double w = f ? atof(f) : 1.0; if (w > 1.0) go();'], 1, "ROGUESQ_PLANT")
        g1 = judge([("P:1",) + a, ("P:2",) + b], None)
        g2 = judge([("P:1",) + a, ("P:3",) + d], None)
        print(f"control plant cap2 vs raw>3 kinds={a[0]},{b[0]} want SPLIT got {'SPLIT' if g1 else 'AGREE'} {'PASS' if g1 else 'FAIL'}")
        print(f"control plant cap2 vs raw>1 want AGREE got {'SPLIT' if g2 else 'AGREE'} {'PASS' if not g2 else 'FAIL'}")
        ok &= bool(g1) and not g2
        if not ok:
            return 2
    bad = census(models, owner, san)
    n = sum(1 for ms in models.values() if any(m[1] == "clamp" for m in ms) and any(m[1] == "raw" and m[3] for m in ms))
    print(f"s7713: {len(models)} names with >=2 reader sites, {n} with a clamp site + a raw-threshold site, {len(bad)} unreviewed SPLIT")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
