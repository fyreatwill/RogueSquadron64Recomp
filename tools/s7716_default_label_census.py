#!/usr/bin/env python3
"""s7716 default-on label audit: close the idiom class behind the s7714 AUDIO_UCODE and s7715 M5_C88_VALUE defects.

Idiom: a setting's DEFAULT was flipped to on ("unset = on, =0 restores old") while some reader kept the generic
`e && e[0] && e[0] != '0'` test, so that reader (usually a log label) names the wrong arm for unset.

  (A) DEFAULT-ON set = every name with a modelled on/off reader that reads UNSET as on (s7714 site model over the s7711
      site finder, ALL sites incl. single-reader names) plus every name the docs call default-on (`X=0` in a row saying
      on by default / restores / turns it off, or a `| on |` default column).
  (B) For each default-on name, every reader is classified: AGREES (unset on), LABEL-WRONG (unset off, the site only
      prints: fprintf/snprintf within its statement window), BEHAVIOUR-SPLIT (unset off, not print-only), DEFERRED
      (unset decided by another variable: auto-default on dd/hooks, or an inverted `if (!e)` reading) or UNMODELLED
      (listed; each one hand-read in REVIEWED).
  (C) DOC CHECK: every docs/debug-trace-env-vars.md row whose default column is on/off is compared with the code's
      consensus unset reading (all modelled sites agree, no setenv auto-default of the name). A mismatch = DOC-WRONG.

Exit 0 = no unreviewed LABEL-WRONG / BEHAVIOUR-SPLIT / DOC-WRONG / UNMODELLED; 1 = findings; 2 = control failure.
--controls: (1) the pre-s7715 C88 label text (git show <s7714 commit>:src/main/upstream_compat.cpp) must flag
ROGUESQ_M5_C88_VALUE as LABEL-WRONG; (2) the current tree must NOT flag it; (3) a planted doc row
`| ROGUESQ_FPS60 | on |` must be DOC-WRONG; (4) the pre-s7714 vendored AUDIO_UCODE label planted back must be flagged; (5) a planted default-on pair (behaviour `!(e && *e == '0')`, label
`fprintf(.. e && *e != '0' ..)`) must give exactly one LABEL-WRONG.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7711_optval_census as c7711
import s7714_truth_census as t

ROOT = c7711.ROOT
DEBUG_DOC = "docs/debug-trace-env-vars.md"
CLAIM_DOCS = ["docs/OWNER-OPT-INS.md", DEBUG_DOC, "README.md"]
CLAIM = re.compile(r"(?i)on by default|default on|default-on|\| on \||restores|turns it off|shows them")
SETENV = re.compile(r'setenv\(\s*\\?"(ROGUESQ_[A-Z0-9_]+)')
PRINT = re.compile(r"\b(f?printf|snprintf|fputs|puts)\s*\(")
C88_COMMIT = "b7ea1c3eb"  # s7714: last tree carrying the pre-s7715 C88 label

# name -> reason; every unmodelled or deferred default-on reader read by hand at s7716.
REVIEWED = {
    "ROGUESQ_A14_YIELD": "apply_s4694_a14_boundary.py:44 label is `(e && e[0] == '0') ? 0 : 1` (unset on): agrees",
    "ROGUESQ_CONTROLS": "main.cpp:12664 rs64_bind_path: a file path, not on/off (unset = default controls.json path)",
    "ROGUESQ_DD_OFFMAPCULL": "upstream_compat.cpp:182 presence arms the s7030 hook only; numeric radius (s7714 REVIEWED)",
    "ROGUESQ_DD_WIDEWIN_CAP": "upstream_compat.cpp:397 comma list parse; unset = n=0, the s7012 auto-default applies it",
    "ROGUESQ_G1D_RECT_WRAP": "dpc_bridge.cpp:5839 `r && *r == '0'` disables glue fuse (unset keeps it on): agrees",
    "ROGUESQ_G1E_TRIM": "all 7 pass-on readers (upstream_compat 4865, dpc_bridge 8286, apply_s5835 x2, apply_s5908 x2, "
                        "apply_s7445) restore the OLD always-on path only at `g[0] == '0'`: unset = trim on, agrees",
    "ROGUESQ_SPIN_YIELD": "apply_s4199_m5_spin_yield_default.py:18 is the rewriter that flips the reader default, no call",
    "ROGUESQ_CUT_LIVE": "upstream_compat.cpp:136 s6919_mode(name, 1): default arg 1 = on when unset: agrees",
    "ROGUESQ_DD_FOG": "upstream_compat.cpp:87 fog start/end auto from dd>1 when unset; value = 'a,b' or 't': deferred",
    "ROGUESQ_DD_OFFMAPCULL_KEDGE": "upstream_compat.cpp:256 value list; main.cpp:14431 setenv auto-default: deferred",
    "ROGUESQ_DD_WIDEWIN_MERGE": "upstream_compat.cpp:581 fraction; main.cpp:14447 setenv auto-default: deferred",
    "ROGUESQ_DRAIN_INLOOP_TICK": "main.cpp:14325 writes the default when unset (s7714 REVIEWED): deferred",
    "ROGUESQ_G1E_CELLIDX": "upstream_compat.cpp:10131 mode defaults on at dd>1, retail walk at dd1: deferred on dd",
    "ROGUESQ_G1E_FAST": "main.cpp:4975 unset = auto: on unless rsp hooks / a diag env is armed; its label prints the "
                        "decided value and reason: agrees",
    "ROGUESQ_G5B_TG_FIX": "dpc_bridge.cpp:3527 unset = on iff DRAW_DISTANCE > 1 (doc: on above dd1): deferred",
    "ROGUESQ_G5G_AIM": "apply_s6907_aim.py:27 `md = 1; if (e && *e) md = ...`: unset = 1 (on); the s7714 model reads "
                       "only the if-branch. Label `[g5g] aim mode %d` prints md: agrees",
    "ROGUESQ_STICK_GATE": "main.cpp:13701 rs64_stick_gate_parse(e) (unset -> on, s7513); label prints g.on: agrees",
    "ROGUESQ_PARTICLE_FIX": "doc-only name (OWNER-OPT-INS row), no reader in src/lib/tools: nothing to mislabel",
    "ROGUESQ_TEXRECT_ALPHA_FIX": "doc-only name (OWNER-OPT-INS row), no reader in src/lib/tools: nothing to mislabel",
    "ROGUESQ_DD_OFFMAPCULL_K": "numeric K list; main.cpp:14424 presence guard of the s7037 dd-bundle setenv 0.6 auto-default, "
                               "14433 prints the decided value: deferred",
    "ROGUESQ_DIAG_GATE": "main.cpp:5899 `=0` forces the diag gate open, else the OR of named diag envs: same =0 reading as the "
                         "other three readers (dpc_bridge 2229, rt64_interpreter 258, upstream_compat 3223): agrees",
    "ROGUESQ_G1D_SPANCELL": "upstream_compat.cpp:705 numeric mode atoi(e), unset = 3: a mode number, not on/off",
    "ROGUESQ_RUMBLE_SCALE": "main.cpp:12214 float gain 0..2, unset = 1.0: a value, not on/off",
    "ROGUESQ_S7679_NEAR": "rs64_standins.cpp:858 near radius, unset = 15.0 ('odd' = -15): a value, not on/off",
    "ROGUESQ_VI_RT": "events.cpp:833 mode atoi(e), unset = 1 (s6967 default on), =2 QoS variant: agrees with main.cpp",
    "ROGUESQ_LOG_M4_Y8000": "dpc_bridge.cpp:1132 opt-in since s6712 (was default on); the debug doc row said on until s7716",
    "ROGUESQ_M5_B40_VALUE": "s7715 REVIEWED: live replay form `!= '0' ? r2 : 0` reads unset off like the labels; the "
                            "vendored `== '0'` form the audit sees as default-on is rewritten at regen. Owner item, never flip",
    "ROGUESQ_M5_C88_VALUE": "upstream_compat.cpp 2021/2141/2176/6399 hand e to rs64_s7715_c88_label (0 only at =0): fixed s7715",
}


# name -> reason: a deliberate on/off split between readers (hand-read at s7716).
REVIEWED_SPLIT = dict(t.REVIEWED)  # s7714/s7715 hand-read splits (B40 replay form, OVL2C dead reader, PRESENT_EARLY_FORCE)
# name -> reason: a debug-doc default column that is right although the readers' consensus differs.
REVIEWED_DOC = {}


def claims(doc_texts):
    out = set()
    for d, txt in doc_texts:
        for l in txt.split("\n"):
            if CLAIM.search(l):
                out.update(re.findall(r"(ROGUESQ_[A-Z0-9_]+)=0\b", l))
            m = re.match(r"\| `(ROGUESQ_[A-Z0-9_]+)` \| on \|", l)
            if m:
                out.add(m.group(1))
    return out


def debug_defaults(txt):
    out = {}
    for i, l in enumerate(txt.split("\n")):
        m = re.match(r"\| `(ROGUESQ_[A-Z0-9_]+)` \| (on|off) \|", l)
        if m:
            out[m.group(1)] = (m.group(2), f"{DEBUG_DOC}:{i + 1}")
    return out


def model_all(overrides=None):
    """Every getenv/helper call of a ROGUESQ_ name, INCLUDING getenvs inside printf arguments (the s7711 finder skips
    those, and they are exactly where a label lives). Overrides are {rel: lines}; sites are found in the override text."""
    out = {}
    for path in c7711.source_files():
        rel = os.path.relpath(path, ROOT)
        lines = (overrides or {}).get(rel) or open(path, errors="replace").read().split("\n")
        if not any("ROGUESQ_" in l for l in lines):
            continue
        for i, l in enumerate(lines):
            for name in dict.fromkeys(m.group(2) for m in c7711.CALL.finditer(l)):
                sig, node = t.model_site(lines, i + 1, name, rel.endswith(".py"))
                win = "\n".join(lines[i:i + 3])
                pos = l.find(f'"{name}') if f'"{name}' in l else l.find(name)
                print_only = bool(PRINT.search(l[:pos])) or (bool(PRINT.search(win)) and not re.search(
                    r"\breturn\b|\bif\s*\(|\?\s*[A-Za-z_]+\s*:|=\s*[^=]*\?", l[pos:].split(";")[0] if pos >= 0 else ""))
                out.setdefault(name, []).append((f"{rel}:{i + 1}", sig, node, print_only))
    return out


def reading(sig):
    """Polarity-free: ON = unset reads like =1 (and =0 differs); OFF = unset reads like =0 (and =1 differs)."""
    if not sig or any(v not in (0, 1) for v in sig[:3]):
        return None
    if sig[0] == sig[2] != sig[1]:
        return "on"
    if sig[0] == sig[1] != sig[2]:
        return "off"
    return None


def setenv_names():
    s = set()
    for f in c7711.source_files():
        s.update(SETENV.findall(open(f, errors="replace").read()))
    return s


def audit(models, claimed, dbg, auto, quiet=False):
    finds = []
    on_code = {n for n, ss in models.items() if any(not t.is_num(x[2]) and reading(x[1]) == "on" for x in ss)}
    don = sorted(on_code | claimed)
    counts = dict(AGREES=0, LABEL_WRONG=0, BEHAVIOUR_SPLIT=0, UNMODELLED=0, DEFERRED=0)
    for n in don:
        ss = models.get(n, [])
        for site, sig, node, po in ss:
            r = reading(sig) if sig and not t.is_num(node) else None
            if not sig:
                k = "UNMODELLED"
            elif r == "on":
                k = "AGREES"
            elif r == "off" and n in on_code:
                k = "LABEL_WRONG" if po else "BEHAVIOUR_SPLIT"
            else:
                k = "DEFERRED"
            counts[k] += 1
            if k in ("LABEL_WRONG", "BEHAVIOUR_SPLIT") and n in REVIEWED_SPLIT:
                continue
            if k in ("LABEL_WRONG", "BEHAVIOUR_SPLIT") or (k in ("UNMODELLED", "DEFERRED") and n not in REVIEWED):
                finds.append((k, n, site))
                if not quiet:
                    print(f"{k:15s} {n} {site} sig={''.join(map(str, sig)) if sig else node} print_only={po}")
        if not ss and n not in REVIEWED:
            finds.append(("NO_READER", n, "-"))
            if not quiet:
                print(f"NO_READER       {n}")
    for n, (d, where) in sorted(dbg.items()):
        rs = {reading(x[1]) for x in models.get(n, []) if x[1] and not t.is_num(x[2])} - {None}
        if len(rs) != 1 or n in auto or n in REVIEWED_DOC:
            continue
        code = rs.pop()
        if code != d:
            finds.append(("DOC_WRONG", n, where))
            if not quiet:
                print(f"DOC_WRONG       {n} {where} doc={d} code={code}")
    return finds, len(don), counts


def load(overrides=None, extra_dbg=""):
    docs = [(d, open(os.path.join(ROOT, d), errors="replace").read()) for d in CLAIM_DOCS]
    dbg = debug_defaults(dict(docs)[DEBUG_DOC] + extra_dbg)
    return model_all(overrides), claims(docs), dbg, setenv_names()


def main():
    ok = True
    if "--controls" in sys.argv:
        rel = "src/main/upstream_compat.cpp"
        old = subprocess.run(["git", "show", f"{C88_COMMIT}:{rel}"], cwd=ROOT, capture_output=True, text=True).stdout
        m, cl, dbg, auto = load({rel: old.split("\n")})
        f, _, _ = audit(m, cl, dbg, auto, quiet=True)
        g = any(k == "LABEL_WRONG" and n == "ROGUESQ_M5_C88_VALUE" for k, n, _ in f)
        print(f"control pre-s7715 C88 label ({C88_COMMIT}) want LABEL_WRONG {'PASS' if g else 'FAIL'}")
        ok &= g
        vend = "tools/fixup_game_funcs_vendored.py"
        vt = open(os.path.join(ROOT, vend), errors="replace").read()
        new_label = "const char* arm = !(audio && audio[0] == '0') ?"
        m, cl, dbg, auto = load({vend: vt.replace(new_label, t.OLD_LABEL).split("\n")})
        f, _, _ = audit(m, cl, dbg, auto, quiet=True)
        g = new_label in vt and any(k in ("LABEL_WRONG", "BEHAVIOUR_SPLIT") and n == "ROGUESQ_AUDIO_UCODE" for k, n, _ in f)
        print(f"control pre-s7714 AUDIO_UCODE label planted back want flagged {'PASS' if g else 'FAIL'}")
        ok &= g
        m, cl, dbg, auto = load(extra_dbg="\n| `ROGUESQ_FPS60` | on | planted |\n")
        f, _, _ = audit(m, cl, dbg, auto, quiet=True)
        g = not any(n == "ROGUESQ_M5_C88_VALUE" and k == "LABEL_WRONG" for k, n, _ in f)
        print(f"control current C88 label want no LABEL_WRONG {'PASS' if g else 'FAIL'}")
        ok &= g
        g = any(k == "DOC_WRONG" and n == "ROGUESQ_FPS60" for k, n, _ in f)
        print(f"control planted FPS60 doc row 'on' want DOC_WRONG {'PASS' if g else 'FAIL'}")
        ok &= g
        pm = {"ROGUESQ_PLANT": [
            ("P:1",) + t.model_site(['const char* e = getenv("ROGUESQ_PLANT"); return !(e && *e == \'0\');'], 1,
                                    "ROGUESQ_PLANT", False) + (False,),
            ("P:2",) + t.model_site(['fprintf(stderr, "on=%d", (getenv("ROGUESQ_PLANT") && *getenv("ROGUESQ_PLANT") != \'0\'));'],
                                    1, "ROGUESQ_PLANT", False) + (True,)]}
        f, _, _ = audit(pm, set(), {}, set(), quiet=True)
        g = [k for k, n, _ in f] == ["LABEL_WRONG"]
        print(f"control planted default-on pair want exactly one LABEL_WRONG got {[k for k, _, _ in f]} {'PASS' if g else 'FAIL'}")
        ok &= g
        if not ok:
            return 2
    m, cl, dbg, auto = load()
    f, nd, counts = audit(m, cl, dbg, auto)
    print(f"s7716: {nd} default-on names ({len(cl)} doc-claimed), readers {counts}, {len(dbg)} debug-doc defaults, "
          f"{len(f)} unreviewed findings")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
