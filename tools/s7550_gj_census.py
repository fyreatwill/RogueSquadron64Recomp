#!/usr/bin/env python3
"""s7550 class GJ census: RDRAM addresses RT64 (lib/rt64/src) keeps ACROSS frames, and whether any host write into guest RAM
goes through one.

The guest frees and reuses heap blocks (s7545).  RT64 keeps a framebuffer registry (FramebufferManager::framebuffers, keyed by
RDRAM address, with a retained maxHeight / RAMBytes / RAMHash per entry), a present-side screen fb lookup, and fb storage.  If a
default-on RDRAM write used an address (or a row range) taken from that registry rather than from the current command stream, a
reused block could receive stale native framebuffer data.  Classes GB/GC (s7538-s7542) audited WHEN RT64 writes; GJ audits
WHERE the address and extent come from.

Part A (writes): every RDRAM write site in lib/rt64/src (s7542 GC idiom engine, contrib/ and imgui/ excluded) must match a
WRITE rule.  A rule's proofs are regexes that must hold in the named function (or file); a failed proof turns the row OPEN.
  H-percmd     address = the current workload pair's SETCIMG/SETZIMG (fbPair.colorImage/.depthImage), width = colorImg.width,
               rows = the pair's drawColorRect/drawDepthRect; the retained fb.height only enters as a min() clamp (can only shrink)
  H-gated-diag write exists only under a default-off diagnostic env (named)
  H-def        the primitive (copyNativeToRAM definition: the caller supplies dst)
  H-read       a non-const alias that is never written through (negative proof)
Part B (retained-address uses): every line indexing RDRAM by a registry key / registry entry / storage or screen address
(it->first, it->second.*, fb->addressStart, screenFb->addressStart, colorFb/depthFb->addressStart, storageAddress,
screenFbAddress) must match a USE rule:
  H-hash-read  registry walk through a `const uint8_t *RDRAM` parameter (compiler-enforced read-only): storeRAM, checkRAM,
               uploadRAM (hash revalidation -> RAM->native upload), hashTracking
  H-percmd-read / H-percmd  read (or the Part A write) whose address is the current pair's image or the current VI origin
  H-read-diag  read under a default-off diagnostic env
OPEN: a write through a retained address, or a retained row extent not clamped by the current command.  UNCLASSIFIED: no rule.
DRIFT: a rule that matches no site (source moved; re-derive the rule).  Exit 0 iff 0 OPEN, 0 UNCLASSIFIED, 0 DRIFT.

  python3 tools/s7550_gj_census.py              # rows + summary
  python3 tools/s7550_gj_census.py --controls   # (1) planted registry-walk write -> UNCLASSIFIED, (2) deleted rule ->
      UNCLASSIFIED, (3) cRowEnd = retained colorFb->height (no min with the current rect) -> OPEN, (4) renamed function ->
      DRIFT, (5) const dropped from checkRAM's RDRAM param -> OPEN, (6) depth address taken from the registry -> OPEN,
      (7) store through the gbi scan cursor -> OPEN, (8) the real tree -> rc 0
"""
import os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7542_gc_census as gc
import s7538_gb_census as gb
import s7533_fz_census as fz

REPO = gb.REPO
T = "lib/rt64/src/"
ST, FM, FB = T + "hle/rt64_state.cpp", T + "hle/rt64_framebuffer_manager.cpp", T + "hle/rt64_framebuffer.cpp"

