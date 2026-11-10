#!/usr/bin/env python3
"""s7090 fixup-layer statement census.

Compares, per function and per guest address, the multiset of retail statements
N64Recomp emits (pristine front-end pass, scratch/s7082/regen) with the live
fixup-patched output (../N64Recomp/RecompiledFuncs). Instrumentation wrappers
are normalised back to the bare statement; diagnostic calls are dropped.

Every (function, address, statement) whose live count != pristine count is
classified:
  patched   - extra copies all come from PATCH-tagged lines, or (for a
              shortfall) a PATCH tag sits inside that address block
  dup       - live count from UNTAGGED lines alone exceeds pristine
  dropped   - live count < pristine, no PATCH tag in the block
  foreign   - extra untagged copy of a statement N64Recomp emits elsewhere in
              this function but not at this address
  moved     - a foreign/dup excess paired with a dropped shortfall of the same
              statement in the same function (a patch swallowed the `// 0x` comment)
  added     - untagged code N64Recomp never emits in this function (body
              lines of multi-line PATCH blocks); listed only with -v

Usage: s7090_fixup_statement_census.py [--pristine DIR] [--live DIR]
       [--file-override funcs_24.c=path.gz] [--only FUNC] [-v]
Controls (s7090): --file-override funcs_24.c=scratch/s7089/funcs_24.pre.c.gz
must report reapplyAudioConfig 0x80091CB0/0x80091CBC as dup.
"""
import argparse, collections, gzip, os, re, sys

