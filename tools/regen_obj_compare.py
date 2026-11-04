#!/usr/bin/env python3
"""s6864: per-function machine-code compare of two sets of Mach-O arm64 objects (live build vs regen tree).
Hashes each function's __text bytes plus the names of the external symbols it references. Debug info, static data
layout, unrelocated adrp pages and the outliner's numbering (its helpers are not compared) do not count, so a function that compares equal runs the same code in both trees.
Usage: regen_obj_compare.py <dirA> <dirB> [out.json]   (objects are matched by basename, recursively)"""
import hashlib, json, pathlib, struct, sys

def funcs(path):
    b = path.read_bytes()
    assert struct.unpack_from("<I", b)[0] == 0xFEEDFACF, path
    ncmds = struct.unpack_from("<I", b, 16)[0]
    off, secs, sym = 32, [], None
    for _ in range(ncmds):
        cmd, size = struct.unpack_from("<II", b, off)
        if cmd == 0x19:
            for i in range(struct.unpack_from("<I", b, off + 64)[0]):
                s = off + 72 + 80 * i
                addr, sz, foff, _a, roff, nrel = struct.unpack_from("<QQIIII", b, s + 32)
                secs.append((b[s:s + 16].rstrip(b"\0"), b[s + 16:s + 32].rstrip(b"\0"), addr, sz, foff, roff, nrel))
        elif cmd == 2:
            sym = struct.unpack_from("<IIII", b, off + 8)
        off += size
    ti = next(i for i, s in enumerate(secs) if s[0] == b"__text" and s[1] == b"__TEXT")
    _n, _g, taddr, tsz, tfoff, roff, nrel = secs[ti]
    symoff, nsyms, stroff, _ = sym
    names, syms = [], []
    for i in range(nsyms):
        strx, typ, sect, _d, val = struct.unpack_from("<IBBHQ", b, symoff + 16 * i)
        e = b.index(b"\0", stroff + strx)
        name = b[stroff + strx:e].decode("latin1")
        names.append(name)
        if not typ & 0xE0 and sect == ti + 1 and not name.startswith(("ltmp", "l_", "L", "_OUTLINED_FUNCTION_")):
            syms.append((val, name))
    syms.sort()
    rel, b = [], bytearray(b)
    for i in range(nrel):
        a, info = struct.unpack_from("<iI", b, roff + 8 * i)
        kind = (info >> 28) & 15
        if kind in (3, 5, 8):  # PAGE21 family: the unrelocated adrp immediate encodes the function's own page
            struct.pack_into("<I", b, tfoff + a, struct.unpack_from("<I", b, tfoff + a)[0] & 0x9F00001F)
        if (info >> 27) & 1 and kind != 10:  # external, not ADDEND
            n = names[info & 0xFFFFFF]
            if not n.startswith(("l_", "ltmp", "L")):
                rel.append((a + taddr, "_OUTLINED" if n.startswith("_OUTLINED_FUNCTION_") else n))
    rel.sort()
    out, r = {}, 0
    for i, (v, n) in enumerate(syms):
        end = syms[i + 1][0] if i + 1 < len(syms) else taddr + tsz
        h = hashlib.sha1(b[tfoff + v - taddr:tfoff + end - taddr])
        while r < len(rel) and rel[r][0] < v:
            r += 1
        q = r
        while q < len(rel) and rel[q][0] < end:
            h.update(rel[q][1].encode()); q += 1
        out[n] = (h.hexdigest(), end - v)
    return out

def main():
    A = {p.name: p for p in pathlib.Path(sys.argv[1]).rglob("funcs_*.o")}
    B = {p.name: p for p in pathlib.Path(sys.argv[2]).rglob("funcs_*.o")}
    res = {"same": 0, "diff": {}, "only_a": {}, "only_b": {}}
    for name in sorted(set(A) & set(B)):
        a, b = funcs(A[name]), funcs(B[name])
        for f in a:
            if f not in b: res["only_a"].setdefault(name, []).append(f)
            elif a[f][0] == b[f][0]: res["same"] += 1
            else: res["diff"].setdefault(name, []).append([f, a[f][1], b[f][1]])
        for f in b:
            if f not in a: res["only_b"].setdefault(name, []).append(f)
    nd = sum(map(len, res["diff"].values()))
    print(f"files {len(set(A) & set(B))} same {res['same']} diff {nd} only_a {sum(map(len, res['only_a'].values()))} only_b {sum(map(len, res['only_b'].values()))}")
    for k, v in sorted(res["diff"].items(), key=lambda x: -len(x[1]))[:12]:
        print(f"  {k}: {len(v)} e.g. {[x[0] for x in v[:4]]}")
    if len(sys.argv) > 3:
        json.dump(res, open(sys.argv[3], "w"), indent=0)

if __name__ == "__main__":
    main()
