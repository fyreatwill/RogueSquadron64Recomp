#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2364_m5_post_task_publication_join}
OUT="$ROOT/scratch/agent/$TAG"

# The prior driver owns the oracle controls, same-build arms, phase gating,
# positive controls, and SIGKILL cleanup. This unit changes only the retained
# join: it requires the exact stage DMA tuple and post-task PCM/completion rows.
if [[ "${PARSE_ONLY:-0}" != 1 ]]; then
    zsh "$ROOT/scratch/agent/run_s2327_m5_task_ordinal_prepost_join.sh" "$TAG"
    rc=$?
    if (( rc != 0 )); then exit "$rc"; fi
fi

python3 - "$OUT/image.log" "$OUT/post-task-publication-table.tsv" "$OUT/post-task-publication-summary.tsv" <<'PY'
import re, sys

log_path, table_path, summary_path = sys.argv[1:]
kv = re.compile(r'([^=\s]+)=([^\s]+)')
def n(v, base=0):
    try: return int(v, base)
    except (TypeError, ValueError): return 0
def parse(line):
    words = line.split()
    return (words[0] if words else '', dict(kv.findall(line)))
def scope(x):
    return (n(x.get('phase')), n(x.get('width')), n(x.get('origin')))

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
          n(s.get('origin')) == 0x6AB400 and n(s.get('stage')) in (2, 3) and
          n(s.get('nz')) > 0]
rows = []
for stage in stages:
    candidates = [t for t in tasks if scope(t) == scope(stage) and
                  n(t.get('begin')) <= n(stage.get('event')) <= n(t.get('end'))]
    if not candidates:
        continue
    task = min(candidates, key=lambda t: abs(n(t.get('end')) - n(stage.get('event'))))
    task_n = n(task.get('n'))
    task_dmas = [d for d in dmas if n(d.get('n')) == task_n]
    exact = [d for d in task_dmas
             if n(d.get('dram','').split('..', 1)[0]) == n(stage.get('dest'))
             and n(d.get('len')) == n(stage.get('len'))
             and n(d.get('payload_fnv'), 16) == n(stage.get('fnv'), 16)
             and n(d.get('payload_nz')) == n(stage.get('nz'))]
    if not exact:
        rows.append((stage, task, None, [], [], []))
        continue
    dma = exact[-1]
    lo, hi = n(task.get('end')), n(task.get('end')) + 512
    matched = [p for p in pcms if scope(p) == scope(stage) and lo < n(p.get('event')) <= hi
               and (n(p.get('guest')) & 0x007FFFFF) == n(stage.get('dest'))
               and n(p.get('bytes')) == n(stage.get('len'))
               and n(p.get('fnv'), 16) == n(stage.get('fnv'), 16)
               and n(p.get('nz')) == n(stage.get('nz'))]
    sources = [p for p in matched if p.get('kind') == 'source']
    consumers = [p for p in matched if p.get('kind') == 'consumer']
    updates = [t for t in tasks if t.get('n') == task.get('n') and scope(t) == scope(stage)
               and t.get('begin') == task.get('begin') and t.get('end') == task.get('end')]
    latest = max(updates, key=lambda t: n(t.get('_seq'))) if updates else task
    rows.append((stage, task, dma, sources, consumers, latest))

header = ('arm ordinal row stage stage_event task_n task_begin task_end '
          'dest len fnv nz dma_event source_events consumer_events '
          'latest_complete latest_source_matches latest_consumer_matches').split()
with open(table_path, 'w') as out:
    out.write('\t'.join(header) + '\n')
    for stage, task, dma, sources, consumers, latest in rows:
        out.write('\t'.join(map(str, [
            stage.get('arm',''), stage.get('ordinal',''), stage.get('row',''),
            stage.get('stage',''), stage.get('event',''), task.get('n',''),
            task.get('begin',''), task.get('end',''), stage.get('dest',''),
            stage.get('len',''), stage.get('fnv',''), stage.get('nz',''),
            dma.get('event','') if dma else '',
            ','.join(p.get('event','') for p in sources),
            ','.join(p.get('event','') for p in consumers),
            latest.get('complete',''), latest.get('source_matches',''),
            latest.get('consumer_matches','')])) + '\n')

exact_dma = sum(1 for *_, dma, __, ___, ____ in rows if dma)
closed = sum(1 for *_, dma, sources, consumers, latest in rows
             if dma and sources and consumers and n(latest.get('complete')) == 1)
with open(summary_path, 'w') as out:
    out.write('metric\tvalue\n')
    out.write(f'target_stage_rows\t{len(rows)}\n')
    out.write(f'exact_dma_rows\t{exact_dma}\n')
    out.write(f'post_task_source_consumer_completion_rows\t{closed}\n')
print(f'post_task_table target_stage_rows={len(rows)} exact_dma_rows={exact_dma} closed_rows={closed}')
PY

cat "$OUT/post-task-publication-table.tsv" >> "$OUT/driver.log"
cat "$OUT/post-task-publication-summary.tsv" >> "$OUT/driver.log"
controls=$(grep -a -E '^controls oracle=1 .*stub_abi=[1-9].*image_abi=[1-9].*stub_vi=[1-9].*image_vi=[1-9].*stub_filter=[1-9].*image_filter=[1-9].*image_join=[1-9]' "$OUT/driver.log" | tail -1 | wc -l | tr -d ' ')
target=$(awk -F '\t' '$1 == "target_stage_rows" {print $2}' "$OUT/post-task-publication-summary.tsv")
dma=$(awk -F '\t' '$1 == "exact_dma_rows" {print $2}' "$OUT/post-task-publication-summary.tsv")
closed=$(awk -F '\t' '$1 == "post_task_source_consumer_completion_rows" {print $2}' "$OUT/post-task-publication-summary.tsv")
if (( controls == 0 || target == 0 )); then
    verdict=H-TimingCaptureInvalid
elif (( closed == target && dma == target )); then
    verdict=H-PostTaskPublicationClosed
else
    verdict=H-ContainingTaskInternalOnly
fi
print "verdict=$verdict controls=$controls target_stage_rows=$target exact_dma_rows=$dma closed_rows=$closed" | tee -a "$OUT/driver.log"
exit 0
