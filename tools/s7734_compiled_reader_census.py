#!/usr/bin/env python3
"""s7734: compiled-tree reader census. s7714/s7733 model the SCRIPT text of every ROGUESQ_* reader; the compiled tree
(../N64Recomp/RecompiledFuncs/*.c, build/factor5_ucode/*.c) is what runs. For every getenv("ROGUESQ_*") line there,
model its on/off signature and compare it with the signatures of the live script/host sites of the same name.
  COVERED : the compiled signature equals some live modelled site's signature
  HIDDEN  : it models, but no live site of that name models to it (a later rewrite changed the reading)
  ORPHAN  : no live script/host site of that name models at all
  UNMOD   : the compiled line does not model (passed on / parse)
--controls: planted funcs_24 S4562 line with its s4786 default stripped must model differently (unset 1 -> 0).
rc 0 = controls PASS and every HIDDEN name is in REVIEWED; 1 otherwise. Skips (rc 0) when ../N64Recomp is absent.
--tree DIR (s7735): census a regen-replay RecompiledFuncs tree instead of the live one (tools/s7719_regen_gate.py runs it on
its fresh replay, so a fixup that stops reproducing a hand-synced compiled reading reads HIDDEN at the next sweep)."""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7714_truth_census as t

ROOT = t.ROOT
GLOBS = ("../N64Recomp/RecompiledFuncs/*.c", "build/factor5_ucode/*.c")
PAT = re.compile(r'getenv\("(ROGUESQ_[A-Z0-9_]+)"\)')
REVIEWED = {}  # name -> why a HIDDEN compiled reading is deliberate (filled from this pass's reads)
# s7734: NOREF (no live script/host site models) rows read by hand: numbers / -1 sentinels / diagnostic unset-off guards
NOREF_OK = {"ROGUESQ_S7103_CAMFIX", "ROGUESQ_LOG_M5_PRECLEAR_SPAN", "ROGUESQ_FORCE_CINE_A0", "ROGUESQ_FORCE_ALLOC_TAIL_GUARD3",
            "ROGUESQ_FORCE_ALLOC_TAIL_GUARD4", "ROGUESQ_LOG_EMIT_DL_GUARD4", "ROGUESQ_LOG_HEAPLISTDEQ_GUARD4", "ROGUESQ_FORCE_UNLOCK",
            "ROGUESQ_FORCE_PLANET_UNLOCK", "ROGUESQ_LOG_SCENE_NODE_LIST_GUARD4", "ROGUESQ_SPANFORCE", "ROGUESQ_SPANFORCE_PERIOD",
            "ROGUESQ_DD_FARCLIP_MUL", "ROGUESQ_DD_POOLX",
            # s7898: det-pair diagnostic list (c / fire numbers), unset = 0 = off; became modelable when the list parse landed
            "ROGUESQ_SNAP3_ONLY"}


if "--tree" in sys.argv:
    GLOBS = (os.path.join(os.path.abspath(sys.argv[sys.argv.index("--tree") + 1]), "*.c"),) + GLOBS[1:]


def compiled_sites():
    out = []
    for g in GLOBS:
        for f in sorted(glob.glob(os.path.join(ROOT, g))):
            lines = open(f, errors="replace").read().split("\n")
            for i, ln in enumerate(lines):
                for m in PAT.finditer(ln):
                    out.append((os.path.relpath(f, ROOT), i + 1, m.group(1), lines))
    return out


def script_sigs():
    """name -> set of live modelled signatures, over ALL live sites (single-reader names too)."""
    corpus = t.gen_corpus()
    _p, site_map, _c, _d = t.c7711.load()
    texts, pyc, sigs = {}, {}, {}
    for name, sl in site_map.items():
        for site, _w in sl:
            rel, ln = site.rsplit(":", 1)
            if rel not in texts:
                texts[rel] = open(os.path.join(ROOT, rel), errors="replace").read().split("\n")
            if rel.endswith(".py") and corpus is not None:
                if rel not in pyc:
                    pyc[rel] = t.py_c_text(texts[rel])
                cl = pyc[rel][int(ln) - 1] if 0 < int(ln) <= len(pyc[rel]) else ""
                if not t.py_text_live(cl, corpus):
                    continue
            sig, node = t.model_site(texts[rel], int(ln), name, rel.endswith(".py"))
            s = sigs.setdefault(name, set())
            if sig:
                s.add(sig)
    return sigs


