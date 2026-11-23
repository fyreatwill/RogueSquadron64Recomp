#!/usr/bin/env python3
"""One selected-level flight; kill the recipe process group on probe completion."""
# s7450 class DG: shared fatal-exit list (tools/agent/fatal_patterns.txt), also used by m6_god_common.sh / fatal_scan.sh
import pathlib as _pl
_FATAL = '|'.join('(?:%s)' % l for l in (_pl.Path(__file__).resolve().parent / 'agent' / 'fatal_patterns.txt').read_text().splitlines() if l)
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys as _s7848_sys, os as _s7848_os
_s7848_sys.path.insert(0, _s7848_os.path.dirname(_s7848_os.path.abspath(__file__)))
from rs64_zopen import zopen, resolve  # s7848: retained logs may survive only as .zst
import signal
import subprocess
import time


def activation_table(rows, ownership):
    table = {'definitions': [], 'predicates': [], 'scalar_writers': {}, 'spawn': {},
             'named_lifetimes': [], 'timer_min': None, 'timer_max': None}
    for row in rows:
        event = row['event']
        f = dict(re.findall(r'(\w+)=([^\s]+)', event))
        if '[objresp-definition]' in event:
            table['definitions'].append(row | {'fields': f})
        elif '[objresp-activation]' in event:
            table['predicates'].append(row | {'fields': f})
            timer = float(f['timer1'])
            table['timer_min'] = timer if table['timer_min'] is None else min(timer, table['timer_min'])
            table['timer_max'] = timer if table['timer_max'] is None else max(timer, table['timer_max'])
        elif '[objresp-scalar]' in event:
            table['scalar_writers'].setdefault(f['pc'], []).append(row | {'fields': f})
        elif '[objresp-spawn]' in event:
            key = f['index'] + ':' + f['pc']
            table['spawn'].setdefault(key, []).append(row | {'fields': f})
    definitions = {d['fields']['desc']: d['fields'] for d in table['definitions']}
    for life in ownership['lifetimes']:
        if life.get('desc') in definitions:
            table['named_lifetimes'].append(life | {'definition': definitions[life['desc']]})
    return table


def qualify_level2_loss(transport, rows):
    lethal = [h for h in transport if h['pre']['lethal'] == '1']
    getters = []
    for row in rows:
        if '[objresp-counter-return]' in row['event']:
            getters.append(row | {'fields': dict(re.findall(r'(\w+)=([^\s]+)', row['event']))})
    dose_count = sum('[objresp-transport-pre]' in r['event'] and 'lethal=1' in r['event'] for r in rows)
    chains = []
    if len(lethal) == dose_count == 1:
        hit = lethal[0]
        for chain in hit.get('objective_chains', []):
            if (hit.get('qualified_lethal') and chain['id'] == 40 and chain['pc'] == '8006594c'
                    and chain['old'] == '0' and chain['new'] == '1' and 'readback_line' in chain):
                for getter in getters:
                    f = getter['fields']
                    if (getter['line'] > chain['readback_line'] and f['pc'] == '801020b8'
                            and f['returned'] == f['memory'] == '1' and f['observed'] == '1'
                            and f['bool109'] == f['bool101'] == '0'):
                        chains.append(chain | {'getter': getter})
    return {'qualified': bool(chains), 'lethal_count': dose_count, 'chains': chains,
            'getter_zero_control': any(g['fields']['returned'] == g['fields']['memory'] == '0' for g in getters),
            'getters': getters}


