#!/usr/bin/env python3
"""s7363 class AN census: host arrays of constant extent N (`T name[N]`, `std::array<T, N> name`) and every
subscript `name[expr]` on them, classified by whether expr is provably in [0, N).

Rows: CONST (literal < N), MASK (top-level `& M`, M < N), FIELD (`(x >> s) & M`, M < N; same rule), MOD (`% K`, K <= N),
LOOP (expr is a for-counter whose bound is a literal <= N, the array's own extent / countof, or a name with the same
value), CHECKED (a dominating `idx < N` / `idx >= N` / `idx > N-1` compare, or min/clamp to N-1, within the function),
OOB (literal >= N: a defect), B (the rest: by hand, verdict table REVIEWED).
`--check` exits 1 on OOB or an unreviewed B. `--selftest` runs planted rows of every class. Scope: owned host code
(src/**, librecomp, ultramodern) and, with --rt64, lib/rt64/src.
"""
import re, sys, os, glob
from collections import Counter

def strip_comments(t):
    t = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), t, flags=re.S)
    t = re.sub(r'//[^\n]*', lambda m: ' ' * len(m.group(0)), t)
    t = re.sub(r'"(?:\\.|[^"\\\n])*"', lambda m: '"' + ' ' * (len(m.group(0)) - 2) + '"', t)
    return t

def ival(s, consts):
    s = s.strip()
    try:
        return int(eval(re.sub(r'\b(0[xX][0-9a-fA-F]+|\d+)[uUlL]*\b', r'\1', s), {'__builtins__': {}}, dict(consts)))
    except Exception:
        return None

CONSTDEF = re.compile(r'(?:#define\s+([A-Za-z_]\w*)\s+\(?\s*((?:0[xX][0-9a-fA-F]+|\d+)[uUlL]*(?:\s*[*+<-]+\s*(?:0[xX][0-9a-fA-F]+|\d+)[uUlL]*)*)\s*\)?\s*$)'
                      r'|(?:\b(?:static\s+)?(?:constexpr|const)\s+(?:[\w:]+\s+)+([A-Za-z_]\w*)\s*=\s*([^;{]+);)', re.M)
DECL = re.compile(r'(?<![\w.>\]])\b((?:unsigned\s+|signed\s+|const\s+|static\s+|volatile\s+|struct\s+)*[A-Za-z_][\w:<>,* ]*?[\s*&])\s*([A-Za-z_]\w*)\s*\[\s*([^\[\]\n;]+?)\s*\]')
STDARR = re.compile(r'std::array\s*<\s*[^,<>]+(?:<[^<>]*>)?\s*,\s*([^<>]+?)\s*>\s*&?\s*([A-Za-z_]\w*)\s*[;={(\[]')
NOTTYPE = {'return', 'else', 'case', 'sizeof', 'delete', 'new', 'goto', 'throw', 'do'}

def consts_of(t, base):
    c = dict(base)
    for m in CONSTDEF.finditer(t):
        n, v = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        if not m.group(1) and not file_scope(t, m.start()):
            continue   # a function-local const: its name would shadow loop counters elsewhere
        x = ival(v, c)
        if x is not None:
            c[n] = x
    return c

def block_end(t, pos):
    """end of the innermost {...} block that contains pos (len(t) at file scope); a declaration inside (...) is a
    parameter: its scope is the block that follows the parameter list."""
    d = 0; i = pos
    # parameter? look for unmatched '(' before pos on the same statement
    pd = 0; k = pos
    while k > 0 and t[k - 1] not in ';{}':
        k -= 1
        if t[k] == ')':
            pd += 1
        elif t[k] == '(':
            if pd == 0:
                ob = t.find('{', pos); semi = t.find(';', pos)
                if ob >= 0 and (semi < 0 or ob < semi):
                    return block_end(t, ob + 1)
                return pos
            pd -= 1
    while i < len(t):
        c = t[i]
        if c == '{':
            d += 1
        elif c == '}':
            if d == 0:
                return i
            d -= 1
        i += 1
    return len(t)

