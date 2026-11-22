#!/usr/bin/env python3
"""s7789 quiet-skip census: which inline blocks of fixup_game_funcs_vendored.py never apply, WITHOUT printing a WARNING?

s7788 reviewed every vendored block that reports a WARNING on an anchor miss. Many blocks instead guard with
`if text.count(old) == 1:` / `if marker in text: continue` and skip silently, so a drifted anchor there leaves no trace.
This runs the vendored fixer itself on a fresh pristine tree with every `<str>.replace(...)` and `<str>.count(...)` call
rewritten (AST) into a recorder keyed by source line, then classifies every `.replace` site:
  HIT        some call found its `old` text (the block applied at least once)
  MISS       called, `old` never present (anchor drift that the block did not report)
  NOTCALLED  never reached (guard false: count != 1, p.name filter, env opt-in, marker already present)
For MISS/NOTCALLED the site's `new` text (DYNTEXT when neither the run nor a literal assignment gives it) is resolved (runtime value, or the nearest literal assignment in the same def) and its
most distinctive added line counted in the LIVE tree: PRESENT (emitted by another route / an earlier site: shadowed) or ABSENT.
Sites whose enclosing def is only called under an `os.environ.get("RS64_...")` mode read OPTIN (not the default chain).
Usage: s7789_replace_site_census.py [--live <dir>] [--keep <dir>] [--pristine <N64Recomp output dir>] [--all] [--json <out>]
(run by tools/s7719_regen_gate.py as step 5c on its own pristine tree; ~65 s)
rc 0 = controls pass and 0 unreviewed ABSENT behaviour sites; 1 = open rows; 3 = controls failed / chain failed.
Controls (same run): >=90% of HIT sites (>=100) must read PRESENT in the vendored output of this run (the presence measure\nsees what the replay emitted); PRESENT/ABSENT = in the live tree OR this run's vendored output; the s517 HEAPLISTDEQ_ATTR_WRITE site (retired s7788,
its anchor gone since the s2190 parity line) must read NOTCALLED+ABSENT.
"""
import ast, atexit, json, os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
VEND = ROOT / "tools" / "fixup_game_funcs_vendored.py"
TRIVIAL = re.compile(r"^[\s{}();]*$")