# proofs: (path, fn or None = whole file, regex, must_hold=True)
P_COLOR = [
    (ST, "fullSync", r'FramebufferPair &fbPair = workload\.fbPairs\[f\];'),
    (ST, "fullSync", r'const auto &colorImg = fbPair\.colorImage;'),
    (ST, "fullSync", r'colorFb = &framebufferManager\.get\(colorImg\.address, colorImg\.siz, colorImg\.width, colorHeight\);'),
    (ST, "fullSync", r'colorWriteWidth = \(colorHeight > 1\) \? colorImg\.width'),
    (ST, "fullSync", r'colorRowStart = fbPair\.drawColorRect\.top\(false\);'),
    (ST, "fullSync", r'colorRowEnd = fbPair\.drawColorRect\.bottom\(true\);'),
    (ST, "fullSync", r'if \(getFramebufferPairs\(pairCursor\)\)'),
    (ST, "fullSync", r'uint32_t cRowEnd = std::min\(colorRowEnd, colorFb->height\);'),
    (FM, "get", r'fb\.addressStart = address;'),          # registry entry address == the requested (current) address
    (FM, "get", r'auto &fb = framebuffers\[address\];'),
]
P_DEPTH = [
    (ST, "fullSync", r'FramebufferPair &fbPair = workload\.fbPairs\[f\];'),
    (ST, "fullSync", r'const auto &depthImg = fbPair\.depthImage;'),
    (ST, "fullSync", r'depthFb = &framebufferManager\.get\(depthImg\.address, G_IM_SIZ_16b, colorImg\.width, colorHeight\);'),
    (ST, "fullSync", r'depthWriteWidth = \(fbPair\.drawDepthRect\.bottom\(true\) > 1\) \? colorImg\.width'),
    (ST, "fullSync", r'depthRowStart = fbPair\.drawDepthRect\.top\(false\);'),
    (ST, "fullSync", r'depthRowEnd = fbPair\.drawDepthRect\.bottom\(true\);'),
    (ST, "fullSync", r'if \(getFramebufferPairs\(pairCursor\)\)'),
    (ST, "fullSync", r'const uint32_t dRowEnd = std::min\(depthRowEnd, depthFb->height\);'),
    (FM, "get", r'fb\.addressStart = address;'),
]
# Part A write rules: (path, fn, kind, text regex, class, why, proofs)
WRITE = [
    (T + "gbi/rt64_gbi.cpp", "getGBIForUCode", "ptr", r'rdramCursor = &RDRAM\[textAddress\]', "H-read",
     "ucode text/data scan cursor; never stored through",
     [(T + "gbi/rt64_gbi.cpp", "getGBIForUCode", r'(?<!uint8_t )\*\s*\(?\s*rdramCursor\b[^;=]*=(?!=)|rdramCursor\s*\[[^]]*\]\s*=(?!=)', False)]),
    (FB, "<file>", "fbwb", r'copyNativeToRAM\(uint8_t \*dst', "H-def", "definition; dst supplied by each fullSync call site", []),
    (T + "hle/rt64_framebuffer.h", "<file>", "fbwb", r'copyNativeToRAM\(uint8_t \*dst', "H-def", "declaration", []),
    (ST, "fullSync", "memfn", r'memset\(&RDRAM\[storageAddress\]', "H-gated-diag", "ROGUESQ_RI_CLEAR (s6249), default off",
     [(ST, "fullSync", r'getenv\("ROGUESQ_RI_CLEAR"\)')]),
    (ST, "fullSync", "memfn", r'memset\(&RDRAM\[colorFb->addressStart\]', "H-gated-diag", "ROGUESQ_WB_CLEAR (s6246), default off",
     [(ST, "fullSync", r'getenv\("ROGUESQ_WB_CLEAR"\) != nullptr')]),
    (ST, "fullSync", "cast", r'reinterpret_cast<uint32_t \*>\(&RDRAM\[a\]\) = 0xF83FF83Fu', "H-gated-diag",
     "s7707: ROGUESQ_S7704_POISON=<width> magenta fill (s7704), default off; span < 16 MB",
     [(ST, "fullSync", r'getenv\("ROGUESQ_S7704_POISON"\)')]),
    (ST, "fullSync", "fbwb", r'copyNativeToRAM\(&RDRAM\[colorFb->addressStart\]', "H-percmd",
     "colour writeback: current pair SETCIMG address/width, rows = drawColorRect clamped by min(., fb.height)", P_COLOR),
    (ST, "fullSync", "fbwb", r'copyNativeToRAM\(&RDRAM\[depthFb->addressStart\]', "H-percmd",
     "depth writeback: current pair SETZIMG address, colorImg.width, rows = drawDepthRect clamped by min(., fb.height)", P_DEPTH),
]
KEY = r'RDRAM\[\s*\(?\s*(?:it->first|it->second\.\w+|fb->addressStart|screenFb->addressStart|colorFb->addressStart|' \
      r'depthFb->addressStart|storageAddress|screenFbAddress)\b'