def in_struct(t, pos):
    k = pos; d = 0
    while k > 0:
        k -= 1
        c = t[k]
        if c == '}':
            d += 1
        elif c == '{':
            if d == 0:
                head = t[t.rfind(';', 0, k) + 1:k]
                head = head[head.rfind('}') + 1:]
                return bool(re.search(r'\b(struct|class|union)\b', head)) and '(' not in head
            d -= 1
    return False

def file_scope(t, pos):
    st = []
    for m in re.finditer(r'[{}]|\bnamespace\b[^{;]*\{|\bextern\s+"C"\s*\{', t[:pos]):
        g = m.group(0)
        if g == '}':
            if st:
                st.pop()
        else:
            st.append(g == '{')
    return not any(st)

def decls_of(t, consts):
    out = {}
    for m in DECL.finditer(t):
        ty, name, ext = m.group(1), m.group(2), m.group(3)
        if ty.strip().split()[-1].strip('*&') in NOTTYPE or ty.strip() in NOTTYPE:
            continue
        # must look like a declaration: type word, not an expression like `a = b[i]`
        pre = t[max(0, m.start() - 2):m.start()]
        if re.search(r'[=(,+\-/%|^!?:]\s*$', t[max(0, m.start() - 40):m.start()]) and not re.search(r'[;{}(,]\s*(?:static\s+|const\s+)*$', t[max(0, m.start() - 40):m.start()]):
            continue
        n = ival(ext, consts)
        if n is None or n <= 1:
            continue
        out.setdefault(name, []).append((m.start(2), block_end(t, m.start(2)), n, in_struct(t, m.start(2))))
    for m in STDARR.finditer(t):
        n = ival(m.group(1), consts)
        if n:
            out.setdefault(m.group(2), []).append((m.start(), block_end(t, m.start()), n, in_struct(t, m.start())))
    return out

def resolve(decls, name, pos, member):
    if member:
        ns = {n for (st, en, n, mem) in decls.get(name, []) if mem}
        return ns.pop() if len(ns) == 1 else None   # ambiguous member name across structs: skip
    vis = [(st, n) for (st, en, n, mem) in decls.get(name, []) if not mem and st <= pos <= en]
    return max(vis)[1] if vis else None

def take_br(t, i):
    d = 0; j = i
    while j < len(t):
        c = t[j]
        if c in '([{':
            d += 1
        elif c in ')]}':
            if d == 0:
                return t[i:j], j
            d -= 1
        j += 1
    return t[i:], j

def top_and(e):
    """top-level `X & M` operands"""
    d = 0; parts = []; cur = ''
    i = 0
    while i < len(e):
        c = e[i]
        if c in '([':
            d += 1
        elif c in ')]':
            d -= 1
        if d == 0 and c == '&' and e[i + 1:i + 2] != '&' and e[i - 1:i] != '&':
            parts.append(cur); cur = ''; i += 1; continue
        cur += c; i += 1
    parts.append(cur)
    return parts if len(parts) > 1 else None

def strip_par(e):
    e = e.strip()
    while e.startswith('(') and e.endswith(')'):
        inner, j = take_br(e, 1)
        if j != len(e) - 1:
            break
        e = inner.strip()
    e = re.sub(r'^\((?:u?int\d+_t|size_t|unsigned|int|u8|u16|u32|s32|uint|long)\)\s*', '', e)
    return e

def top_ternary(e):
    d = 0; q = -1
    for i, c in enumerate(e):
        if c in '([':
            d += 1
        elif c in ')]':
            d -= 1
        elif d == 0 and c == '?' and q < 0:
            q = i
        elif d == 0 and c == ':' and q >= 0 and e[i - 1:i] != ':' and e[i + 1:i + 2] != ':':
            return e[q + 1:i], e[i + 1:]
    return None

