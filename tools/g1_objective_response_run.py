#!/usr/bin/env python3
"""One selected-level flight; kill the recipe process group on probe completion."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


def summarize(out, tag, elapsed_s=None, done=None, level=0):
    rows, joins, forces, sends, changes, arms = [], [], {}, {}, [], []
    crash = 0
    in_epoch = False
    log = out / 'run.log'
    if log.exists():
        with log.open(errors='replace') as stream:
            for n, line in enumerate(stream, 1):
                if '[objresp-epoch]' in line:
                    in_epoch = True
                if '[objresp-' in line or (in_epoch and '[eff2] SEND' in line):
                    row = {'line': n, 'event': line.strip()}
                    rows.append(row)
                    fields = dict(re.findall(r'(\w+)=([^\s]+)', line))
                    if '[objresp-force]' in line:
                        forces[fields['seq']] = (n, fields)
                    elif '[objresp-send]' in line:
                        sends[(fields['node'], fields['desc'])] = (n, fields)
                    elif '[eff2] SEND' in line and level == 0:
                        sends[(fields['n'], fields['d'])] = (n, fields)
                    elif '[objresp-arm]' in line:
                        arms.append(row)
                    elif '[objresp-readback]' in line and fields.get('initialized') == '1' and fields['old'] != fields['new']:
                        changes.append(row)
                    elif '[objresp-write]' in line and fields['old'] != fields['new']:
                        force = forces.get(fields['force_seq'])
                        send = sends.get((fields.get('node', ''), fields.get('desc', '')))
                        if force and send and force[0] < send[0] < n:
                            f = force[1]
                            if level == 1 and (send[1].get('force_seq') != fields['force_seq'] or send[1].get('proj') != f.get('proj') or send[1].get('npc') != f['npc']):
                                continue
                            if (f['node'], f['npc'], f['desc']) == (fields['node'], fields['victim'], fields['desc']):
                                joins.append({'force_line': force[0], 'send_line': send[0], 'write_line': n,
                                              'seq': fields['force_seq'], 'vi': fields['vi'], 'age_vi': fields['age_vi'],
                                              'node': fields['node'], 'npc': fields['victim'], 'desc': fields['desc'],
                                              'id': int(fields['id']), 'callback_relevant': int(fields['id']) in ((1,) if level == 0 else (13, 40, 41)), 'pc': fields['pc'], 'old': fields['old'], 'new': fields['new']})
                    if '[objresp-done]' in line:
                        done = line.strip()
                        in_epoch = False
                if re.search(r'CRASH|SIGSEGV|SIGBUS|abort', line):
                    crash += 1
    for join in joins:
        for read in changes:
            fields = dict(re.findall(r'(\w+)=([^\s]+)', read['event']))
            if read['line'] > join['write_line'] and int(fields['id']) == join['id'] and fields['new'] == join['new']:
                join['readback_line'] = read['line']
                join['readback_vi'] = fields['vi']
                break
    populations = []
    for arm in range(3):
        live, candidates, control, accepted = set(), set(), set(), set()
        identities = {}
        for row in rows:
            fields = dict(re.findall(r'(\w+)=([^\s]+)', row['event']))
            if fields.get('arm') != str(arm):
                continue
            key = (fields.get('node'), fields.get('npc'), fields.get('desc'))
            if '[objresp-live]' in row['event'] or '[objresp-candidate]' in row['event']:
                identities[key] = fields
                if fields.get('selected') == '1':
                    if '[objresp-live]' in row['event']:
                        live.add(key)
                    elif fields.get('reason') == 'eligible':
                        candidates.add(key)
                if ('[objresp-candidate]' in row['event'] and fields.get('mark_all') == '1'
                        and fields.get('id') == '10' and fields.get('c1f') == '1'
                        and float(fields.get('radius', 0)) > 0):
                    control.add(key)
            elif '[objresp-send]' in row['event']:
                identity = identities.get(key, {})
                if identity.get('selected') == '1':
                    accepted.add(key)
        populations.append(dict(arm=arm, sampled_named_live=len(live), named_eligible_candidates=len(candidates),
                                id10_mark_all_controls=len(control), named_send_identities=len(accepted),
                                live_without_candidate=[list(k) for k in sorted(live - candidates)]))
    relevant = [j for j in joins if j['callback_relevant']]
    incidental = [j for j in joins if not j['callback_relevant']]
    result = dict(tag=tag, level=level, analyzer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), elapsed_s=elapsed_s, done=done, crashlines=crash,
                  populations=populations, arms=arms, readback_changes=changes, linked_objective_changes=relevant, linked_incidental_changes=incidental,
                  completed_chains=sum('readback_line' in j for j in relevant),
                  completed_incidental_chains=sum('readback_line' in j for j in incidental), linked_counter1_changes=relevant if level == 0 else [], rows=rows)
    (out / 'response.json').write_text(json.dumps(result, indent=2) + '\n')
    with (out / 'response.log').open('w') as stream:
        for row in rows:
            stream.write(f"L{row['line']} {row['event']}\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'arms', 'readback_changes', 'linked_counter1_changes', 'linked_objective_changes', 'linked_incidental_changes')}
                     | {'linked_objective_changes': len(relevant), 'linked_incidental_changes': len(incidental), 'readback_changes': len(changes)}))
    return 0 if done and not crash else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='fresh TAG_SUFFIX (never overwrite evidence)')
    parser.add_argument('--analyze', action='store_true', help='rebuild the joined table from an existing tag')
    parser.add_argument('--level', type=int, choices=(0, 1), default=0)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = root / 'scratch/agent/m6' / (f'g1_lvl{args.level}' + args.tag)
    if args.analyze:
        if not (out / 'run.log').exists():
            parser.error(f'missing log: {out}')
        previous = json.loads((out / 'response.json').read_text()) if (out / 'response.json').exists() else {}
        return summarize(out, args.tag, previous.get('elapsed_s'), level=args.level)
    if out.exists():
        parser.error(f'evidence path already exists: {out}')
    lock = subprocess.check_output(['/usr/sbin/ioreg', '-n', 'Root', '-d1'], text=True)
    if re.search(r'"CGSSessionScreenIsLocked"\s*=\s*Yes', lock):
        parser.error('screen locked: key-driven route cannot run')
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(LEVEL=str(args.level), TAG_SUFFIX=args.tag, HOLD_S='150',
               ROGUESQ_OBJECTIVE_RESPONSE='1', ROGUESQ_OBJECTIVE_RESPONSE_LEVEL=str(args.level), ROGUESQ_TELE_BOLT='1', ROGUESQ_LOG_HITS='1')
    manifest = {'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                'files': {}, 'env': {k: v for k, v in env.items()
                                    if k.startswith(('ROGUESQ_', 'PROBE_')) or k in ('LEVEL', 'TAG_SUFFIX', 'HOLD_S')}}
    for rel in ('build/RogueSquadron64Recomp', 'tools/apply_s6657_objective_response.py',
                'tools/g1_objective_response_run.py', 'tools/apply_s5857_dmg_log.py',
                'scratch/agent/g1_level_coverage_common.zsh',
                'scratch/agent/m6_god_common.sh'):
        manifest['files'][rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with (out / 'wrapper.log').open('w') as wrapper:
        process = subprocess.Popen(['zsh', 'scratch/agent/g1_level_coverage_common.zsh'],
                                   cwd=root, env=env, stdout=wrapper, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        start = time.monotonic()
        done = None
        crashed = False
        offset = 0
        try:
            while time.monotonic() - start < 360:
                log = out / 'run.log'
                if log.exists():
                    if log.stat().st_size < offset:
                        offset = 0
                    with log.open('rb') as stream:
                        stream.seek(offset)
                        for line in stream:
                            if re.search(rb'\[CRASH\]|SIGSEGV|SIGBUS|\[ABORT\]', line):
                                crashed = True
                            if b'[objresp-done]' in line:
                                done = line.decode(errors='replace').strip()
                        offset = stream.tell()
                if done or crashed or process.poll() is not None:
                    break
                time.sleep(0.5)
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    return summarize(out, args.tag, round(time.monotonic() - start, 2), done, args.level)



if __name__ == '__main__':
    raise SystemExit(main())
