import json, collections
data = json.load(open('scratch/agent/s494_item317_step3_report.json'))
groups = collections.defaultdict(list)
for site in data:
    if site.get('verdict') != 'NEEDS_GUARD':
        continue
    for hit in site.get('hits', []):
        key = (site['file'], hit['line'], hit['kind'], hit['off'], hit['reg'])
        groups[key].append({'func': site['func'], 'reload_line': site['reload_line']})

ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))
for key, sites in ranked[:20]:
    file, line, kind, off, reg = key
    funcs = sorted(set(s['func'] for s in sites))
    print(file, 'line=', line, 'kind=', kind, 'off=', off, 'reg=', reg, 'count=', len(sites), 'funcs=', funcs[:3])
