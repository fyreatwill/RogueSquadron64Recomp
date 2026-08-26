#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2366_m5_payload_transformation_provenance}
OUT="$ROOT/scratch/agent/$TAG"

if [[ "${PARSE_ONLY:-0}" != 1 ]]; then
    zsh "$ROOT/scratch/agent/run_s2365_m5_mixed_stage_publication_split.sh" "$TAG"
    rc=$?
    if (( rc != 0 )); then exit "$rc"; fi
fi

python3 - "$OUT/image.log" "$OUT/payload-provenance-table.tsv" "$OUT/payload-provenance-summary.tsv" <<'PY'
import re, sys

log_path, table_path, summary_path = sys.argv[1:]
kv = re.compile(r'([^=\s]+)=([^=\s]+)')
def n(v, base=0):
    try: return int(v, base)
    except (TypeError, ValueError): return 0
def parse(line):
    words = line.split()
    return (words[0] if words else '', dict(kv.findall(line)))
def scope(x):
    return (n(x.get('phase')), n(x.get('width')), n(x.get('origin')))
def phys(v):
    return n(v) & 0x007fffff
def tuple_payload(x):
    return (n(x.get('payload_fnv', x.get('fnv')), 16),
            n(x.get('payload_nz', x.get('nz'))))
def event_detail(x):
    return ';'.join(f'{k}={v}' for k, v in sorted(x.items())
                    if k not in {'_seq', 'phase', 'width', 'origin'})

stages, tasks, dmas, pcms = [], [], [], []
phase = {'phase':'', 'width':'', 'origin':''}
with open(log_path, errors='replace') as stream:
    for seq, line in enumerate(stream, 1):
        tag, fields = parse(line)
        for key in phase:
            if key in fields: phase[key] = fields[key]
        if tag in ('[audtask-image-stage-row]', '[audtask-join]',
                   '[audtask-dma-range]', '[audio-join-pcm]'):
            fields = {**phase, **fields, '_seq': str(seq)}
        if tag == '[audtask-image-stage-row]': stages.append(fields)
        elif tag == '[audtask-join]': tasks.append(fields)
        elif tag == '[audtask-dma-range]': dmas.append(fields)
        elif tag == '[audio-join-pcm]': pcms.append(fields)

stages = [s for s in stages if n(s.get('width')) == 512 and
          n(s.get('origin')) == 0x6ab400 and n(s.get('stage')) in (2, 3) and
          n(s.get('nz')) > 0]
rows = []
for stage in stages:
    containing = [t for t in tasks if scope(t) == scope(stage) and
                  n(t.get('begin')) <= n(stage.get('event')) <= n(t.get('end'))]
    if not containing: continue
    task = min(containing, key=lambda t: abs(n(t.get('end')) - n(stage.get('event'))))
    task_n = task.get('n', '')
    task_dmas = [d for d in dmas if d.get('n') == task_n and
                 (scope(d) == scope(stage) or not d.get('origin'))]
    dma_candidates = [d for d in task_dmas
                      if phys(d.get('dram', '').split('..', 1)[0]) == phys(stage.get('dest'))
                      and n(d.get('len')) == n(stage.get('len'))]
    phase_events = [p for p in pcms if scope(p) == scope(stage) and
                    phys(p.get('guest')) == phys(stage.get('dest')) and
                    n(p.get('bytes')) == n(stage.get('len'))]
    candidates = phase_events
    changed = [p for p in candidates if tuple_payload(p) !=
               (n(stage.get('fnv'), 16), n(stage.get('nz')))]
    source = [p for p in phase_events if p.get('kind') == 'source']
    consumer = [p for p in phase_events if p.get('kind') == 'consumer']
    task_scope = [t for t in tasks if scope(t) == scope(stage)]
    changed_desc = []
    for dma in changed:
        d_event = n(dma.get('event'))
        event_tasks = [t for t in task_scope if n(t.get('begin')) <= d_event <= n(t.get('end'))]
        owner = min(event_tasks, key=lambda t: abs(n(t.get('end')) - d_event)) if event_tasks else None
        changed_desc.append('%s:%s:%s:%s:task=%s:begin=%s:end=%s:complete=%s:%s' % (
            dma.get('event',''), dma.get('payload_fnv',''), dma.get('payload_nz',''),
            dma.get('dram', dma.get('guest','')), owner.get('n','') if owner else '',
            owner.get('begin','') if owner else '', owner.get('end','') if owner else '',
            owner.get('complete','') if owner else '', event_detail(dma)))
    source_desc = ','.join(f"{p.get('event','')}:{event_detail(p)}" for p in source)
    consumer_desc = ','.join(f"{p.get('event','')}:{event_detail(p)}" for p in consumer)
    completions = ','.join(f"{t.get('n','')}:{t.get('end','')}:{t.get('complete','')}" for t in task_scope)
    writer_source_n = sum(1 for p in phase_events if n(p.get('writer_pc')) or n(p.get('writer_writes')))
    rows.append([stage.get('arm',''), stage.get('ordinal',''), stage.get('row',''),
                 stage.get('stage',''), stage.get('event',''), task_n,
                 task.get('begin',''), task.get('end',''), task.get('complete',''),
                 stage.get('dest',''), stage.get('len',''), stage.get('fnv',''), stage.get('nz',''),
                 len(candidates), len(changed), ';'.join(changed_desc),
                 len(source), len(consumer), writer_source_n, source_desc, consumer_desc, completions])

