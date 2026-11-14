#!/usr/bin/env python3
"""s7364 class AO census: host buffers whose extent is a RUNTIME value (std::vector / std::deque / std::string / std::span,
raw pointers from new T[n] / malloc / calloc / realloc / aligned_alloc / make_unique<T[]>), and every subscript
`name[expr]`, `name.data()[expr]`, `name.data() + expr`, plus memcpy/memmove/memset ranges that touch one.

Row classes:
  FIXED-<AN class>  the buffer's extent is a provable constant N (constant-size alloc, or a vector built with (N) and never
                    resized / pushed / cleared in the file): the s7363 classifier proves expr < N (CONST/MASK/LOOP/...).
  LOOP              an enclosing for whose bound is `name.size()` / `.length()` (or a local assigned from it, or the counter
                    runs down from it) for the index expression.
  SIZECHK           a dominating `E < name.size()` / `name.size() > E` (positive) or `E >= name.size()` -> return/continue/
                    break/throw (negative), E == the index expression (or E+1 <= / <= size()-1 forms).
  GROWN             the buffer was resized to cover the index in this function (`name.resize(E + k)`, `idx = name.size();`
                    followed by push_back/emplace_back/resize), or the index is `name.size() - k` under a non-empty check.
  LIT               a literal index into a buffer this function sized/filled or checked non-empty first (host-only).
  SIZED (memcpy)    the length is `name.size()` / sizeof / a FIXED extent; otherwise B.
  B-GUEST / B-PARAM / B-CTR / B-HOST   unproven; the suffix is the index taint (guest source, a function parameter,
                    a host post-increment counter, host-only). Every B row needs a hand verdict in s7364_heapbuf_reviewed.tsv.
`--check` exits 1 on an unreviewed B. `--selftest` runs planted rows of every class.
"""
import re, sys, os, glob
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7363_hostarr_census as an

TPL = r'<(?:[^<>]|<(?:[^<>]|<[^<>]*>)*>)*>'
VECDECL = re.compile(r'\b(?:std::)?(vector|deque|basic_string\s*' + TPL + r'|string|u16string|u32string|wstring|span|array_view)'
                     r'\s*(' + TPL + r')?\s*(?:const\s*)?[&*]?\s*(?:const\s+)?([A-Za-z_]\w*)\s*(?=[;={(,)\[]|$)', re.M)
ALLOC = re.compile(r'\b([A-Za-z_]\w*)\s*(?:=|\()\s*(?:\(\s*[\w:<>\s]+\*\s*\)\s*|static_cast\s*<[^>]*>\s*\(\s*|reinterpret_cast\s*<[^>]*>\s*\(\s*)?'
                   r'(?:std::)?(malloc|calloc|realloc|aligned_alloc|new\s+[\w:<>]+\s*\[|make_unique\s*<\s*[\w:<>\s*]+\[\s*\]\s*>)\s*\(?([^;]*)')
UPTR = re.compile(r'\bstd::unique_ptr\s*<\s*([\w:<>\s*]+)\[\s*\]\s*>\s*([A-Za-z_]\w*)')
MUT = r'(?:push_back|emplace_back|resize|clear|erase|insert|assign|pop_back|swap|reserve|shrink_to_fit|emplace|append)'
ELSZ = {'uint8_t': 1, 'char': 1, 'u8': 1, 'int8_t': 1, 'uint16_t': 2, 'int16_t': 2, 'u16': 2, 'uint32_t': 4, 'int32_t': 4, 'u32': 4,
        'int': 4, 'float': 4, 'uint64_t': 8, 'int64_t': 8, 'double': 8}

