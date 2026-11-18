#!/usr/bin/env python3
"""s7558 class GR: behaviour changes the regen chain makes to generated code with NO env switch.

GQ (s7557) enumerated default-on env levers; it cannot see a guard/clamp/skip that no env read controls. GR diffs the
pristine N64Recomp output (renamed only, so names match) against the fully fixed tree, function by function, and
classifies every changed hunk:

  INERT      inserted text that writes no guest state (no ctx-> register/MEM_ store, goto, return, guest call) and keeps
             every pristine statement verbatim (a wrap). Breadcrumbs, counters, void host notifications.
  GATED      every effectful residual statement sits under a condition that reads an env-derived flag (conjunction, no
             top-level ||), or calls a host helper whose body reads one (getenv / g_rs64_* / *_on / *_en()).
  then, for the rest (UNGATED effectful), the hand table RULES keyed by PATCH tag:
  CORRECT    restores retail semantics N64Recomp got wrong (link register, delay slot, $zero write, cross-function branch,
             trap stubs) - no switch needed.
  HOSTPLUMB  routes a guest call/load into a host replacement with the same contract.
  GUARD      game-behaviour change that only acts on a value retail would fault on (wild pointer, OOB, 0/0) - documented.
  BEHAV      game-behaviour change on legal values - must be documented and should carry a ROGUESQ_<X>=0 switch.
  OPEN       no verdict: --check exits 1.

Inputs: --pristine DIR (regen_front.sh output + rename_generated_symbols.py) and --tree DIR (regen_replay.sh output).
  tools/regen_front.sh S/pristine; cp -R S/pristine S/renamed; python3 tools/rename_generated_symbols.py S/renamed
  cp -R S/pristine S/replay; tools/regen_replay.sh S/replay    (the trailing host-code census gates may fail: the fixups
  have all run by then)
--controls plants one hunk of every class into an in-memory copy and checks the verdict. --check exits 1 on OPEN/BEHAV-undoc.
"""
import argparse, collections, difflib, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FN = re.compile(r'^RECOMP_FUNC void (\w+)\(')
TAG = re.compile(r'PATCH:?\s*([^*\n]{0,60}?)(?:\*/|--| —|;|\(|$)', re.M)
GATE = re.compile(r'getenv|\bg_rs64_\w+|\brs64_\w*_on\b|\w+_en\(\)|_enabled\b|\bs_\w*(?:on|enabled|en)\b|__builtin_expect\(\w+, 0\)'
                  r'|\bRS64_S\d+_[A-Z]+\(')
# breadcrumbs that look like gate tokens but are unconditional stores
NOT_GATE = re.compile(r'g_rs64_last_guest_pc|g_rs64_last_\w+ =')
EFF = re.compile(r'ctx->[rf]\d+(?:\.\w+)?\s*(?:=|\+=|-=|\*=|\|=|&=)(?!=)|MEM_\w+\([^;]*?\)\s*=(?!=)|\bgoto\b|\breturn\b'
                 r'|\(rdram, ctx(?:, [^)]*)?\)|\bdo_break\(|__builtin_trap')
CALL = re.compile(r'\b((?:rs64_|rs\d|s\d{3,4}_)\w*)\s*\(')

