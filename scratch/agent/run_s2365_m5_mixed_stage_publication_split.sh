#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2365_m5_mixed_stage_publication_split}
OUT="$ROOT/scratch/agent/$TAG"

if [[ "${PARSE_ONLY:-0}" != 1 ]]; then
    zsh "$ROOT/scratch/agent/run_s2364_m5_post_task_publication_join.sh" "$TAG"
    rc=$?
    if (( rc != 0 )); then exit "$rc"; fi
fi

python3 - "$OUT/image.log" "$OUT/mixed-stage-publication-table.tsv" "$OUT/mixed-stage-publication-summary.tsv" <<'PY'
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

stages, tasks, dmas, pcms = [], [], [], []
phase = {'phase':'', 'width':'', 'origin':''}
with open(log_path, errors='replace') as stream:
    for seq, line in enumerate(stream, 1):
        tag, f = parse(line)
        for key in phase:
            if key in f: phase[key] = f[key]
        if tag in ('[audtask-image-stage-row]', '[audtask-join]',
                   '[audtask-dma-range]', '[audio-join-pcm]'):
            f = {**phase, **f, '_seq': str(seq)}
        if tag == '[audtask-image-stage-row]': stages.append(f)
        elif tag == '[audtask-join]': tasks.append(f)
        elif tag == '[audtask-dma-range]': dmas.append(f)
        elif tag == '[audio-join-pcm]': pcms.append(f)

stages = [s for s in stages if n(s.get('width')) == 512 and
          n(s.get('origin')) == 0x6ab400 and n(s.get('stage')) in (2, 3) and
          n(s.get('nz')) > 0]
rows = []
for stage in stages:
    containing = [t for t in tasks if scope(t) == scope(stage) and
                  n(t.get('begin')) <= n(stage.get('event')) <= n(t.get('end'))]
    if not containing:
        continue
    task = min(containing, key=lambda t: abs(n(t.get('end')) - n(stage.get('event'))))
    task_n = task.get('n', '')
    task_dmas = [d for d in dmas if d.get('n') == task_n and
                 (scope(d) == scope(stage) or not d.get('origin'))]
    dma_candidates = [d for d in task_dmas
                      if phys(d.get('dram', '').split('..', 1)[0]) == phys(stage.get('dest'))
                      and n(d.get('len')) == n(stage.get('len'))]
    exact_dmas = [d for d in dma_candidates
                  if n(d.get('payload_fnv'), 16) == n(stage.get('fnv'), 16)
                  and n(d.get('payload_nz')) == n(stage.get('nz'))]
    post = [p for p in pcms if scope(p) == scope(stage) and
            n(task.get('end')) < n(p.get('event')) <= n(task.get('end')) + 512 and
            phys(p.get('guest')) == phys(stage.get('dest')) and
            n(p.get('bytes')) == n(stage.get('len'))]
    post_exact = [p for p in post if n(p.get('fnv'), 16) == n(stage.get('fnv'), 16)
                  and n(p.get('nz')) == n(stage.get('nz'))]
    sources = [p for p in post if p.get('kind') == 'source']
    consumers = [p for p in post if p.get('kind') == 'consumer']
    exact_sources = [p for p in post_exact if p.get('kind') == 'source']
    exact_consumers = [p for p in post_exact if p.get('kind') == 'consumer']
    rows.append((stage, task, dma_candidates, exact_dmas, post, post_exact,
                 sources, consumers, exact_sources, exact_consumers))

header = ('arm ordinal row stage stage_event task_n task_begin task_end dest len fnv nz '
          'dma_candidates dma_exact dma_payloads post_candidates post_exact post_payloads '
          'post_sources post_consumers post_exact_sources post_exact_consumers').split()
with open(table_path, 'w') as out:
    out.write('\t'.join(header) + '\n')
    for stage, task, candidates, exact, post, post_exact, sources, consumers, exact_sources, exact_consumers in rows:
        dma_payloads = ','.join(f"{d.get('event')}:{d.get('payload_fnv')}:{d.get('payload_nz')}" for d in candidates)
        post_payloads = ','.join(f"{p.get('event')}:{p.get('kind')}:{p.get('fnv')}:{p.get('nz')}" for p in post)
        out.write('\t'.join(map(str, [
            stage.get('arm',''), stage.get('ordinal',''), stage.get('row',''), stage.get('stage',''),
            stage.get('event',''), task.get('n',''), task.get('begin',''), task.get('end',''),
            stage.get('dest',''), stage.get('len',''), stage.get('fnv',''), stage.get('nz',''),
            len(candidates), len(exact), dma_payloads, len(post), len(post_exact), post_payloads,
            len(sources), len(consumers), len(exact_sources), len(exact_consumers)])) + '\n')

with open(summary_path, 'w') as out:
    out.write('metric\tvalue\n')
    out.write(f'target_stage_rows\t{len(rows)}\n')
    out.write(f'destination_length_candidate_rows\t{sum(bool(r[2]) for r in rows)}\n')
    out.write(f'exact_dma_rows\t{sum(bool(r[3]) for r in rows)}\n')
    out.write(f'post_candidate_rows\t{sum(bool(r[4]) for r in rows)}\n')
    out.write(f'post_exact_payload_rows\t{sum(bool(r[5]) for r in rows)}\n')
    out.write(f'post_exact_source_consumer_rows\t{sum(r[8] and r[9] != [] for r in rows)}\n')
print('mixed_stage_table target_stage_rows=%d destination_length_candidate_rows=%d exact_dma_rows=%d post_candidate_rows=%d post_exact_payload_rows=%d' % (
    len(rows), sum(bool(r[2]) for r in rows), sum(bool(r[3]) for r in rows),
    sum(bool(r[4]) for r in rows), sum(bool(r[5]) for r in rows)))
PY

cat "$OUT/mixed-stage-publication-table.tsv" >> "$OUT/driver.log"
cat "$OUT/mixed-stage-publication-summary.tsv" >> "$OUT/driver.log"
controls=$(grep -a -E '^controls oracle=1 .*stub_abi=[1-9].*image_abi=[1-9].*stub_vi=[1-9].*image_vi=[1-9].*stub_filter=[1-9].*image_filter=[1-9].*image_join=[1-9]' "$OUT/driver.log" | tail -1 | wc -l | tr -d ' ')
target=$(awk -F '\t' '$1 == "target_stage_rows" {print $2}' "$OUT/mixed-stage-publication-summary.tsv")
candidates=$(awk -F '\t' '$1 == "destination_length_candidate_rows" {print $2}' "$OUT/mixed-stage-publication-summary.tsv")
post=$(awk -F '\t' '$1 == "post_candidate_rows" {print $2}' "$OUT/mixed-stage-publication-summary.tsv")
exact=$(awk -F '\t' '$1 == "post_exact_payload_rows" {print $2}' "$OUT/mixed-stage-publication-summary.tsv")
if (( controls == 0 || target == 0 )); then
    verdict=H-TimingCaptureInvalid
elif (( exact == target )); then
    verdict=H-PostTaskPublicationClosed
elif (( post > 0 && candidates == target )); then
    verdict=H-PayloadTransform
elif (( post == 0 )); then
    verdict=H-NoPostTaskPublication
else
    verdict=H-MixedStageRole
fi
print "verdict=$verdict controls=$controls target_stage_rows=$target destination_length_candidate_rows=$candidates post_candidate_rows=$post post_exact_payload_rows=$exact" | tee -a "$OUT/driver.log"
exit 0