def collect(t, consts):
    """name -> list of (start, scope_end, kind, const_extent_or_None, member?)"""
    out = {}
    for m in VECDECL.finditer(t):
        name = m.group(3)
        if name in an.NOTTYPE or name in ('const', 'operator', 'value_type', 'size_type', 'iterator'):
            continue
        pre = t[max(0, m.start() - 30):m.start()]
        if re.search(r'(?:::|\.|->)\s*$', pre) and not re.search(r'std::\s*$', pre):
            continue
        n = None
        after = t[m.end():m.end() + 80]
        cm = re.match(r'\s*[({]\s*([^,(){}]+?)\s*[,)}]', after)
        if cm and m.group(1) == 'vector' and not re.search(r'[;}]', t[m.end():m.end() + cm.end()]):
            v = an.ival(cm.group(1), consts)
            if v is not None and v > 0 and not after.lstrip().startswith('{'):
                n = v
        out.setdefault(name, []).append((m.start(3), an.block_end(t, m.start(3)), 'VEC', n, an.in_struct(t, m.start(3))))
    for m in UPTR.finditer(t):
        out.setdefault(m.group(2), []).append((m.start(2), an.block_end(t, m.start(2)), 'RAW', None, an.in_struct(t, m.start(2))))
    for m in ALLOC.finditer(t):
        name, fn, args = m.group(1), m.group(2), m.group(3)
        if name in ('return', 'if', 'while', 'sizeof'):
            continue
        n = None
        al, _ = an.take_br(t, m.end(2) + (0 if fn.startswith('new') else t[m.end(2):].find('(') + 1))
        ty = re.search(r'\(\s*([\w:]+)\s*\*\s*\)', t[m.start():m.end(2)])
        es = ELSZ.get(ty.group(1)) if ty else None
        if fn == 'calloc':
            p = [x.strip() for x in al.split(',')]
            if len(p) == 2:
                a = an.ival(p[0], consts); b = an.ival(re.sub(r'sizeof\s*\(\s*(\w+)\s*\)', lambda q: str(ELSZ.get(q.group(1), 'x')), p[1]), consts)
                so = re.fullmatch(r'sizeof\s*\(\s*([\w:]+)\s*\)', p[1])
                if a is not None and so and ty and so.group(1) == ty.group(1):
                    n = a   # calloc(N, sizeof(T)) cast to T*: N elements
                elif a is not None and b is not None and (es is None or es == b):
                    n = a if es else a * b
        elif fn in ('malloc', 'aligned_alloc'):
            a = an.ival(al.split(',')[-1], consts)
            if a is not None:
                n = a // (es or 1)
        elif fn.startswith('new') or fn.startswith('make_unique'):
            a = an.ival(al, consts)
            n = a
        for lst in [out.setdefault(name, [])]:
            if not any(k == 'RAW' for (_, _, k, _, _) in lst):
                lst.append((m.start(1), an.block_end(t, m.start(1)) if re.search(r'[\w*]\s*\**\s*$', t[max(0, m.start(1) - 20):m.start(1)]) else len(t),
                            'RAW', n, an.in_struct(t, m.start(1))))
            else:
                # a second allocation site: the extent is only constant if every site agrees
                lst[:] = [(s, e, k, (x if x == n else None), mem) for (s, e, k, x, mem) in lst]
    return out

def resolve(bufs, name, pos, member):
    if member:
        ks = {(k, n) for (st, en, k, n, mem) in bufs.get(name, []) if mem}
        return ks.pop() if len(ks) == 1 else None
    vis = [(st, k, n) for (st, en, k, n, mem) in bufs.get(name, []) if not mem and st <= pos <= en]
    if not vis:
        ks = {(k, n) for (st, en, k, n, mem) in bufs.get(name, []) if mem}
        return ks.pop() if len(ks) == 1 else None   # a class member used unqualified inside a method
    v = max(vis)
    return (v[1], v[2])

def norm(e):
    return re.sub(r'\s+', '', an.strip_par(e))

def sizeexp(name):
    return r'(?:\b%s\s*(?:\.|->)\s*(?:size|length)\s*\(\s*\))' % re.escape(name)

def _operand_left(t, k):
    """the operand that ends at t[k] (exclusive), scanning back to a delimiter at depth 0"""
    d = 0; j = k
    while j > 0:
        c = t[j - 1]
        if c in ')]':
            d += 1
        elif c in '([':
            if d == 0:
                break
            d -= 1
        elif d == 0 and (c in ';{},?!' or (c in '&|' and t[j - 2:j - 1] == c) or (c == ':' and t[j - 2:j - 1] != ':')):
            break
        j -= 1
    return j

def _operand_right(t, k):
    d = 0; j = k
    while j < len(t):
        c = t[j]
        if c in '([':
            d += 1
        elif c in ')]':
            if d == 0:
                break
            d -= 1
        elif d == 0 and (c in ';{},?' or (c in '&|' and t[j + 1:j + 2] == c) or (c == ':' and t[j + 1:j + 2] != ':')):
            break
        j += 1
    return j

