"""s7489 class EN: census of every guest store form in RecompiledFuncs and whether it reaches rs64_s7475_store.

For each `// 0xPC: <op>` store instruction the generated text up to the next `// 0x` comment is scanned for the hook that
feeds the s7475 freed-block / canary-slack bitmap test:
  RS64_S5798_ST(...)        -> rs64_s5798_st -> rs64_s7475_store   (s5798 STORE_DIAG macro, sw/sh/sb/sd/...)
  rs64_s7488_ust(...)       -> rs64_s7475_store                    (s7488 swl/swr wrapper)
data_gap_* bodies, do_break traps and cache ops are counted separately as not-live. Prints a table: form, sites, hooked, hook names, and up to 5 unhooked pcs per form. Exit 0 = every store site hooked
(H-paths-covered), 1 = some form has unhooked live sites."""
import re, sys, collections
from pathlib import Path
D = Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
STORES = {"sb","sh","sw","sd","swl","swr","sdl","sdr","sc","scd","swc1","sdc1","swc2","sdc2","sdc3","cache"}
HOOKS = {"s5798": re.compile(r"RS64_S5798_ST\("), "s7488": re.compile(r"RS64_S7488_UST\(")}
CMT = re.compile(r"^\s*// (0x[0-9A-Fa-f]{8}): (\w+)\b(.*)$")
tot = collections.Counter(); hk = collections.Counter(); un = collections.defaultdict(list); hookn = collections.defaultdict(collections.Counter); dead = collections.Counter()
for p in sorted(D.glob("funcs_*.c")):
    lines = p.read_text().split("\n"); i = 0; n = len(lines); fn = ""
    while i < n:
        f = re.match(r"^RECOMP_FUNC void (\w+)\(", lines[i])
        if f: fn = f.group(1)
        m = CMT.match(lines[i])
        if not m or m.group(2) not in STORES:
            i += 1; continue
        pc, op = m.group(1), m.group(2); j = i + 1; body = []
        while j < n and not CMT.match(lines[j]) and not lines[j].startswith("}"):
            body.append(lines[j]); j += 1
        # a delay-slot store sits inside the branch's block: its statement precedes the branch; take the first statement only
        txt = "\n".join(body)
        if fn.startswith("data_gap_"): dead["data_gap"] += 1; i = j; continue   # data decoded as code: never executed
        if "do_break(" in txt: dead["trap:" + op] += 1; i = j; continue        # recompiler emits a trap, not a store
        if op == "cache": dead["cache_noop"] += 1; i = j; continue             # cache op: no RDRAM write
        tot[op] += 1
        names = [k for k, r in HOOKS.items() if r.search(txt)]
        if names:
            hk[op] += 1
            for k in names: hookn[op][k] += 1
        else:
            un[op].append((pc, p.name, (body[0].strip() if body else "")[:90]))
        i = j
bad = 0
print(f"{'form':6} {'sites':>6} {'hooked':>6}  hooks / first unhooked")
for op in sorted(tot, key=lambda o: -tot[o]):
    u = tot[op] - hk[op]; bad += u
    print(f"{op:6} {tot[op]:6} {hk[op]:6}  {dict(hookn[op])}")
    for pc, f, s in un[op][:40 if op in ("sw","sh","sb","sd","swl","swr") else 3]: print(f"         unhooked {pc} {f}: {s}")
print("not-live:", dict(dead))
print("unhooked_total=%d verdict=%s" % (bad, "H-paths-covered" if bad == 0 else "GAP"))
sys.exit(0 if bad == 0 else 1)
