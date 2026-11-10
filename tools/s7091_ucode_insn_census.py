#!/usr/bin/env python3
"""s7091: retail-instruction census of the fixed RSP ucode vs a pristine RSPRecomp pass.

A "record" is one RSPRecomp instruction: its disassembly comment ("// mnem  ops") plus the C lines
RSPRecomp emitted for it, up to the next comment / label / blank. Lines carrying a "fixup:" tag are
dropped (they are owned by a named block). Labels/gotos are normalised (OVL24_135C -> L_135C) so a
spliced overlay copy matches its pristine overlay source.

Per compiled file: added = live - pristine, removed = pristine - live (multisets).
main ucode: added records must come from a pristine overlay file (fixup 6* splices); an added record
found in no overlay, or ANY removed record, is listed for attribution.
Controls (--controls): positive = duplicate one retail record in a copy of live main, and drop one;
both must be flagged. Exit 1 if unexplained records remain (after the allowlist in EXPLAINED).
Usage: s7091_ucode_insn_census.py <pristine_dir> <live_dir> [--controls]
"""
import collections, re, sys
from pathlib import Path

CMT = re.compile(r"^\s*// [a-z][a-z0-9.]*(?: {2,}\S.*)?$")
LBL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:\s*$")
NAME = re.compile(r"\b(?:[A-Z][A-Z0-9]*_)+([0-9A-F]{4})\b")
FILES = ["factor5_ucode_recompiled.c", "factor5_ucode_b_recompiled.c", "factor5_boot_recompiled.c",
         "factor5_ucode_ovl20_recompiled.c"]


def norm(s):
    return NAME.sub(r"L_\1", s.strip())


def records(text):
    return collections.Counter(seq(text))


PFX = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*?)_?([0-9A-F]{4})?:\s*$")
SRC = {"CLIP": "factor5_ucode_ovl4_recompiled.c"}


def runs(text):
    """Ordered (prefix, [records]) runs of the live main ucode; a run changes at a label whose prefix
    differs (L / RS64_UCODE_ENTRY / do_indirect_jump / rs64_clip_stray = resident)."""
    out, cur_pfx, buf = [], "L", []
    for line in text.split("\n"):
        m = PFX.match(line)
        if m and not CMT.match(line):
            pfx = m.group(1) if m.group(2) else "L"
            pfx = pfx if (pfx == "CLIP" or pfx.startswith("OVL")) else "L"
            if pfx != cur_pfx:
                tail = seq(buf)
                if tail:
                    out.append((cur_pfx, tail))
                cur_pfx, buf = pfx, []
        buf.append(line)
    if seq(buf):
        out.append((cur_pfx, seq(buf)))
    return out


def contains(hay, needle):
    n = len(needle)
    return any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def region_census(pristine, live_main, quiet=False):
    """Resident records vs pristine main (multiset); each spliced run must be a contiguous run of its
    source overlay's pristine record sequence."""
    src = {}
    bad = []
    resident = collections.Counter()
    for pfx, recs in runs(live_main):
        if pfx == "L":
            resident.update(recs)
            continue
        fn = SRC.get(pfx, f"factor5_ucode_ovl{pfx[3:].lower()}_recompiled.c")
        if fn not in src:
            src[fn] = seq((pristine / fn).read_text())
        if not contains(src[fn], recs):
            # find the first record that breaks the run, for attribution
            k = 1
            while k <= len(recs) and contains(src[fn], recs[:k]):
                k += 1
            bad.append((pfx, len(recs), k - 1, recs[k - 2:k] if k > 1 else recs[:1]))
    P = records((pristine / "factor5_ucode_recompiled.c").read_text())
    add, rem = resident - P, P - resident
    if not quiet:
        nr = sum(1 for p, _ in runs(live_main) if p != "L")
        print(f"region census: resident records {sum(resident.values())} vs pristine main {sum(P.values())}: "
              f"+{sum(add.values())} -{sum(rem.values())}; spliced runs {nr}, not a contiguous source run: {len(bad)}")
        for rec, k in add.items():
            print("  RESIDENT-ADDED x%d: %s" % (k, " | ".join(rec)[:220]))
        for rec, k in rem.items():
            print("  RESIDENT-REMOVED x%d: %s" % (k, " | ".join(rec)[:220]))
        for pfx, n, ok, ctx in bad:
            print(f"  SPLICE-BREAK {pfx}: run of {n} records matches source for first {ok}; at: "
                  + " || ".join(" | ".join(r) for r in ctx)[:300])
    return add, rem, bad


XFER = re.compile(r"^(goto \w+;|return RspExitReason::\w+;)$")