def size_check(t, fs, pos, name, expr):
    """a dominating compare of the index expression against name.size() (or a local assigned from it)"""
    body = t[fs:pos]
    e = norm(expr)
    S = sizeexp(name)
    sz_vars = [m.group(1) for m in re.finditer(r'\b([A-Za-z_]\w*)\s*=\s*(?:static_cast\s*<[^>]*>\s*\(\s*)?(?:\(\w+\)\s*)?' + S, body)]
    SZ = re.compile(S + ''.join(r'|\b%s\b' % re.escape(v) for v in sz_vars))
    def clean(x):
        x = norm(x)
        x = re.sub(r'^\((?:size_t|uint32_t|int|unsigned|uint64_t|int64_t|int32_t)\)', '', x)
        x = re.sub(r'^static_cast<[^>]*>\((.*)\)$', r'\1', x)
        return x
    for sm in SZ.finditer(body):
        s0, s1 = fs + sm.start(), fs + sm.end()
        # SZ on the right: lhs OP SZ  [- 1]
        lm = re.search(r'(<=|>=|<|>)\s*$', t[max(fs, s0 - 4):s0])
        tail = re.match(r'\s*-\s*1\b', t[s1:s1 + 8])
        if lm and not re.search(r'(<<|>>)\s*$', t[max(fs, s0 - 5):s0]):
            op = lm.group(1); oe = s0 - (len(t[max(fs, s0 - 4):s0]) - lm.start())
            ls = _operand_left(t, oe)
            lhs = clean(t[ls:oe])
            plus1 = lhs.endswith('+1')
            if plus1:
                lhs = lhs[:-2]
            if lhs == e:
                if op == '<' and not tail and not plus1 or op == '<=' and (tail or plus1):
                    if an.guard_dominates(t, ls, s1, pos, True): return True
                if op == '>=' and not tail and not plus1 or op == '>' and (tail or plus1):
                    if an.guard_dominates(t, ls, s1, pos, False) or _neg_compound(t, fs, ls, pos): return True
        # SZ on the left: SZ OP rhs
        rm = re.match(r'\s*(<=|>=|<|>)(?![<>=])\s*', t[s1:s1 + 6])
        if rm:
            op = rm.group(1); rs = s1 + rm.end(); re_ = _operand_right(t, rs)
            rhs = clean(t[rs:re_])
            if rhs == e:
                if op == '>' and an.guard_dominates(t, s0, re_, pos, True): return True
                if op == '<=' and (an.guard_dominates(t, s0, re_, pos, False) or _neg_compound(t, fs, s0, pos)): return True
    return False

def _neg_compound(t, fs, cs, pos):
    """`if (a || E >= size) return;` before pos"""
    k = t.rfind('if', fs, cs)
    if k < 0 or ';' in t[k:cs] or '{' in t[k:cs]:
        return False
    po = t.find('(', k)
    _, pc = an.take_br(t, po + 1)
    se = an.stmt_end(t, pc + 1)
    return pc < pos and se < pos and '&&' not in t[po:pc] and \
        bool(re.match(r'\s*\{?\s*(?:[^;{}]*;\s*)?(return|continue|break|goto|throw|abort|std::abort)\b', t[pc + 1:se + 1]))