# Part B use rules: (path, fn, line regex, class, why, proofs)
USE = [
    (FM, "storeRAM", r'const uint8_t \*fbRAM = &RDRAM\[it->first\]', "H-hash-read", "registry walk, const RDRAM",
     [(FM, None, r'void FramebufferManager::storeRAM\(FramebufferStorage &fbStorage, const uint8_t \*RDRAM')]),
    (FM, "checkRAM", r'const uint8_t \*fbRAM = &RDRAM\[it->first\]', "H-hash-read", "XXH3 revalidation, const RDRAM",
     [(FM, None, r'void FramebufferManager::checkRAM\(const uint8_t \*RDRAM')]),
    (FM, "uploadRAM", r'const uint8_t \*fbRAM = &RDRAM\[fb->addressStart\]', "H-hash-read",
     "changed-hash fbs: RAM -> native upload (host GPU side only), const RDRAM",
     [(FM, None, r'void FramebufferManager::uploadRAM\([^)]*const uint8_t \*RDRAM')]),
    (FM, "hashTracking", r'XXH3_64bits\(&RDRAM\[it->first\]', "H-hash-read", "post-writeback rehash, const RDRAM",
     [(FM, None, r'void FramebufferManager::hashTracking\(const uint8_t \*RDRAM\)')]),
    (ST, "fullSync", r'memset\(&RDRAM\[storageAddress\]', "H-gated-diag", "= Part A RI_CLEAR row", []),
    (ST, "fullSync", r'fbStorage\.store\(pairCursor, storageAddress, &RDRAM\[storageAddress\]', "H-percmd-read",
     "read-in copy into host fb storage; storageAddress = current colorImg/depthImg.address + rows",
     [(ST, "fullSync", r'uint32_t storageAddress = colorImg\.address \+ readRowBytes \* colorFb->readHeight;'),
      (ST, "fullSync", r'uint32_t storageAddress = depthImg\.address \+ readRowBytes \* depthFb->readHeight;')]),
    (ST, "fullSync", r'rs64FloorRdramLog\("b", &RDRAM\[storageAddress\]', "H-read-diag", "floor log read", []),
    (ST, "fullSync", r'memset\(&RDRAM\[colorFb->addressStart\]', "H-gated-diag", "= Part A WB_CLEAR row", []),
    (ST, "fullSync", r'auto wvPx = .*&RDRAM\[\(colorFb->addressStart', "H-read-diag", "ROGUESQ_WB_VAL_PROBE pixel read",
     [(ST, "fullSync", r'getenv\("ROGUESQ_WB_VAL_PROBE"\)')]),
    (ST, "fullSync", r'auto px = .*&RDRAM\[\(colorFb->addressStart', "H-read-diag", "ROGUESQ_WB_COL_PROBE pixel read",
     [(ST, "fullSync", r'getenv\("ROGUESQ_WB_COL_PROBE"\)')]),
    (ST, "fullSync", r'copyNativeToRAM\(&RDRAM\[colorFb->addressStart\]', "H-percmd", "= Part A colour writeback", P_COLOR),
    (ST, "fullSync", r'copyNativeToRAM\(&RDRAM\[depthFb->addressStart\]', "H-percmd", "= Part A depth writeback", P_DEPTH),
    (ST, "?", r'const uint8_t \*fbRAM = &RDRAM\[screenFb->addressStart\]', "H-percmd-read",
     "present: screenFb = registry find(current VI origin), const read",
     [(ST, None, r'const uint32_t screenFbAddress = newVI\.fbAddress\(\);'),
      (ST, None, r'Framebuffer \*screenFb = framebufferManager\.find\(screenFbAddress\);')]),
    (ST, "?", r'memcpy\(present\.storage\.data\(\), &RDRAM\[screenFbAddress\]', "H-percmd-read",
     "present: copy current VI origin into host present storage (destination host)",
     [(ST, None, r'const uint32_t screenFbAddress = newVI\.fbAddress\(\);')]),
]
INFO = [(T + "common/rt64_emulator_configuration.cpp", None, r'framebuffer\.renderToRAM = true;',
         "renderToRAM default ON (the writeback rows above are live in the default config; ROGUESQ_RENDER_TO_RAM=0 = off)")]


