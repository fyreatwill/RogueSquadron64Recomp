#!/usr/bin/env python3
"""s7790: prune confirmed-dead inline blocks from tools/fixup_game_funcs_vendored.py.

Input: the s7789 census rows (--json) re-scored with its REVIEWED table. A block is a direct child statement of the
vendored fixer's big `for p in ...:` loop. It is deleted when every `.replace` site it holds is a NOTCALLED/MISS row whose
review is RETIRED (s109 + s390-s568 item -317 lineage) or the matching DYNTEXT lineage row, and none of the names it binds
(other than text/changed/report bookkeeping) is read by a statement that survives. Then loop-level and module-level
assignments / defs whose names are read only by deleted statements are deleted too (iterated to a fixpoint).
The leading comment lines between the previous surviving statement and a deleted block go with it.
The s517 HEAPLISTDEQ_ATTR_WRITE site is kept: it is the s7789 census's NOTCALLED+ABSENT control.
Usage: s7790_prune_dead_blocks.py <rows.json> [--shadowed] [--write] [--list]   (dry run prints the plan)
--shadowed (s7791): also count NOTCALLED+PRESENT rows (the block never ran; its distinctive added text is already in the
replay's output from an earlier route, so it only ever skipped on its own idempotence marker) as dead. OPTIN rows are
'NOTCALLED/OPTIN' and never qualify; blocks reading os.environ are kept as before. --list prints each deleted block's span
and first guard line for spot review.
Proof is external: tools/s7719_regen_gate.py --strict (replay byte-identical) + the s7789 census.
"""
import ast, importlib.util, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VEND = ROOT / "tools" / "fixup_game_funcs_vendored.py"
BOOK = {"text", "changed", "report", "p", "n", "_old", "_new"}