def loop_check(t, fs, pos, name, expr):
    body = t[fs:pos]
    e = norm(expr)
    S = sizeexp(name)
    sz_vars = [m.group(1) for m in re.finditer(r'\b([A-Za-z_]\w*)\s*=\s*(?:static_cast\s*<[^>]*>\s*\(\s*)?(?:\(\w+\)\s*)?' + S + r'\s*[;,)]', body)]
    for lm in re.finditer(r'\bfor\s*\(([^;]*);\s*([^;]*);([^)]*)\)', body):
        if not an.loop_encloses(t, fs + lm.start(), pos):
            continue
        init, cond, step = lm.group(1), lm.group(2), lm.group(3)
        for cm in re.finditer(r'\b([A-Za-z_]\w*)\s*(<|!=)\s*(%s|%s)' % (S, '|'.join(r'\b%s\b' % re.escape(v) for v in sz_vars) or '(?!x)x'), cond):
            iv = cm.group(1)
            # the counter must not be reassigned in the body (crude: no `iv =`, `iv +=` between the loop head and pos)
            seg = t[fs + lm.end():pos]
            if re.search(r'(?<![\w.>])%s\s*(?:[-+*/|&^]?=)(?!=)' % re.escape(iv), seg):
                continue
            if cm.group(2) == '!=' and not re.search(r'\+\+|\+=\s*1\b', step):
                continue
            init_m = re.search(r'\b%s\s*=\s*([^,;]+)' % re.escape(iv), init)
            lo = an.ival(init_m.group(1), an.CONSTS) if init_m else None
            if e == iv and (lo is None or lo >= 0):
                return True
        # down-counting: for (i = name.size(); i > 0; i--) name[i - 1]
        dm = re.search(r'\b([A-Za-z_]\w*)\s*=\s*(?:%s)' % S, init)
        if dm and re.search(r'\b%s\s*(>|!=)\s*0\b' % re.escape(dm.group(1)), cond) and e == dm.group(1) + '-1':
            return True
    # while (i < name.size()) { ... name[i] ... }
    for wm in re.finditer(r'\bwhile\s*\(', body):
        po = fs + wm.end() - 1
        cond, pc = an.take_br(t, po + 1)
        if re.search(r'^\s*\(?\s*%s\s*<\s*%s\s*\)?\s*(&&.*)?$' % (re.escape(e), S), cond, re.S) and an.stmt_end(t, pc + 1) >= pos:
            seg = t[pc:pos]
            if not re.search(r'(?<![\w.>])%s\s*(?:\+\+|\+=|=(?!=))' % re.escape(e), seg):
                return True
    return False

def grown(t, fs, pos, name, expr):
    body = t[fs:pos]
    e = norm(expr)
    if re.fullmatch(r'%s(?:\.|->)(?:size|length)\(\)-\d+' % re.escape(name), e):
        return bool(re.search(r'!\s*%s\s*(?:\.|->)\s*empty\s*\(\)|%s\s*(?:>|!=)\s*0|%s\s*>=\s*1|%s\s*(?:\.|->)\s*(?:push_back|emplace_back)'
                              % (re.escape(name), sizeexp(name), sizeexp(name), re.escape(name)), body)) or \
               bool(re.search(r'%s\s*(?:\.|->)\s*empty\s*\(\)\s*\)\s*(?:\{?\s*)?(?:return|continue|break)' % re.escape(name), body))
    for rm in re.finditer(r'\b%s\s*(?:\.|->)\s*resize\s*\(' % re.escape(name), body):
        arg, _ = an.take_br(t, fs + rm.end())
        a = norm(arg)
        if a in (e + '+1',) or re.fullmatch(re.escape(e) + r'\+\d+', a) or (a.startswith('std::max(') and e + '+1' in a):
            return True
    iv = re.fullmatch(r'[A-Za-z_]\w*', e)
    if iv:
        for am in re.finditer(r'(?<![\w.>])%s\s*=\s*(?:\(\w+\)\s*)?(?:static_cast\s*<[^>]*>\s*\(\s*)?%s' % (re.escape(e), sizeexp(name)), body):
            seg = body[am.end():]
            if re.search(r'\b%s\s*(?:\.|->)\s*(?:push_back|emplace_back|resize|emplace)\s*\(' % re.escape(name), seg) and \
               not re.search(r'(?<![\w.>])%s\s*(?:[-+]?=)(?!=)' % re.escape(e), seg):
                return True
    return False

def lit_ok(t, fs, pos, name):
    body = t[fs:pos]
    return bool(re.search(r'\b%s\s*(?:\.|->)\s*(?:push_back|emplace_back|resize|assign|emplace|insert)\s*\(|!\s*%s\s*(?:\.|->)\s*empty\s*\(|%s\s*(?:>|>=|==|!=)\s*\w+|%s\s*(?:\.|->)\s*empty\s*\(\)\s*\)\s*\{?\s*(?:return|continue|break|throw)'
                          % (re.escape(name), re.escape(name), sizeexp(name), re.escape(name)), body)) or \
           bool(re.search(r'\b%s\s*(?:\.|->)\s*resize\s*\(|\b%s\s*=\s*\{' % (re.escape(name), re.escape(name)), t))

