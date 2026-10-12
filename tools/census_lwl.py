#!/usr/bin/env python3
"""Census of lwl/lwr (do_lwl/do_lwr) in generated code: pair each lwl with its
lwr (same dst, same base, offsets k and k+3 in either order, within 3 sites),
then check whether the assembled dst is used as a memory-address base within
the next few statements (pointer reconstruction) or only stored/consumed."""

from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CALL = re.compile(r"ctx->r(\d+) = do_(lw[lr])\(rdram, ctx->r(\d+), ctx->r(\d+), (-?0[xX][0-9A-Fa-f]+|-?\d+)\)")
FUNCTION = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")


def is_stmt(line):
    s = line.strip()
    return bool(s) and not s.startswith("//")


def main():
    n_l = n_r = 0
    sites = []
    cache = {}
    for p in sorted(ROOT.glob("funcs_*.c")):
        lines = p.read_text(errors="replace").splitlines()
        cache[p.name] = lines
        cur = ""
        for i, line in enumerate(lines):
            m = FUNCTION.search(line)
            if m:
                cur = m.group(1)
            m = CALL.search(line)
            if not m:
                continue
            if m.group(2) == "lwl":
                n_l += 1
            else:
                n_r += 1
            sites.append((p.name, i, cur, m.group(2), int(m.group(1)), int(m.group(3)), int(m.group(4)), int(m.group(5), 0)))
    paired = set()
    used = []
    for k, s in enumerate(sites):
        if k in paired:
            continue
        for j in range(k + 1, min(k + 4, len(sites))):
            t = sites[j]
            if j in paired or t[0] != s[0] or t[2] != s[2] or t[1] - s[1] > 8:
                continue
            if {s[3], t[3]} == {"lwl", "lwr"} and s[4] == t[4] and s[6] == t[6]:
                l, r = (s, t) if s[3] == "lwl" else (t, s)
                if r[7] - l[7] == 3:
                    paired.add(k)
                    paired.add(j)
                    lines = cache[s[0]]
                    nxt = [x.strip() for x in lines[t[1] + 1:t[1] + 12] if is_stmt(x)][:4]
                    d = re.escape(f"ctx->r{s[4]}")
                    addr_re = re.compile(rf"\b(?:MEM_\w+|LD|S[WDBH]|SDC1|SWC1|LWC1)\(\s*{d}\s*,|\b(?:MEM_\w+|LD|S[WDBH]|SDC1|SWC1|LWC1)\(\s*[^,()]*,\s*{d}\s*[,)]|= *{d} *\+")
                    addr = any(addr_re.search(x) for x in nxt)
                    used.append((s[0], s[1] + 1, s[2], f"r{s[4]}", addr, nxt[:2]))
                    break
    orphans = [s for k, s in enumerate(sites) if k not in paired]
    print(f"lwl={n_l} lwr={n_r} pairs={len(paired) // 2} orphans={len(orphans)}")
    assert 2 * (len(paired) // 2) + len(orphans) == n_l + n_r
    ptr = [u for u in used if u[4]]
    print(f"pairs_dst_used_as_address_base={len(ptr)}")
    for u in ptr:
        print("PTR?\t" + "\t".join(map(str, u[:4])), u[5])
    for o in orphans:
        print("ORPHAN\t", o[:4], o[4:])


if __name__ == "__main__":
    main()