def flip(sig):
    return tuple({0: 1, 1: 0}.get(a, a) for a in sig)


def classify(sig, have):
    if not sig:
        return "UNMOD"
    if not have:
        return "NOREF"
    return "COVERED" if (sig in have or flip(sig) in have) else "HIDDEN"


def controls(sigs):
    # planted positive: the pre-s7734 presence-only DD_CAPX_TOG line must classify HIDDEN against the live readers
    pl = ['  int cx = getenv("ROGUESQ_DD_CAPX_TOG") != 0; if (cx) n++;']
    psig, _ = t.model_site(pl, 1, "ROGUESQ_DD_CAPX_TOG", False)
    pk = classify(psig, sigs.get("ROGUESQ_DD_CAPX_TOG", set()))
    print(f"control planted presence DD_CAPX_TOG -> {pk} {'PASS' if pk == 'HIDDEN' else 'FAIL'}")
    if pk != "HIDDEN":
        return False
    f = os.path.join(os.path.dirname(os.path.join(ROOT, GLOBS[0])), "funcs_24.c")
    lines = open(f, errors="replace").read().split("\n")
    idx = next((i for i, l in enumerate(lines) if 's_hold = (e && (e[0] == 50' in l and "ROGUESQ_S4562_PAUSE" in l), None)
    if idx is None:
        print("control S4562 line not found FAIL"); return False
    real, _ = t.model_site(lines, idx + 1, "ROGUESQ_S4562_PAUSE", False)
    planted = list(lines)
    planted[idx] = planted[idx].replace('if (!e) e = "4"; /* s4786 default */', "")
    strip, _ = t.model_site(planted, idx + 1, "ROGUESQ_S4562_PAUSE", False)
    ok = bool(real) and bool(strip) and real[0] == 1 and strip[0] == 0
    print(f"control S4562 real unset={real and real[0]} stripped unset={strip and strip[0]} {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    if not glob.glob(os.path.join(ROOT, GLOBS[0])):
        print("skip: ../N64Recomp/RecompiledFuncs absent"); return 0
    sigs = script_sigs()
    ok = controls(sigs)
    rows, seen = [], set()
    for rel, ln, name, lines in compiled_sites():
        sig, node = t.model_site(lines, ln, name, False)
        k = classify(sig, sigs.get(name, set()))
        key = (name, sig, k)
        if key in seen:
            continue
        seen.add(key)
        rows.append((k, name, f"{rel}:{ln}", sig, sorted(sigs.get(name, set()), key=str)))
    cnt = {}
    for r in rows:
        cnt[r[0]] = cnt.get(r[0], 0) + 1
    print("distinct (name,signature) compiled readings:", len(rows), " ", " ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
    verbose = "-v" in sys.argv
    bad = 0
    for k, name, site, sig, have in rows:
        if k == "HIDDEN":
            rv = REVIEWED.get(name)
            if not rv:
                bad += 1
            print(f"HIDDEN {name} {site} compiled={sig} live={have} {'reviewed: ' + rv if rv else 'UNREVIEWED'}")
        elif k == "NOREF" and name not in NOREF_OK:
            bad += 1
            print(f"NOREF {name} {site} compiled={sig} UNREVIEWED")
        elif verbose and k != "COVERED":
            print(f"{k} {name} {site} compiled={sig}")
    print(f"unreviewed HIDDEN/NOREF={bad} controls={'PASS' if ok else 'FAIL'}")
    return 0 if ok and bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