def param_taint(t, pos, expr):
    fs = an.func_start(t, pos)
    ob = None
    for bm in re.finditer(r'\)\s*(?:const\s*)?(?:noexcept\s*)?(?:override\s*)?(?:->\s*[\w:<>*& ]+)?\{', t[fs:pos]):
        ob = fs + bm.end(); break
    if ob is None:
        return False
    po = t.rfind('\n', 0, ob)
    head = t[max(fs, t.rfind('\n', 0, max(fs, t.find('(', fs) )) ):ob]
    ids = [x for x in an.ID.findall(expr) if x not in an.KW]
    for x in ids:
        if re.search(r'[\w&*>]\s+%s\s*[,)=]' % re.escape(x), head):
            return True
    return False

GUESTP = re.compile(r'\b(?:word\d*|w[01]|cmd\w*|addr\w*|address\w*|offset|len|length|size|count|index|idx|tile\w*|tmem\w*|vaddr|paddr|phys\w*)\b')

def classify(t, pos, name, kind, n, expr):
    fs = an.func_start(t, pos)
    if n is not None:
        c, w = an.classify(t, pos, name, n, expr, an.CONSTS)
        if c not in ('B',):
            return ('FIXED-' + c if c != 'OOB' else 'OOB'), w
        sm = re.fullmatch(r'\(?\s*\(?([^()]*?)\s*&\s*(0[xX][0-9a-fA-F]+|\d+)[uUlL]*\s*\)\s*>>\s*(\d+)[uU]?\s*\)?', an.strip_par(expr))
        if sm and (int(sm.group(2), 0) >> int(sm.group(3))) < n:
            return 'FIXED-SHIFTMASK', '(& %s) >> %s' % (sm.group(2), sm.group(3))
    e = norm(expr)
    if an.ival(e, an.CONSTS) is not None:
        return ('LIT', e) if lit_ok(t, fs, pos, name) else ('B-HOST', 'literal')
    if loop_check(t, fs, pos, name, expr):
        return 'LOOP', 'size()'
    if size_check(t, fs, pos, name, expr):
        return 'SIZECHK', ''
    if grown(t, fs, pos, name, expr):
        return 'GROWN', ''
    tn = an.taint(t, pos, expr)
    if tn == 'HOST' and param_taint(t, pos, expr):
        tn = 'PARAM'
    return 'B-' + tn, ''

MEMFN = re.compile(r'\b(?:std::)?(memcpy|memmove|memset)\s*\(')

def split_args(s):
    d = 0; cur = ''; out = []
    for c in s:
        if c in '([{':
            d += 1
        elif c in ')]}':
            d -= 1
        if c == ',' and d == 0:
            out.append(cur); cur = ''; continue
        cur += c
    out.append(cur)
    return [x.strip() for x in out]