def capped_counter(t, cv, n, consts=None):
    """every increment of counter cv in the file is dominated (same or previous 3 lines) by `cv < K` / `cv >= K` with
    K <= n, or the counter is reset/wrapped with `% K` / `& M`: then cv < n wherever it is used as a bound."""
    sites = list(re.finditer(r'(?<![\w.>])%s\s*(?:\+\+|\+=)|\+\+\s*%s\b' % (re.escape(cv), re.escape(cv)), t))
    if not sites:
        return False
    for m in sites:
        ls = t.rfind('\n', 0, m.start())
        for _ in range(3):
            ls = t.rfind('\n', 0, ls) if ls > 0 else 0
        win = t[ls:m.start()]
        ok = False
        for cm in re.finditer(r'\b%s\s*(<|>=|<=|>)\s*([\w()+\-* ]+?)\s*(?=[)&|;?])' % re.escape(cv), win):
            b = ival(cm.group(2), CONSTS)
            if b is None:
                continue
            lim = b if cm.group(1) in ('<', '>=') else b + 1
            if lim <= n and guard_dominates(t, ls + cm.start(), ls + cm.end(), m.start(), cm.group(1) in ('<', '<=')):
                ok = True
        if not ok:
            return False
    return True

def ubound(t, fs, pos, bexp, consts, n, decls, depth=0):
    """an upper bound (exclusive) of a loop-bound expression, or None"""
    bexp = strip_par(bexp)
    b = ival(bexp, consts)
    if b is not None:
        return b
    sm = re.fullmatch(r'sizeof\s*\(?\s*([A-Za-z_]\w*)\s*\)?(?:\s*/\s*sizeof\s*\(?\s*\w+(?:\[0\])?\s*\)?)?', bexp)
    if sm:
        en = resolve(decls, sm.group(1), pos, False)
        el = elem_size(t, sm.group(1))
        if en is not None and ('/' in bexp or el == 1):
            return en
        return None
    mm = re.fullmatch(r'(?:std::)?(?:min|MIN)\s*\((.*)\)', bexp)
    if mm:
        bs = [ubound(t, fs, pos, a, consts, n, decls, depth + 1) for a in mm.group(1).split(',')]
        bs = [x for x in bs if x is not None]
        return min(bs) if bs else None
    tq = top_ternary(bexp)
    if tq:
        cm = re.match(r'\s*\(?\s*([\w.>-]+)\s*<\s*(\w+)\s*\)?\s*$', bexp[:bexp.index('?')])
        if cm and tq[0].strip() == cm.group(1) and tq[1].strip() == cm.group(2):
            return ubound(t, fs, pos, cm.group(2), consts, n, decls, depth + 1)
        a = ubound(t, fs, pos, tq[0], consts, n, decls, depth + 1); c = ubound(t, fs, pos, tq[1], consts, n, decls, depth + 1)
        return max(a, c) if a is not None and c is not None else None
    if depth < 3 and re.fullmatch(r'[\w.>-]+', bexp):
        cv = re.split(r'\.|->', bexp)[-1]
        if capped_counter(t, cv, n):
            return n
        if '.' not in bexp and '->' not in bexp:
            body = t[fs:pos]
            asg = list(re.finditer(r'(?<![\w.>=!<])%s\s*=(?!=)\s*([^;]*);' % re.escape(cv), body))
            if asg and not re.search(r'(?<![\w.>])%s\s*(?:\+\+|--|[-+*|^<>]=)|(?:\+\+|--)\s*%s\b' % (re.escape(cv), re.escape(cv)), body):
                bs = [ubound(t, fs, pos, a.group(1), consts, n, decls, depth + 1) for a in asg]
                if all(x is not None for x in bs):
                    return max(bs)
            bt = re.search(r'\b%s\s*=\s*(?:::)?backtrace\s*\(\s*\w+\s*,\s*(\w+)\s*\)' % re.escape(cv), body)
            if bt:
                return (ival(bt.group(1), consts) or 0) + 1 or None
            # clamp after assignment: if (cv > K) cv = K;
            cl = re.search(r'if\s*\(\s*%s\s*>\s*(\w+)\s*\)\s*%s\s*=\s*\1\s*;' % (re.escape(cv), re.escape(cv)), body)
            if cl:
                k = ival(cl.group(1), consts)
                if k is not None:
                    return k + 1
    return None

