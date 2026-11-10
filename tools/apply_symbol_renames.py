#!/usr/bin/env python3
"""s7076: apply a misnomer-rename TSV (old<TAB>new[<TAB>...]) across a set of files with \\b word
matching, replacing the s7072-s7075 scratch recipe (renames.tsv + cnt.py before/after by hand).

Safety checks, all before any write:
  - every new name is a valid C identifier and occurs 0 times in every target file
    (no collision with an existing symbol);
  - no old or new name appears twice in the TSV;
  - every old name occurs at least once somewhere (a stale TSV line is an error).
After writing it re-counts: per file, count(new) must equal the pre-write count(old), and
count(old) must be 0. Lines whose 2nd column is KEEP or empty are skipped.

usage: apply_symbol_renames.py <renames.tsv> [@files.txt | file...] [--dry-run]
       @files.txt = whitespace-separated paths (relative to the cwd).
Default target set when none is given: the live generated sources + symbol files that carry
guest function names (RecompiledFuncs/*.c, funcs.h, recomp_overlays.inl,
../rogue_squadron64/symbol_files/*.txt, syms/rogue_squadron.syms.toml, tools/*.py)."""
import glob, re, sys

IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
# Comments are left untouched and not counted: symbol files keep history notes like
# "(was copyMorphTargetVertices)" that must neither be rewritten nor read as a live collision.
C_COMMENT = re.compile(r'//[^\n]*|/\*.*?\*/', re.S)
H_COMMENT = re.compile(r'#[^\n]*')


def split_code(path, text):
    """[(is_code, chunk), ...] covering text exactly."""
    rx = H_COMMENT if path.endswith(('.toml', '.py')) else C_COMMENT
    out, i = [], 0
    for m in rx.finditer(text):
        out.append((True, text[i:m.start()])); out.append((False, m.group(0))); i = m.end()
    out.append((True, text[i:]))
    return out


def count(path, text, name):
    r = re.compile(r'\b%s\b' % re.escape(name))
    return sum(len(r.findall(c)) for code, c in split_code(path, text) if code)


def subst(path, text, pairs):
    segs = []
    for code, c in split_code(path, text):
        if code:
            for o, n in pairs: c = re.sub(r'\b%s\b' % re.escape(o), n, c)
        segs.append(c)
    return ''.join(segs)


def default_files():
    fs = glob.glob('../N64Recomp/RecompiledFuncs/*.c') + glob.glob('../N64Recomp/RecompiledFuncs/*.h')
    fs += glob.glob('../N64Recomp/RecompiledFuncs/*.inl')
    fs += glob.glob('../rogue_squadron64/symbol_files/*.txt') + ['syms/rogue_squadron.syms.toml']
    fs += [f for f in glob.glob('tools/*.py') if not f.endswith('apply_symbol_renames.py')]
    return sorted(set(fs))


def main(argv):
    dry = '--dry-run' in argv
    argv = [a for a in argv if a != '--dry-run']
    if not argv:
        print(__doc__); return 2
    pairs = []
    for ln in open(argv[0]):
        c = ln.rstrip('\n').split('\t')
        if len(c) < 2 or not c[0].strip() or c[0].startswith('#'): continue
        old, new = c[0].strip(), c[1].strip()
        if not new or new == 'KEEP': continue
        pairs.append((old, new))
    files = []
    for a in argv[1:]:
        files += open(a[1:]).read().split() if a.startswith('@') else [a]
    files = files or default_files()
    err = []
    olds = [p[0] for p in pairs]; news = [p[1] for p in pairs]
    for n in set(olds + news):
        if (olds + news).count(n) > 1: err.append('duplicate name in TSV: ' + n)
    for o, n in pairs:
        if not IDENT.match(n) or not IDENT.match(o): err.append('bad identifier: %s -> %s' % (o, n))
    texts = {f: open(f, errors='surrogateescape').read() for f in files}
    pre = {f: {o: count(f, t, o) for o, _ in pairs} for f, t in texts.items()}
    for o, n in pairs:
        if sum(pre[f][o] for f in files) == 0: err.append('old name not found anywhere: ' + o)
        hit = [f for f, t in texts.items() if count(f, t, n)]
        if hit: err.append('new name already exists: %s in %s' % (n, ', '.join(hit)))
    if err:
        print('\n'.join('ERROR ' + e for e in err)); return 1
    changed = 0
    for f, t in texts.items():
        u = subst(f, t, pairs)
        if u != t:
            changed += 1
            if not dry: open(f, 'w', errors='surrogateescape').write(u)
            texts[f] = u
    bad = 0
    for f, t in texts.items():
        for o, n in pairs:
            a = count(f, t, o); b = count(f, t, n)
            if a != 0 or b != pre[f][o]:
                bad += 1; print('MISMATCH %s %s->%s pre=%d now old=%d new=%d' % (f, o, n, pre[f][o], a, b))
    for o, n in pairs:
        print('%-40s -> %-40s %d sites in %d files' % (o, n, sum(pre[f][o] for f in files),
                                                     sum(1 for f in files if pre[f][o])))
    print('%s: %d renames, %d files changed, %d mismatches' % ('DRY-RUN' if dry else 'APPLIED', len(pairs), changed, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