FUNC_RE = re.compile(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')
ADDR_RE = re.compile(r'^\s*// 0x([0-9A-F]{8}):')
# PATCH tags, or a session comment like `// s6869: ...` naming the change
TAG_LINE_RE = re.compile(r'PATCH|(?://|/\*)\s*[sS]\d{3,4}\b')
CALL_RE = re.compile(r'^\w+\(rdram, ctx\);$')
# statements that are pure instrumentation (dropped after splitting)
DIAG_RE = re.compile(r'^(?:extern |static |const |rs64_|RS64_|rs\d+_|g_rs64|fprintf|fflush|printf|recomp_printf|'
                     r'(?:u?int\d+_t|unsigned|int|uint64_t|bool|char|double|float) \w+(?:\[\d*\])? ?=|'
                     r'if \(__builtin_expect\(g_rs64|\(void\))')


def opener(p):
    return gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')


def strip_comments(line):
    line = re.sub(r'/\*.*?\*/', '', line)
    i = line.find('//')
    if i >= 0:
        line = line[:i]
    return line.strip()


def split_stmts(s):
    """Split a line into top-level statements, unwrapping one brace level."""
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '{':
            depth += 1
            if depth == 1 and cur.strip() == '':
                cur = ''
                continue
        if ch == '}':
            depth -= 1
            if depth == 0:
                if cur.strip():
                    out.append(cur.strip())
                cur = ''
                continue
        if ch == ';' and depth <= 1:
            out.append(cur.strip() + ';')
            cur = ''
            continue
        cur += ch
    if cur.strip():
        out.append(cur.strip())
    return [x for x in out if x not in (';', '')]


def norm(stmt):
    stmt = re.sub(r'\s+', ' ', stmt).strip()
    if CALL_RE.match(stmt):      # symbol renames between the passes are not defects
        return 'CALL(rdram, ctx);'
    return stmt


def parse(path):
    """-> {funcname: (start_addr, {addr: Counter(stmt)}, {addr: tagged_bool})}"""
    funcs = {}
    name = None
    addr = None
    with opener(path) as f:
        for raw in f:
            m = FUNC_RE.match(raw)
            if m:
                name = m.group(1)
                funcs[name] = [None, collections.defaultdict(collections.Counter), collections.defaultdict(bool), collections.defaultdict(collections.Counter)]
                addr = 'pre'
                pdepth = 0
                continue
            if name is None:
                continue
            if (raw.startswith('}') and not raw.startswith('};')) or raw.startswith(';}'):
                name = None
                continue
            m = ADDR_RE.match(raw)
            if m:
                addr = m.group(1)
                if funcs[name][0] is None:
                    funcs[name][0] = addr
                continue
            fn = funcs[name]
            # a PATCH-tagged line that opens braces tags every line until they close
            code = strip_comments(raw)
            has_tag = bool(TAG_LINE_RE.search(raw))
            tagline = has_tag or pdepth > 0
            if 'g_rs64' in raw or 'rs64_' in raw:   # untagged in-place rewrite (e.g. g_rs64_ww stride)
                fn[2][addr] = True
            if has_tag and pdepth == 0:
                pdepth = max(0, code.count('{') - code.count('}'))
            elif pdepth > 0:
                pdepth = max(0, pdepth + code.count('{') - code.count('}'))
            if tagline:
                fn[2][addr] = True
            body = strip_comments(raw)
            if not body:
                continue
            # a guarded diagnostic line: if (__builtin_expect(g_rs64...)) X;
            if body.startswith('if (__builtin_expect(g_rs64'):
                continue
            for st in split_stmts(body):
                if DIAG_RE.match(re.sub(r"\s+", " ", st).strip()):
                    continue
                st = norm(st)
                if not st:
                    continue
                fn[1][addr][st] += 1
                if not tagline:
                    fn[3][addr][st] += 1
    return funcs


def load_dir(d, overrides):
    res = {}
    for fn in sorted(os.listdir(d)):
        if not re.match(r'funcs_\d+\.c$', fn):
            continue
        p = overrides.get(fn, os.path.join(d, fn))
        for k, v in parse(p).items():
            res[k] = (fn, v)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pristine', default='scratch/s7082/regen')
    ap.add_argument('--live', default='../N64Recomp/RecompiledFuncs')
    ap.add_argument('--file-override', action='append', default=[])
    ap.add_argument('--only')
    ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    ov = dict(x.split('=', 1) for x in a.file_override)
    P = load_dir(a.pristine, {})
    L = load_dir(a.live, ov)
    # key by start address so renames do not matter
    pk = {v[1][0]: (k, v) for k, v in P.items() if v[1][0]}
    lk = {v[1][0]: (k, v) for k, v in L.items() if v[1][0]}
    cls = collections.Counter()
    rows = []
    only_p = sorted(set(pk) - set(lk)); only_l = sorted(set(lk) - set(pk))
    nfun_same = nfun_diff = 0
    extent = []
    for start in sorted(set(pk) & set(lk)):
        pname, (pf, pv) = pk[start]
        lname, (lf, lv) = lk[start]
        if a.only and a.only not in (pname, lname):
            continue
        pa = [int(x, 16) for x in pv[1] if x != 'pre']; la = [int(x, 16) for x in lv[1] if x != 'pre']
        if pa and la and (max(la) > max(pa) + 8 or max(pa) > max(la) + 8):
            extent.append((lname, lf, start, '%X' % max(pa), '%X' % max(la)))
            nfun_diff += 1
            continue
        laddrs = sorted(int(x, 16) for x in set(lv[1]) | set(lv[2]) if x != 'pre')
        diff = False
        ptot = collections.Counter()
        for c in pv[1].values():
            ptot.update(c)
        for addr in sorted(set(pv[1]) | set(lv[1])):
            pc, lc = pv[1].get(addr, collections.Counter()), lv[1].get(addr, collections.Counter())
            tagged = lv[2].get(addr, False)
            for st in sorted(set(pc) | set(lc)):
                if pc[st] == lc[st]:
                    continue
                diff = True
                if st in ('}', '} else {', 'else {', '{'):
                    continue
                if st.endswith(':') and ('goto %s;' % st[:-1]) not in ptot:
                    cls['unref-label'] += 1   # label nothing in this function jumps to
                    continue
                if lc[st] > pc[st]:
                    lu = lv[3].get(addr, collections.Counter())[st]
                    if lu <= pc[st]:
                        kind = 'patched'
                    elif pc[st] >= 1:
                        kind = 'dup'
                    elif ptot[st]:
                        kind = 'foreign'   # retail stmt from another address of this function
                    else:
                        kind = 'added'     # code N64Recomp never emits in this function
                else:
                    kind = 'patched' if tagged else 'dropped'
                    if kind == 'dropped' and addr != 'pre' and addr not in lv[1] and addr not in lv[2]:
                        # the whole `// 0x` block is gone: replaced if the preceding live block is tagged
                        prev = [x for x in laddrs if x < int(addr, 16)]
                        if prev and lv[2].get('%08X' % prev[-1], False):
                            kind = 'patched'
                cls[kind] += 1
                rows.append((kind, lname, lf, addr, pc[st], lc[st], st))
        # pair foreign excess with dropped shortfall of the same statement: comment-attribution shift
        fr = [r for r in rows if r[1] == lname and r[0] in ('foreign', 'dropped', 'dup')]
        for i, r in enumerate(fr):
            if r[0] not in ('foreign', 'dup'):
                continue
            for q in [x for x in rows if x[1] == lname and x[0] in ('dropped', 'patched') and x[4] > x[5]]:
                if q[6] == r[6]:
                    idx_r, idx_q = rows.index(r), rows.index(q)
                    rows[idx_r] = ('moved',) + r[1:]; rows[idx_q] = ('moved',) + q[1:]
                    cls[r[0]] -= 1; cls[q[0]] -= 1; cls['moved'] += 2
                    fr = [x for x in rows if x[1] == lname and x[0] in ('foreign', 'dropped', 'dup')]
                    break
        nfun_diff += diff; nfun_same += not diff
    print(f'functions: pristine={len(P)} live={len(L)} matched-by-start={len(set(pk)&set(lk))} '
          f'identical={nfun_same} differing={nfun_diff} only-pristine={len(only_p)} only-live={len(only_l)}')
    print('classes:', dict(cls))
    for r in rows:
        if r[0] not in ('patched', 'added') or a.v:
            print('%-8s %s %s 0x%s pristine=%d live=%d | %s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6][:200]))
    print('extent-mismatch (function sized differently by the two passes; not compared): %d' % len(extent))
    for e in extent:
        print('  extent %s %s start=%s pristine-max=0x%s live-max=0x%s' % e)
    if only_p:
        print('only-pristine starts:', ' '.join(f'{pk[s][0]}@{s}' for s in only_p[:40]))
    if only_l:
        print('only-live starts:', ' '.join(f'{lk[s][0]}@{s}' for s in only_l[:40]))
    return 1 if (cls['dup'] or cls['dropped'] or cls['foreign']) else 0


if __name__ == '__main__':
    sys.exit(main())