# Hand verdicts by (enclosing def or tag regex on the new text) -> reason. Filled after reading each ABSENT row (rule 11).
REVIEWED = [
    (r"_guard(_[a-z])?_enabled < 0\) \{ const char\* e = getenv\(\"ROGUESQ_|PATCH: unguarded (derived-pointer|free-list-allocated-node|stack-slot)",
     "RETIRED s7789: s109 + s467-s566 item -317 skip-guard lineage (~100 sites), none applied in a pristine replay (anchors "
     "drifted by the s2190 parity line / braced stores, same as s563/s566 in s7788); their 130 site pcs appear in 0 crash lines "
     "of PORTING-STATE after s2190 (same scan finds 97 for the known crash pcs 0x80022160/0x8000834C) and 19 levels held 660 s "
     "clean without them; rule 11: mitigations with no live writer, not restored"),
    (r" apply_s1993_drain_inloop_gate \| | apply_s2190_m5_writer_parity \| ",
     "M5 diagnostic print/table blocks (s1993 tick-site, s2190 writer-parity tables) in opt-in arms; M5 closed"),
    (r"\[avf-gate\]|\[spin-yield\]|\[vi-cb-slot\]|siten_menu_spin|s1924 menuOverlayInit",
     "s1924-s1942 avf-gate / menu-spin / VI-callback probes (s7788 WARN family), diagnostic only"),
    (r"^tag=s590 |s_sel_n_a|gPlayerShip|model-viewer|sign-extended KSEG0 base",
     "s590-s637 hangar-exit / ship-store / model-viewer probes + s616 base fix inside the dead s605 force body (s7788 WARN family)"),
    (r"s145/s146 race window",
     "SHADOWED s7789: s147 count-write reorder is dead, but the same 0x8008F0CC count publication is now an s4984 atomic "
     "release store + s4986 voice-lock exit + s4987 alloc-pair hook (live funcs_23.c), which close the s146 race window"),
    (r"s_process_scene_node_depth = 0",
     "conditional build repair: only fires when the s175 exit-decrement survives without its declaration; not the case"),
    (r"^tag=s(39\d|4[0-9]\d|5[0-6]\d) |^tag=\? <module> \| text = text.replace\(_old, _new, 1\)",
     "DYNTEXT (new text built at runtime, not resolvable statically) rows of the same s390-s568 skip-guard lineage (count != 1 -> continue; incl. the s4xx sibling-ptr table): "
     "retired with the family above"),
    (r"^tag=s(811|192[3-7]|1942|2031|3556|4204|5533) |^tag=\? (_s1985_insert_after|_s1987_patch_store|apply_s2190_m5_writer_parity|"
     r"apply_s3277_swapbuffer_delay_slot_text|add_probe) |rs64_probe_submit_gfx|^tag=\? <module> \| (text3|text) = \2?",
     "diagnostic probes in opt-in or superseded arms: s811 VI-arg, s1923-s1942 menu/avf, s2031 M5 seed, s3556 rs_malloc "
     "route table, s4204/s4079 voice-modulation, s5533/s5228 store census, s1985/s1987 M5 helpers, s1151/s1152 submitGfx "
     "callsite probes (module-level RS64_S1151/S1152 modes), s3277 probe-window branch (the skip-goto branch is the live one)"),
    (r"^tag=s4648 ", "filter-voice field probe: 'else applied by the post-flow stage' (s4648), diagnostic"),
]