def elem_size(t, name):
    m = re.search(r'\b(u?int8_t|char|unsigned char|uint8_t|u8|s8|bool)\s+(?:const\s+)?%s\s*\[' % re.escape(name), t)
    return 1 if m else None

def stmt_end(t, k):
    """end of the statement starting at k (a {block} or up to the first depth-0 ';')"""
    while k < len(t) and t[k] in ' \t\n':
        k += 1
    if k < len(t) and t[k] == '{':
        return block_end(t, k + 1)
    d = 0; j = k
    while j < len(t):
        c = t[j]
        if c in '([{':
            d += 1
        elif c in ')]}':
            d -= 1
            if d < 0:
                return j
        elif c == ';' and d == 0:
            return j
        j += 1
    return j

def guard_dominates(t, cs, ce, pos, positive):
    # the innermost unmatched '(' before the compare, and the keyword in front of it
    d = 0; k = cs
    while k > 0:
        k -= 1
        c = t[k]
        if c == ')':
            d += 1
        elif c == '(':
            if d == 0:
                break
            d -= 1
        elif c in ';{}' and d == 0:
            k = -1; break
    if k > 0:
        kw = re.search(r'(\w+)\s*$', t[max(0, k - 12):k])
        kw = kw.group(1) if kw else ''
        _, pc = take_br(t, k + 1)
        cond = t[k + 1:pc]
        if kw == 'for':
            return False
        if kw in ('if', 'while'):
            se = stmt_end(t, pc + 1)
            if positive and pc < pos <= se and '||' not in cond:
                return True
            if not positive and kw == 'if' and pos > se and '&&' not in cond:
                body = t[pc + 1:se + 1]
                if re.match(r'\s*\{?\s*(?:[^;{}]*;\s*)?(return|continue|break|goto|std::abort|abort)\b', body):
                    return True
            return False
    # same statement: `iv < K && ...` or `iv < K ? ...`
    if positive and ';' not in t[ce:pos] and re.match(r'\s*\)*\s*(&&|\?)', t[ce:ce + 8]):
        return True
    return False

def loop_encloses(t, fpos, pos):
    po = t.find('(', fpos)
    _, pc = take_br(t, po + 1)
    k = pc + 1
    while k < len(t) and t[k] in ' \t\n':
        k += 1
    if k < len(t) and t[k] == '{':
        return block_end(t, k + 1) >= pos
    # single statement: up to the next ';' at depth 0 (a nested for/if chain counts as one statement)
    d = 0; j = k
    while j < len(t):
        c = t[j]
        if c in '([{':
            d += 1
        elif c in ')]}':
            d -= 1
            if d < 0:
                break
        elif c == ';' and d == 0:
            break
        j += 1
    return j >= pos

def func_start(t, pos):
    # crude: last line that starts at column 0 with a non-space and contains '(' before pos, followed by '{'
    k = t.rfind('\n}', 0, pos)
    return k if k >= 0 else 0

