#!/usr/bin/env python3
"""s6871: what is the tail of each function whose ELF size runs past its toml size? make_elf sizes to the next symbol, so the
bytes between the toml end and the ELF end are real code, an unnamed function, or data. Walks the ELF bytes from the entry
(independent of the generated C that fixup_cut_decoded_tails.py walks), then lists every jal/j, branch, data word and
lui+addiu/ori pair that lands in the tail, split by whether the source sits in live code (inside some function's toml range,
outside every tail). Overlays share vram, so a source only counts from its own section or from resident .text.
Controls: addresses known to be called or taken as pointers must hit, or a zero on the tails means nothing.
usage: audit_elf_tails.py <elf> <syms toml> [--min 0x20] [--controls a,b,...] [--json out]"""
import argparse, json, re, struct, subprocess, sys

RESIDENT = ('.entry', '.text')


def sections(path):
    d = open(path, 'rb').read()
    shoff, = struct.unpack_from('>I', d, 32)
    shentsize, shnum, shstr = struct.unpack_from('>HHH', d, 46)
    raw = [struct.unpack_from('>IIIIII', d, shoff + i * shentsize) for i in range(shnum)]
    names = d[raw[shstr][4]:raw[shstr][4] + raw[shstr][5]]
    out = {}
    for i, (nm, typ, _f, addr, off, size) in enumerate(raw):
        if typ == 1 and size and addr >= 0x80000000:
            n = names[nm:names.index(b'\0', nm)].decode()
            out[i] = (n, addr, struct.unpack(f'>{size // 4}I', d[off:off + size - size % 4]))
    return out


def elf_funcs(path):
    out = []
    for l in subprocess.check_output(['mips64-elf-readelf', '-sW', path], text=True).splitlines():
        p = l.split()
        if len(p) >= 8 and p[3] == 'FUNC' and p[6].isdigit():
            out.append((p[7], int(p[1], 16), int(p[2]), int(p[6])))
    return out


def toml_syms(path):
    """{section name: {vram: (name, size)}}: the overlays share vram, so an address alone names nothing."""
    out, sec = {}, None
    for l in open(path):
        m = re.match(r'name = "([^"]+)"', l)
        if m:
            sec = out.setdefault(m.group(1), {})
        m = re.search(r'name = "([^"]+)", vram = (0x[0-9A-Fa-f]+), size = (0x[0-9A-Fa-f]+)', l)
        if m:
            sec[int(m.group(2), 16)] = (m.group(1), int(m.group(3), 16))
    return out


def branch(w, pc):
    """target of a conditional or always branch, else None; second value: it cannot fall through."""
    op, rs, rt = w >> 26, (w >> 21) & 31, (w >> 16) & 31
    off = (w & 0xFFFF) - (0x10000 if w & 0x8000 else 0)
    t = (pc + 4 + off * 4) & 0xFFFFFFFF
    if op in (4, 20):
        return t, rs == 0 and rt == 0
    if op in (5, 21):
        return (None, False) if rs == rt else (t, False)
    if op in (6, 7, 22, 23):
        return t, op in (6, 22) and rs == 0
    if op == 1 and rt in (0, 1, 2, 3, 16, 17, 18, 19):
        return t, rs == 0 and rt in (1, 3, 17, 19)
    if op == 17 and rs == 8:
        return t, False
    return None, False


def walk(words, base, entry, end):
    """(pcs reached, register jumps other than jr ra, cut off at a break/eret)"""
    seen, regj, work = set(), [], [entry]
    get = lambda pc: words[(pc - base) >> 2]
    while work:
        pc = work.pop()
        while entry <= pc < end and pc not in seen:
            seen.add(pc)
            w = get(pc)
            op, fn = w >> 26, w & 63
            t, always = branch(w, pc)
            if t is not None:
                seen.add(pc + 4)
                work.append(t)
                if always:
                    break
                pc += 8
                continue
            if op == 2:
                seen.add(pc + 4)
                work.append((pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2))
                break
            if op == 0 and fn == 8:
                seen.add(pc + 4)
                if (w >> 21) & 31 != 31:
                    regj.append(pc)
                break
            if w == 0x42000018 or (op == 0 and fn == 13):
                break
            pc += 4
    return seen, regj