def dose_self_test():
    import copy
    chain = dict(id=40, pc='8006594c', old='0', new='1', readback_line=40)
    hit = dict(pre={'lethal': '1'}, qualified_lethal=True, objective_chains=[chain])
    rows = [dict(line=30, event='[objresp-transport-pre] lethal=1'), dict(line=50, event='[objresp-counter-return] pc=801020b8 returned=1 memory=1 observed=1 bool109=0 bool101=0')]
    assert qualify_level2_loss([hit], rows)['qualified']
    assert not qualify_level2_loss([hit, hit], rows)['qualified']
    assert not qualify_level2_loss([hit], rows + [dict(line=60, event='[objresp-transport-pre] lethal=1')])['qualified']
    assert not qualify_level2_loss([hit], [])['qualified']
    bad = copy.deepcopy(hit); bad['qualified_lethal'] = False
    assert not qualify_level2_loss([bad], rows)['qualified']
    for key in ('readback_line', 'pc'):
        bad = copy.deepcopy(hit)
        if key == 'readback_line': del bad['objective_chains'][0][key]
        else: bad['objective_chains'][0][key] = 'wrong'
        assert not qualify_level2_loss([bad], rows)['qualified']
    bad = copy.deepcopy(hit); bad['objective_chains'] = []
    assert not qualify_level2_loss([bad], rows)['qualified']
    print('level2 dose fixtures pass: complete, second dose, missing getter, unqualified identity/control, missing readback/store, wrong writer')
    import contextlib
    import io
    import tempfile
    identity = 'node=80210000 npc=80350000 desc=80310000 proj=80370000'
    actor = 'actor=80360000'
    lines = [
        '[objresp-epoch] epoch=1 vi=5000 B40=2',
        '[objresp-counter-return] vi=5000 pc=801020b8 id=40 returned=0 memory=0 observed=0 bool109=0 bool101=0',
        f'[objresp-force] vi=15000 seq=1 {identity}',
        f'[objresp-send] vi=15001 force_seq=1 {identity}',
        f'[objresp-transport-pre] vi=15001 force_seq=1 {identity} {actor} lethal=0 eligible=1 hp=2000 raw=10 requested=10',
        f'[objresp-transport-return] vi=15001 force_seq=1 {identity} {actor} hp_new=1990 returned=1990',
        f'[objresp-force] vi=15020 seq=2 {identity}',
        f'[objresp-send] vi=15021 force_seq=2 {identity}',
        f'[objresp-transport-pre] vi=15021 force_seq=2 {identity} {actor} lethal=1 eligible=1 hp=1990 raw=10 requested=1991',
        f'[objresp-transport-return] vi=15021 force_seq=2 {identity} {actor} hp_new=-1 returned=-1',
        f'[objresp-transport-effect] vi=15021 force_seq=2 {identity} {actor} lethal=1',
        '[objresp-write] vi=15021 node=80210000 victim=80350000 desc=80310000 force_seq=2 age_vi=1 id=40 pc=8006594c old=0 new=1',
        '[objresp-readback] vi=15025 id=40 old=0 new=1 initialized=1',
        '[objresp-counter-return] vi=15025 pc=801020b8 id=40 returned=1 memory=1 observed=1 bool109=0 bool101=0',
        '[objresp-done] vi=15025',
    ]
    fixtures = {
        'complete': (lines, True),
        'wrong_actor': ([s.replace(actor, 'actor=80360004') if 'force_seq=2' in s else s for s in lines], False),
        'missing_ordinary': ([s for s in lines if not ('transport-' in s and 'force_seq=1' in s)], False),
        'missing_force': ([s for s in lines if not ('objresp-force' in s and 'seq=2' in s)], False),
        'wrong_projectile': ([s.replace('proj=80370000', 'proj=80370004') if 'objresp-send' in s and 'force_seq=2' in s else s for s in lines], False),
        'missing_store': ([s for s in lines if 'objresp-write' not in s], False),
        'missing_readback': ([s for s in lines if 'objresp-readback' not in s], False),
        'missing_getter': ([s for s in lines if not ('counter-return' in s and 'returned=1' in s)], False),
        'failure_already_set': ([s.replace('bool109=0', 'bool109=1') for s in lines], False),
        'second_pre_only': (lines + [s.replace('force_seq=2', 'force_seq=3') for s in lines if 'transport-pre' in s and 'force_seq=2' in s], False),
        'second_dose': (lines + [s.replace('force_seq=2', 'force_seq=3') for s in lines if 'transport-' in s and 'force_seq=2' in s], False),
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        for name, (rows, expected) in fixtures.items():
            (out / 'run.log').write_text('\n'.join(rows)+'\n')
            with contextlib.redirect_stdout(io.StringIO()):
                summarize(out, name, level=2)
            result = json.loads((out / 'response.json').read_text())
            assert result['level2_loss']['qualified'] == expected, (name, result['transport'])
            print(name, 'PASS')


def summarize(out, tag, elapsed_s=None, done=None, level=0):
    rows, joins, forces, sends, changes, arms = [], [], {}, {}, [], []
    crash = 0
    in_epoch = False
    log = out / 'run.log'
    if resolve(log):
        with zopen(log) as stream:
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
                            if level >= 1 and (send[1].get('force_seq') != fields['force_seq'] or send[1].get('proj') != f.get('proj') or send[1].get('npc') != f['npc']):
                                continue
                            if (f['node'], f['npc'], f['desc']) == (fields['node'], fields['victim'], fields['desc']):
                                joins.append({'force_line': force[0], 'send_line': send[0], 'write_line': n,
                                              'seq': fields['force_seq'], 'vi': fields['vi'], 'age_vi': fields['age_vi'],
                                              'node': fields['node'], 'npc': fields['victim'], 'desc': fields['desc'],
                                              'id': int(fields['id']), 'callback_relevant': int(fields['id']) in ((1,) if level == 0 else (40,) if level == 2 else (28,) if level == 3 else (13, 40, 41)), 'pc': fields['pc'], 'old': fields['old'], 'new': fields['new']})
                    if '[objresp-done]' in line:
                        done = line.strip()
                        in_epoch = False
                if re.search(_FATAL, line):
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
        live, candidates, control, eligible_control, accepted = set(), set(), set(), set(), set()
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
                        and fields.get('c1f') == '1' and float(fields.get('radius', 0)) > 0):
                    eligible_control.add(key)
                if ('[objresp-candidate]' in row['event'] and fields.get('mark_all') == '1'
                        and fields.get('id') == '10' and fields.get('c1f') == '1'
                        and float(fields.get('radius', 0)) > 0):
                    control.add(key)
            elif '[objresp-send]' in row['event']:
                identity = identities.get(key, {})
                if identity.get('selected') == '1':
                    accepted.add(key)
        populations.append(dict(arm=arm, sampled_named_live=len(live), named_eligible_candidates=len(candidates),
                                id10_mark_all_controls=len(control), mark_all_eligible_controls=len(eligible_control), named_send_identities=len(accepted),
                                live_without_candidate=[list(k) for k in sorted(live - candidates)]))
    ownership = {'census': [], 'handlers': {}, 'retirements': 0, 'selection_controls': [],
                 'candidate_rows': [0, 0, 0], 'unresolved_is_not_absent': True}
    lifetimes = {}
    for row in rows:
        f = dict(re.findall(r'(\w+)=([^\s]+)', row['event']))
        if '[objresp-census]' in row['event'] and 'valid' in f:
            ownership['census'].append(f)
        elif '[objresp-select-control]' in row['event']:
            ownership['selection_controls'].append(f)
        elif '[objresp-retire]' in row['event']:
            ownership['retirements'] += 1
            key = (f['slot'], f['generation'])
            if key in lifetimes: lifetimes[key]['retirement_vi'] = f['vi']
        elif '[objresp-live]' in row['event'] and 'generation' in f:
            key = (f['slot'], f['generation'])
            lifetimes[key] = lifetimes.get(key, {}) | f
        elif '[objresp-candidate]' in row['event']:
            ownership['candidate_rows'][int(f['arm'])] += 1
    ownership['lifetimes'] = list(lifetimes.values())
    for f in lifetimes.values():
        h = ownership['handlers'].setdefault(f['handler'], {'slot_generations': 0, 'typed': f['typed'], 'nodes': set(), 'descriptors': set()})
        h['slot_generations'] += 1
        h['nodes'].add(f['node'])
        h['descriptors'].add(f['desc'])
    for h in ownership['handlers'].values():
        h['nodes'] = sorted(h['nodes'])
        h['descriptors'] = sorted(h['descriptors'])
    transport = []
    pending = {}
    effects = {}
    transport_sends = []
    for row in rows:
        fields = dict(re.findall(r'(\w+)=([^\s]+)', row['event']))
        key = (fields.get('npc'), fields.get('desc'), fields.get('force_seq'))
        if '[objresp-send]' in row['event']:
            transport_sends.append(row | {'fields': fields})
        if '[objresp-transport-pre]' in row['event']:
            pending[key] = row | {'fields': fields}
        elif '[objresp-transport-return]' in row['event']:
            pre = pending.get(key)
            if pre:
                transport.append({'pre_line': pre['line'], 'return_line': row['line'],
                                  'pre': pre['fields'], 'returned': fields})
        elif '[objresp-transport-effect]' in row['event']:
            effects[key] = row | {'fields': fields}
    for hit in transport:
        f = hit['pre']
        key = (f['npc'], f['desc'], f['force_seq'])
        effect = effects.get(key)
        force = forces.get(f['force_seq'])
        hit['exact_force'] = bool(force and (force[1]['node'], force[1]['npc'], force[1]['desc'], force[1]['proj']) ==
                                 (f['node'], f['npc'], f['desc'], f['proj']) and force[0] < hit['pre_line'])
        matching_sends = [r for r in transport_sends if r['line'] < hit['pre_line'] and
            all(r['fields'].get(k) == f.get(k) for k in ('node', 'npc', 'desc', 'proj', 'force_seq'))]
        if matching_sends:
            hit['send_line'] = matching_sends[-1]['line']
        hit['exact_send'] = bool(matching_sends and force and force[0] < matching_sends[-1]['line'])
        hit['ordinary_health_control'] = (f['lethal'] == '0' and f['eligible'] == '1' and
            int(hit['returned']['hp_new']) > 0 and int(f['hp']) - int(hit['returned']['hp_new']) == int(f['raw']) and
            int(f['raw']) > 0 and hit['returned']['returned'] == hit['returned']['hp_new'])
        if effect and effect['line'] > hit['return_line']:
            hit['effect_line'] = effect['line']
            hit['effect'] = effect['fields']
            hit['objective_chains'] = [
                j for j in joins if j['seq'] == f['force_seq'] and j['npc'] == f['npc'] and
                j['desc'] == f['desc'] and j['write_line'] > effect['line']]
    lethal_hits = [h for h in transport if h['pre']['lethal'] == '1']
    lethal_requests = sum('[objresp-transport-pre]' in r['event'] and 'lethal=1' in r['event'] for r in rows)
    for hit in lethal_hits:
        f = hit['pre']
        hit['prior_ordinary_control'] = any(
            h['ordinary_health_control'] and h['exact_force'] and h['exact_send'] and
            h['return_line'] < hit['pre_line'] and h['pre']['force_seq'] != f['force_seq'] and
            all(h['pre'][k] == f[k] for k in ('node', 'npc', 'desc', 'actor')) for h in transport)
        hit['qualified_lethal'] = (len(lethal_hits) == lethal_requests == 1 and hit['exact_force'] and hit['exact_send'] and hit['prior_ordinary_control'] and
            int(f['requested']) == int(f['hp']) + 1 and hit['returned']['returned'] == '-1' and
            hit['returned']['hp_new'] == '-1' and hit.get('effect', {}).get('lethal') == '1')
    dose_validation = dict(lethal_count=lethal_requests,
        ordinary_controls=sum(h['ordinary_health_control'] for h in transport),
        completed_lethal_chains=sum('readback_line' in j for h in lethal_hits if h['qualified_lethal'] for j in h.get('objective_chains', [])))
    relevant = [j for j in joins if j['callback_relevant']]
    incidental = [j for j in joins if not j['callback_relevant']]
    result = dict(tag=tag, level=level, analyzer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), elapsed_s=elapsed_s, done=done, crashlines=crash,
                  populations=populations, ownership=ownership, transport=transport, dose_validation=dose_validation, arms=arms, readback_changes=changes, linked_objective_changes=relevant, linked_incidental_changes=incidental,
                  completed_chains=sum('readback_line' in j for j in relevant),
                  completed_incidental_chains=sum('readback_line' in j for j in incidental), linked_counter1_changes=relevant if level == 0 else [], rows=rows)
    result['activation'] = activation_table(rows, ownership)
    if level == 3:
        result['level3_building'] = qualify_level3(rows)
        result['level3_api'] = qualify_level3_api([r for r in rows if 'api_seq=2' not in r['event']])
        result['level3_loss'] = qualify_level3_loss(rows)
    if level == 7:
        result['level7_ordinary'] = qualify_level6(rows, level=7)
    if level == 6:
        result['level6_ordinary'] = qualify_level6(rows)
    if level == 5:
        result['level5_ordinary'] = qualify_level5([r for r in rows if 'api_seq=2' not in r['event']])
        result['level5_loss'] = qualify_level4_loss(rows, level=5)
    if level == 4:
        result['level4_ordinary'] = qualify_level4([r for r in rows if 'api_seq=2' not in r['event']])
        result['level4_loss'] = qualify_level4_loss(rows)
    if level == 2: result['level2_loss'] = qualify_level2_loss(transport, rows)
    (out / 'response.json').write_text(json.dumps(result, indent=2) + '\n')
    with (out / 'response.log').open('w') as stream:
        for row in rows:
            stream.write(f"L{row['line']} {row['event']}\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'arms', 'readback_changes', 'linked_counter1_changes', 'linked_objective_changes', 'linked_incidental_changes', 'transport', 'ownership', 'activation')}
                     | {'linked_objective_changes': len(relevant), 'linked_incidental_changes': len(incidental), 'readback_changes': len(changes)}))
    return 0 if done and not crash else 1