def classify(t, pos, name, n, expr, consts, depth=0):
    e = strip_par(expr)
    v = ival(e, consts)
    if v is not None:
        return ('CONST' if 0 <= v < n else 'OOB'), str(v)
    tq = top_ternary(e)
    if tq:
        cm = re.match(r'\s*\(?\s*([\w.>-]+)\s*(<|<=|>|>=)\s*(\w+)\s*\)?\s*$', e[:e.index('?')])
        if cm:
            x, op, k = cm.group(1), cm.group(2), cm.group(3)
            kv = ival(k, consts)
            a1, a2 = strip_par(tq[0]), strip_par(tq[1])
            if kv is not None and ((op in ('<', '<=') and a1 == x and a2 == k) or (op in ('>', '>=') and a1 == k and a2 == x)):
                hi = kv + 1 if op in ('<', '>') or op in ('<=', '>=') else kv
                if 0 <= kv < n and not re.search(r'\b(int|int32_t|int64_t|short|long)\b\s+%s\b' % re.escape(x.split('.')[-1]), t[func_start(t, pos):pos]):
                    return 'CLAMP', '%s %s %s' % (x, op, k)
    if tq and depth < 3:
        c1, w1 = classify(t, pos, name, n, tq[0], consts, depth + 1)
        c2, w2 = classify(t, pos, name, n, tq[1], consts, depth + 1)
        if c1 not in ('B', 'OOB') and c2 not in ('B', 'OOB'):
            return 'TERN', '%s|%s' % (w1, w2)
    a = top_and(e)
    if a:
        for p in a:
            m = ival(strip_par(p), consts)
            if m is not None and 0 <= m < n:
                return ('FIELD' if '>>' in e else 'MASK'), '& %d' % m
    mm = re.search(r'%\s*\(?\s*([\w]+)\s*\)?\s*$', e)
    if mm:
        k = ival(mm.group(1), consts)
        if k is not None and 0 < k <= n and '+' not in e[:mm.start()].split('(')[-1]:
            return 'MOD', '%% %d' % k
    e2 = re.sub(r'^([A-Za-z_][\w.>-]*)\s*(\+\+|--)$', r'\1', e)
    e2 = re.sub(r'^\+\+\s*([A-Za-z_]\w*)$', r'\1 + 1', e2)
    e2 = re.sub(r'^--\s*([A-Za-z_]\w*)$', r'\1 - 1', e2)
    idv = re.fullmatch(r'([A-Za-z_]\w*)(?:\s*([+-])\s*(\d+))?', e2)
    fs = func_start(t, pos)
    body = t[fs:pos]
    if idv:
        iv = idv.group(1); off = int(idv.group(3) or 0) * (1 if idv.group(2) == '+' else -1)
        # loop bound
        for lm in re.finditer(r'for\s*\(([^;]*);\s*([^;]*);', body):
            if not loop_encloses(t, fs + lm.start(), pos):
                continue   # an earlier, finished loop: the counter may sit at its exit value
            cond = lm.group(2)
            for cm in re.finditer(r'\b%s\s*(<=?)\s*([^&|);]+)' % re.escape(iv), cond):
              bexp = cm.group(2).strip()
              b = ubound(t, fs, pos, bexp, consts, n, DECLS)
              if b is None and re.search(r'\b%s\b' % re.escape(name), bexp) and not re.search(r'\bsizeof\b', bexp):  # countof(name) / name.size()
                  b = n
              if b is None:
                  continue
              hi = b + (1 if cm.group(1) == '<=' else 0)
              init = re.search(r'\b%s\s*=\s*([^,;]+)' % re.escape(iv), lm.group(1))
              lo = ival(init.group(1), consts) if init else None
              if hi + off <= n and (lo is None or lo + off >= 0):
                  return 'LOOP', '%s<%d' % (iv, hi)
        # dominating check, context-aware: `if (iv < K) <stmt containing pos>`, `if (iv >= K) return/continue/break;`
        # before pos, `while (iv < K) {pos}`, or `iv < K && ...pos` / `iv < K ? ...pos` in the same statement.
        for cm in re.finditer(r'\b%s\s*(<|>=|>|<=)\s*([\w:()+\-*. ]+?)\s*(?=[)&|;?])' % re.escape(iv), body):
            b = ubound(t, fs, pos, cm.group(2), consts, n, DECLS)
            if b is None or b != ival(cm.group(2), consts) and not re.fullmatch(r'\s*sizeof.*', cm.group(2)) and ival(cm.group(2), consts) is None:
                # a variable bound: only its proven upper bound counts (ubound), and only for `<` forms
                pass
            if b is None:
                continue
            op = cm.group(1)
            lim = b if op in ('<', '>=') else b + 1
            if lim + max(off, 0) > n:
                continue
            cpos = fs + cm.start()
            if guard_dominates(t, cpos, fs + cm.end(), pos, op in ('<', '<=')):
                return 'CHECKED', '%s %s %d' % (iv, op, b)
        for cm in re.finditer(r'\b%s\s*=\s*(?:std::)?(?:min|MIN|clamp|std::clamp)\s*\(([^;]*)\);' % re.escape(iv), body):
            nums = [ival(x, consts) for x in re.split(r',', cm.group(1))]
            nums = [x for x in nums if x is not None]
            if nums and max(nums) + off < n:
                return 'CHECKED', 'min %d' % max(nums)
        # the index variable's own definitions: every assignment masked / a narrow C type
        dm = re.search(r'\b(uint8_t|u8|unsigned char|uint16_t|u16|bool)\s+(?:const\s+)?%s\s*[=;,)]' % re.escape(iv), body) or \
             re.search(r'\b(uint8_t|u8|unsigned char|uint16_t|u16|bool)\s+(?:const\s+)?[^;(]*?[,\s]%s\s*[=;,]' % re.escape(iv), body)
        if dm:
            tb = {'uint8_t': 256, 'u8': 256, 'unsigned char': 256, 'uint16_t': 65536, 'u16': 65536, 'bool': 2}[dm.group(1)]
            if tb + max(off, 0) <= n and off >= 0:
                return 'TYPE', '%s %s' % (dm.group(1), iv)
        asg = [(fs + a.start(), a.group(1)) for a in re.finditer(r'(?<![\w.>=!<])%s\s*=(?!=)\s*([^;]*);' % re.escape(iv), body)]
        if asg and not re.search(r'(?<![\w.>])%s\s*(?:\+\+|--|[-+*|^<>]=)|(?:\+\+|--)\s*%s\b' % (re.escape(iv), re.escape(iv)), body):
            ok = True; why = []
            for ap, a in asg:
                c2, w2 = classify(t, ap, name, n, a, consts, depth + 1) if a.strip() != iv and depth < 3 else ('B', '')
                if c2 in ('B', 'OOB'):
                    ok = False; break
                why.append(w2)
            if ok and off == 0:
                return 'DEFMASK', '%s=%s' % (iv, ','.join(why))
    return 'B', ''