def files():
    return [f for f in gc.files() if f.startswith(T) and "/contrib/" not in f and "/imgui/" not in f]


def body(path, fn, over):
    t = gb.read(path, over)
    if fn is None or fn == "<file>":
        return t
    return "\n".join(t[o:c + 1] for o, c, n in fz.func_spans(t) if n == fn)


def check(proofs, over):
    fails = []
    for p in proofs:
        path, fn, rx = p[:3]
        hold = p[3] if len(p) > 3 else True
        if bool(re.search(rx, body(path, fn, over))) != hold:
            fails.append("%s%s:%s /%s/" % ("" if hold else "NOT ", os.path.basename(path), fn, rx[:70]))
    return fails


def uses(path, over):
    t = gb.read(path, over)
    spans = fz.func_spans(t)
    out = []
    for m in re.finditer(KEY, t):
        ls, le = t.rfind("\n", 0, m.start()) + 1, t.find("\n", m.start())
        enc = [s for s in spans if s[0] <= m.start() <= s[1]]
        out.append(dict(path=path, line=t.count("\n", 0, m.start()) + 1, fn=enc[-1][2] if enc else "<file>",
                        text=t[ls:le if le > 0 else len(t)].strip(), at=t[m.start():m.start() + 90]))
    return out


def census(over=None, write=None, use=None, quiet=False):
    over = over or {}
    write = WRITE if write is None else write
    use = USE if use is None else use
    rows, hitw, hitu = [], set(), set()
    for f in files() + [p for p in over if p not in files()]:
        for s in gc.sites(f, over):
            r = next((i for i, w in enumerate(write) if w[0] == f and w[1] == s["fn"] and w[2] == s["kind"]
                      and re.search(w[3], s["text"])), None)
            if r is None:
                rows.append(("A", s["path"], s["line"], s["fn"], "UNCLASSIFIED", s["text"], []))
                continue
            hitw.add(r)
            fails = check(write[r][6], over)
            rows.append(("A", s["path"], s["line"], s["fn"], "OPEN" if fails else write[r][4], write[r][5], fails))
        if "/hle/" not in f:
            continue
        for u in uses(f, over):
            r = next((i for i, w in enumerate(use) if w[0] == f and w[1] in (u["fn"], "?")
                      and re.search(w[2], u["text"])), None)
            if r is None:
                rows.append(("B", u["path"], u["line"], u["fn"], "UNCLASSIFIED", u["text"][:120], []))
                continue
            hitu.add(r)
            fails = check(use[r][5], over)
            rows.append(("B", u["path"], u["line"], u["fn"], "OPEN" if fails else use[r][3], use[r][4], fails))
    drift = ["WRITE %s:%s /%s/" % (os.path.basename(w[0]), w[1], w[3]) for i, w in enumerate(write) if i not in hitw]
    drift += ["USE %s:%s /%s/" % (os.path.basename(w[0]), w[1], w[2][:50]) for i, w in enumerate(use) if i not in hitu]
    info = [(why, bool(re.search(rx, body(p, fn, over)))) for p, fn, rx, why in INFO]
    c = Counter(r[4] for r in rows)
    st = dict(rows=len(rows), open=c["OPEN"], unclassified=c["UNCLASSIFIED"], drift=len(drift))
    if not quiet:
        for part, p, ln, fn, cls, why, fails in rows:
            print("%s %s:%d [%s] -> %s  %s%s" % (part, p.replace(T, "rt64/"), ln, fn, cls, why[:110],
                                                 ("  FAILED " + "; ".join(fails)) if fails else ""))
        for d in drift:
            print("DRIFT " + d)
        for why, ok in info:
            print("info: %s -> %s" % (why, "confirmed" if ok else "NOT FOUND"))
        print("summary: rows=%d open=%d unclassified=%d drift=%d  %s" % (len(rows), st["open"], st["unclassified"],
                                                                           st["drift"], dict(c)))
    return rows, st