def qualify_level3(rows):
    parsed = [(r['line'], r['event'], dict(re.findall(r'(\w+)=([^\s]+)', r['event']))) for r in rows]
    forces = [(n, f) for n, e, f in parsed if '[objresp-force]' in e]
    chains = []
    for n, event, f in parsed:
        if '[objresp-building]' not in event or f.get('stage') != '1' or f.get('name') != 'City_1':
            continue
        identity = ('node', 'npc', 'desc', 'proj')
        matching = [(fn, ff) for fn, ff in forces if fn < n and ff['seq'] == f['force_seq'] and all(ff[k] == f[k] for k in identity)]
        sends = [(sn, sf) for sn, se, sf in parsed if '[objresp-send]' in se and sn < n and sf.get('force_seq') == f['force_seq'] and all(sf.get(k) == f[k] for k in identity)]
        entries = [(en, ef) for en, ee, ef in parsed if '[objresp-building]' in ee and ef.get('stage') == '0' and en < n and all(ef.get(k) == f[k] for k in identity + ('message','force_seq'))]
        returns = [(rn, rf) for rn, revent, rf in parsed if '[objresp-building]' in revent and rf.get('stage') == '3' and rn > n and all(rf.get(k) == f[k] for k in identity + ('message','force_seq'))]
        health = int(f['store_old']) - int(f['store_new']) == int(f['request']) > 0 and int(f['store_new']) > 0
        ordered = bool(matching and sends and entries and matching[-1][0] < sends[-1][0] < entries[-1][0] < n)
        complete = bool(len(forces) == 1 and ordered and returns and health and f['pc'] == '8006cfe8' and f['handler'] == '8006cbb0' and f['subtype'] == '20' and returns[0][1]['hp'] == f['store_new'])
        effects = [en for en, ee, ef in parsed if '[objresp-building]' in ee and ef.get('stage') == '2' and ef.get('force_seq') == f['force_seq'] and ef.get('desc') == f['desc']]
        chains.append(dict(store_line=n, fields=f, qualified_ordinary=complete, effect_lines=effects, return_line=returns[0][0] if returns else None))
    readers = [dict(line=n, fields=f) for n, e, f in parsed if '[objresp-building-reader]' in e]
    return dict(force_count=len(forces), ordinary_chains=chains, qualified_ordinary=any(c['qualified_ordinary'] for c in chains), readers=readers,
                reader_values_match=bool(readers) and all(r['fields']['value'] == r['fields']['expected'] for r in readers))


def building_self_test():
    import copy
    identity='node=80210000 npc=80350000 desc=80310000 proj=80370000'
    base=f'{identity} message=80380000 force_seq=1 handler=8006cbb0 subtype=20 name=City_1'
    lines=[f'[objresp-force] seq=1 {identity}', f'[objresp-send] force_seq=1 {identity}',
           f'[objresp-building] stage=0 {base}',
           f'[objresp-building] stage=1 {base} pc=8006cfe8 store_old=2000 store_new=1990 request=10',
           f'[objresp-building] stage=3 {base} hp=1990',
           '[objresp-building-reader] value=100 expected=100']
    def check(ls): return qualify_level3([dict(line=i,event=e) for i,e in enumerate(ls)])['qualified_ordinary']
    assert check(lines)
    for omit in range(5): assert not check(lines[:omit]+lines[omit+1:]),omit
    for old,new in [('store_new=1990','store_new=2000'),('handler=8006cbb0','handler=800ece10'),('hp=1990','hp=1980')]:
        assert not check([l.replace(old,new) for l in lines]), old
    assert not check(lines+[lines[0]])
    assert not check([l.replace('proj=80370000','proj=80370004') if 'objresp-send' in l else l for l in lines])
    print('level3 building fixtures pass: complete, missing joins, health, handler, return, duplicate force, projectile mismatch')

def qualify_level3_api(rows):
    parsed=[(r['line'],r['event'],dict(re.findall(r'(\w+)=([^\s]+)',r['event']))) for r in rows]
    pre=[(n,f) for n,e,f in parsed if '[objresp-api]' in e and f['stage']=='pre']
    post=[(n,f) for n,e,f in parsed if '[objresp-api]' in e and f['stage']=='post']
    matches=[]
    if len(pre)==len(post)==1:
        pn,p=pre[0]; qn,q=post[0]
        identity=('api_seq','desc','node','npc')
        chain=[]
        for stage in ('0','1','3'):
            found=[(n,f) for n,e,f in parsed if '[objresp-building]' in e and f['stage']==stage and pn<n<qn and all(f.get(k)==p[k] for k in identity)]
            if len(found)!=1: break
            chain.append(found[0])
        if len(chain)==3:
            (en,e),(sn,st),(rn,r)=chain
            health=(int(st['store_old'])==int(p['hp']) and int(st['store_new'])==int(p['hp'])-10>0 and
                    int(st['request'])==int(p['request'])==10 and st['hp']==st['store_old'] and
                    r['hp']==q['hp']==q['returned']==st['store_new'])
            route=(p['route']=='named-script' and p['name']=='City_1' and p['handler']==st['handler']=='8006cbb0' and st['pc']=='8006cfe8' and
                   all(f[k]==p[k] for f in (e,st,r) for k in ('slot','handler','detail')) and
                   all(f['subtype']=='20' for f in (e,st,r)) and e['message']==st['message']==r['message'])
            if pn<en<sn<rn<qn and health and route and all(q[k]==p[k] for k in identity):
                matches.append(dict(pre_line=pn,entry_line=en,store_line=sn,return_line=rn,post_line=qn,pre=p,store=st,post=q))
    getters=[dict(line=n,fields=f) for n,e,f in parsed if '[objresp-probe-getter]' in e]
    values={}
    for g in getters: values.setdefault(g['fields']['id'],set()).add(g['fields']['returned'])
    return dict(qualified_ordinary=bool(matches),request_count=len(pre),chains=matches,probe_getters=getters,
                probe_getters_match=bool(getters) and all(g['fields']['probe_call']=='1' and g['fields']['returned']==g['fields']['memory'] for g in getters),
                changing_getter_ids=[i for i,v in values.items() if len(v)>1],
                scope='instrument-invoked original named script damage and pure getters; not player-shot or game-invoked friendlies proof')