def main(a):
    spec = importlib.util.spec_from_file_location("c", ROOT / "tools" / "s7789_replace_site_census.py")
    cen = importlib.util.module_from_spec(spec); spec.loader.exec_module(cen)
    rows = json.load(open(a[0]))
    dead = set()
    allsites = set()
    ran = set()  # sites that executed in the pristine replay (HIT or MISS): a block holding one is not inert
    for r in rows:
        allsites.add(r["line"])
        if r["st"] in ("HIT",) or r.get("calls"):
            ran.add(r["line"])
        if r["st"] not in ("NOTCALLED", "MISS") or r["pres"] not in ("ABSENT", "PART", "DYNTEXT"):
            continue
        if r["src"].startswith("text = text.replace(_heaplistdeq_attr_write_old"):
            continue  # census control
        key = f"tag={r['tag']} {r['fn']} | {r['src']} | {r['probe']}"
        rv = next((v for k, v in cen.REVIEWED if re.search(k, key)), "")
        if rv.startswith("RETIRED") or rv.startswith("DYNTEXT"):
            dead.add(r["line"])
    if "--shadowed" in a:  # s7791: never-run sites whose added text the replay emits via another (earlier) route
        for r in rows:
            if r["st"] == "NOTCALLED" and r["pres"] == "PRESENT":
                dead.add(r["line"])
    src = VEND.read_text()
    lines = src.split("\n")
    tree = ast.parse(src)
    loop = max((s for s in tree.body if isinstance(s, ast.For)), key=lambda s: s.end_lineno - s.lineno)
    body = loop.body

    def sites_in(s):
        return {n.lineno for n in ast.walk(s) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "replace" and n.lineno in allsites}

    def stores(s):
        out = set()
        for n in ast.walk(s):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                out.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)):
                out.add(n.name)
        return out

    def loads(s):
        return {n.id for n in ast.walk(s) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}

    srcs = {r["line"]: r["src"] for r in rows}

    def shadow_ok(s, st):
        """s7791: a never-run .replace inside a block is evidence only for its own branch. The block may be dropped only if
        (1) >=1 dead site is not a bare `#include` add (those skip whenever the include exists, whatever the block did),
        (2) every mutation of a non-local in it is a dead .replace site: no `text = new`, slicing, subn/sub, write, etc.,
        (3) it is not the s7789 census-control block (s517 HEAPLISTDEQ_ATTR_WRITE)."""
        if not any("#include" not in srcs.get(l, "") for l in st & dead):
            return False
        for n in ast.walk(s):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                if n.func.attr in ("sub", "subn", "write_text", "write", "insert", "extend", "update", "pop", "remove"):
                    return False
                if n.func.attr == "replace" and isinstance(n.func.value, ast.Name) and "_heaplistdeq_attr_write_old" in ast.unparse(n):
                    return False
            if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tg = n.targets if isinstance(n, ast.Assign) else [n.target]
                names = {t.id for t in tg if isinstance(t, ast.Name)}
                if any(not isinstance(t, ast.Name) for t in tg):
                    return False  # subscript / attribute / tuple store
                if "text" in names or "body" in names or "src" in names:
                    v = n.value
                    if not (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == "replace"
                            and v.lineno in dead):
                        return False
        return True

    # candidate statements: loop-body children + module-level statements (defs / assigns only)
    cand = [(s, "loop") for s in body] + [(s, "mod") for s in tree.body if s is not loop]
    deleted = set()
    for s, where in cand:
        if where == "loop":
            st = sites_in(s)
            seg = "\n".join(lines[s.lineno - 1:s.end_lineno])
            if st & dead and not (st - dead) & ran and "environ" not in seg:
                if "--shadowed" in a and not shadow_ok(s, st):
                    continue
                deleted.add(id(s))
    mixed = [s for s, w in cand if w == "loop" and sites_in(s) & dead and id(s) not in deleted]
    # fixpoint: drop (a) deleted blocks that bind a name a survivor reads (restore them), (b) pure binders read only by deleted
    while True:
        surv = [s for s, _ in cand if id(s) not in deleted]
        live_loads = set().union(*(loads(s) for s in surv))
        # any deleted statement (block or binder) that binds a name a survivor reads comes back
        restore = [s for s, w in cand if id(s) in deleted and (stores(s) - BOOK) & live_loads]
        for s in restore:
            deleted.discard(id(s))
        grew = False
        for s, w in cand:
            if id(s) in deleted or sites_in(s):
                continue
            if not isinstance(s, (ast.Assign, ast.FunctionDef, ast.AnnAssign)):
                continue
            names = stores(s) if not isinstance(s, ast.FunctionDef) else {s.name}
            if not names or names & BOOK:
                continue
            if names & live_loads - (loads(s) if isinstance(s, ast.FunctionDef) else set()):
                # read by a survivor (other than itself)
                others = set().union(*(loads(x) for x in surv if x is not s))
                if names & others:
                    continue
            # only delete binders that something deleted actually read (never unrelated dead code)
            dl = set().union(*(loads(x) for x, _ in cand if id(x) in deleted))
            if names & dl:
                deleted.add(id(s)); grew = True
        if not grew and not restore:
            break
    # line spans (with leading comments / blank lines)
    order = sorted(cand, key=lambda c: c[0].lineno)
    spans = []
    prev_end = {}
    seq = {"loop": [s for s in body], "mod": [s for s in tree.body]}
    for where, ss in seq.items():
        for i, s in enumerate(ss):
            if id(s) not in deleted:
                continue
            start = (s.decorator_list[0].lineno if getattr(s, "decorator_list", None) else s.lineno)
            pe = ss[i - 1].end_lineno if i else (loop.lineno if where == "loop" else 0)
            k = start - 1
            while k - 1 > pe and lines[k - 2].strip().startswith("#"):
                k -= 1
            spans.append((k, s.end_lineno, where, s.lineno, len(sites_in(s))))
    spans.sort()
    covered = set()
    for a0, b0, *_ in spans:
        covered.update(range(a0, b0 + 1))
    kept_dead = sorted(dead - {l for l in dead if l in covered})
    nsites = sum(x[4] for x in spans)
    print(f"dead sites={len(dead)} deleted stmts={len(spans)} (loop={sum(x[2]=='loop' for x in spans)} "
          f"mod={sum(x[2]=='mod' for x in spans)}) sites removed={nsites} lines removed={len(covered)}")
    print(f"dead sites kept (mixed/coupled blocks): {len(kept_dead)} {kept_dead[:20]}")
    for s in mixed:
        print(f"  mixed block L{s.lineno}-{s.end_lineno}: dead {sorted(sites_in(s) & dead)[:5]} live {sorted(sites_in(s) - dead)[:5]}")
    if "--list" in a:
        for a0, b0, where, ln, ns in spans:
            g = next((l.strip() for l in lines[ln - 1:b0] if l.strip().startswith(("if ", "for ", "elif "))), lines[ln - 1].strip())
            print(f"  DEL {where} L{a0}-{b0} sites={ns} | {lines[ln - 1].strip()[:70]} | {g[:90]}")
    if "--write" in a:
        out = [l for i, l in enumerate(lines, 1) if i not in covered]
        VEND.write_text("\n".join(out))
        print(f"wrote {VEND} ({len(lines)} -> {len(out)} lines)")


if __name__ == "__main__":
    main(sys.argv[1:])