# Hand verdicts for every UNGATED effectful tag (s7558). key: tag prefix -> (class, note).
RULES = [
    # CORRECT: retail semantics N64Recomp gets wrong
    ('s1971 bltzal-link', 'CORRECT', 'bltzal writes $ra; N64Recomp dropped the link'),
    ('s2475 JAL link', 'CORRECT', 'jal $ra link restored'),
    ('s3277', 'CORRECT', 'delay slot executed before the jal; N64Recomp also emitted a post-call copy (commented out)'),
    ('s7081 selfbranch', 'CORRECT', 'fixup_selfbranch: the goto is the retail beq target; the sbx return only under g_rs64_sbx_on'),
    # GATED by hand: the analyser cannot see the gate
    ('s7103 camfix', 'GATED', 's7102_c4 = s7102_cam4_on() (env); off -> retail 0X3'),
    ('s4889 first gate-zero dereg', 'GATED', 'ROGUESQ_S4889_FIRST_DEREG default ON (=0 off): a GQ default-on lever, listed there'),
    ('s5728 bool suppress', 'GATED', 's_m[] filled only from ROGUESQ_SUPPRESS_BOOL'),
    ('s7239 widewin merge', 'GATED', 'g_rs64_s7239_skip set only by the widewin path (ROGUESQ_ASPECT); 0 -> retail +0x28'),
    ('s6860 hudelem', 'GATED', 'inside if (an && ...): an = ROGUESQ_HUD_ANCHOR'),
    ('s7104 cellcull', 'GATED', 's7104_flush returns unless s7104_live and the env-opened s7101_cf log'),
    ('s6311 edgefade', 'GATED', 'en6311 bits set only from its getenv pair (fade scale / log)'),
    ('s6286 pregrow', 'GATED', 'inside if (_pd < 2 && rs64_s6099_en())'),
    ('s6836 hangar fov', 'GATED', 'i6836 = 1 only when ROGUESQ_HANGAR_FOV is set'),
    ('s6718 intro vsu', 'GATED', 'vi = rs64_s6718_on() && ...; ctx->r4 changes only when vi'),
    ('s1978 drain-base/hdr', 'GUARD', 'drain-timeout hang breaker: after 1e7 spin iterations force idle (retail would spin forever)'),
    # BEHAV: game behaviour on legal values, default differs from retail
    # INERT by hand: value-preserving rewrites and one-shot prints
    ('s5520 b40 writer log', 'INERT', 'sb kept as MEM_B = (uint8_t)(v0 & 0xFF); prints <=200 lines for 0x80130B40 (ungated log)'),
    ('s2190 m5 scalar', 'INERT', 'matcher displaced a pristine sw; the store is kept, wrapped by the gated s5798 macro'),
    # HOSTPLUMB: same contract through a host routine
    ('s4984 atomic', 'HOSTPLUMB', 'voice count/base loaded via an atomic host read of the same guest field'),
    ('s4700 cbtable', 'HOSTPLUMB', 'musyxSynthFrame skipped while the host pauses the synth (s4562 audio thread handoff)'),
    # GUARD: acts only on a value retail would fault on
    ('musyxKeyOnVoice div-trap', 'GUARD', 'teq div-by-zero trap (retail: break exception) -> early return'),
    ('s6963 cellidx', 'HOSTPLUMB', 'rs64_s6963_post records the lookup into a host memo; writes no ctx/guest state'),
]


def funcs(text):
    out, cur, buf = {}, None, []
    for l in text.splitlines():
        m = FN.match(l)
        if m:
            if cur:
                out[cur] = buf
            cur, buf = m.group(1), []
            if l.rstrip().endswith('}') and '{' in l:  # one-line wrapper: RECOMP_FUNC void f(...) { ...; f_sNNNN_inner(...); }
                out[cur], cur = [l[l.index('{') + 1:].rstrip()[:-1]], None
        elif cur is not None:
            buf.append(l)
            if l in ('}', ';}'):
                out[cur], cur, buf = buf, None, []
    if cur:
        out[cur] = buf
    return out


def stmt(l):
    s = l.strip()
    return '' if not s or s.startswith('//') else s


_HOST = None


def host_index():
    """name -> body text for every function defined in owned host code (src/) and lib/N64ModernRuntime."""
    global _HOST
    if _HOST is None:
        _HOST = {}
        for d in ('src', 'lib/N64ModernRuntime/librecomp/src', 'lib/N64ModernRuntime/ultramodern/src'):
            for p in (ROOT / d).rglob('*'):
                if p.suffix in ('.c', '.cpp', '.h', '.hpp', '.inl') and p.is_file():
                    index_defs(p.read_text(errors='replace'), _HOST)
    return _HOST


DEF = re.compile(r'(?:^|[;}]\s*|\bstatic\s+|\binline\s+|extern "C"\s+)(?:static\s+|inline\s+)*[A-Za-z_][\w\*]*(?:\s+[\w\*]+)*?\s*\*?\s*\b((?:rs64_|rs\d|s\d{3,4}_)\w*|\w+_s\d{4}_(?:inner|impl))\s*\([^;{()]*(?:\([^()]*\)[^;{()]*)*\)\s*\{', re.M)