def refs(words, base, lo_hi):
    """yield (source pc, kind, target) for targets inside any range of lo_hi (sorted (lo, hi))"""
    inside = lambda a: any(lo <= a < hi for lo, hi in lo_hi)
    for i, w in enumerate(words):
        pc, op = base + i * 4, w >> 26
        if inside(w):
            yield pc, 'word', w
        if op in (2, 3):
            t = (pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
            if inside(t):
                yield pc, 'jal' if op == 3 else 'j', t
        t, _ = branch(w, pc)
        if t is not None and inside(t):
            yield pc, 'branch', t
        if op == 0x0F:
            hi, reg = w & 0xFFFF, (w >> 16) & 31
            for x in words[i + 1:i + 17]:
                xo = x >> 26
                if xo in (9, 13, 8) and (x >> 21) & 31 == reg:
                    lo = x & 0xFFFF
                    v = (hi << 16) | lo if xo == 13 else ((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo)) & 0xFFFFFFFF
                    if inside(v):
                        yield pc, 'lui', v


def verdict(r):
    """pad: all zero. H-data: nothing enters the function and nothing but lui pairs lands in the tail; lui pairs are what data
    looks like (audioCompandS16's table has 240). H-real: the entry is entered and the walk runs into the tail. H-unnamed: a
    call, branch, pointer word or toml symbol lands in the tail. A walk from an entry nothing reaches proves nothing: it is
    decoded data, and the jr ra words in those tails are RSP code, which keeps no stack frame."""
    hard = [x for x in r['refs'] if x[4] and x[2] in ('jal', 'j', 'branch', 'word') and not x[5]]
    if r['nop_only']:
        return 'pad'
    if r['tail_walked'] and r['entry_refs']:
        return 'H-real'
    if hard or r['toml_inside']:
        return 'H-unnamed'
    return 'H-data'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('elf')
    ap.add_argument('toml')
    ap.add_argument('--min', type=lambda s: int(s, 0), default=0x20)
    ap.add_argument('--controls', default='')
    ap.add_argument('--json')
    a = ap.parse_args()
    secs, funcs, toml = sections(a.elf), elf_funcs(a.elf), toml_syms(a.toml)
    rows = []
    live = {}  # toml body of every function; data_gap_ ranges are not known to be code
    for name, addr, size, shndx in funcs:
        if shndx not in secs:
            continue
        t = toml.get(secs[shndx][0], {}).get(addr)
        if t and size - t[1] >= a.min:
            rows.append(dict(name=name, entry=addr, elf=size, toml=t[1], tname=t[0], shndx=shndx))
        if not (t and t[0].startswith('data_gap_')):
            live.setdefault(shndx, []).append((addr, addr + (t[1] if t else size)))
    is_live = lambda sh, pc: any(lo <= pc < hi for lo, hi in live.get(sh, ()))
    ctrl = [int(x, 16) for x in a.controls.split(',') if x]
    for r in rows:
        sh = r['shndx']
        sn, base, words = secs[sh]
        lo, hi = r['entry'] + r['toml'], r['entry'] + r['elf']
        r.update(section=sn, lo=lo, hi=hi)
        seen, regj = walk(words, base, r['entry'], hi)
        r['walk_end'] = max(seen) + 4
        r['regj'] = regj
        r['tail_walked'] = sum(lo <= p < hi for p in seen)
        tw = words[(lo - base) >> 2:(hi - base) >> 2]
        r['nop_only'] = not any(tw)
        r['jr_ra'] = sum(w == 0x03E00008 for w in tw)
        r['frames'] = sum(w >> 16 == 0x27BD and w & 0x8000 != 0 for w in tw)
        r['toml_inside'] = sorted((hex(v), n[0]) for v, n in toml.get(sn, {}).items() if lo <= v < hi)
        ext = []
        for s2, (n2, b2, w2) in secs.items():
            if s2 != sh and n2 not in RESIDENT and sn not in RESIDENT:
                continue
            for pc, kind, t in refs(w2, b2, [(lo, hi)]):
                if s2 == sh and r['entry'] <= pc < hi:
                    continue
                # A resident jal names a vram, not an overlay: it belongs to whichever overlay has a symbol there.
                other = n2 in RESIDENT and sn not in RESIDENT and any(t in v for k, v in toml.items() if k != sn and k not in RESIDENT)
                ext.append((hex(pc), n2, kind, hex(t), is_live(s2, pc), other))
        r['refs'] = ext
        r['entry_refs'] = sum(1 for s2, (n2, b2, w2) in secs.items() if s2 == sh or n2 in RESIDENT or sn in RESIDENT
                              for _ in refs(w2, b2, [(r['entry'], r['entry'] + 4)]))
    cres = {}
    for c in ctrl:
        n = 0
        for s2, (n2, b2, w2) in secs.items():
            n += sum(1 for _ in refs(w2, b2, [(c, c + 4)]))
        cres[hex(c)] = n
    for r in sorted(rows, key=lambda r: -(r['elf'] - r['toml'])):
        r['verdict'] = verdict(r)
        k = {}
        for x in r['refs']:
            if x[4]:
                k[x[2]] = k.get(x[2], 0) + 1
        hard = [x[:4] for x in r['refs'] if x[4] and x[2] in ('jal', 'j', 'branch', 'word') and not x[5]]
        print(f"{r['verdict']:9} {r['name']} {r['section']} {r['entry']:08X} toml_end {r['lo']:08X} elf_end {r['hi']:08X} tail {r['hi'] - r['lo']:#x} walk_end {r['walk_end']:08X} "
              f"entry_refs {r['entry_refs']} walked {r['tail_walked']} jr_ra {r['jr_ra']} frames {r['frames']} toml_inside {[x[1] for x in r['toml_inside']][:5]} live_refs {k} {hard[:4]}")
    print('controls', cres)
    if a.json:
        json.dump(dict(rows=rows, controls=cres), open(a.json, 'w'), indent=0)
    return 0 if all(cres.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