GUEST = re.compile(r'\bMEM_\w+\s*\(|\brdram\b|\bctx->|\b_arg\s*<|\b(?:dmem|imem|DMEM|IMEM)\b|\bget_dmem|\bgetenv\b|\bato[il]\b|\bstrto\w+\b|'
                   r'\b(?:w0|w1|cmd|cmd0|cmd1|word|hi|lo)\b|\b(?:rd|rd32|rd16|rd8|read32|read16|read8|g32|g16|g8|rw|rh|rb|be32|load32|ld32)\s*\(|\bRDRAM\b|\b(?:guest|phys|vaddr|paddr|addr)\w*\b|\bpc\b|\bra\b')
ID = re.compile(r'[A-Za-z_]\w*')
KW = {'int', 'unsigned', 'uint32_t', 'int32_t', 'uint8_t', 'uint16_t', 'size_t', 'uint64_t', 'int64_t', 'static_cast', 'const', 'auto', 'u32', 's32',
      'sizeof', 'std', 'min', 'max'}

def taint(t, pos, expr, depth=0):
    """'GUEST' if expr (or the assignments of its identifiers in the enclosing function, 2 levels) mentions a guest source;
    'CTR' if it is a post-increment of a host counter; else 'HOST'."""
    if GUEST.search(expr):
        return 'GUEST'
    body = t[func_start(t, pos):pos]
    ids = [x for x in ID.findall(expr) if x not in KW]
    for x in ids:
        for am in re.finditer(r'(?<![\w.>])%s\s*(?:\[[^\]]*\])?\s*(?:[-+|^&]?=)(?!=)\s*([^;]*);' % re.escape(x), body):
            rhs = am.group(1)
            if GUEST.search(rhs):
                return 'GUEST'
            if depth < 1 and taint(t, pos, ' '.join(y for y in ID.findall(rhs) if y not in KW and y != x), depth + 1) == 'GUEST':
                return 'GUEST'
        # function parameter: guest when the parameter list mentions guest-ish types
    if depth == 0 and re.search(r'\+\+|--', expr):
        return 'CTR'
    return 'HOST'

