#!/usr/bin/env python3
"""Reconcile saved G1 ctl/TELE logs without treating call counts as objectives."""
import argparse
from collections import Counter, defaultdict
import gzip
from pathlib import Path
import re
import sys as _s7848_sys, os as _s7848_os
_s7848_sys.path.insert(0, _s7848_os.path.dirname(_s7848_os.path.abspath(__file__)))
from rs64_zopen import zopen, resolve  # s7848: retained logs may survive only as .zst


PHASE = re.compile(r"^\[phase\] vi_width=(\d+).*origin=0x([\dA-Fa-f]+).*update_screen #(\d+)")
SNAP = re.compile(r"^\[(objsnap(?:-t)?)\] id=(\d+) (\d+)->(\d+)")
COUNT = re.compile(r"^\[objcount\] get id=(\d+) val=(\d+)")
REQUEST = re.compile(r"^\[m47\] fn=requestMissionTransitionMode .*?a0=(\d+).*?ph=(\d+).*?vi=(\d+)")


def scan(lines):
    result = dict(route=[], start=None, stop=None, tele=[], segin=[], heartbeat=[],
                  snapshots=defaultdict(list), gets=defaultdict(list),
                  writers=Counter(), requests=Counter(), request_first={},
                  bools=[], cleanup=[], counter_prestate=[], objective_callers=[])
    active = False
    for number, line in enumerate(lines, 1):
        m = re.search(r"\[lvsel\] init .*?B40=(\d+)", line)
        if m:
            result['route'].append((number, int(m[1])))
        m = PHASE.match(line)
        if m:
            if active:
                result['stop'] = (number, line.strip())
                break
            if int(m[1]) == 512 and int(m[2], 16) in (0x690400, 0x620400):
                result['start'] = (number, line.strip())
                active = True
        if not active:
            continue
        if line.startswith('[sph] TELE '):
            result['tele'].append(number)
        elif line.startswith('[sph] SEGIN '):
            result['segin'].append(number)
        elif line.startswith('[objsnap-t] hb '):
            result['heartbeat'].append((number, line.strip()))
        elif m := SNAP.match(line):
            result['snapshots'][(m[1], int(m[2]))].append((number, int(m[3]), int(m[4])))
        elif m := COUNT.match(line):
            result['gets'][int(m[1])].append((number, int(m[2])))
        elif m := re.match(r"^\[objwr\] (\w+)", line):
            result['writers'][m[1]] += 1
        elif m := REQUEST.match(line):
            mode = int(m[1])
            result['requests'][mode] += 1
            result['request_first'].setdefault(mode, (number, int(m[2]), int(m[3])))
        elif line.startswith('[hudbit4dump]'):
            result['bools'].append((number, line.strip().split('| timers:')[0]))
        elif line.startswith('[mend] fn=endMissionCleanup '):
            result['cleanup'].append((number, line.strip()))
        elif line.startswith('[ctr1] set '):
            m = re.search(r' c=(\d+),(\d+),(\d+)', line)
            if m:
                result['counter_prestate'].append((number, *map(int, m.groups())))
        elif m := re.match(r'\[cco\] (lv\d+_checkComplexObjectives) ', line):
            if not result['objective_callers']:
                result['objective_callers'].append((number, m[1]))
    return result


def load(root, level, arm):
    base = root / f'g1_lvl{level}{arm}'
    for name in ('run.log', 'run.log.gz'):
        path = base / name
        if resolve(path):
            with zopen(path) as stream:
                return path, scan(stream)
    return base, None


def events(data):
    return {key: [(a, b) for _, a, b in rows]
            for key, rows in data['snapshots'].items()}


def checks(rows):
    for level in range(1, 10):
        for arm in ('ctl', 'tele'):
            assert rows[level][arm][1]['route'][0][1] == level
    for level, arm in ((7, 'tele'), (8, 'tele'), (9, 'ctl'), (9, 'tele')):
        assert rows[level][arm][1]['start'], (level, arm, 'missing flight scope')
    seven = events(rows[7]['tele'][1])
    eight = events(rows[8]['tele'][1])
    assert seven['objsnap', 2] == [(0, 2), (2, 3), (3, 0)], seven
    assert eight['objsnap', 6] == [(0, 1), (1, 2), (2, 3), (3, 4)], eight
    assert ('objsnap', 2) not in events(rows[7]['ctl'][1])
    assert ('objsnap', 6) not in events(rows[8]['ctl'][1])
    assert rows[7]['tele'][1]['tele'] and rows[8]['tele'][1]['tele']
    assert not rows[7]['ctl'][1]['tele'] and not rows[8]['ctl'][1]['tele']
    assert set(key[1] for key in events(rows[9]['ctl'][1])) == {1, 3, 5}
    assert set(key[1] for key in events(rows[9]['tele'][1])) == {1, 3, 5}
    synthetic = scan([
        '[objsnap] id=2 90->91\n',
        '[phase] vi_width=512 origin=0x00690400 update_screen #100\n',
        '[objsnap] id=2 0->1\n',
        '[phase] vi_width=1024 origin=0x00790400 update_screen #200\n',
        '[objsnap] id=2 1->99\n',
    ])
    assert events(synthetic) == {('objsnap', 2): [(0, 1)]}