def qualify_level6(rows, level=6):
    target = "20_Dest_Tanks_01" if level == 7 else "OBJ_ConYard_Barracks"
    offset = 0x05d0 if level == 7 else 0x4a2c
    prefix = f"[objresp-lvl{level}-"
    parsed=[(r['line'],r['event'],dict(re.findall(r'(\w+)=([^\s]+)',r['event']))) for r in rows]
    pre=[(n,f) for n,e,f in parsed if (prefix+'api]') in e and f.get('stage')=='pre']
    post=[(n,f) for n,e,f in parsed if (prefix+'api]') in e and f.get('stage')=='post']
    fallback=[n for n,e,f in parsed if (prefix+'fallback]') in e]
    effects=[n for n,e,f in parsed if (prefix+'building]') in e and f.get('stage')=='2']
    getters=[dict(line=n,fields=f) for n,e,f in parsed if (prefix+'getter]') in e]
    controls=[dict(line=n,fields=f) for n,e,f in parsed if (prefix+'control]') in e and f.get('mark_all')=='1']
    values={}
    for g in getters:
        if g['fields'].get('returned')==g['fields'].get('memory'):
            values.setdefault(g['fields']['id'],set()).add(g['fields']['returned'])
    changing=[i for i,v in values.items() if len(v)>1]
    matches=[]
    if len(pre)==len(post)==1 and not fallback and not effects:
        pn,p=pre[0];qn,q=post[0]; chain=[]
        for stage in ('0','1','3'):
            found=[(n,f) for n,e,f in parsed if (prefix+'building]') in e and f.get('stage')==stage and pn<n<qn]
            if len(found)!=1: break
            chain.append(found[0])
        if len(chain)==3:
            (en,e),(sn,st),(rn,r)=chain
            identity=('api_seq','desc','node','npc')
            route=(p.get('epoch')=='1' and p.get('arm')=='1' and p.get('route')=='named-script' and
                p.get('name')==target and p.get('handler')=='8006cbb0' and p.get('detail')=='0' and
                int(p['desc'],16)==int(p['base'],16)+offset and int(p['generation'])>0 and
                p.get('source_gate')=='0' and all(q.get(k)==p.get(k) for k in identity) and
                all(f.get(k)==p.get(k) for f in (e,st,r) for k in identity+('slot','generation','handler','detail','epoch','arm','source_gate','effect_gate')) and
                all(f.get('subtype')=='20' for f in (e,st,r)) and e.get('message')==st.get('message')==r.get('message') and
                e.get('source')==st.get('source')==r.get('source') and
                st.get('pc')=='8006cfe8' and r.get('pc')=='8006d8c0')
            address=int(p['desc'],16)+0x6c
            health=(int(st['store_old'])==int(p['hp'])>10 and int(st['store_new'])==int(p['hp'])-10>0 and
                int(st['request'])==int(p['request'])==10 and st['hp']==st['store_old'] and
                r['hp']==q['hp']==q['returned']==st['store_new'] and r['returned']=='1' and
                all(int(f['health_addr'],16)==address for f in (e,st,r)) and int(st['store_addr'],16)==address)
            if pn<en<sn<rn<qn and route and health:
                matches.append(dict(pre_line=pn,entry_line=en,store_line=sn,return_line=rn,post_line=qn,pre=p,store=st,handler_return=r,post=q))
    getter_match=bool(getters) and all(g['fields'].get('probe_call')=='1' and g['fields']['returned']==g['fields']['memory'] for g in getters)
    after=bool(matches) and all(any(g['line']>matches[0]['post_line'] and g['fields']['id']==i for g in getters) for i in (('20',) if level == 7 else ('50','90')))
    reached={f['arm'] for n,e,f in parsed if '[objresp-arm]' in e}
    controlled=reached and reached<={g['fields']['arm'] for g in controls}
    return dict(qualified_health_chain=bool(matches),qualified_ordinary=bool(matches and getter_match and after and controlled and changing),
        request_count=len(pre),chains=matches,fallback_lines=fallback,effect_lines=effects,controls=controls,
        reached_arms=sorted(reached),owned_controls_each_arm=bool(controlled),probe_getters_match=getter_match,
        named_getters_after_request=after,changing_getter_ids=changing,probe_getters=getters,
        scope='ordinary original named API health only; destruction untested; no player-shot or retail-equivalence claim')


def level6_self_test():
    ident='epoch=1 arm=1 api_seq=1 desc=80314a2c node=80210000 npc=80350000'
    common=ident+' slot=42 generation=1 handler=8006cbb0 detail=0 source_gate=0 effect_gate=0 subtype=20 message=80400000 source=65535 health_addr=80314a98'
    events=['[objresp-arm] epoch=1 arm=1',
        '[objresp-lvl6-control] epoch=1 arm=1 mark_all=1',
        '[objresp-lvl6-getter] probe_call=1 id=3 returned=0 memory=0',
        f'[objresp-lvl6-api] stage=pre {ident} base=80310000 slot=42 generation=1 handler=8006cbb0 detail=0 source_gate=0 effect_gate=0 route=named-script name=OBJ_ConYard_Barracks hp=500 request=10',
        f'[objresp-lvl6-building] stage=0 {common}',
        f'[objresp-lvl6-building] stage=1 {common} pc=8006cfe8 hp=500 store_addr=80314a98 store_old=500 store_new=490 request=10',
        f'[objresp-lvl6-building] stage=3 {common} pc=8006d8c0 hp=490 returned=1',
        f'[objresp-lvl6-api] stage=post {ident} hp=490 returned=490',
        '[objresp-lvl6-getter] probe_call=1 id=50 returned=0 memory=0',
        '[objresp-lvl6-getter] probe_call=1 id=90 returned=0 memory=0',
        '[objresp-lvl6-getter] probe_call=1 id=3 returned=1 memory=1']
    def result(es):return qualify_level6([dict(line=i,event=e) for i,e in enumerate(es)])
    assert result(events)['qualified_ordinary']
    for i in range(len(events)):
        assert not result(events[:i]+events[i+1:])['qualified_ordinary'],i
    for old,new in [('base=80310000','base=80310004'),('detail=0','detail=1'),('handler=8006cbb0','handler=800d93c0'),('store_new=490','store_new=491'),('request=10','request=11'),('returned=490','returned=500'),('epoch=1','epoch=2'),('source_gate=0','source_gate=1'),('generation=1','generation=0'),('store_addr=80314a98','store_addr=80314a9c')]:
        assert not result([e.replace(old,new) for e in events])['qualified_ordinary'],old
    for key in ('node','npc','desc','message','generation','source'):
        bad=[e.replace(key+'=',key+'=bad') if 'stage=3' in e else e for e in events]
        assert not result(bad)['qualified_ordinary'],key
    for extra in ('[objresp-lvl6-fallback] stage=0','[objresp-lvl6-building] stage=2',events[3]):
        assert not result(events+[extra])['qualified_ordinary']
    assert result(events[:-1])['qualified_health_chain'] and not result(events[:-1])['qualified_ordinary']
    print('level6 fixtures pass: chain links, ownership/detail/route/HP/return, getter and mark-all controls; sensitivity stays separate')


