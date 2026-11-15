#!/usr/bin/env python3
"""s7378 class AU: census of every RT64::SharedQueueResources field access.

s7377 (class AT) closed the present-thread reads of the shared maps only. SharedQueueResources is one struct touched by
four threads (gfx = RT64 State/Application/render_context on the ultramodern gfx thread, rt64_render = WorkloadQueue,
rt64_present = PresentQueue, init = Application::setup before the queue threads exist) with three different mutexes.

For every access `sharedResources->F` / `sharedQueueResources->F` (and every member access through a reference alias
`T &name = ...->F[...]`, and every call of a header setter, which writes its fields under configurationMutex) in the
files below, the tool prints: file:line, field, R/W, function, thread, and the mutexes lexically held at that line
(scoped_lock / unique_lock / lock_guard until their brace scope closes or `.unlock()`, explicit `X.lock()/unlock()`,
and a function whose body opens with a scoped lock holds it for the whole body).

Per field verdict:
  CONFINED  every access from one thread (init accesses do not count: they precede the threads)
  ATOMIC    declared std::atomic in the header
  GUARDED   one mutex held on every write and on every read from a thread other than a writer's
  REVIEW    anything else -> needs a hand verdict in tools/s7378_shared_res_reviewed.tsv
            (BENIGN / ORDERED <handoff> / IDLE <why> / FIXED <how> / RACE).
Fields whose only access is the declaration/setter are listed as UNUSED.

--check : exit 1 on a REVIEW field without a hand verdict, or a hand verdict for a field that is no longer REVIEW
          (stale), or a positive-control failure.
--rev R : analyse lib/rt64 at git revision R (HEAD = upstream+committed submodule state; used as the pre-fix control).
Positive control (always run): setSwapChainRate's write of swapChainRate must read lock {configurationMutex};
the present thread's resolutionScale read must read {configurationMutex}; s7377's colorImageAddressVector snapshot
in threadPresent must read {managerMutex}.
"""
import argparse, os, re, subprocess, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, 'lib', 'rt64')
HDR = 'src/hle/rt64_shared_queue_resources.h'
FILES = [('rt64', 'src/hle/rt64_workload_queue.cpp'), ('rt64', 'src/hle/rt64_present_queue.cpp'),
         ('rt64', 'src/hle/rt64_state.cpp'), ('rt64', 'src/hle/rt64_application.cpp'),
         ('main', 'src/main/rt64_render_context.cpp')]
TSV = os.path.join(ROOT, 'tools', 's7378_shared_res_reviewed.tsv')

THREAD = {
    ('rt64_workload_queue.cpp', 'threadConfigurationUpdate'): 'rt64_render',
    ('rt64_workload_queue.cpp', 'threadConfigurationValidate'): 'rt64_render',
    ('rt64_workload_queue.cpp', 'threadRenderFrame'): 'rt64_render',
    ('rt64_workload_queue.cpp', 'renderThreadLoop'): 'rt64_render',
    ('rt64_workload_queue.cpp', 'updateMultisampling'): 'gfx',
    ('rt64_present_queue.cpp', 'threadPresent'): 'rt64_present',
    ('rt64_present_queue.cpp', 'threadLoop'): 'rt64_present',
    ('rt64_present_queue.cpp', 'skipInterpolation'): 'rt64_present',
    ('rt64_application.cpp', 'setup'): 'init',
    ('rt64_application.cpp', 'end'): 'init',
}
FILE_DEFAULT = {'rt64_state.cpp': 'gfx', 'rt64_application.cpp': 'gfx', 'rt64_render_context.cpp': 'gfx'}
SETTERS = {  # header inline setters: fields written, all under configurationMutex
    'setSwapChainSize': ['swapChainWidth', 'swapChainHeight', 'swapChainSizeChanged'],
    'setSwapChainRate': ['swapChainRate'],
    'setUserConfig': ['userConfig', 'userConfigChanged', 'fbConfigChanged', 'newConfigValidated'],
    'setEmulatorConfig': ['emulatorConfig'], 'setEnhancementConfig': ['enhancementConfig'],
    'setRtConfig': ['rtConfig', 'rtConfigChanged'],
}
SKIP_FIELDS = {'configurationMutex', 'managerMutex', 'interpolatedMutex', 'workloadMutex', 'interpolatedCondition',
               'framebufferManager', 'renderTargetManager', 'updateMultisampling'} | set(SETTERS)