class Hook(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr in ("replace", "count") and not any(isinstance(a, ast.Starred) for a in node.args):
            return ast.copy_location(ast.Call(func=ast.Name(id="__rs7789", ctx=ast.Load()),
                                              args=[ast.Constant(node.lineno), ast.Constant(f.attr), f.value] + node.args,
                                              keywords=node.keywords), node)
        return node


def recorder(rec):
    def hook(line, attr, obj, *a, **k):
        r = getattr(obj, attr)(*a, **k)
        if isinstance(obj, str) and a and isinstance(a[0], str) and a[0]:
            e = rec.setdefault(f"{attr}:{line}", {"calls": 0, "hits": 0, "new": None, "old": None})
            e["calls"] += 1
            hit = (a[0] in obj) if attr == "replace" else (r == 1)
            e["hits"] += hit
            if attr == "replace" and len(a) > 1 and isinstance(a[1], str) and e["new"] is None:
                e["new"], e["old"] = a[1], a[0]
        return r
    return hook


def run_instrumented(tree_dir, out_json):
    """Child mode: exec the AST-hooked vendored fixer on tree_dir (as if `python3 vendored.py tree_dir`), dump the records."""
    rec = {}
    atexit.register(lambda: json.dump(rec, open(out_json, "w")))
    code = compile(ast.fix_missing_locations(Hook().visit(ast.parse(VEND.read_text(), str(VEND)))), str(VEND), "exec")
    sys.argv = [str(VEND), tree_dir]
    sys.path.insert(0, str(VEND.parent))
    exec(code, {"__name__": "__main__", "__file__": str(VEND), "__rs7789": recorder(rec), "__builtins__": __builtins__})


def static_sites():
    """Every .replace site: line -> (enclosing def, resolved new text or None, arg source)."""
    src = VEND.read_text()
    mod = ast.parse(src)
    lines = src.split("\n")
    out = {}

    def literal_of(fn, name, before):
        best = None
        for n in ast.walk(fn):
            if isinstance(n, ast.Assign) and n.lineno < before and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
                try:
                    v = ast.literal_eval(n.value)
                except Exception:
                    continue
                if isinstance(v, str) and (best is None or n.lineno > best[0]):
                    best = (n.lineno, v)
        return best[1] if best else None

    def walk(node, fn):
        for ch in ast.iter_child_nodes(node):
            nfn = ch if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
            if isinstance(ch, ast.Call) and isinstance(ch.func, ast.Attribute) and ch.func.attr == "replace" and len(ch.args) >= 2:
                a0, a1 = ch.args[0], ch.args[1]
                new = None
                try:
                    new = ast.literal_eval(a1)
                except Exception:
                    if isinstance(a1, ast.Name):
                        new = literal_of(fn or mod, a1.id, ch.lineno)
                try:
                    old = ast.literal_eval(a0)
                except Exception:
                    old = literal_of(fn or mod, a0.id, ch.lineno) if isinstance(a0, ast.Name) else None
                out[ch.lineno] = (fn.name if fn else "<module>", new if isinstance(new, str) else None,
                                  old if isinstance(old, str) else None, lines[ch.lineno - 1].strip()[:110])
            walk(ch, nfn)
    walk(mod, None)
    # OPTIN defs: every call to the def sits right under an RS64_ env check
    defs = {n.name for n in ast.walk(mod) if isinstance(n, ast.FunctionDef)}
    optin = set()
    for d in defs:
        calls = [i for i, x in enumerate(lines) if re.search(r"\b" + d + r"\(", x) and not x.lstrip().startswith("def ")]
        if calls and all(any('os.environ.get("RS64_' in lines[c - k] for k in range(4)) for c in calls):
            optin.add(d)
    return out, optin


def distinctive(new, old):
    """Added lines of new (not in old), longest first, non-trivial."""
    oldl = set((old or "").split("\n"))
    cand = [l.strip() for l in new.split("\n") if l.strip() and l not in oldl and not TRIVIAL.match(l) and len(l.strip()) >= 12]
    return sorted(set(norm(c) for c in cand), key=lambda x: (-len(x), x))


def norm(t):
    """Undo the s7580 unsigned-LUI rewrite (fixup_lui_unsigned runs last: `0X8013 << 16` -> `0X8013u << 16`)."""
    return t.replace("u << 16", " << 16").replace("U << 16", " << 16")


def load_tree(d):
    return norm("\n".join(f.read_text(errors="surrogateescape") for f in sorted(pathlib.Path(d).iterdir()) if f.is_file()))


def main(a):
    if a[:1] == ["--child"]:
        run_instrumented(a[1], a[2]); return 0
    live = pathlib.Path(a[a.index("--live") + 1]) if "--live" in a else ROOT.parent / "N64Recomp" / "RecompiledFuncs"
    tmp = pathlib.Path(a[a.index("--keep") + 1]) if "--keep" in a else pathlib.Path(tempfile.mkdtemp(prefix="s7789"))
    pr, work, rj = tmp / "pristine", tmp / "work", tmp / "sites.json"
    if not rj.exists() or "--rerun" in a:
        for d in (pr, pathlib.Path(str(pr) + ".work"), work):
            shutil.rmtree(d, ignore_errors=True)
        if "--pristine" in a:  # s7719 gate: reuse its fresh N64Recomp output
            shutil.copytree(a[a.index("--pristine") + 1], work)
        else:
            r = subprocess.run(["zsh", "tools/regen_front.sh", str(pr)], cwd=ROOT, capture_output=True, text=True)
            if r.returncode:
                print("CHAIN-FAIL regen_front", r.stdout[-300:]); return 3
            shutil.copytree(pr, work)
        env = dict(os.environ); env.pop("RS64_REPLAY_TRACE", None)
        r = subprocess.run([sys.executable, __file__, "--child", str(work), str(rj)], cwd=ROOT, env=env,
                           capture_output=True, text=True)
        (tmp / "vendored.log").write_text(r.stdout + r.stderr)
        if r.returncode or not rj.exists():
            print("CHAIN-FAIL vendored rc", r.returncode, (r.stdout + r.stderr)[-400:]); return 3
    rec = json.load(open(rj))
    sites, optin = static_sites()
    tree = load_tree(live)
    wtree = load_tree(work)  # the vendored fixer's own output (this run): text present here but not live = removed later
    stripped = re.compile(re.search(r'TAGS = r"([^"]+)"', (ROOT / "tools" / "strip_diag_layers.py").read_text()).group(1))
    rows, counts, wpres = [], {}, []
    vsrc = VEND.read_text().split("\n")

    def tag_of(line):
        for k in range(line - 1, max(0, line - 400), -1):
            m = re.search(r"#\s*(s\d{3,4}[a-z]?)\b", vsrc[k - 1])
            if m:
                return m.group(1)
        return "?"
    for line, (fn, snew, sold, srcl) in sorted(sites.items()):
        e = rec.get(f"replace:{line}")
        st = "NOTCALLED" if not e else ("HIT" if e["hits"] else "MISS")
        new = (e or {}).get("new") or snew
        old = (e or {}).get("old") or sold
        pres = "-"
        probe = ""
        if st != "HIT" and fn in optin:
            st += "/OPTIN"
        else:
            if new is None:
                pres = "DYNTEXT"
            elif stripped.search(new):
                pres = "STRIPPED"  # strip_diag_layers removes it on purpose (diagnostic layer)
            else:
                d = distinctive(new, old)
                if not d:
                    pres = "NOADD"
                else:
                    probe = d[0]
                    n = sum(x in tree or x in wtree for x in d[:3])
                    pres = "PRESENT" if n == len(d[:3]) else ("PART" if n else "ABSENT")
                    if st == "HIT":  # control datum: the replay emitted it, so the measure must find it in its own output
                        wpres.append(all(x in wtree for x in d[:3]))
        counts[(st, pres)] = counts.get((st, pres), 0) + 1
        rows.append(dict(line=line, tag=tag_of(line), fn=fn, st=st, pres=pres, probe=probe[:120], src=srcl, calls=(e or {}).get("calls", 0)))
    # controls
    ok = True
    hp, nh = sum(wpres), len(wpres)
    c1 = nh >= 100 and hp >= 0.95 * nh  # the presence measure must see what the replay demonstrably emitted
    s517 = [r for r in rows if r["src"].startswith("text = text.replace(_heaplistdeq_attr_write_old")]
    c2 = len(s517) == 1 and s517[0]["st"] == "NOTCALLED" and s517[0]["pres"] == "ABSENT"
    print(f"control HIT-sites PRESENT in the replay's own output: {hp}/{nh} {'PASS' if c1 else 'FAIL'}")
    print(f"control s517 NOTCALLED+ABSENT: {'PASS' if c2 else 'FAIL'} {[(r['st'], r['pres']) for r in s517]}")
    ok = c1 and c2
    opn = 0
    for r in rows:
        if r["st"] == "HIT" or r["pres"] not in ("ABSENT", "PART", "DYNTEXT"):
            continue
        key = f"tag={r['tag']} {r['fn']} | {r['src']} | {r['probe']}"
        rv = next((v for k, v in REVIEWED if re.search(k, key)), None)
        opn += rv is None and "OPTIN" not in r["st"]
        if rv is None or "--all" in a:
            print(f"{r['st']:14s} {r['pres']:10s} L{r['line']} {r['tag']} {r['fn']} | {r['src'][:70]} | {r['probe'][:90]}"
                  + (f" | REVIEWED: {rv}" if rv else ""))
    if "--json" in a:
        json.dump(rows, open(a[a.index("--json") + 1], "w"), indent=0)
    print("sites=%d " % len(rows) + " ".join(f"{s}:{p}={n}" for (s, p), n in sorted(counts.items())) + f" open={opn}")
    if "--keep" not in a:
        shutil.rmtree(tmp, ignore_errors=True)
    return 3 if not ok else (1 if opn else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