def level7_self_test():
    ident='epoch=1 arm=1 api_seq=1 desc=803105d0 node=80210000 npc=80350000'
    common=ident+' slot=42 generation=1 handler=8006cbb0 detail=0 source_gate=0 effect_gate=0 subtype=20 message=80400000 source=65535 health_addr=8031063c'
    events=['[objresp-arm] epoch=1 arm=1',
        '[objresp-lvl7-control] epoch=1 arm=1 mark_all=1',
        '[objresp-lvl7-getter] probe_call=1 id=3 returned=0 memory=0',
        f'[objresp-lvl7-api] stage=pre {ident} base=80310000 slot=42 generation=1 handler=8006cbb0 detail=0 source_gate=0 effect_gate=0 route=named-script name=20_Dest_Tanks_01 hp=50 request=10',
        f'[objresp-lvl7-building] stage=0 {common}',
        f'[objresp-lvl7-building] stage=1 {common} pc=8006cfe8 hp=50 store_addr=8031063c store_old=50 store_new=40 request=10',
        f'[objresp-lvl7-building] stage=3 {common} pc=8006d8c0 hp=40 returned=1',
        f'[objresp-lvl7-api] stage=post {ident} hp=40 returned=40',
        '[objresp-lvl7-getter] probe_call=1 id=20 returned=0 memory=0',
        '[objresp-lvl7-getter] probe_call=1 id=3 returned=1 memory=1']
    def result(es):return qualify_level6([dict(line=i,event=e) for i,e in enumerate(es)], level=7)
    assert result(events)['qualified_ordinary']
    for i in range(len(events)):
        assert not result(events[:i]+events[i+1:])['qualified_ordinary'],i
    for old,new in [('base=80310000','base=80310004'),('detail=0','detail=1'),('handler=8006cbb0','handler=800d93c0'),('store_new=40','store_new=41'),('request=10','request=11'),('returned=40','returned=50'),('epoch=1','epoch=2'),('source_gate=0','source_gate=1'),('generation=1','generation=0'),('store_addr=8031063c','store_addr=80310640')]:
        assert not result([e.replace(old,new) for e in events])['qualified_ordinary'],old
    for key in ('node','npc','desc','message','generation','source'):
        bad=[e.replace(key+'=',key+'=bad') if 'stage=3' in e else e for e in events]
        assert not result(bad)['qualified_ordinary'],key
    for extra in ('[objresp-lvl7-fallback] stage=0','[objresp-lvl7-building] stage=2',events[3]):
        assert not result(events+[extra])['qualified_ordinary']
    assert result(events[:-1])['qualified_health_chain'] and not result(events[:-1])['qualified_ordinary']
    print('level7 fixtures pass: chain links, ownership/detail/route/HP/return, getter and mark-all controls; sensitivity stays separate')


def api_self_test():
    ident='api_seq=1 desc=80310000 node=80210000 npc=80350000'
    common=f'{ident} slot=42 handler=8006cbb0 detail=0 subtype=20 message=80400000'
    events=[f'[objresp-api] stage=pre {ident} slot=42 handler=8006cbb0 detail=0 route=named-script name=City_1 hp=2000 request=10',
            f'[objresp-building] stage=0 {common}',
            f'[objresp-building] stage=1 {common} pc=8006cfe8 hp=2000 store_old=2000 store_new=1990 request=10',
            f'[objresp-building] stage=3 {common} hp=1990',
            f'[objresp-api] stage=post {ident} hp=1990 returned=1990']
    def check(es):return qualify_level3_api([dict(line=i,event=e) for i,e in enumerate(es)])['qualified_ordinary']
    assert check(events)
    for i in range(5):assert not check(events[:i]+events[i+1:]),i
    for old,new in [('request=10','request=11'),('store_new=1990','store_new=1991'),('handler=8006cbb0','handler=800ece10'),('returned=1990','returned=2000')]:
        assert not check([e.replace(old,new) for e in events]),old
    assert not check(events+[events[0]])
    assert not check([e.replace('message=80400000','message=80400004') if 'stage=3' in e else e for e in events])
    assert not check([e.replace('npc=80350000','npc=80350004') if 'stage=1' in e else e for e in events])
    print('level3 API fixtures pass: complete, missing stages, dose/store/handler/return, duplicate request, message/identity mismatch')

def qualify_level3_loss(rows):
    parsed=[(r['line'],r['event'],dict(re.findall(r'(\w+)=([^\s]+)',r['event']))) for r in rows]
    ordinary=qualify_level3_api([r for r in rows if 'api_seq=2' not in r['event']])
    pres=[(n,f) for n,e,f in parsed if '[objresp-api]' in e and f.get('stage')=='pre']
    chains=[]
    if len(pres)==2 and ordinary['qualified_ordinary']:
        control=ordinary['chains'][0]
        pn,p=pres[1]
        def find(tag, **fields):
            return [(n,f) for n,e,f in parsed if n>pn and tag in e and all(f.get(k)==v for k,v in fields.items())]
        identity={k:p[k] for k in ('api_seq','desc','node','npc')}
        entries=find('[objresp-building]',stage='0',**identity)
        returns=find('[objresp-building]',stage='3',**identity)
        stores=find('[objresp-building]',stage='1',**identity)
        effects=find('[objresp-building-effect]',**identity)
        posts=find('[objresp-api]',stage='post',**identity)
        if len(entries)==len(returns)==len(stores)==len(effects)==len(posts)==1:
            entryn,entry=entries[0]; rn,ret=returns[0]
            sn,st=stores[0]; en,ef=effects[0]; qn,q=posts[0]
            same=all(p[k]==control['pre'][k] for k in ('desc','node','npc','slot','handler','detail','generation'))
            health=(p['api_seq']=='2' and int(p['request'])==int(p['hp'])+1<=65535 and p['hp']==control['post']['hp'] and st['pc']=='8006cfe8' and
                    st['hp']==st['store_old']==p['hp'] and st['store_new']=='-1' and st['request']==p['request'] and q['hp']==q['returned']=='-1')
            route=(p['handler']==st['handler']=='8006cbb0' and p['slot']==st['slot'] and p['detail']==st['detail'] and st['subtype']=='20' and
                   all(f[k]==p[k] for f in (entry,st,ret) for k in ('slot','handler','detail')) and entry['message']==st['message']==ret['message'] and ret['hp']=='-1' and
                   ef['pc']=='8006d6f0' and ef['id']=='28' and ef['delta']=='1' and ef['delta2']=='1' and all(ef[k]=='0' for k in ('bool','bval','id2')))
            for wn,e,w in parsed:
                if ('[objresp-write]' not in e or not en<wn<qn or w.get('id')!='28' or w.get('pc')!='8006594c' or w.get('old')!='0' or w.get('new')!='1' or w.get('desc')!=p['desc'] or w.get('victim')!=p['npc']): continue
                reads=[(n,f) for n,e,f in parsed if '[objresp-readback]' in e and n>qn and f.get('id')=='28' and f.get('old')=='0' and f.get('new')=='1']
                getters=[(n,f) for n,e,f in parsed if '[objresp-probe-getter]' in e and n>qn and f.get('id')=='28' and f.get('returned')==f.get('memory')=='1']
                done=[(n,f) for n,e,f in parsed if '[objresp-done]' in e and f.get('reason')=='level3-named-response' and all(f.get(k)=='0' for k in ('bool4','bool18','bool21','c22'))]
                if same and health and route and control['post_line']<pn<entryn<sn<en<wn<rn<qn and reads and getters and done and reads[0][0]<getters[0][0]<done[0][0]:
                    chains.append(dict(control=control,pre=p,store=st,effect=ef,post=q,writer=w,readback=reads[0],getter=getters[0],done=done[0]))
    return dict(qualified=bool(chains),requests=len(pres),chains=chains,changing_getter_ids=ordinary['changing_getter_ids'])