def classify(add, rem):
    """Pair each removed pristine record with an added live record of the same instruction. A pair is
    MODIFIED-RETAIL-KEPT when every retail C line survives in order and the only pristine line lost is a
    control transfer (an exit rewrite: fixup 1/1a). Anything else is UNEXPLAINED."""
    add, rem = collections.Counter(add), collections.Counter(rem)
    kept, unexplained = [], []
    for r in list(rem.elements()):
        cand = next((a for a in add if add[a] and a[:2] == r[:2]), None)
        body = [l for l in r[1:] if not XFER.match(l)]
        if cand is not None and all(l in cand for l in body) and \
                [l for l in cand if l in body] == body:
            kept.append((r, cand)); add[cand] -= 1
        else:
            unexplained.append(("REMOVED", r))
    unexplained += [("ADDED", a) for a in add.elements()]
    return kept, unexplained


def seq(text):
    if isinstance(text, list):
        text = "\n".join(text)
    out, cur = [], None
    for line in text.split("\n"):
        if "fixup:" in line or "fixup " in line and line.strip().startswith("/*"):
            continue
        if CMT.match(line):
            if cur:
                out.append(tuple(cur))
            cur = [norm(line)]
        elif cur is not None and (LBL.match(line) or not line.strip() or line.strip() == "}"):
            out.append(tuple(cur)); cur = None
        elif cur is not None:
            cur.append(norm(line))
    if cur:
        out.append(tuple(cur))
    return out


def census(pristine, live_texts, quiet=False):
    ovl = collections.Counter()
    for f in sorted(pristine.glob("factor5_ucode_ovl*_recompiled.c")):
        ovl |= records(f.read_text())          # union: a splice may copy a region once per overlay
    res = {}
    for name in FILES:
        P = records((pristine / name).read_text())
        L = records(live_texts[name])
        add, rem = L - P, P - L
        add_foreign = (add - collections.Counter({r: 64 * c for r, c in ovl.items()})) if name == "factor5_ucode_recompiled.c" else add
        res[name] = (sum(P.values()), sum(L.values()), add, rem, add_foreign)
        if not quiet:
            print(f"{name}: pristine {sum(P.values())} live {sum(L.values())} | +{sum(add.values())} "
                  f"(not from an overlay source: {sum(add_foreign.values())}) | -{sum(rem.values())}")
    return res


def show(res, n=40):
    for name, (_, _, add, rem, fa) in res.items():
        for tag, c in (("ADDED-FOREIGN", fa), ("REMOVED", rem)):
            for rec, k in list(c.items())[:n]:
                print(f"  {name} {tag} x{k}: " + " | ".join(rec)[:220])


if __name__ == "__main__":
    pristine, live = Path(sys.argv[1]), Path(sys.argv[2])
    texts = {n: (live / n).read_text() for n in FILES}
    res = census(pristine, texts)
    show(res)
    add, rem, bad = region_census(pristine, texts["factor5_ucode_recompiled.c"])
    kept, unexp = classify(add, rem)
    for name in FILES[1:]:
        _, _, a2, r2, _ = res[name]
        k2, u2 = classify(a2, r2)
        kept += k2; unexp += u2
    print(f"verdict: {len(kept)} modified-retail-kept, {len(unexp)} unexplained, {len(bad)} splice breaks")
    for tag, r in unexp:
        print(f"  UNEXPLAINED {tag}: " + " | ".join(r)[:220])
    rc = 1 if (unexp or bad) else 0
    if "--controls" in sys.argv:
        t = texts["factor5_ucode_recompiled.c"]
        lines = t.split("\n")
        i = next(k for k, l in enumerate(lines) if l.strip().startswith("// vmadn"))
        j = i + 1
        while not CMT.match(lines[j]) and lines[j].strip():
            j += 1
        dup = "\n".join(lines[:j] + lines[i:j] + lines[j:])
        k = next(k for k, l in enumerate(lines) if l.strip().startswith("// sqv"))
        m = k + 1
        while not CMT.match(lines[m]) and lines[m].strip():
            m += 1
        drop = "\n".join(lines[:k] + lines[m:])
        # splice-break control: drop one record inside the first spliced run
        o = next(k for k, l in enumerate(lines) if re.match(r"^(OVL[0-9A-F]+|CLIP)_[0-9A-F]{4}:", l))
        q = next(k for k in range(o + 3, len(lines)) if CMT.match(lines[k]))
        q2 = q + 1
        while not CMT.match(lines[q2]) and lines[q2].strip():
            q2 += 1
        sdrop = "\n".join(lines[:q] + lines[q2:])
        for label, txt in (("dup", dup), ("drop", drop), ("splice-drop", sdrop)):
            r = census(pristine, dict(texts, **{"factor5_ucode_recompiled.c": txt}), quiet=True)
            b = r["factor5_ucode_recompiled.c"]
            base = res["factor5_ucode_recompiled.c"]
            print(f"control {label}: +{sum(b[2].values())} (base {sum(base[2].values())}) "
                  f"-{sum(b[3].values())} (base {sum(base[3].values())})")
            a, rm, bd = region_census(pristine, txt, quiet=True)
            print(f"  region: resident +{sum(a.values())} -{sum(rm.values())} splice-breaks {len(bd)} "
                  f"unexplained {len(classify(a, rm)[1])}")
    sys.exit(rc)