FUNC = re.compile(r'^( {0,4})(?=\S)(?!if\b|for\b|while\b|switch\b|else\b|return\b|case\b|do\b|\})[\w:<>&*,\s]*?\b(\w+)\s*\([^;{}]*\)\s*(const\s*)?(override\s*)?\{?\s*$')
LOCKDECL = re.compile(r'(?:scoped_lock|unique_lock|lock_guard)(?:<[^>]*>)?\s+(\w+)\s*[({][^;]*?(\w+Mutex)\s*(,\s*std::defer_lock\s*)?[)}]')
WRITE_AFTER = re.compile(r'^\s*(?:\[[^\]]*\])?\s*(?:\.\s*\w+\s*)*(?:=(?!=)|\+=|-=|\|=|&=|\^=|\+\+|--|\.(?:push_back|emplace_back|insert|emplace|erase|clear|resize|reset)\s*\()')


def load(kind, rel, rev):
    base = SUB if kind == 'rt64' else ROOT
    if rev and kind == 'rt64':
        return subprocess.run(['git', '-C', SUB, 'show', f'{rev}:{rel}'], capture_output=True, text=True, check=True).stdout
    return open(os.path.join(base, rel)).read()


def header_fields(text):
    fields, atomic = [], set()
    body = text.split('struct SharedQueueResources', 1)[1]
    for m in re.finditer(r'^ {8}(?=\w)([\w:<>,\s*]+?)\s+(\w+)(\[\d+\])?\s*(?:=[^;]*|\{[^;]*\})?;', body, re.M):
        typ, name = m.group(1), m.group(2)
        if typ.strip() in ('return',) or '(' in typ:
            continue
        if name not in fields:
            fields.append(name)
        if 'atomic' in typ:
            atomic.add(name)
    return fields, atomic


def strip(line):
    line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
    return line.split('//', 1)[0]


def analyse_file(fname, text, fields):
    rows = []
    lines = text.split('\n')
    func, fdepth, depth = None, 0, 0
    held = []          # list of [mutex, depth_at_decl, varname, active]
    alias = {}         # name -> field
    incomment = False
    for i, raw in enumerate(lines):
        code = strip(raw)
        if incomment:
            if '*/' in code:
                code = code.split('*/', 1)[1]; incomment = False
            else:
                continue
        if '/*' in code:
            pre, _, post = code.partition('/*')
            if '*/' in post:
                code = pre + post.split('*/', 1)[1]
            else:
                code = pre; incomment = True
        fm = FUNC.match(code)
        if fm and depth <= 2:
            func, fdepth, held, alias = fm.group(2), depth, [], {}
        ln = i + 1
        # lock events
        for m in LOCKDECL.finditer(code):
            held.append([m.group(2), depth, m.group(1), not m.group(3)])
        for m in re.finditer(r'(\w+Mutex)\.(lock|unlock)\(\)', code):
            if m.group(2) == 'lock':
                held.append([m.group(1), -1, None, True])
            else:
                for h in held:
                    if h[0] == m.group(1) and h[3]:
                        h[3] = False
        for m in re.finditer(r'\b(\w+)\.(lock|unlock)\(\)', code):
            for h in held:
                if h[2] == m.group(1):
                    h[3] = (m.group(2) == 'lock')
        locks = sorted({h[0] for h in held if h[3]})
        thread = THREAD.get((fname, func), FILE_DEFAULT.get(fname, '?'))
        # alias declarations
        am = re.search(r'&\s*(\w+)\s*=\s*[\w.]*?(?:sharedResources|sharedQueueResources)->(\w+)', code)
        if am and am.group(2) in fields:
            alias[am.group(1)] = am.group(2)
        # direct accesses
        for m in re.finditer(r'(?:sharedResources|sharedQueueResources)->(\w+)', code):
            f = m.group(1)
            if f in SETTERS:
                for sf in SETTERS[f]:
                    rows.append((fname, ln, sf, 'W', func, thread, ['configurationMutex'], raw.strip(), 'setter:' + f))
                continue
            if f == 'updateMultisampling':
                rows.append((fname, ln, 'interpolatedFrames', 'W', func, thread, locks, raw.strip(), 'updateMultisampling'))
                continue
            if f in SKIP_FIELDS or f not in fields:
                continue
            rest = code[m.end():]
            rw = 'W' if WRITE_AFTER.match(rest) else 'R'
            if am and am.group(2) == f and am.end() == m.end():
                rw = 'A'   # alias bind: counted through member accesses below
            rows.append((fname, ln, f, rw, func, thread, locks, raw.strip(), ''))
        for name, f in alias.items():
            if am and am.group(1) == name:
                continue
            for m in re.finditer(rf'(?<![\w.>]){name}\s*(\.\s*\w+|\[[^\]]*\]|\.(?:size|resize)\s*\()', code):
                rest = code[m.end():]
                meth = re.match(r'\.(push_back|emplace_back|insert|emplace|erase|clear|resize|reset)$', m.group(1).replace(' ', '').rstrip('('))
                rw = 'W' if (WRITE_AFTER.match(rest) or (meth and (rest.lstrip().startswith('(') or m.group(1).endswith('(')))) else 'R'
                rows.append((fname, ln, f, rw, func, thread, locks, raw.strip(), 'alias:' + name + m.group(1).replace(' ', '')))
        # braces
        for ch in code:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                held = [h for h in held if not (h[1] >= 0 and h[1] > depth)]
                if depth <= fdepth:
                    held = []
    return rows