def level3_loss_self_test():
    ident='desc=80310000 node=80210000 npc=80350000'
    owner='slot=42 handler=8006cbb0 detail=0 generation=1'
    events=[]
    for seq,hp,request,new in ((1,2000,10,1990),(2,1990,1991,-1)):
        key=f'api_seq={seq} {ident}'
        events += [f'[objresp-api] stage=pre {key} {owner} route=named-script name=City_1 hp={hp} request={request}',
                   f'[objresp-building] stage=0 {key} {owner} subtype=20 message=80400000',
                   f'[objresp-building] stage=1 {key} {owner} subtype=20 message=80400000 pc=8006cfe8 hp={hp} store_old={hp} store_new={new} request={request}']
        if seq==2:
            events += [f'[objresp-building-effect] {key} pc=8006d6f0 bool=0 bval=0 id=28 delta=1 id2=0 delta2=1',
                       f'[objresp-write] pc=8006594c id=28 old=0 new=1 desc=80310000 victim=80350000']
        events += [f'[objresp-building] stage=3 {key} {owner} subtype=20 message=80400000 hp={new}',
                   f'[objresp-api] stage=post {key} hp={new} returned={new}']
    events += ['[objresp-readback] id=28 old=0 new=1',
               '[objresp-probe-getter] probe_call=1 id=28 returned=1 memory=1',
               '[objresp-done] reason=level3-named-response bool4=0 bool18=0 bool21=0 c22=0']
    def check(es): return qualify_level3_loss([dict(line=i,event=e) for i,e in enumerate(es)])['qualified']
    assert check(events)
    for i in range(len(events)): assert not check(events[:i]+events[i+1:]),i
    for old,new in [('generation=1','generation=2'),('request=1991','request=1992'),('store_new=-1','store_new=0'),('pc=8006594c','pc=80065974'),('victim=80350000','victim=80350004'),('bool4=0','bool4=1'),('id2=0','id2=22'),('delta2=1','delta2=0')]:
        mutated=[e.replace(old,new) if ('api_seq=2' in e or '[objresp-write]' in e or '[objresp-done]' in e) else e for e in events]
        assert not check(mutated),old
    assert not check([e.replace('message=80400000','message=80400004') if 'api_seq=2' in e and 'stage=3' in e else e for e in events])
    assert not check(events+[events[5]])
    print('level3 loss fixtures pass: complete, missing links, ownership, dose, health, writer, victim, flags, repeat dose')



def qualify_level4(rows):
    parsed=[(r['line'],r['event'],dict(re.findall(r'(\w+)=([^\s]+)',r['event']))) for r in rows]
    stages={}
    for n,e,f in parsed:
        if '[objresp-wingman]' in e: stages.setdefault(f['stage'],[]).append((n,f))
    names=('api-pre','entry','damage-pre','store','damage-post','api-post')
    chains=[]
    if all(len(stages.get(k,[]))==1 for k in names) and not stages.get('effect'):
        chain=[stages[k][0] for k in names]; ns=[n for n,f in chain]; fs=[f for n,f in chain]
        p,en,b,st,r,q=fs
        identity=('api_seq','node','npc','desc','slot','generation','handler','actor','detail','mode','health_addr')
        exact=all(f.get(k)==p[k] for f in fs for k in identity)
        addr=int(p['health_addr'],16); actor=int(p['actor'],16)
        storage=(st['pc']=='800f2158' and int(p['mode'])!=0 and addr==actor+0x190) or (st['pc']=='800f2148' and p['mode']=='0')
        hp=int(p['hp']); health=hp>10 and all(int(f['hp'])==hp for f in (en,b,st)) and int(st['next'])==hp-10 and all(int(f['hp'])==int(f['returned'])==hp-10 for f in (r,q))
        messages=en['message']==b['message']==st['message']==r['message']==q['message']!='00000000'
        live=[(n,f) for n,e,f in parsed if '[objresp-live]' in e and n<ns[0] and all(f.get(k)==p[k] for k in ('node','npc','desc','slot','generation','handler')) and f.get('owned')=='1' and f.get('canonical')==p['slot']]
        eligible=[(n,f) for n,e,f in parsed if '[objresp-wingman-eligibility]' in e and n<ns[0] and all(f.get(k)==p[k] for k in ('node','npc','desc','slot','generation','handler','actor','health_addr')) and f.get('lookup')==p['desc'] and f.get('reason')=='eligible' and f.get('owned')==f.get('valid')=='1']
        control=[(n,f) for n,e,f in parsed if '[objresp-wingman-control]' in e and n<ns[0] and f.get('mark_all')=='1' and all(f.get(k)==p[k] for k in ('node','actor','mode','detail','health_addr'))]
        getter=[(n,f) for n,e,f in parsed if '[objresp-probe-getter]' in e and n>ns[-1] and f.get('id')=='40' and f.get('returned')==f.get('memory')==q['c40'] and f.get('probe_call')=='1']
        observed=[]
        for stage,left,right in (('0',ns[0],ns[1]),('1',ns[1],ns[2]),('2',ns[3],ns[4])):
            observed.append(any('[objresp-wingman-observed]' in e and left<n<right and f.get('stage')==stage and f.get('action')=='5' and all(f.get(k)==p[k] for k in ('node','npc','desc','actor')) and f.get('message')==en['message'] for n,e,f in parsed))
        store_observed=any('[objresp-wingman-store-observed]' in e and ns[2]<n<ns[3] and f.get('pc')==st['pc'] and f.get('actor')==p['actor'] and f.get('address')==p['health_addr'] and all(f.get(k)==p[k] for k in ('mode','detail')) for n,e,f in parsed)
        no_reap=not any('[objresp-retire]' in e and ns[0]<n<ns[-1] and f.get('slot')==p['slot'] for n,e,f in parsed)
        if (all(observed) and store_observed and ns==sorted(set(ns)) and exact and storage and health and messages and live and eligible and control and getter and no_reap and
            p['api_seq']=='1' and p['handler']=='800d93c0' and all(f['request']=='10' for f in fs) and all(f['c40']==p['c40'] for f in fs) and
            en['pc']=='800d93c0' and b['pc']=='800d9c54' and r['pc']=='800d9c5c'):
            chains.append(dict(lines=dict(zip(names,ns)),pre=p,store=st,post=q,live_line=live[-1][0],eligibility_line=eligible[-1][0],control_line=control[-1][0],getter_line=getter[0][0]))
    values={};getters=[]
    for n,e,f in parsed:
        if '[objresp-probe-getter]' in e:
            getters.append(f); values.setdefault(f['id'],set()).add(f['returned'])
    changing=[k for k,v in values.items() if len(v)>1]
    getters_ok=bool(getters) and all(f['returned']==f['memory'] and f.get('probe_call')=='1' for f in getters)
    return dict(qualified_ordinary=bool(chains) and bool(changing) and getters_ok,exact_health_chain=bool(chains),request_count=len(stages.get('api-pre',[])),chains=chains,changing_getter_ids=changing,getters_match=getters_ok,
                scope='one instrument-invoked original named API ordinary hit; no destruction, named counter response, player-shot or retail-equivalence proof')


def qualify_level5(rows):
    result=qualify_level4(rows)
    parsed=[(r['line'],r['event'],dict(re.findall(r'(\w+)=([^\s]+)',r['event']))) for r in rows]
    epochs=[n for n,e,f in parsed if '[objresp-epoch]' in e and f.get('B40')=='5' and f.get('callback')=='lv5_checkComplexObjectives' and f.get('width')=='512']
    definitions=[(n,f) for n,e,f in parsed if '[objresp-definition]' in e and f.get('name')=='x_wing_wedge' and f.get('offset')=='1afc' and f.get('subtype')=='39' and f.get('id')=='40' and f.get('delta')=='1' and int(f['desc'],16)==int(f['base'],16)+0x1afc]
    result['named_identity']=bool(result['chains']) and len(epochs)==1 and all(any(n<c['lines']['api-pre'] and f['desc']==c['pre']['desc'] for n,f in definitions) and epochs[0]<c['lines']['api-pre'] for c in result['chains'])
    result['qualified_ordinary'] &= result['named_identity']
    return result