header = ('arm ordinal row stage stage_event containing_task task_begin task_end task_complete '
          'dest len stage_fnv stage_nz candidate_n changed_candidate_n changed_candidates '
          'phase_source_n phase_consumer_n writer_source_n phase_source_events phase_consumer_events '
          'phase_task_completion_order').split()
with open(table_path, 'w') as out:
    out.write('\t'.join(header) + '\n')
    for row in rows: out.write('\t'.join(map(str, row)) + '\n')

changed_rows = sum(bool(r[14]) for r in rows)
source_rows = sum(bool(r[16]) for r in rows)
consumer_rows = sum(bool(r[17]) for r in rows)
writer_rows = sum(bool(r[18]) for r in rows)
with open(summary_path, 'w') as out:
    out.write('metric\tvalue\n')
    out.write(f'target_stage_rows\t{len(rows)}\n')
    out.write(f'destination_length_candidate_rows\t{sum(r[13] > 0 for r in rows)}\n')
    out.write(f'changed_payload_candidate_rows\t{changed_rows}\n')
    out.write(f'changed_rows_with_phase_source\t{source_rows}\n')
    out.write(f'changed_rows_with_phase_consumer\t{consumer_rows}\n')
    out.write(f'changed_rows_with_writer_source\t{writer_rows}\n')
print('payload_provenance_table target_stage_rows=%d changed_payload_candidate_rows=%d changed_rows_with_phase_source=%d changed_rows_with_phase_consumer=%d' %
      (len(rows), changed_rows, source_rows, consumer_rows))
PY

cat "$OUT/payload-provenance-table.tsv" >> "$OUT/driver.log"
cat "$OUT/payload-provenance-summary.tsv" >> "$OUT/driver.log"
controls=$(grep -a -E '^controls oracle=1 .*stub_abi=[1-9].*image_abi=[1-9].*stub_vi=[1-9].*image_vi=[1-9].*stub_filter=[1-9].*image_filter=[1-9].*image_join=[1-9]' "$OUT/driver.log" | tail -1 | wc -l | tr -d ' ')
target=$(awk -F '\t' '$1 == "target_stage_rows" {print $2}' "$OUT/payload-provenance-summary.tsv")
changed=$(awk -F '\t' '$1 == "changed_payload_candidate_rows" {print $2}' "$OUT/payload-provenance-summary.tsv")
sources=$(awk -F '\t' '$1 == "changed_rows_with_phase_source" {print $2}' "$OUT/payload-provenance-summary.tsv")
consumers=$(awk -F '\t' '$1 == "changed_rows_with_phase_consumer" {print $2}' "$OUT/payload-provenance-summary.tsv")
writers=$(awk -F '\t' '$1 == "changed_rows_with_writer_source" {print $2}' "$OUT/payload-provenance-summary.tsv")
if (( controls == 0 || target == 0 )); then
    verdict=H-TimingCaptureInvalid
elif (( changed == 0 )); then
    verdict=H-NoChangedCandidate
elif (( sources > 0 && consumers > 0 && writers > 0 )); then
    verdict=H-LegitimateTransformSource
else
    verdict=H-MixedOrUnrelatedCandidate
fi
print "verdict=$verdict controls=$controls target_stage_rows=$target changed_payload_candidate_rows=$changed changed_rows_with_phase_source=$sources changed_rows_with_phase_consumer=$consumers changed_rows_with_writer_source=$writers" | tee -a "$OUT/driver.log"
exit 0