def rc(st):
    return 0 if st["open"] == 0 and st["unclassified"] == 0 and st["drift"] == 0 else 1


def mutate(path, old, new):
    t = open(os.path.join(REPO, path), errors="replace").read()
    assert old in t, (path, old)
    import tempfile
    fd, tmp = tempfile.mkstemp(suffix=os.path.splitext(path)[1])
    with os.fdopen(fd, "w") as f:
        f.write(t.replace(old, new))
    return {path: tmp}


def controls():
    res = []
    plant = mutate(FM, "    Framebuffer *FramebufferManager::find(uint32_t address) const {",
                   "    void FramebufferManager::plantGJ(uint8_t *RDRAM) {\n        for (auto it = framebuffers.begin(); "
                   "it != framebuffers.end(); it++) { it->second.copyNativeToRAM(&RDRAM[it->first], 1, 0, 1); }\n    }\n\n"
                   "    Framebuffer *FramebufferManager::find(uint32_t address) const {")
    _, st = census(plant, quiet=True); res.append(("plant", st["unclassified"] >= 2))
    _, st = census(write=[w for w in WRITE if not (w[2] == "fbwb" and "colorFb" in w[3])], quiet=True)
    res.append(("rule-del", st["unclassified"] >= 2))
    _, st = census(mutate(ST, "uint32_t cRowEnd = std::min(colorRowEnd, colorFb->height);",
                          "uint32_t cRowEnd = colorFb->height;"), quiet=True)
    res.append(("retained-rows", st["open"] >= 4))
    _, st = census(mutate(T + "gbi/rt64_gbi.cpp", "GBIManager::getGBIForUCode(", "GBIManager::getGBIForUCodeX("), quiet=True)
    res.append(("drift", st["drift"] >= 1))
    _, st = census(mutate(FM, "void FramebufferManager::checkRAM(const uint8_t *RDRAM",
                          "void FramebufferManager::checkRAM(uint8_t *RDRAM"), quiet=True)
    res.append(("const-drop", st["open"] == 1))
    _, st = census(mutate(ST, "depthFb = &framebufferManager.get(depthImg.address, G_IM_SIZ_16b, colorImg.width, colorHeight);",
                          "depthFb = framebufferManager.find(lastDepthAddress);"), quiet=True)
    res.append(("depth-registry", st["open"] >= 4))
    _, st = census(mutate(T + "gbi/rt64_gbi.cpp", "rdramCursor += rdramToHash;", "rdramCursor += rdramToHash; *rdramCursor = 0;"),
                   quiet=True)
    res.append(("alias-store", st["open"] == 1))
    _, st = census(quiet=True); res.append(("real", rc(st) == 0))
    ok = sum(1 for _, v in res if v)
    print("controls: " + " ".join("%s=%s" % (k, "ok" if v else "FAIL") for k, v in res) + " -> %d/%d" % (ok, len(res)))
    return 0 if ok == len(res) else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    _, st = census()
    sys.exit(rc(st))


if __name__ == "__main__":
    main()