def qualify_level4_loss(rows, level=4):
    ordinary=(qualify_level5 if level==5 else qualify_level4)([r for r in rows if 'api_seq=2' not in r['event']])
    parsed=[(r['line'],r['event'],dict(re.findall(r'(\w+)=([^\s]+)',r['event']))) for r in rows]
    stages={}
    for n,e,f in parsed:
        if '[objresp-wingman]' in e and f.get('api_seq')=='2': stages.setdefault(f['stage'],[]).append((n,f))
    chains=[]
    names=('api-pre','entry','damage-pre','store','damage-post','effect','api-post')
    if ordinary['exact_health_chain'] and all(len(stages.get(k,[]))==1 for k in names) and sum('[objresp-wingman]' in e and f.get('stage')=='api-pre' for n,e,f in parsed)==2:
        ns=[stages[k][0][0] for k in names]; fs=[stages[k][0][1] for k in names]
        p,en,b,st,r,ef,q=fs
        control=ordinary['chains'][0]; prior=control['post']; hp=int(p['hp']); request=hp+1
        identity=('node','npc','desc','slot','generation','handler','actor','detail','mode','health_addr')
        same=all(f.get(k)==p[k]==prior[k] for f in fs for k in identity)
        health=hp==int(prior['hp']) and 0<hp<65535 and all(int(f['hp'])==hp for f in (en,b,st)) and st['next']=='-1' and all(f['hp']=='-1' for f in (r,ef,q)) and r['returned']==q['returned']=='-1'
        messages=all(f['message']==en['message']!='00000000' for f in (b,st,r,ef,q))
        requests=all(int(f['request'])==request for f in fs)
        addr=int(p['health_addr'],16);actor=int(p['actor'],16)
        storage=(st['pc']=='800f2158' and int(p['mode'])!=0 and addr==actor+0x190) or (st['pc']=='800f2148' and p['mode']=='0')
        observed=[]
        for stage,left,right in (('0',ns[0],ns[1]),('1',ns[1],ns[2]),('2',ns[3],ns[4])):
            observed.append(any('[objresp-wingman-observed]' in e and left<n<right and f.get('stage')==stage and f.get('action')=='5' and all(f.get(k)==p[k] for k in ('node','npc','desc','actor')) and f.get('message')==en['message'] for n,e,f in parsed))
        stores=[(n,f) for n,e,f in parsed if '[objresp-wingman-store-observed]' in e and ns[2]<n<ns[3] and f.get('pc')==st['pc'] and f.get('actor')==p['actor'] and f.get('address')==p['health_addr'] and all(f.get(k)==p[k] for k in ('mode','detail'))]
        effects=[(n,f) for n,e,f in parsed if '[objresp-wingman-effect]' in e and ns[4]<n<ns[5] and f.get('api_seq')=='2' and f.get('pc')=='800d9d28' and all(f.get(k)==p[k] for k in ('node','npc','desc')) and [f.get(k) for k in ('id','delta','bool','bval','id2','delta2')]==['40','1','0','0','0','1']]
        writes=[(n,f) for n,e,f in parsed if '[objresp-write]' in e and ns[5]<n<ns[6] and f.get('pc')=='8006594c' and f.get('id')=='40' and f.get('old')=='0' and f.get('new')=='1' and f.get('victim')==p['npc'] and f.get('desc')==p['desc']]
        reads=[(n,f) for n,e,f in parsed if '[objresp-readback]' in e and n>ns[6] and f.get('id')=='40' and f.get('old')=='0' and f.get('new')=='1' and f.get('initialized')=='1']
        getters=[(n,f) for n,e,f in parsed if '[objresp-probe-getter]' in e and n>ns[6] and f.get('id')=='40' and f.get('returned')==f.get('memory')=='1' and f.get('probe_call')=='1']
        done=[(n,f) for n,e,f in parsed if '[objresp-done]' in e and f.get('reason')==f'level{level}-named-response' and f.get('c40')==f.get('getter')=='1' and all(f.get(k)=='0' for k in (('c2','c4','latch2','latch4') if level==5 else ('c15','c16','c28','bool26')))]
        safety=True
        if level==5:
            safety=ordinary['named_identity'] and all(any('[objresp-wingman-safety]' in e and f.get('api_seq')==seq and lo<n<hi and all(f.get(k)=='0' for k in ('c2','c4','latch2','latch4')) for n,e,f in parsed) for seq,lo,hi in (('1',0,control['lines']['api-pre']),('2',control['lines']['api-post'],ns[0])))
        no_reap=not any('[objresp-retire]' in e and control['lines']['api-pre']<n<ns[0] and f.get('slot')==p['slot'] for n,e,f in parsed)
        if (safety and same and health and messages and requests and storage and all(observed) and len(stores)==len(effects)==len(writes)==1 and reads and getters and done and no_reap and
            ns==sorted(set(ns)) and control['getter_line']<ns[0] and reads[0][0]<getters[0][0]<done[0][0] and all(f['c40']=='0' for f in (p,en,b,st,r,ef)) and q['c40']=='1' and ordinary['getters_match'] and '40' in ordinary['changing_getter_ids']):
            chains.append(dict(control=control,lines=dict(zip(names,ns)),pre=p,store=st,effect=effects[0],writer=writes[0],readback=reads[0],getter=getters[0],done=done[0]))
    return dict(qualified=bool(chains),chains=chains,changing_getter_ids=ordinary['changing_getter_ids'],scope='instrument-invoked named API death response; dynamic causality single-flight, no player-shot or retail-equivalence proof')