SUB = None
DECLS = {}
CONSTS = {}
GEN = False

def scan(path, text, base_consts, gdecls=None):
    t = strip_comments(text)
    consts = consts_of(t, base_consts)
    global DECLS, CONSTS
    CONSTS = consts
    decls = decls_of(t, consts)
    DECLS = decls
    for k, v in (gdecls or {}).items():
        decls.setdefault(k, []).extend(v)
    rows = []
    if not decls:
        return rows
    pat = re.compile(r'(?<![\w])(%s)\s*\[' % '|'.join(sorted(map(re.escape, decls), key=len, reverse=True)))
    for m in pat.finditer(t):
        name = m.group(1)
        pre = t[max(0, m.start() - 2):m.start()]
        member = pre.endswith('.') or pre.endswith('->')
        n = resolve(decls, name, m.start(), member)
        if n is None:
            continue
        expr, j = take_br(t, m.end())
        line = t.count('\n', 0, m.start()) + 1
        # skip the declaration itself
        ld = t[t.rfind('\n', 0, m.start()) + 1:m.start()]
        if ival(expr, consts) == n and re.search(r'[\w>*&]\s*$', ld) and not re.search(r'[=(\[,+]\s*$', ld):
            continue
        if not expr.strip():
            continue
        if any(st == m.start() for (st, _, _, _) in decls[name]):
            continue
        cls, why = classify(t, m.start(), name, n, expr, consts)
        if cls == 'B':
            cls = 'B-' + taint(t, m.start(), expr)
        rows.append((path, line, name, n, ' '.join(expr.split())[:70], cls, why))
    return rows

def scope(rt64=False):
    fs = []
    pats = ['src/**/*.cpp', 'src/**/*.c', 'src/**/*.h', 'src/**/*.hpp',
            'lib/N64ModernRuntime/librecomp/src/*.cpp', 'lib/N64ModernRuntime/librecomp/include/**/*.h*',
            'lib/N64ModernRuntime/ultramodern/src/*.cpp', 'lib/N64ModernRuntime/ultramodern/include/**/*.h*']
    if rt64:
        pats += ['lib/rt64/src/**/*.cpp', 'lib/rt64/src/**/*.h']
    for p in pats:
        fs += glob.glob(p, recursive=True)
    return sorted(set(f for f in fs if '/imgui/' not in f and '/contrib/' not in f))

SELFTEST = r'''
#define NT 8
static uint32_t tab[NT];
static int big[16];
void f(uint8_t* rdram, recomp_context* ctx, uint32_t w) {
    tab[3] = 1;                         // CONST
    tab[w & 7] = 1;                     // MASK
    tab[(w >> 24) & 0x7] = 1;           // FIELD
    tab[w % NT] = 1;                    // MOD
    for (int i = 0; i < NT; i++) tab[i] = 0;   // LOOP
    uint32_t k = ctx->r4;
    if (k >= NT) return;
    tab[k] = 2;                         // CHECKED
    tab[8] = 1;                         // OOB
    big[MEM_W(0, ctx->r5)] = 1;         // B
    tab[w & 15] = 1;                    // B (mask too wide)
    const uint32_t sl = w == 1024u ? 0u : 1u;
    tab[sl] = 1;                        // DEFMASK (ternary of constants)
    tab[w < 7 ? w : 7] = 1;             // CLAMP (unsigned clamp)
    for (int i = 0; i < 4; i++) {}
    int j; for (j = 0; j < NT; j++) {}
    tab[j] = 1;                         // B (index after the loop exits = NT)
    static uint32_t ring[NT]; static uint32_t nr;
    if (nr < NT) ring[nr++] = w;        // CHECKED
    static uint32_t r2[NT]; static uint32_t n2;
    if (n2 < NT) { w++; } r2[n2++] = w; // B-CTR (the check does not dominate the increment)
    for (uint32_t q = 0; q < n2; q++) r2[q] = 0;     // B-HOST
    for (uint32_t q = 0; q < nr; q++) ring[q] = 0;   // LOOP (nr is a capped counter)
    static uint32_t ov[4]; static uint32_t no;
    ov[no++] = w;                       // B-CTR (uncapped)
    for (uint32_t q = 0; q < no; q++) ov[q] = 0;     // B (no is not capped)
    uint64_t wide[4];
    for (size_t q = 0; q < sizeof(wide); q++) wide[q] = 0;   // B (sizeof is bytes, not elements)
}
'''
EXPECT = ['CONST', 'MASK', 'FIELD', 'MOD', 'LOOP', 'CHECKED', 'OOB', 'B-GUEST', 'B-HOST', 'DEFMASK', 'CLAMP', 'B-HOST', 'CHECKED', 'B-CTR', 'B-HOST', 'LOOP',
          'B-CTR', 'B-HOST', 'B-HOST']

