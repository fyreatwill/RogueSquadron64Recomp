#!/usr/bin/env python3
"""s7377 class AT: lock-state table for every present-thread access to the shared RT64 maps.

Walks PresentQueue::threadPresent in lib/rt64/src/hle/rt64_present_queue.cpp and, for each access to
fbManager / targetManager / colorImageAddressVector / interpolatedColorTargets, prints the workloadMutex
state at that line:
  LOCKED   - a lock that is still open on every path to the line (explicit lock at an enclosing scope, a
             default-on env-gated lock whose block closed (if (s7377Early) / if (s_pqlock ...)), or a
             RAII unique_lock locked in an enclosing scope)
  LOCKED*  - locked, except on a branch that unlocked in a sibling block (named in the note)
  COND     - only locked on some branch (lock taken inside a closed non-default branch)
  NONE     - no lock on the path
and the origin: UPSTREAM (line text present in the submodule HEAD = upstream author's commit) or PORT.

Lexical, path-insensitive approximation (brace scopes, lambdas counted as scopes). --check compares
against tools/s7377_present_lock_reviewed.tsv (key = access text + occurrence) and exits 1 on any row
without a verdict, or a verdict LOCKED-REQUIRED row whose state is not LOCKED.
--assume-off models ROGUESQ_S7377_EARLYLOCK=0 (positive control: viFb find must read NONE, s7376 rows LOCKED).
--rev <git-rev> analyses lib/rt64's file at that revision instead (HEAD = upstream positive control).
"""
import argparse, re, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, 'lib', 'rt64')
REL = 'src/hle/rt64_present_queue.cpp'
TSV = os.path.join(ROOT, 'tools', 's7377_present_lock_reviewed.tsv')
ACCESS = re.compile(r'\b(fbManager|targetManager)\s*\.\s*(\w+)|colorImageAddressVector|interpolatedColorTargets|\bs7377Colors\b')
DEFAULT_ON = re.compile(r'if\s*\(\s*(s7377Early|s_pqlock)\b')


def load(rev):
    if rev:
        return subprocess.run(['git', '-C', SUB, 'show', f'{rev}:{REL}'], capture_output=True, text=True, check=True).stdout
    return open(os.path.join(SUB, REL)).read()


def strip_code(line):
    line = re.sub(r'"(\\.|[^"\\])*"', '""', line)
    line = re.sub(r"'(\\.|[^'\\])*'", "''", line)
    return line.split('//', 1)[0]


def analyse(text):
    lines = text.split('\n')
    start = next(i for i, l in enumerate(lines) if 'void PresentQueue::threadPresent(' in l)
    end = next(i for i in range(start + 1, len(lines)) if re.match(r'\s*void PresentQueue::', lines[i]))
    scope = []          # stack of block ids
    block_head = {}     # block id -> header code line text
    next_id = [0]
    events = []         # (lineno, kind, scope_tuple, block_header_of_innermost, extra)
    raii = {}           # name -> scope tuple where declared
    rows = []
    in_block_comment = False
    for i in range(start, end):
        raw = lines[i]
        code = strip_code(raw)
        if in_block_comment:
            if '*/' in code:
                code = code.split('*/', 1)[1]; in_block_comment = False
            else:
                continue
        if '/*' in code and '*/' not in code:
            code = code.split('/*', 1)[0]; in_block_comment = True
        ln = i + 1
        cur = tuple(scope)
        # events on this line (evaluated in the scope in force at the line start)
        m = re.search(r'std::unique_lock<std::mutex>\s+(\w+)\(\s*ext\.sharedResources->workloadMutex', code)
        if m:
            raii[m.group(1)] = cur
        for name, sc in list(raii.items()):
            if re.search(rf'\b{name}\.(lock|try_lock)\(\)', code):
                events.append((ln, 'raii', cur, name))
        if re.search(r'workloadMutex\.lock\(\)', code):
            events.append((ln, 'lock', cur, None))
        if re.search(r'workloadMutex\.unlock\(\)', code):
            events.append((ln, 'unlock', cur, None))
        acc = ACCESS.search(code)
        if acc and 'RenderTargetManager &' not in code and 'FramebufferManager &' not in code and 'std::vector<uint32_t> &s7377Colors' not in code:
            rows.append((ln, acc.group(0).replace(' ', ''), cur, raw.strip()))
        # braces
        for ch in code:
            if ch == '{':
                next_id[0] += 1; scope.append(next_id[0]); block_head[next_id[0]] = code
            elif ch == '}':
                if scope:
                    scope.pop()
    return lines, rows, events, block_head


def state_for(row, events, block_head, lines):
    ln, _, sc, _ = row
    held, note = 'NONE', ''
    for (eln, kind, esc, extra) in events:
        if eln > ln:
            break
        on_path = esc == sc[:len(esc)]
        if kind == 'raii':
            if on_path:
                held, note = 'LOCKED', f'raii {extra}@{eln}'
            continue
        # header of the innermost block containing the event
        head = block_head.get(esc[-1], '') if esc else ''
        if kind == 'lock':
            if on_path:
                held, note = 'LOCKED', f'lock@{eln}'
            elif DEFAULT_ON.search(head):
                held, note = 'LOCKED', f'default-on lock@{eln}'
            elif held == 'NONE':
                held, note = 'COND', f'branch lock@{eln}'
        elif kind == 'unlock':
            if on_path:
                held, note = 'NONE', f'unlock@{eln}'
            elif held == 'LOCKED':
                held, note = 'LOCKED*', note + f'; sibling unlock@{eln}'
    # RAII objects go out of scope: a raii lock whose scope is not a prefix is not held (handled by on_path)
    return held, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rev')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--tsv', default=TSV)
    ap.add_argument('--assume-off', action='store_true', help='model ROGUESQ_S7377_EARLYLOCK=0 (control)')
    a = ap.parse_args()
    global DEFAULT_ON
    if a.assume_off:
        DEFAULT_ON = re.compile(r'if\s*\(\s*(s_pqlock)\b')
    text = load(a.rev)
    upstream = set(l.strip() for l in load('HEAD').split('\n'))
    lines, rows, events, block_head = analyse(text)
    reviewed = {}
    if os.path.exists(a.tsv):
        for l in open(a.tsv):
            if l.startswith('#') or not l.strip():
                continue
            k, v = l.rstrip('\n').split('\t')[:2]
            reviewed[k] = v
    seen = {}
    bad = 0
    print('line\tstate\torigin\taccess\tverdict\tnote\ttext')
    for row in rows:
        ln, accname, sc, txt = row
        st, note = state_for(row, events, block_head, lines)
        origin = 'UPSTREAM' if txt in upstream else 'PORT'
        n = seen.get(txt, 0); seen[txt] = n + 1
        key = f'{txt}#{n}'
        v = reviewed.get(key, '-')
        flag = ''
        if a.check:
            if v == '-':
                flag = ' <-- NO VERDICT'; bad += 1
            elif v.startswith('LOCKED') and not st.startswith('LOCKED'):
                flag = ' <-- EXPECTED LOCKED'; bad += 1
        print(f'{ln}\t{st}\t{origin}\t{accname}\t{v}\t{note}\t{txt[:110]}{flag}')
    if a.check:
        print(f'# check: rows={len(rows)} bad={bad}')
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