def scan(path, text, base_consts, gbufs=None):
    t = an.strip_comments(text)
    consts = an.consts_of(t, base_consts)
    an.CONSTS = consts
    an.DECLS = an.decls_of(t, consts)
    bufs = collect(t, consts)
    for k, v in (gbufs or {}).items():
        bufs.setdefault(k, []).extend(v)
    rows = []
    if not bufs:
        return rows
    names = sorted(map(re.escape, bufs), key=len, reverse=True)
    pat = re.compile(r'(?<![\w])(%s)\s*(\[|(?:\.|->)\s*data\s*\(\s*\)\s*(?:\[|\+(?!\+)))' % '|'.join(names))
    for m in pat.finditer(t):
        name = m.group(1)
        pre = t[max(0, m.start() - 2):m.start()]
        member = pre.endswith('.') or pre.endswith('->')
        # a fixed-size array of the same name in scope belongs to class AN
        if an.resolve(an.DECLS, name, m.start(), member) is not None:
            continue
        r = resolve(bufs, name, m.start(), member)
        if r is None:
            continue
        kind, n = r
        if m.group(2) == '[':
            expr, j = an.take_br(t, m.end())
            ld = t[t.rfind('\n', 0, m.start()) + 1:m.start()]
            if any(st == m.start() for (st, _, _, _, _) in bufs[name]) or not expr.strip():
                continue
            if re.search(r'\b(?:new|delete)\s*[\w:<>]*\s*$', ld) or re.search(r'unique_ptr\s*<[^>]*$', ld):
                continue
        elif m.group(2).endswith('['):
            expr, j = an.take_br(t, m.end())
        else:
            # data() + expr: the operand up to the next top-level , ; ) or comparison
            k = m.end(); d = 0; s = k
            while k < len(t):
                c = t[k]
                if c in '([':
                    d += 1
                elif c in ')]':
                    if d == 0:
                        break
                    d -= 1
                elif d == 0 and c in ',;?:<>=|&' :
                    break
                k += 1
            expr = t[s:k]
        if kind == 'VEC' and n is not None and re.search(r'\b%s\s*(?:\.|->)\s*%s\s*\(|\b%s\s*=(?!=)' % (re.escape(name), MUT, re.escape(name)), t):
            n = None   # resized somewhere: the constructor extent is not invariant
        line = t.count('\n', 0, m.start()) + 1
        cls, why = classify(t, m.start(), name, kind, n, expr)
        rows.append((path, line, name, n or 0, ' '.join(expr.split())[:70], cls, why))
    # memcpy/memmove/memset ranges that touch a runtime buffer
    for m in MEMFN.finditer(t):
        args_s, j = an.take_br(t, m.end())
        args = split_args(args_s)
        if len(args) != 3:
            continue
        touched = [nm for nm in bufs if re.search(r'(?<![\w])%s\s*(?:\.|->)\s*data\s*\(|&\s*%s\s*\[|(?<![\w.>&])%s\s*(?:[+,)]|$)' % (re.escape(nm), re.escape(nm), re.escape(nm)), args[0] + ' ,' + args[1])]
        touched = [nm for nm in touched if an.resolve(an.DECLS, nm, m.start(), False) is None and resolve(bufs, nm, m.start(), False) is not None]
        if not touched:
            continue
        ln = args[2]
        fs = an.func_start(t, m.start())
        ok = None
        for nm in touched:
            kind, n = resolve(bufs, nm, m.start(), False)
            if re.search(sizeexp(nm), ln) or re.search(r'\bsizeof\b', ln) and not re.search(r'[\w)]\s*\*\s*sizeof|sizeof\s*\([^)]*\)\s*\*', ln):
                ok = 'SIZED'
            elif n is not None and an.ival(ln, consts) is not None and an.ival(ln, consts) <= n:
                ok = 'SIZED'
            elif an.ival(ln, consts) is not None:
                ok = ok or None
        line = t.count('\n', 0, m.start()) + 1
        if ok is None:
            tn = an.taint(t, m.start(), ln)
            if tn == 'HOST' and param_taint(t, m.start(), ln):
                tn = 'PARAM'
            ok = 'B-' + tn
        rows.append((path, line, '+'.join(sorted(touched))[:40], 0, ('%s len=%s' % (m.group(1), ' '.join(ln.split())))[:70], 'MEM-' + ok if ok == 'SIZED' else ok, ''))
    return rows

SELFTEST = r'''
#include <vector>
struct S { std::vector<uint32_t> mv; };
void f(uint8_t* rdram, recomp_context* ctx, uint32_t w, std::vector<int>& pv, uint32_t pidx) {
    std::vector<uint32_t> v;
    v.push_back(1);
    uint32_t a = v[0];                          // LIT
    for (size_t i = 0; i < v.size(); i++) v[i] = 0;   // LOOP
    uint32_t k = ctx->r4;
    if (k >= v.size()) return;
    v[k] = 2;                                   // SIZECHK
    uint32_t g = MEM_W(0, ctx->r5);
    v[g] = 3;                                   // B-GUEST
    if (g < v.size()) v[g] = 4;                 // SIZECHK
    uint32_t* tab = (uint32_t*)calloc(0x100, sizeof(uint32_t));
    tab[w & 0xFF] = 1;                          // FIXED-MASK
    tab[w & 0x1FF] = 1;                         // B-PARAM (mask too wide; w is a parameter)
    size_t ni = v.size(); v.push_back(9);
    v[ni] = 5;                                  // GROWN
    pv[pidx] = 1;                               // B-PARAM
    v[v.size() - 1] = 6;                        // GROWN (non-empty: pushed above)
    std::vector<uint8_t> fx(64);
    fx[w & 63] = 1;                             // FIXED-MASK
    memcpy(v.data(), rdram, v.size() * 4);      // MEM-SIZED... (size() mention)
    memcpy(v.data(), rdram, MEM_W(0, ctx->r6)); // B-GUEST (guest length)
    v.data()[k] = 1;                            // SIZECHK (the k >= v.size() return above dominates)
    size_t j; for (j = 0; j < v.size(); j++) {}
    v[j] = 1;                                   // B-HOST (after the loop exits, j == size())
    v.resize(w + 1);
    v[w] = 1;                                   // GROWN
    for (size_t q = v.size(); q > 0; q--) v[q - 1] = 0;   // LOOP (down-counter)
    char* big = new char[16];
    big[pidx] = 0;                              // B-PARAM
    std::vector<int> e2;
    int z = e2[0];                              // B-HOST (literal into a buffer never filled here)
}
'''
EXPECT = ['LIT', 'LOOP', 'SIZECHK', 'B-GUEST', 'SIZECHK', 'FIXED-MASK', 'B-PARAM', 'GROWN', 'B-PARAM', 'GROWN', 'FIXED-MASK',
          'SIZECHK', 'B-HOST', 'GROWN', 'LOOP', 'B-PARAM', 'B-HOST', 'MEM-SIZED', 'B-GUEST']