def index_defs(text, into):
    for m in DEF.finditer(text):
        i, depth = m.end() - 1, 0
        for j in range(i, min(len(text), i + 20000)):
            c = text[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    into.setdefault(m.group(1), text[i:j + 1])
                    break


def helper_gated(name, local, seen=None):
    seen = seen or set()
    if name in seen or len(seen) > 4:
        return False
    seen.add(name)
    body = local.get(name) or host_index().get(name)
    if body is None:
        return False
    if GATE.search(NOT_GATE.sub('', body)):
        return True
    return any(helper_gated(c, local, seen) for c in CALL.findall(body) if c != name)


IDENT = re.compile(r'\b[A-Za-z_]\w*\b')
ASSIGN = re.compile(r'(?:^|[;{(,]\s*|\b(?:static\s+)?(?:const\s+)?(?:unsigned\s+|signed\s+)?(?:int|char|float|double|uint\d+_t|int\d+_t|bool|unsigned)\s*\*?\s*)'
                    r'([A-Za-z_]\w*)\s*=(?!=)([^;]*)')


def taint(text):
    """Identifiers whose value derives from an env read inside text (fixpoint over assignments)."""
    t = set()
    base = NOT_GATE.sub('', text)
    for _ in range(4):
        n = len(t)
        for m in ASSIGN.finditer(base):
            rhs = m.group(2)
            if GATE.search(rhs) or any(i in t for i in IDENT.findall(rhs)):
                t.add(m.group(1))
        if len(t) == n:
            break
    return t


def is_gate(expr, tainted):
    expr = NOT_GATE.sub('', expr)
    return bool(GATE.search(expr)) or any(i in tainted for i in IDENT.findall(expr))


def cond_gated(cond, tainted=frozenset()):
    if not is_gate(cond, tainted):
        return False
    depth = 0
    for i, c in enumerate(cond):  # a top-level || means the effect can run without the flag
        depth += (c == '(') - (c == ')')
        if depth == 0 and cond[i:i + 2] == '||':
            return False
    return True


# a condition that is true only for a value retail would fault on: a guest pointer outside KSEG0 RDRAM, misaligned, or 0
WILDX = re.compile(r'<\s*0x800[0-9A-Fa-f]{5}u?|\brs64_s4805_a9_bad\(|!=\s*0xFFFFFFFFu?|>=\s*(?:RS64_RAM_TOP|0x80[48]00000u?)|>\s*0x807FFFFFu?|&\s*(?:3u?|0x3u?)\b|==\s*0(?:u|x0)?\b'
                   r'|!\s*\(?\s*\w+\s*\)?\s*$')


def wild_taint(text):
    """Identifiers assigned from a wild-pointer test (int bad = (p < 0x80000000u || p >= RS64_RAM_TOP))."""
    t = set()
    for m in ASSIGN.finditer(text):
        if WILDX.search(m.group(2)):
            t.add(m.group(1))
    return t


def is_wild(cond, wild):
    if not cond:
        return False
    # every top-level || term must be a wild test (a FORCE env flag beside it only adds logging/forcing under env)
    terms, depth, cur = [], 0, ''
    for i, ch in enumerate(cond):
        depth += (ch == '(') - (ch == ')')
        if depth == 0 and cond[i:i + 2] == '||':
            terms.append(cur); cur = ''
            continue
        if not (cur == '' and ch == '|'):
            cur += ch
    terms.append(cur)
    terms = [x.strip(' |()') for x in terms if x.strip(' |()')]
    def ok(x):
        return bool(WILDX.search(x)) or any(i in wild for i in IDENT.findall(x)) or bool(re.search(r'_force\b', x))
    return bool(terms) and all(ok(x) for x in terms)


def split_if(r):
    """'if (c) rest' / '} else if (c) {' -> (c, rest) with paren matching, else (None, r)."""
    m = re.match(r'\s*(?:\}\s*else\s+)?(?:if|while|for)\s*\(', r)
    if not m:
        return None, r
    i, depth = m.end() - 1, 0
    for j in range(i, len(r)):
        depth += (r[j] == '(') - (r[j] == ')')
        if depth == 0:
            return r[i + 1:j], r[j + 1:]
    return r[i + 1:], ''


def classify_hunk(old, new, local):
    """old/new: statement lists. Returns (cls, residual effectful statements)."""
    olds = [s for s in map(stmt, old) if s]
    news = [s for s in map(stmt, new) if s]
    joined = '\n'.join(news)
    rewrite = any(o not in joined for o in olds)
    tainted = taint(joined) | local.get('__ftaint__', set())
    stack, eff, conds = [], [], []
    wild = wild_taint(joined)
    unguarded = []  # effectful statements NOT under a wild-pointer condition
    for s in news:
        r = s
        for o in olds:
            r = r.replace(o, '')
        r = re.sub(r'/\*.*?\*/', '', r)
        r = re.sub(r'//.*$', '', r)
        # walk the statement as a sequence of if-prefixed segments: a gate on any enclosing if covers the rest
        gated_here, rest, seg_conds, here, body_at = False, r, 0, [], 0
        while True:
            c, rest2 = split_if(rest)
            if c is None:
                break
            seg_conds += 1
            here.append(c)
            body_at = len(r) - len(rest2)
            if cond_gated(c, tainted):
                gated_here = True
                break
            rest = rest2
        tail = rest if not gated_here else ''
        dflt = r
        for _ in range(3):
            dflt = re.sub(r'\(\s*!?\s*([A-Za-z_]\w*)\s*\?\s*([^:()?]+?)\s*:\s*([^()?]+?)\s*\)',
                          lambda m: m.group(3) if is_gate(m.group(1), tainted) else m.group(0), dflt)
            dflt = re.sub(r'([(,]\s*)!?\s*([A-Za-z_]\w*)\s*\?\s*([^:(),?]+?)\s*:\s*([^(),?]+?)\s*([),])',
                          lambda m: m.group(1) + m.group(4) + m.group(5) if is_gate(m.group(2), tainted) else m.group(0), dflt)
        dflt = re.sub(r'\s*/\*.*?\*/', '', dflt).strip()
        if dflt != r.strip() and (dflt in olds or not EFF.search(dflt.replace(';', '')) or any(dflt == re.sub(r'\s*/\*.*?\*/', '', o).strip() for o in olds)):
            gated_here = True  # retail form whenever the flag is off
        tern = re.search(r'=\s*\(?\s*!?\s*\(?([A-Za-z_][\w.>-]*)[^?;]*\?', r)
        if tern and is_gate(tern.group(1), tainted):
            gated_here = True  # x = gate ? new : old
        if EFF.search(r) and not gated_here and not any(stack):
            body = tail if seg_conds else r
            if EFF.search(body) or seg_conds == 0:
                calls = [c for c in CALL.findall(r)]
                if not (calls and all(helper_gated(c, local) for c in calls)):
                    eff.append(s)
                    if not any(is_wild(c, wild) for c in here + conds):
                        unguarded.append(s)
        first = True
        for at, ch in enumerate(r):  # in order: "if (x < 0) { ... }" opens and closes on one line
            if ch == '{':
                body = first and at >= body_at  # braces inside the condition (statement expressions) are not the body
                stack.append(gated_here if body else False)
                conds.append(' && '.join(here) if body else '')
                if body:
                    first = False
            elif ch == '}' and stack:
                stack.pop()
                conds.pop()
        if r.startswith('} else') and conds and here == []:
            conds[-1] = ''  # an else branch is not under the if's condition
    if rewrite and not eff:
        calls = CALL.findall(joined)
        return ('GATED' if (calls and all(helper_gated(c, local) for c in calls)) or is_gate(joined, tainted) else 'UNGATED'), olds
    if not eff:
        return ('GATED' if is_gate(joined, tainted) else 'INERT'), []
    if not unguarded:
        return 'WILDGUARD', eff
    return 'UNGATED', eff


def tag_of(lines):
    m = TAG.search('\n'.join(lines))
    return re.sub(r'\s+', ' ', m.group(1).strip())[:48] if m else 'untagged'


STMT_RULES = [
    (r'^0 = ', 'CORRECT', '$zero write discarded'),
    (r'^__builtin_trap\(\);', 'CORRECT', 'unreachable data-gap stub'),
    (r'^L_[0-9A-F]{8}:$', 'CORRECT', 'label realign (fixup_label_realign)'),
    (r'M5_B40_VALUE.*!= \'0\'\) \? ctx->r2 : 0', 'BEHAV', 'MusyX gate 0x800A0F50 store at 0x8008EB40: default stores 0, retail '
     'stores v0; ROGUESQ_M5_B40_VALUE=1 = retail. CONTRADICTS s4701 (documented default pass-through); CURRENT-TRUTH s7558'),
    (r'M5_C88_VALUE.*== \'0\'\) \? 0 : ctx->r2', 'GATED', 'MusyX gate store at 0x8008EC88: default retail v0, ROGUESQ_M5_C88_VALUE=0 stores 0'),
    (r'^rs5858_inner\(rdram, ctx\);$', 'GATED', 's5858 wrapper: the retail call runs first under if (!rs5858_en); this one only when ROGUESQ_LOG_HITS=1'),
    (r'^ctx->r3 = dlentry_tail_prewalk_\d+;$', 'GUARD', 'reserveAndEmitDLEntry tail walk: next ptr outside RDRAM -> keep the pre-walk node'),
]


# whole-function verdicts: a wrapper whose pristine body moved into a static (not RECOMP_FUNC) inner the matcher cannot pair
FUNC_RULES = {
    'npcGroundTroopUpdate': ('HOSTPLUMB', 's5858 wrapper: pristine body moved to static rs5858_inner, called on both paths'),
}


def rule_for(tag, eff=()):
    for rx, cls, note in STMT_RULES:
        if eff and all(re.search(rx, e) for e in eff):
            return cls, note
    return rule_for_tag(tag)


def rule_for_tag(tag):
    for k, cls, note in RULES:
        if tag.startswith(k):
            return cls, note
    return 'OPEN', ''


def census(pristine, tree, plants=None):
    rows = []
    files = sorted(tree.glob('funcs_*.c'))
    glob = {}
    ftaint = set()
    for f in files:
        t = f.read_text()
        index_defs(t, glob)
        fscope = '\n'.join(l for l in t.splitlines() if not l.startswith('    ') and not l.startswith('RECOMP_FUNC'))
        ftaint |= taint(fscope)
    glob['__ftaint__'] = ftaint
    for f in files:
        t = f.read_text()
        local = glob
        a, b = funcs((pristine / f.name).read_text()), funcs(t)
        if plants and f.name in plants:
            for name, body in plants[f.name].items():
                b[name] = body
                a.setdefault(name, [l for l in body if 'PLANT' not in l])
        for name, bl in b.items():
            al = a.get(name)
            mi = re.match(r'(\w+)_s\d{4}_(?:inner|impl)$', name)
            if al is None and mi and mi.group(1) in a:
                al = a[mi.group(1)]  # pristine body moved into the inner; the one-line wrapper is diffed against []
            elif mi is None and any(n.startswith(name + '_s') and re.match(r'_s\d{4}_(?:inner|impl)$', n[len(name):]) for n in b):
                al = []
            if al is None:
                rows.append((f.name, name, 0, 'NEWFUNC', 'new function', []))
                continue
            if al == bl:
                continue
            sm = difflib.SequenceMatcher(None, al, bl, autojunk=False)
            ca, cb = collections.Counter(map(stmt, al)), collections.Counter(map(stmt, bl))
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == 'equal':
                    continue
                cls, eff = classify_hunk(al[i1:i2], bl[j1:j2], local)
                if cls == 'UNGATED' and op == 'insert':
                    eff = [e for e in eff if cb[e] > ca[e]]  # a pristine statement the matcher displaced is not new
                    if not eff:
                        cls = 'MOVED'
                elif cls == 'UNGATED' and op == 'delete' and all(cb[stmt(l)] >= ca[stmt(l)] for l in al[i1:i2] if stmt(l)):
                    cls, eff = 'MOVED', []
                tag = tag_of(bl[j1:j2] + al[i1:i2])
                if eff:  # the tag on (or last before) the first effectful statement, not the hunk's first breadcrumb
                    hl = bl[j1:j2]
                    k = next((x for x, l in enumerate(hl) if l.strip() == eff[0]), None)
                    if k is not None:
                        for l in reversed(hl[:k + 1]):
                            if TAG.search(l):
                                tag = tag_of([l])
                                break
                rows.append((f.name, name, j1, cls, tag, eff))
    return rows


def documented(sid, docs):
    return bool(sid) and re.search(r'\b' + re.escape(sid) + r'\b', docs) is not None


def report(rows, verbose):
    cnt = collections.Counter(r[3] for r in rows)
    wg = collections.Counter(r[4] for r in rows if r[3] == 'WILDGUARD')
    print('WILDGUARD (ungated, acts only on a pointer outside RDRAM / misaligned / 0):', sum(wg.values()), 'hunks,', len(wg), 'tags')
    print('hunks', len(rows), dict(cnt))
    tags = collections.defaultdict(list)
    out = collections.Counter()
    for r in rows:
        if r[3] == 'UNGATED' and r[1] in FUNC_RULES:
            out[FUNC_RULES[r[1]][0]] += 1
            continue
        if r[3] == 'UNGATED':
            sc = next((c for rx, c, _ in STMT_RULES if r[5] and all(re.search(rx, e) for e in r[5])), None)
            if sc:
                out[sc] += 1
                if sc == 'BEHAV':
                    note = next(n for rx, c, n in STMT_RULES if c == 'BEHAV' and all(re.search(rx, e) for e in r[5]))
                    print(f'    1 BEHAV     | {r[0]}:{r[1]}+{r[2]} | {note}')
            else:
                tags[r[4]].append(r)
    docs = '\n'.join((ROOT / p).read_text(errors='replace') for p in
                     ('PORTING-STATE.md', 'docs/CURRENT-TRUTH.md', 'docs/PROJECT-OVERVIEW.md', 'docs/OWNER-OPT-INS.md',
                      'docs/DEFAULT-ON-LEVERS.md') if (ROOT / p).exists())
    bad = []
    for tag, rs in sorted(tags.items(), key=lambda kv: -len(kv[1])):
        cls, note = rule_for(tag)
        sid = (re.match(r's\d{3,4}[a-z]?', tag) or [None])[0]
        doc = documented(sid, docs) if sid else None
        out[cls] += len(rs)
        flag = ''
        if cls == 'OPEN' or (cls == 'BEHAV' and not doc):
            bad.append(tag)
            flag = '  <-- ' + ('OPEN' if cls == 'OPEN' else 'BEHAV undocumented')
        if verbose or flag:
            r = rs[0]
            print(f'{len(rs):5d} {cls:9s} doc={"-" if doc is None else int(doc)} | {tag} | {r[0]}:{r[1]}+{r[2]} | '
                  f'{(r[5][0] if r[5] else "")[:110]}{flag}')
    used = {k for k, _, _ in RULES if any(t.startswith(k) for t in tags)}
    unused = [k for k, _, _ in RULES if k not in used]
    if unused:
        print('rules matching no UNGATED hunk (stale, informational):', '; '.join(unused))
    print('UNGATED by verdict', dict(out), 'tags', len(tags), 'open/undoc', len(bad))
    return bad


def controls():
    """Plant one hunk per class into a synthetic pristine/tree pair and check the verdicts."""
    base = ['    uint64_t hi = 0;', '    // 0x80001000: lw $v0, 0x0($a0)', '    ctx->r2 = MEM_W(ctx->r4, 0X0);', '}']
    cases = {
        'inert': (['    rs64_s9999_note(0x80001000u); /* PATCH: s9999 note */'], 'INERT'),
        'gated': (['    if (__builtin_expect(g_rs64_s9999_on, 0)) ctx->r2 = 0; /* PATCH: s9999 g */'], 'GATED'),
        'clamp': (['    if (ctx->r2 > 0x10) ctx->r2 = 0x10; /* PATCH: s9998 clamp */'], 'UNGATED'),
        'logonly': (['    if (ctx->r2 >= RS64_RAM_TOP) { if (s_x_enabled) { fprintf(stderr, "x"); } ctx->r2 = 0; } /* PATCH: s9997 g */'],
                    'WILDGUARD'),
        'wild': (['    uint32_t h = U32(ctx->r2);', '    if (h < 0x80000000u || h >= RS64_RAM_TOP) {', '    ctx->r2 = 0;', '    }'], 'WILDGUARD'),
        'oneline': (['    static int s_e = -1;', '    if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_X"); s_e = e != 0; }',
                     '    if (ctx->r2 >= RS64_RAM_TOP) { if (s_e) { fprintf(stderr, "x"); } ctx->r2 = 0; } /* PATCH: s9993 */'], 'WILDGUARD'),
        'stmtexpr': (['    if (rs64_x_en() && ({ uint32_t _w = 1; while (_w < 4) { ++_w; } _w == 4; })) {', '    MEM_W(0, ctx->r4) = 0;', '    }'], 'GATED'),
        'oneline2': (['    static int s_e = -1;', '    if (s_e < 0) { const char* e = getenv("ROGUESQ_LOG_X"); s_e = e != 0; }',
                      '    if (ctx->r2 > 0x40) { if (s_e) { fprintf(stderr, "x"); } ctx->r2 = 0x40; } /* PATCH: s9992 */'], 'UNGATED'),
        'orforce': (['    if (bad || s_force_enabled) { ctx->r2 = 0; } /* PATCH: s9996 */'], 'UNGATED'),
        'zero': (['    // 0 = ctx->r8 + 1; /* PATCH: write to $zero discarded */'], 'INERT'),
    }
    ok = 0
    for name, (ins, want) in cases.items():
        new = base[:3] + ins + base[3:]
        cls, _ = classify_hunk([], ins, {})
        good = cls == want
        ok += good
        print(f'control {name:8s} want {want:8s} got {cls:8s} {"ok" if good else "FAIL"}')
    # rewrite with a gated helper (s6820 shape) and an ungated rewrite
    c1, _ = classify_hunk(['    ctx->r2 = SIGNED(ctx->r2) < 0X15 ? 1 : 0;'],
                          ['    ctx->r2 = SIGNED(ctx->r2) < rs64_pl_t() ? 1 : 0;'],
                          {'rs64_pl_t': '{ static int on = -1; if (on < 0) on = getenv("X") != 0; return on ? 42 : 0x15; }'})
    c2, _ = classify_hunk(['    ctx->r2 = SIGNED(ctx->r2) < 0X15 ? 1 : 0;'],
                          ['    ctx->r2 = SIGNED(ctx->r2) < 0X16 ? 1 : 0; /* PATCH: s9995 */'], {})
    c3, _ = classify_hunk(['    ctx->r2 = MEM_W(ctx->r4, 0X0);'],
                          ['    { RS64_S7484_LD(0x80001000u, ctx->r4, 0X0, 4); ctx->r2 = MEM_W(ctx->r4, 0X0); }'], {})
    for name, got, want in (('gatedhelper', c1, 'GATED'), ('rewrite', c2, 'UNGATED'), ('ldwrap', c3, 'GATED')):
        good = got == want
        ok += good
        print(f'control {name:8s} want {want:8s} got {got:8s} {"ok" if good else "FAIL"}')
    n = len(cases) + 3
    # rule table: an unknown tag must be OPEN, a correctness tag CORRECT
    for tag, want in (('s9994 new guard', 'OPEN'), ('s7081 selfbranch', 'CORRECT'), ('s1971 bltzal-link at 0x1', 'CORRECT')):
        got = rule_for(tag)[0]
        good = got == want
        ok += good
        n += 1
        print(f'control rule {tag[:20]:20s} want {want:8s} got {got:8s} {"ok" if good else "FAIL"}')
    print(f'controls {ok}/{n}')
    return ok == n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pristine', default=str(ROOT / 'scratch/s7558/renamed'))
    ap.add_argument('--tree', default=str(ROOT / 'scratch/s7558/replay'))
    ap.add_argument('--controls', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    if a.controls:
        sys.exit(0 if controls() else 1)
    rows = census(pathlib.Path(a.pristine), pathlib.Path(a.tree))
    bad = report(rows, a.v)
    sys.exit(1 if (a.check and bad) else 0)


if __name__ == '__main__':
    main()
