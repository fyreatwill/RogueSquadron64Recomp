#!/usr/bin/env python3
"""s7788 dead-emitter census: which replayed fixup/apply steps silently emit NOTHING, or fewer sites than they mean to?

s7787 found the s2586 "store" branch dead (0 emitted: it keyed store pcs off a tracker only branch comments set) and s6336 losing
one store to an s4984 rewrite. Those were found by accident; this asks the question of every step at once.

Input: the RS64_REPLAY_TRACE jsonl of a fresh replay from pristine (one record per RS64_REPLAY step: lines added / removed per
file; produce it with `env RS64_REPLAY_TRACE=<f> python3 tools/s7719_regen_gate.py --strict --keep <dir>`) and that replay's log
(the `[s4648-replay] <name>: <status> <stdout>` lines carry each script's own report).

Per step:
  LIVE       added or removed >=1 non-trivial line
  REDUNDANT  changed nothing, but every marker the script writes (`/* PATCH: <tag>` literals, MARK/TAG constants) is already in
             the live tree: an earlier step (usually the vendored fixer's inline copy) emitted it first
  DEAD       changed nothing and none of its markers is in the live tree: its pattern never matched (a null from its rows is a
             false zero)
  NOOP       changed nothing, script carries no harvestable marker: judged by its own stdout (listed with it)
Also, independent of the trace, MARKER rows: every `/* PATCH: <tag>` literal written by an in-chain script with 0 live-tree hits
(strip_diag_layers TAGS are counted as STRIPPED, on purpose).
PARTIAL candidates: LIVE steps whose own stdout reports a miss (missing/not found/anchor/skip/warn/0 of/fewer).

WARN rows: every vendored-fixer `WARNING` report line in the replay log must match a REVIEWED_WARN family (a NEW anchor drift
reads open).
Usage: s7788_dead_emitter_census.py <trace.jsonl> <replay.log> [live_dir] [--controls]
rc 0: every step classified, 0 DEAD, 0 unreviewed NOOP/PARTIAL/MARKER rows (REVIEWED below); 1 open rows; 3 controls failed.
--controls: planted steps (no change + absent marker -> DEAD; no change + live marker -> REDUNDANT; one added line -> LIVE) and a
planted log line reporting "anchor not found" -> PARTIAL, all run through the same classifier.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
TRIVIAL = re.compile(r"^[\s{}();]*$")
MARK_LIT = re.compile(r"/\* PATCH: ([A-Za-z0-9_][^*\"'{%\\]*?)\s*(?:\*/|[\"'{%\\])")
MARK_CONST = re.compile(r"^\s*(?:MARK\w*|TAG\w*|MARKER\w*)\s*=\s*[rbf]?[\"']([^\"'{]{6,})[\"']", re.M)
MISS = re.compile(r"missing|not found|no anchor|anchor (?:absent|not)|skipp?ed [1-9]|warn|\b0 of [1-9]|fewer|unmatched|FAILED to",
                  re.I)
# Hand verdicts after reading each script (key -> reason). Keep tight; every entry names why the zero is correct.
REVIEWED = {
    **{n: "s7788: patch text present in the live tree (the vendored fixer's inline copy emits it first; script says 'fixup already')"
       for n in ("apply_s4192b_wait_spin_default.py", "apply_s4199_m5_spin_yield_default.py", "apply_s4913_marks.py",
                 "apply_s5792_npc_victim.py", "apply_s5793_npc_diff.py", "apply_s5806_npc_invuln.py", "apply_s5849_cnt_log.py",
                 "apply_s5794_shooter.py", "apply_s5797_aim.py", "apply_s5796_victim.py")},
    "apply_s4598_complete_store_census.py": "s7788: its census hook calls rs64_s4597_target_store, which strip_diag_layers drops on "
                                            "purpose (TAGS s4597); the writer-parity half is live via the vendored copy",
    "apply_s5835_sphere_probe.py": "s7788: rs5904_tally is in the tree x3; '/* PATCH: s5904' is harvest noise (the code says /* s5904 */)",
}
# s7788: the vendored fixer's own default-path "WARNING ... count=0 / not found / missing" report lines, by family. Every one was
# read; none is a behaviour patch the current game needs, and no PORTING-STATE conclusion after each went dead cites its tag.
REVIEWED_WARN = [
    (r"alloc-tail GUARD[34] site=", "shadowed: the same pcs carry the s251 DLENTRY_TAIL prewalk / s350 drain-mesh tail guards"),
    (r"s563 HEAPLISTDEQ_ATTR_WRITE|s566 HEAP_FREE_LIST_DEQUEUE_R6",
     "RETIRED s7788: s517-s566 freelist skip-guards, never applied since the s2190 parity line + braced stores broke their "
     "`    MEM_W(...) = ...;` anchors; 0 crashes at 0x8000D6D0/D944-D994 in PORTING-STATE after s2190 (~5,600 sessions); "
     "rule 11: not restored (a mitigation without a live writer)"),
    (r"s6(39|41|50|52) \w+-[\w-]+ missing after regen",
     "diagnostic FL_ZERO_WATCH guest blocks (s639-s652); s6571 used the live host [fl-zero-poll] side with a control, not these"),
    (r"s57[45] |s612 ship|s637 mv-b8|s80[8] VI writer|s811 VI argument",
     "s574-s811 era probes (selector/ship/VI writer attribution), threads closed; 0 citations after s2190"),
    (r"s19(2[0-8]|42) |s2031 wait seed", "s1920-s2031 avf-gate / menu-spin / M5 seed probes; s1927 noted dead already (PS line 154991)"),
]


def harvest(src):
    tags = set()
    for m in MARK_LIT.finditer(src):
        t = m.group(1).strip()
        if len(t) >= 4:
            tags.add("/* PATCH: " + t)
    for m in MARK_CONST.finditer(src):
        tags.add(m.group(1))
    return tags


def load_tree(d):
    return "\n".join(f.read_text(errors="surrogateescape") for f in sorted(pathlib.Path(d).iterdir()) if f.is_file())


def parse_log(path):
    out = {}
    for ln in open(path, errors="replace"):
        m = re.match(r"\[s4648-replay\] (\S+): (ok(?: \(tolerated[^)]*\))?|FAIL[^|]*?)(?: (.*))?$", ln.rstrip("\n"))
        if m:
            out[m.group(1)] = (m.group(2), m.group(3) or "")
    return out


def classify(rec, src, tree, report):
    add = sum(1 for v in rec["files"].values() for l in v["add"] if not TRIVIAL.match(l))
    dele = sum(1 for v in rec["files"].values() for l in v["del"] if not TRIVIAL.match(l))
    tags = harvest(src) if src is not None else set()
    hit = {t: tree.count(t) for t in tags}
    if add or dele:
        verdict = "PARTIAL?" if MISS.search(report or "") else "LIVE"
    elif not tags:
        verdict = "NOOP"
    elif all(hit.values()):
        verdict = "REDUNDANT"
    elif not any(hit.values()):
        verdict = "DEAD"
    else:
        verdict = "DEAD-PART"  # some markers live (emitted elsewhere), others nowhere
    return verdict, add, dele, hit


REVIEWED_MARK = [
    (r"s(1151|1152|2008|2445|3352|3556|4079|408[2-7]|4323|4329|4342|4597|4712|4714)\b",
     "M5/s1151-s4714 diagnostic witness/census blocks: stripped (strip_diag_layers/fixup_live_replay) or anchor-drifted; "
     "M5 closed; diagnostic only (log/count), no default-path behaviour"),
    (r"s2586 M5 writer store", "s7787: dead store branch (keys pcs off a tracker only branch comments set), found and recorded"),
]


def vendored_marker0(tree, stripped):
    """(line, OPTIN|TOP|CALLED|UNCALLED, marker) for vendored `/* PATCH:` literals with 0 live hits. OPTIN = the enclosing def is
    only called right under an `os.environ.get("RS64_...")` one-shot mode (opt-in diagnostic builds, not the default chain)."""
    src = (TOOLS / "fixup_game_funcs_vendored.py").read_text(errors="replace").split("\n")
    defs = [(i, m.group(1)) for i, l in enumerate(src) if (m := re.match(r"^def (\w+)\(", l))]
    out, seen = [], set()
    for i, l in enumerate(src):
        for m in MARK_LIT.finditer(l):
            t = "/* PATCH: " + m.group(1).strip()
            if len(t) < 14 or t in tree or t in seen or stripped.search(t):
                continue
            seen.add(t)
            enc = None
            for j, n in defs:
                if j > i:
                    break
                enc = (j, n)
            if enc and any(src[k] and not src[k][0].isspace() and not src[k].startswith(("#", ")", "]", "}"))
                           for k in range(enc[0] + 1, i)):
                enc = None
            kind = "TOP"
            if enc:
                calls = [k for k, x in enumerate(src) if re.search(r"\b" + enc[1] + r"\(", x) and not x.startswith("def ")]
                if not calls:
                    kind = "UNCALLED"
                elif all(any('os.environ.get("RS64_' in src[c - d] for d in range(4)) for c in calls):
                    kind = "OPTIN"
                else:
                    kind = "CALLED"
            out.append((i + 1, kind, t))
    return out


def controls(tree):
    ok = True
    live_tag = next((t for t in ("/* PATCH: s6336", "/* PATCH: s4296") if t in tree), None)
    cases = [
        ({"step": "ctl_dead", "files": {}}, 'x = "/* PATCH: s9999 planted never emitted */"', "", "DEAD"),
        ({"step": "ctl_red", "files": {}}, f'x = "{live_tag} */"' if live_tag else None, "", "REDUNDANT"),
        ({"step": "ctl_live", "files": {"funcs_0.c": {"add": ["    ctx->r2 = 1;"], "del": []}}}, "", "patched 1", "LIVE"),
        ({"step": "ctl_part", "files": {"funcs_0.c": {"add": ["    ctx->r2 = 1;"], "del": []}}}, "", "anchor not found x", "PARTIAL?"),
    ]
    w = "WARNING: s9999 planted anchor count=0"
    got = "open" if next((v for k, v in REVIEWED_WARN if re.search(k, w)), None) is None else "reviewed"
    print(f"control planted-warn: want open got {got} {'PASS' if got == 'open' else 'FAIL'}"); ok &= got == "open"
    w = "WARNING: s563 HEAPLISTDEQ_ATTR_WRITE site=0x8000D944 off=0X4 count=0"
    got = "open" if next((v for k, v in REVIEWED_WARN if re.search(k, w)), None) is None else "reviewed"
    print(f"control known-warn: want reviewed got {got} {'PASS' if got == 'reviewed' else 'FAIL'}"); ok &= got == "reviewed"
    for rec, src, rep, want in cases:
        got = classify(rec, src, tree, rep)[0]
        print(f"control {rec['step']}: want {want} got {got} {'PASS' if got == want else 'FAIL'}")
        ok &= got == want
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    live = pathlib.Path(args[2]) if len(args) > 2 else ROOT.parent / "N64Recomp" / "RecompiledFuncs"
    if len(args) < 2:
        if "--controls" not in sys.argv:
            sys.exit(__doc__)
        # sweep mode: no trace here (the full census runs inside s7719_regen_gate.py step 5b); controls only on the live tree.
        ok = controls(load_tree(live))
        print("controls-only (full census: s7719_regen_gate.py step 5b) " + ("PASS" if ok else "FAILED"))
        sys.exit(0 if ok else 3)
    tree = load_tree(live)
    if "--controls" in sys.argv and not controls(tree):
        print("controls FAILED"); sys.exit(3)
    log = parse_log(args[1])
    recs = [json.loads(l) for l in open(args[0], errors="surrogateescape")]
    if not recs:
        print("empty trace"); sys.exit(3)
    counts, open_rows = {}, 0
    for rec in recs:
        name = rec["step"]
        p = TOOLS / name
        src = p.read_text(errors="replace") if name.endswith(".py") and p.exists() else None
        st, rep = log.get(name, ("?", ""))
        v, a, d, hit = classify(rec, src, tree, rep)
        counts[v] = counts.get(v, 0) + 1
        if v != "LIVE" and v != "REDUNDANT":
            rv = REVIEWED.get(name)
            open_rows += rv is None
            if rv and "--all" not in sys.argv:
                continue
            hs = " ".join(f"{t[11:40]!r}={n}" for t, n in sorted(hit.items())[:4])
            print(f"{v:10s} {name} +{a}/-{d} {st} | {rep[:150]} | {hs}" + (f" | REVIEWED: {rv}" if rv else ""))
        elif v == "REDUNDANT" and "--all" in sys.argv:
            print(f"REDUNDANT  {name} | {rep[:120]}")
    # marker rows: in-chain scripts' literals with 0 live hits
    strip_src = (TOOLS / "strip_diag_layers.py").read_text()
    stripped = re.compile(re.search(r'TAGS = r"([^"]+)"', strip_src).group(1))
    # Marker rows only for the vendored fixer: its inline blocks are not traced per block (apply_* steps are, above; their
    # literals include anchor text, so a per-literal check there is noise).
    zero, optin = vendored_marker0(tree, stripped), 0
    for line, kind, t in zero:
        if kind == "OPTIN":
            optin += 1; continue
        rv = next((v for k, v in REVIEWED_MARK if re.search(k, t)), None)
        open_rows += rv is None
        if rv and "--all" not in sys.argv:
            continue
        print(f"MARKER0    vendored:{line} {kind} {t!r}" + (f" | REVIEWED: {rv}" if rv else ""))
    warns = [l.strip() for l in open(args[1], errors="replace") if "WARNING" in l and not l.startswith("[s4648-replay]")]
    wopen = 0
    for w in warns:
        rv = next((v for k, v in REVIEWED_WARN if re.search(k, w)), None)
        wopen += rv is None
        if rv is None or "--all" in sys.argv:
            print(f"WARN       {w[:160]}" + (f" | REVIEWED: {rv}" if rv else ""))
    open_rows += wopen
    print(f"steps={len(recs)} " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())) +
          f" vendored_marker0={len(zero)} (optin={optin}) warn={len(warns)} warn_open={wopen} open={open_rows}")
    sys.exit(1 if open_rows else 0)


if __name__ == "__main__":
    main()