REVIEWED = {}
_rv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7364_heapbuf_reviewed.tsv')
if os.path.exists(_rv):
    for _l in open(_rv):
        if _l.startswith('#') or not _l.strip():
            continue
        _f = _l.rstrip('\n').split('\t')
        REVIEWED[(_f[0], _f[1], _f[2])] = _f[3]

GEN = False
def pkey(path):
    path = path.replace('\\', '/')
    return 'RecompiledFuncs/' + os.path.basename(path) if GEN or '/RecompiledFuncs/' in path else path

def verdict(r):
    return REVIEWED.get((pkey(r[0]), r[2], r[4]))

def main():
    global GEN
    if '--selftest' in sys.argv:
        rows = scan('selftest', SELFTEST, {})
        got = [r[5] for r in rows]
        ok = got == EXPECT
        print('selftest', 'PASS' if ok else 'FAIL', got)
        if not ok:
            for r, x in zip(rows, EXPECT):
                if r[5] != x:
                    print('  line %d %s[%s] got %s want %s' % (r[1], r[2], r[4], r[5], x))
        sys.exit(0 if ok else 1)
    files = an.scope('--rt64' in sys.argv)
    if '--gen' in sys.argv:
        GEN = True
        files = sorted(glob.glob(sys.argv[sys.argv.index('--gen') + 1] + '/*.c'))
    if '--files' in sys.argv:
        files = sys.argv[sys.argv.index('--files') + 1].split(',')
    base = {}; gbufs = {}
    hdrs = [f for f in files if f.endswith(('.h', '.hpp'))]
    for f in hdrs:
        tt = an.strip_comments(open(f, errors='replace').read())
        base = an.consts_of(tt, base)
    for f in hdrs:
        tt = an.strip_comments(open(f, errors='replace').read())
        for k, v in collect(tt, base).items():
            for (st, en, kd, n, mem) in v:
                if mem:
                    gbufs.setdefault(k, []).append((st, en, kd, n, True))
    rows = []
    for f in files:
        rows += scan(f, open(f, errors='replace').read(), base, gbufs if not f.endswith(('.h', '.hpp')) else None)
    c = Counter(r[5] for r in rows)
    print('TOTAL', len(rows), dict(sorted(c.items())))
    bad = 0
    for r in rows:
        if r[5].startswith('B') or r[5] == 'OOB':
            v = verdict(r)
            if v is None or r[5] == 'OOB':
                bad += 1
            if (v is None and '-q' not in sys.argv) or '-v' in sys.argv:
                print('%s:%d %s [%s] %s %s' % (r[0], r[1], r[2], r[4], r[5], v or ''))
    keys = {(pkey(r[0]), r[2], r[4]) for r in rows if r[5].startswith('B') and verdict(r) is None}
    print('OPEN', bad, 'keys', len(keys))
    if '--emit-open' in sys.argv:
        with open(sys.argv[sys.argv.index('--emit-open') + 1], 'w') as o:
            seen = set()
            for r in rows:
                k = (pkey(r[0]), r[2], r[4])
                if (r[5].startswith('B') or r[5] == 'OOB') and verdict(r) is None and k not in seen:
                    seen.add(k)
                    o.write('%s\t%s\t%s\t%s:%d\n' % (k[0], k[1], k[2], r[5], r[1]))
    if '--check' in sys.argv:
        sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