def brief(data):
    if not data or not data['start']:
        return 'unknown (missing log or explicit flight scope)'
    parts = []
    for (tag, index), values in sorted(data['snapshots'].items()):
        chain = ', '.join(f'{a}>{b}@L{n}' for n, a, b in values[:8])
        if len(values) > 8:
            chain += f', … ({len(values)} records)'
        parts.append(f'{tag} id={index}: {chain}')
    for index, values in sorted(data['gets'].items()):
        parts.append(f'get id={index}: ' + ', '.join(f'{v}@L{n}' for n, v in values[:8]))
    return '; '.join(parts) or 'no value-change records (not a controlled null)'


def report(rows, legacy):
    out = ['# G1 objective-response saved-evidence table', '',
           'Generated by `python3 tools/g1_objective_evidence.py --check`.', '',
           'Scope: first explicit `[phase] vi_width=512` at origin 0x00690400',
           'or 0x00620400, through the next width transition (exclusive).',
           'L numbers refer to decompressed log lines. No ordinal or event VI is',
           'invented. Scope is a width epoch, not proof of uninterrupted flight.',
           'A missing epoch is unknown. Later re-entries are excluded.', '',
           'TELE records are capped at 10 by the instrument: this is a firing',
           'control, not a hit total or a damage receipt. SEGIN is geometric',
           'intersection, not independently confirmed damage. Writer records are',
           'rate-limited call activity, not successful writes or objective progress.',
           'Snapshot accessors have separate static histories; repeated/discontinuous',
           'records are not a single authoritative counter chain. The snapshot',
           'instruments cover only ids 1–15 and have run-lifetime 400-record budgets.',
           'Heartbeat proves execution only; it is not a value-detection control.',
           'These are animating cross-run arms: differences are descriptive, not',
           'causal A/B proof. All response claims remain single-source.', '',
           '| Level | ctl TELE / tele TELE | ctl values | tele values |',
           '| --- | --- | --- | --- |']
    for level, arms in rows.items():
        ctl, tele = (arms[a][1] for a in ('ctl', 'tele'))
        firing = 'unknown' if not ctl or not tele else f"{len(ctl['tele'])} / {len(tele['tele'])}"
        out.append(f'| {level} | {firing} | {brief(ctl)} | {brief(tele)} |')
    for level, arms in rows.items():
        if not any(data for _, data in arms.values()):
            continue
        out.extend(['', f'## Level {level} provenance and separate gate evidence', ''])
        for arm, (path, data) in arms.items():
            out.append(f'- {arm}: `{path}`')
            if not data:
                out.append('  Missing log; no negative result.')
                continue
            out.append(f"  Selector B40 witnesses: {data['route']}; scope start {data['start']}; stop {data['stop'] or 'EOF'}.")
            out.append(f"  TELE lines {data['tele']}; SEGIN lines {data['segin']}; heartbeat {data['heartbeat']}.")
            out.append('  Writer call records: ' + (', '.join(f'{k}={v}' for k, v in sorted(data['writers'].items())) or 'none') + '.')
            requests = ', '.join(f'a0={mode}: {count} records, first L{data["request_first"][mode][0]} ph={data["request_first"][mode][1]} vi={data["request_first"][mode][2]}' for mode, count in sorted(data['requests'].items()))
            out.append('  Transition requests: ' + (requests or 'none') + '.')
            out.append(f"  Cleanup: {data['cleanup']}; Boolean gate dumps: {data['bools']}.")
    out.extend(['', '## Legacy level-0 evidence (separate route)', '',
                'These runs use g1_fire.sh rather than the forced level-selector',
                'recipe. Caller identity is recorded directly; do not silently',
                'substitute them for missing g1_lvl0ctl/tele logs. `ctr1` logs',
                'counter pre-state at setter entry, not the resulting write.', ''])
    for path, data in legacy:
        out.extend([f'- `{path}`: scope {data["start"]} through {data["stop"] or "EOF"}.',
                    f'  Caller {data["objective_callers"]}; TELE lines {data["tele"]}.',
                    f'  Counter pre-states (line, c1, c2, c10): {data["counter_prestate"]}.'])
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('scratch/agent/m6'))
    parser.add_argument('--check', action='store_true', help='validate known positive and negative saved controls')
    args = parser.parse_args()
    rows = {level: {arm: load(args.root, level, arm) for arm in ('ctl', 'tele')}
            for level in range(19)}
    legacy = []
    for tag in ('s5843', 's5844', 's5845'):
        path = args.root / tag / 'run.log.gz'
        if path.exists():
            with gzip.open(path, 'rt', errors='replace') as stream:
                legacy.append((path, scan(stream)))
    if args.check:
        checks(rows)
        for _, data in legacy:
            assert data['objective_callers'][0][1] == 'lv0_checkComplexObjectives'
    print(report(rows, legacy), end='')


if __name__ == '__main__':
    main()