# Hand verdicts for B rows, line-agnostic: tools/s7363_hostarr_reviewed.tsv = path-key TAB array TAB index-expr TAB verdict.
# A new (array, expr) pair in a file is unreviewed until someone classifies it, so --check fails on new unproven subscripts.
REVIEWED = {}
_rv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7363_hostarr_reviewed.tsv')
if os.path.exists(_rv):
    for _l in open(_rv):
        if _l.startswith('#') or not _l.strip():
            continue
        _f = _l.rstrip('\n').split('\t')
        REVIEWED[(_f[0], _f[1], _f[2])] = _f[3]

def pkey(path):
    path = path.replace('\\', '/')
    return 'RecompiledFuncs/' + os.path.basename(path) if GEN or '/RecompiledFuncs/' in path else path

def verdict(r):
    return REVIEWED.get((pkey(r[0]), r[2], r[4]))

def main():
    if '--selftest' in sys.argv:
        rows = scan('selftest', SELFTEST, {})
        got = [r[5] for r in rows]
        print('selftest', 'PASS' if got == EXPECT else 'FAIL', got)
        sys.exit(0 if got == EXPECT else 1)
    files = scope('--rt64' in sys.argv)
    global GEN
    if '--gen' in sys.argv:
        GEN = True
        files = sorted(glob.glob(sys.argv[sys.argv.index('--gen') + 1] + '/*.c'))
    if '--files' in sys.argv:
        files = sys.argv[sys.argv.index('--files') + 1].split(',')
    # header-level constants and arrays visible everywhere (same-name collisions resolved by first)
    base = {}
    for f in files:
        if f.endswith(('.h', '.hpp')):
            base = consts_of(strip_comments(open(f, errors='replace').read()), base)
    rows = []
    for f in files:
        rows += scan(f, open(f, errors='replace').read(), base)
    c = Counter(r[5] for r in rows)
    print('TOTAL', len(rows), dict(c))
    bad = 0
    for r in rows:
        if r[5].startswith('B') or r[5] == 'OOB':
            v = verdict(r)
            if v is None or r[5] == 'OOB':
                bad += 1
            if v is None or '-v' in sys.argv:
                print('%s:%d %s[%d] [%s] %s %s' % (r[0], r[1], r[2], r[3], r[4], r[5], v or ''))
    print('OPEN', bad)
    if '--emit-open' in sys.argv:   # write the unreviewed rows as TSV stubs (verdict column to fill in)
        with open(sys.argv[sys.argv.index('--emit-open') + 1], 'w') as o:
            for r in rows:
                if (r[5].startswith('B') or r[5] == 'OOB') and verdict(r) is None:
                    o.write('%s\t%s\t%s\t%s:%d\n' % (pkey(r[0]), r[2], r[4], r[5], r[1]))
    if '--check' in sys.argv:
        sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