def verdicts(rows, fields, atomic):
    by = defaultdict(list)
    for r in rows:
        if r[3] != 'A':
            by[r[2]].append(r)
    out = {}
    for f in fields:
        if f in SKIP_FIELDS:
            continue
        rs = by.get(f, [])
        live = [r for r in rs if r[5] != 'init']
        threads = {r[5] for r in live}
        if not live:
            out[f] = ('UNUSED' if not rs else 'CONFINED', threads, rs)
        elif f in atomic:
            out[f] = ('ATOMIC', threads, rs)
        elif len(threads) == 1:
            out[f] = ('CONFINED', threads, rs)
        else:
            writers = {r[5] for r in live if r[3] == 'W'}
            need = [r for r in live if r[3] == 'W' or (r[5] not in writers)]
            common = set.intersection(*[set(r[6]) for r in need]) if need else set()
            out[f] = ('GUARDED' if common else 'REVIEW', threads, rs)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--rev')
    ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    fields, atomic = header_fields(load('rt64', HDR, a.rev))
    rows = []
    for kind, rel in FILES:
        rows += analyse_file(os.path.basename(rel), load(kind, rel, a.rev), set(fields))
    ok = True
    # positive controls
    def pc(name, pred, want):
        nonlocal ok
        hit = [r for r in rows if pred(r)]
        good = bool(hit) and all(set(want) <= set(r[6]) for r in hit)
        print(f'CONTROL {name}: {"PASS" if good else "FAIL"} ({len(hit)} rows, locks {[r[6] for r in hit][:3]})')
        ok &= good
    pc('setSwapChainRate W swapChainRate {configurationMutex}', lambda r: r[8] == 'setter:setSwapChainRate', ['configurationMutex'])
    pc('present resolutionScale R {configurationMutex}', lambda r: r[2] == 'resolutionScale' and r[5] == 'rt64_present', ['configurationMutex'])
    if not a.rev:
        snap = [r for r in rows if r[4] == 'threadPresent' and 'colorImageAddressVector' in r[7]]
        print(f'CONTROL s7377 colorImageAddressVector snapshot: {len(snap)} lines (map field, skipped by design: '
              f'checked by tools/s7377_present_lock_table.py)')
    v = verdicts(rows, fields, atomic)
    reviewed = {}
    if os.path.exists(TSV):
        for line in open(TSV):
            if line.strip() and not line.startswith('#'):
                p = line.rstrip('\n').split('\t')
                reviewed[p[0]] = (p[1], p[2] if len(p) > 2 else '')
    counts = defaultdict(int)
    for f in fields:
        if f not in v:
            continue
        verdict, threads, rs = v[f]
        counts[verdict] += 1
        hand = reviewed.get(f)
        tag = f'  hand={hand[0]}' if hand else ''
        print(f'{f:26s} {verdict:9s} threads={",".join(sorted(threads)) or "-":28s} rows={len(rs)}{tag}')
        if a.v or verdict == 'REVIEW':
            for r in rs:
                if r[3] == 'A':
                    continue
                print(f'    {r[0]}:{r[1]} {r[3]} {r[4]}[{r[5]}] locks={",".join(r[6]) or "NONE"} {r[8]}')
        if a.check:
            if verdict == 'REVIEW' and not hand:
                print(f'  CHECK FAIL: {f} REVIEW without hand verdict'); ok = False
            if hand and verdict not in ('REVIEW', 'ATOMIC') and hand[0] not in ('FIXED', 'CONFINED', 'GUARDED'):
                print(f'  CHECK FAIL: stale hand verdict for {f} (now {verdict})'); ok = False
    print('summary:', dict(counts), 'rows', len(rows))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
