#!/usr/bin/env python3
"""One forced-level-0 flight; kill the recipe process group on probe completion."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


def summarize(out, tag, elapsed_s=None, done=None):
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
                    elif '[eff2] SEND' in line:
                        sends[(fields['n'], fields['d'])] = n
                    elif '[objresp-arm]' in line:
                        arms.append(row)
                    elif '[objresp-readback]' in line and fields.get('initialized') == '1' and fields['old'] != fields['new']:
                        changes.append(row)
                    elif '[objresp-write]' in line and fields['id'] == '1' and fields['old'] != fields['new']:
                        force = forces.get(fields['force_seq'])
                        send = sends.get((fields.get('node', ''), fields.get('desc', '')))
                        if force and send and force[0] < send < n:
                            f = force[1]
                            if (f['node'], f['npc'], f['desc']) == (fields['node'], fields['victim'], fields['desc']):
                                joins.append({'force_line': force[0], 'send_line': send, 'write_line': n,
                                              'seq': fields['force_seq'], 'vi': fields['vi'], 'age_vi': fields['age_vi'],
                                              'node': fields['node'], 'npc': fields['victim'], 'desc': fields['desc'],
                                              'old': fields['old'], 'new': fields['new']})
                    if '[objresp-done]' in line:
                        done = line.strip()
                        in_epoch = False
                if re.search(r'CRASH|SIGSEGV|SIGBUS|abort', line):
                    crash += 1
    result = dict(tag=tag, elapsed_s=elapsed_s, done=done, crashlines=crash,
                  arms=arms, readback_changes=changes, linked_counter1_changes=joins, rows=rows)
    (out / 'response.json').write_text(json.dumps(result, indent=2) + '\n')
    with (out / 'response.log').open('w') as stream:
        for row in rows:
            stream.write(f"L{row['line']} {row['event']}\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'arms', 'readback_changes', 'linked_counter1_changes')}
                     | {'linked_counter1_changes': len(joins), 'readback_changes': len(changes)}))
    return 0 if done and not crash else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='fresh TAG_SUFFIX (never overwrite evidence)')
    parser.add_argument('--analyze', action='store_true', help='rebuild the joined table from an existing tag')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = root / 'scratch/agent/m6' / ('g1_lvl0' + args.tag)
    if args.analyze:
        if not (out / 'run.log').exists():
            parser.error(f'missing log: {out}')
        previous = json.loads((out / 'response.json').read_text()) if (out / 'response.json').exists() else {}
        return summarize(out, args.tag, previous.get('elapsed_s'))
    if out.exists():
        parser.error(f'evidence path already exists: {out}')
    lock = subprocess.check_output(['/usr/sbin/ioreg', '-n', 'Root', '-d1'], text=True)
    if re.search(r'"CGSSessionScreenIsLocked"\s*=\s*Yes', lock):
        parser.error('screen locked: key-driven route cannot run')
    out.mkdir(parents=True)
    env = os.environ.copy()
    env.update(LEVEL='0', TAG_SUFFIX=args.tag, HOLD_S='150',
               ROGUESQ_OBJECTIVE_RESPONSE='1', ROGUESQ_TELE_BOLT='1', ROGUESQ_LOG_HITS='1')
    manifest = {'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                'files': {}, 'env': {k: v for k, v in env.items()
                                    if k.startswith(('ROGUESQ_', 'PROBE_')) or k in ('LEVEL', 'TAG_SUFFIX', 'HOLD_S')}}
    for rel in ('build/RogueSquadron64Recomp', 'tools/apply_s6657_objective_response.py',
                'tools/g1_objective_response_run.py', 'scratch/agent/g1_level_coverage_common.zsh',
                'scratch/agent/m6_god_common.sh'):
        manifest['files'][rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    with (out / 'wrapper.log').open('w') as wrapper:
        process = subprocess.Popen(['zsh', 'scratch/agent/g1_level_coverage_common.zsh'],
                                   cwd=root, env=env, stdout=wrapper, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        start = time.monotonic()
        done = None
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
                            if b'[objresp-done]' in line:
                                done = line.decode(errors='replace').strip()
                        offset = stream.tell()
                if done or process.poll() is not None:
                    break
                time.sleep(0.5)
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    return summarize(out, args.tag, round(time.monotonic() - start, 2), done)



if __name__ == '__main__':
    raise SystemExit(main())