def level4_self_test():
    key='api_seq=1 node=80210000 npc=80350000 desc=80310000 slot=42 generation=1 handler=800d93c0 actor=80360000 detail=0 mode=1 health_addr=80360190'
    events=['[objresp-live] node=80210000 npc=80350000 desc=80310000 slot=42 generation=1 handler=800d93c0 owned=1 canonical=42',
        '[objresp-wingman-eligibility] node=80210000 npc=80350000 desc=80310000 slot=42 generation=1 handler=800d93c0 actor=80360000 health_addr=80360190 lookup=80310000 reason=eligible owned=1 valid=1',
        '[objresp-wingman-control] node=80210000 actor=80360000 mode=1 detail=0 health_addr=80360190 mark_all=1']
    for stage,pc,hp,nxt,ret in [('api-pre','800c7390',400,0,0),('entry','800d93c0',400,0,0),('damage-pre','800d9c54',400,0,400),('store','800f2158',400,390,390),('damage-post','800d9c5c',390,0,390),('api-post','800c7390',390,0,390)]:
        if stage in ('entry','damage-pre','damage-post'):
            ordinal={'entry':0,'damage-pre':1,'damage-post':2}[stage]
            events.append(f'[objresp-wingman-observed] stage={ordinal} node=80210000 npc=80350000 desc=80310000 actor=80360000 message=80400000 action=5')
        if stage=='store': events.append('[objresp-wingman-store-observed] pc=800f2158 actor=80360000 address=80360190 mode=1 detail=0')
        events.append(f'[objresp-wingman] {key} stage={stage} pc={pc} hp={hp} next={nxt} returned={ret} request=10 c40=0 message='+('00000000' if stage=='api-pre' else '80400000'))
    events += ['[objresp-probe-getter] id=40 returned=0 memory=0 probe_call=1','[objresp-probe-getter] id=3 returned=0 memory=0 probe_call=1','[objresp-probe-getter] id=3 returned=1 memory=1 probe_call=1']
    def check(es): return qualify_level4([dict(line=i,event=e) for i,e in enumerate(es)])['qualified_ordinary']
    assert check(events)
    assert check([e.replace('mode=1','mode=0').replace('health_addr=80360190','health_addr=80370000').replace('address=80360190','address=80370000').replace('800f2158','800f2148') for e in events])
    for i in range(len(events)): assert not check(events[:i]+events[i+1:]),i
    for old,new in [('request=10','request=11'),('next=390','next=391'),('returned=390','returned=400'),('pc=800f2158','pc=800f2148'),('owned=1','owned=0'),('lookup=80310000','lookup=80310004'),('health_addr=80360190','health_addr=80360194')]:
        assert not check([e.replace(old,new) for e in events]),old
    for key in ('node','npc','desc','slot','generation','handler','actor','detail','mode','health_addr','message'):
        changed=events.copy(); store_index=next(i for i,e in enumerate(events) if '[objresp-wingman] ' in e and 'stage=store' in e); changed[store_index]=re.sub(r'\b'+key+r'=\S+',key+'=99999999',changed[store_index]); assert not check(changed),key
    assert not check(events+[events[3]])
    assert not check(events+['[objresp-wingman] stage=effect'])
    level4_loss_self_test(events)
    prefix=['[objresp-definition] base=8030e504 offset=1afc desc=80310000 name=x_wing_wedge subtype=39 id=40 delta=1', '[objresp-epoch] B40=5 callback=lv5_checkComplexObjectives width=512']
    def check5(es): return qualify_level5([dict(line=i,event=e) for i,e in enumerate(es)])['qualified_ordinary']
    assert check5(prefix+events)
    for i in range(len(prefix+events)): assert not check5((prefix+events)[:i]+(prefix+events)[i+1:]),i
    for old,new in [('B40=5','B40=4'),('x_wing_wedge','x_wing_hobbie'),('offset=1afc','offset=6a7c'),('base=8030e504','base=8030e508'),('subtype=39','subtype=20')]:
        assert not check5([e.replace(old,new) for e in prefix+events]),old
    print('level5 fixtures pass: exact named definition/epoch and every ordinary-chain missing link')
    print('level4 fixtures pass: inline/array, missing links/controls, identity, dose, health, writer, lookup, duplication and effect')

def level4_loss_self_test(ordinary):
    dose=[]
    template=[e for e in ordinary if not ('[objresp-probe-getter]' in e or '[objresp-live]' in e or '[objresp-wingman-eligibility]' in e or '[objresp-wingman-control]' in e)]
    for e in template:
        e=e.replace('api_seq=1','api_seq=2').replace('hp=400','hp=390').replace('hp=390 next=0 returned=390','hp=-1 next=0 returned=-1').replace('next=390 returned=390','next=-1 returned=-1').replace('request=10','request=391')
        if 'stage=api-post' in e:
            key='api_seq=2 node=80210000 npc=80350000 desc=80310000 slot=42 generation=1 handler=800d93c0 actor=80360000 detail=0 mode=1 health_addr=80360190'
            dose+=['[objresp-wingman-effect] api_seq=2 pc=800d9d28 node=80210000 npc=80350000 desc=80310000 id=40 delta=1 bool=0 bval=0 id2=0 delta2=1',f'[objresp-wingman] {key} stage=effect pc=800d9d28 hp=-1 next=0 returned=0 request=391 c40=0 message=80400000','[objresp-write] pc=8006594c id=40 old=0 new=1 victim=80350000 desc=80310000']
            e=e.replace('c40=0','c40=1')
        dose.append(e)
    events=ordinary+dose+['[objresp-readback] id=40 old=0 new=1 initialized=1','[objresp-probe-getter] id=40 returned=1 memory=1 probe_call=1','[objresp-done] reason=level4-named-response c40=1 getter=1 c15=0 c16=0 c28=0 bool26=0']
    def check(es): return qualify_level4_loss([dict(line=i,event=e) for i,e in enumerate(es)])['qualified']
    assert check(events)
    for i in range(len(ordinary),len(events)): assert not check(events[:i]+events[i+1:]),i
    for old,new in [('request=391','request=390'),('delta2=1','delta2=0'),('pc=8006594c','pc=80065974'),('c15=0','c15=1'),('bool26=0','bool26=1')]:
        assert not check([e.replace(old,new) for e in events]),old
    assert not check(events+dose)
    for key in ('node','npc','desc','slot','generation','handler','actor','detail','mode','health_addr','message'):
        changed=events.copy(); i=next(i for i,e in enumerate(changed) if '[objresp-wingman]' in e and 'api_seq=2' in e and 'stage=store' in e);changed[i]=re.sub(r'\b'+key+r'=\S+',key+'=99999999',changed[i]);assert not check(changed),key
    prefix=['[objresp-definition] base=8030e504 offset=1afc desc=80310000 name=x_wing_wedge subtype=39 id=40 delta=1', '[objresp-epoch] B40=5 callback=lv5_checkComplexObjectives width=512', '[objresp-wingman-safety] api_seq=1 c2=0 c4=0 latch2=0 latch4=0']
    five=prefix+ordinary+['[objresp-wingman-safety] api_seq=2 c2=0 c4=0 latch2=0 latch4=0']+events[len(ordinary):]
    five=[e.replace('level4-named-response','level5-named-response').replace('c15=0 c16=0 c28=0 bool26=0','c2=0 c4=0 latch2=0 latch4=0') for e in five]
    def check5(es): return qualify_level4_loss([dict(line=i,event=e) for i,e in enumerate(es)],level=5)['qualified']
    assert check5(five)
    for i in range(len(five)):
        # id3 changes are optional: counter40 itself controls getter sensitivity.
        if '[objresp-probe-getter]' in five[i] and 'id=3 ' in five[i]: continue
        assert not check5(five[:i]+five[i+1:]),i
    for key in ('c2','c4','latch2','latch4'):
        assert not check5([e.replace(key+'=0',key+'=1') for e in five]),key
    for old,new in [('B40=5','B40=4'),('x_wing_wedge','x_wing_hobbie'),('request=391','request=390'),('pc=8006594c','pc=80065974'),('delta2=1','delta2=0')]:
        assert not check5([e.replace(old,new) for e in five]),old
    assert not check5(five+dose)
    print('level5 loss fixtures pass: named identity, safety, ordinary control, every chain link, dose count, HP, writer/effect/getter')
    print('level4 loss fixtures pass: complete and missing-link, duplicate-dose, identity, writer, effect, safety negatives')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', nargs='?', help='fresh TAG_SUFFIX (never overwrite evidence)')
    parser.add_argument('--analyze', action='store_true', help='rebuild the joined table from an existing tag')
    parser.add_argument('--level', type=int, choices=(0, 1, 2, 3, 4, 5, 6, 7), default=0)
    parser.add_argument('--flight-vi', type=int, default=5400, help='level 2 activation-aware window, 5400..12000 VI')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        dose_self_test()
        building_self_test()
        api_self_test()
        level6_self_test()
        level7_self_test()
        level3_loss_self_test()
        level4_self_test()
        return 0
    if not args.tag:
        parser.error('a fresh tag is required')
    if not 5400 <= args.flight_vi <= 12000 or (args.level != 2 and args.flight_vi != 5400):
        parser.error('extended flight window requires level 2 and 5400..12000 VI')
    root = Path(__file__).resolve().parents[1]
    out = root / 'scratch/agent/m6' / (f'g1_lvl{args.level}' + args.tag)
    if args.analyze:
        if not resolve(out / 'run.log'):
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
    env.update(LEVEL=str(args.level), TAG_SUFFIX=args.tag, HOLD_S=str(150 if args.flight_vi == 5400 else args.flight_vi // 60 + 90),
               ROGUESQ_OBJECTIVE_RESPONSE_VI=str(args.flight_vi),
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
            while time.monotonic() - start < (600 if args.flight_vi > 5400 else 360):
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
