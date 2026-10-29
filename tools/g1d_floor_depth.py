"""Name the writer of the striped depth already present at the 21:9 floor sample 0.

One binary, both widths. History runs from depth-target setup through the
first phase>=4 floor submission's sample 0. The floor attachment capture is
unchanged and supplies the magenta and 16:9 ~0.996 controls.
"""
import json
import os
from pathlib import Path
import struct

import g1d_floor_attachment as att
import g1d_floor_inputs as base

WRITERS = {'tri', 'clear-target', 'clear-rect', 'copy-target', 'copy-changes'}
ROOT = Path(__file__).resolve().parents[1]


def near1(z):
    return abs(z - 1.0) < 1e-3


def is_zero(z):
    return abs(z) < 1e-6


def is_mid(z):
    return 0.94 <= z <= 0.99


def load_events(path):
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_z(path, nsample):
    data = path.read_bytes()
    magic, n = struct.unpack_from('<2I', data)
    assert magic == 0x66346625 and n == nsample, (path, magic, n, nsample)
    body = data[8:]
    assert len(body) == nsample * 142 * 16, (path, len(body))
    out = []
    for s in range(nsample):
        pix = []
        base_off = s * 142 * 16
        for i in range(142):
            z, w, magic_z, prim = struct.unpack_from('<4f', body, base_off + i * 16)
            pix.append((z, w, magic_z, prim))
        out.append(pix)
    return out


def column_counts(sample):
    # s6624 serial 1: exact zeros on rows 0..12, then 1.0 interleaved with
    # ~0.961/0.967/0.984. Those two clusters are not in the same rows.
    zeros = mids = ones = 0
    for col in (0, 1):
        for y in range(71):
            z = sample[(col, y)][4]
            if y < 13 and is_zero(z):
                zeros += 1
            if is_mid(z):
                mids += 1
            elif near1(z):
                ones += 1
    return zeros, mids, ones


def is_stripe(sample):
    zeros, mids, ones = column_counts(sample)
    return zeros >= 20 and mids >= 5 and ones >= 5


def all_ones(sample):
    return all(near1(sample[(col, y)][4]) for col in (0, 1) for y in range(71))


def phase_disagree(sample):
    return sum(abs(sample[(0, y)][4] - sample[(1, y)][4]) > 0.02 for y in range(71))


def alternates(sample):
    jumps = 0
    for col in (0, 1):
        for y in range(70):
            if abs(sample[(col, y)][4] - sample[(col, y + 1)][4]) > 0.2:
                jumps += 1
    return jumps


def pixel_has(sample, pred, rows=None):
    ys = range(13) if rows == 'head' else range(71)
    return any(pred(sample[(col, y)][4]) for col in (0, 1) for y in ys)


def introduced(prev, cur, pred):
    if prev is None:
        return pixel_has(cur, pred)
    for col in (0, 1):
        for y in range(71):
            if pred(cur[(col, y)][4]) and not pred(prev[(col, y)][4]):
                return True
    return False


def z_of(zsample):
    cols = [[], []]
    if not zsample:
        return cols
    for i, rec in enumerate(zsample):
        if abs(rec[2] - 6625.0) < 1e-3:
            cols[0 if i < 71 else 1].append(rec[0])
    return cols


def z_smooth(zsample):
    cols = z_of(zsample)
    usable = [col for col in cols if len(col) >= 8]
    if len(usable) < 1:
        return False
    for col in usable:
        second = [abs(col[i + 2] - 2 * col[i + 1] + col[i]) for i in range(len(col) - 2)]
        if not second or max(second) > 0.02:
            return False
    return True


def z_range(zsample):
    vals = [v for col in z_of(zsample) for v in col]
    if not vals:
        return None
    return [min(vals), max(vals)]


def covers_band(ev, width):
    right = width - 17
    return ev['y0'] <= 180 and ev['y1'] >= 251 and ev['x0'] <= 16 and ev['x1'] > right


def classify(arm):
    events = arm['events']
    samples = arm['samples']
    zs = arm['z']
    by_sample = {ev['sample']: ev for ev in events if ev['sample'] >= 0}
    floor = next((ev for ev in events if ev['kind'] == 'floor-enter' and ev['sample'] >= 0), None)
    setup = next((ev for ev in events if ev['kind'] == 'setup'), None)
    prev = None
    zero_writer = mid_writer = stripe_writer = None
    for ev in events:
        if ev['sample'] < 0:
            continue
        cur = samples[ev['sample']]
        if ev['kind'] in WRITERS:
            if zero_writer is None and introduced(prev, cur, is_zero):
                zero_writer = ev
            if mid_writer is None and introduced(prev, cur, is_mid):
                mid_writer = ev
            if stripe_writer is None and is_stripe(cur):
                stripe_writer = ev
        prev = cur
    writer = stripe_writer or mid_writer
    zinfo = None
    smooth = False
    if writer is not None and writer['sample'] < len(zs):
        zinfo = z_range(zs[writer['sample']])
        smooth = z_smooth(zs[writer['sample']])
    width = arm['width']
    pitch = False
    alt = 0
    if writer is not None:
        img = samples[writer['sample']]
        alt = alternates(img)
        pitch = writer['depthW'] != writer['colorW'] and writer['colorW'] != 0
        if pitch or (smooth and alt >= 8 and covers_band(writer, width)):
            label = 'H-depth-pitch'
        else:
            label = 'H-prior-stripe'
    else:
        label = None
    enter = samples[floor['sample']] if floor is not None else None
    return dict(
        floor=floor, setup_clear=None if setup is None else setup['clear'],
        zero_writer=zero_writer, mid_writer=mid_writer, stripe_writer=stripe_writer,
        writer=writer, label=label, smooth=smooth, z=zinfo, alt=alt, pitch=bool(pitch),
        enter_stripe=bool(enter is not None and is_stripe(enter)),
        enter_ones=bool(enter is not None and all_ones(enter)),
        enter_zeros=column_counts(enter)[0] if enter is not None else 0,
        enter_mids=column_counts(enter)[1] if enter is not None else 0,
        phase=phase_disagree(enter) if enter is not None else 0,
        events=len(events), samples=len(samples),
        overflow=arm.get('overflow', 0),
    )


def controls(wide16, wide21):
    reasons = []
    if not wide16.get('magenta') or not wide21.get('magenta'):
        reasons.append('magenta')
    if not wide16.get('floor_store'):
        reasons.append('floor-store')
    if not wide16.get('pix_match') or not wide21.get('pix_match'):
        reasons.append('pix-match')
    if not wide16['table']['enter_ones']:
        reasons.append('wide16-enter')
    if not wide21['table']['enter_stripe']:
        reasons.append('wide21-stripe')
    if wide16['table'].get('overflow') or wide21['table'].get('overflow'):
        reasons.append('overflow')
    return reasons


def decide(wide16, wide21):
    bad = controls(wide16, wide21)
    if bad:
        return 'H-witness', bad
    writer = wide21['table']['writer']
    if writer is None:
        # ~0.96 still needs its own store. Zeros alone, with the 16:9 floor
        # store read back, are the unwritten-tile case.
        if (wide21['table']['zero_writer'] is None and wide21['table']['enter_zeros'] >= 20
                and wide21['table']['enter_mids'] == 0
                and wide21['table']['setup_clear'] == 1.0 and wide16.get('floor_store')
                and wide21['table']['mid_writer'] is None):
            return 'H-depth-readback', []
        return 'H-witness', ['no-writer']
    return wide21['table']['label'], []


def shader_controls(folder):
    pix_paths = sorted(folder.glob('shader_*.pix'))
    assert pix_paths, folder
    first = att.load_pix(pix_paths[0])
    magenta = att.near(first['samples'][1][(0, 0)], (1, 0, 1), 2.0)
    store = False
    for path in pix_paths:
        pix = att.load_pix(path) if path != pix_paths[0] else first
        for sample in pix['samples'][1:]:
            for col in (0, 1):
                for y in range(71):
                    z = sample[(col, y)][4]
                    if 0.990 <= z <= 0.998:
                        store = True
    enter = first['samples'][0]
    return dict(magenta=magenta, floor_store=store, enter=enter, serial=pix_paths[0].name)


def pix_match(hist_enter, shader_enter):
    if hist_enter is None or shader_enter is None:
        return False
    worst = 0.0
    for col in (0, 1):
        for y in range(71):
            worst = max(worst, abs(hist_enter[(col, y)][4] - shader_enter[(col, y)][4]))
    return worst < 1e-3


def load_arm(root, tag, width):
    depth = root / tag / 'depth'
    events = load_events(depth / 'history.jsonl')
    pix = att.load_pix(depth / 'history.pix')
    zs = load_z(depth / 'history.z', pix['nsample'])
    meta = json.loads((depth / 'history_meta.json').read_text())
    shader = shader_controls(root / tag / 'shader')
    floor = next((ev for ev in events if ev['kind'] == 'floor-enter' and ev['sample'] >= 0), None)
    hist_enter = pix['samples'][floor['sample']] if floor is not None else None
    arm = dict(
        events=events, samples=pix['samples'], z=zs, width=width,
        magenta=shader['magenta'], floor_store=shader['floor_store'],
        pix_match=pix_match(hist_enter, shader['enter']),
        overflow=meta.get('overflow', 0), meta=meta, serial=shader['serial'],
    )
    arm['table'] = classify(arm)
    text = (root / tag / 'run.log').read_text(errors='replace') if (root / tag / 'run.log').exists() else ''
    arm['crashlines'] = sum(text.count(tok) for tok in ('[CRASH]', '[ABORT]', 'SIGSEGV', 'SIGBUS'))
    arm['alive'] = 'alive_at_end'  # filled by summary if present
    summary_path = root / tag / 'summary.json'
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
        arm['summary'] = {k: summary[k] for k in ('seconds', 'alive_at_end', 'stop', 'good_frames', 'crashlines') if k in summary}
    return arm


def public_event(ev):
    if ev is None:
        return None
    keys = ('kind', 'frame', 'pair', 'phase', 'depth', 'colorW', 'depthW', 'x0', 'y0', 'x1', 'y1',
            'zCmp', 'zUpd', 'depthCmp', 'depthWr', 'faces', 'sample', 'captureZ', 'whole')
    return {k: ev[k] for k in keys if k in ev}


def blank(color, depth, n=71):
    sample = {}
    for col in (0, 1):
        for y in range(n):
            z = depth(col, y)
            sample[(col, y)] = (color, color, color, 1.0, z)
    return sample


def ones(col, y):
    return 1.0


def stripe_depth(col, y):
    if y < 13:
        return 0.0
    if (y + col) % 2 == 0:
        return 1.0
    return 0.961 if (y % 4) == 0 else 0.967


def smooth_z(n_pix=142):
    pix = []
    for i in range(n_pix):
        y = i % 71
        pix.append((0.50 + y * 0.001, 1.0, 6625.0, 1.0))
    return pix


def rough_z():
    pix = []
    for i in range(142):
        y = i % 71
        col = 0 if i < 71 else 1
        pix.append((stripe_depth(col, y), 1.0, 6625.0, 1.0))
    return pix


def ev(kind, sample, **extra):
    row = dict(kind=kind, sample=sample, frame=1351, pair=0, phase=4, depth='0x1', colorW=1024, depthW=1024,
               x0=0, y0=0, x1=1024, y1=336, zCmp=1, zUpd=1, depthCmp=2, depthWr=1, faces=4,
               captureZ=1, whole=0, clear=1.0)
    row.update(extra)
    return row


def selftest():
    one = blank(0.2, ones)
    torn = blank(0.2, stripe_depth)
    setup = ev('setup', -1, clear=1.0, zUpd=0, zCmp=0)
    clear = ev('clear-target', 0, whole=1, zCmp=0, depthCmp=8)
    tri = ev('tri', 1, x0=0, y0=0, x1=1024, y1=336)
    floor = ev('floor-enter', 2, zCmp=0, zUpd=0, depthWr=0, captureZ=0)
    base_arm = dict(width=1024, magenta=True, floor_store=True, pix_match=True, overflow=0)
    wide16 = dict(base_arm, width=796, events=[ev('setup', -1), ev('floor-enter', 0, colorW=796, depthW=796, x1=796)],
                  samples=[one], z=[[(0, 0, 0, 0)] * 142])
    wide16['table'] = classify(wide16)
    prior = dict(base_arm, events=[setup, clear, tri, floor], samples=[one, torn, torn], z=[[(0, 0, 0, 0)] * 142, rough_z(), rough_z()])
    prior['table'] = classify(prior)
    pitch = dict(base_arm, events=[setup, clear, ev('tri', 1, depthW=1280, colorW=1024), floor],
                 samples=[one, torn, torn], z=[[(0, 0, 0, 0)] * 142, smooth_z(), smooth_z()])
    pitch['table'] = classify(pitch)
    assert decide(wide16, prior) == ('H-prior-stripe', []), decide(wide16, prior)
    assert decide(wide16, pitch) == ('H-depth-pitch', []), (decide(wide16, pitch), pitch['table']['smooth'], pitch['table']['alt'])
    broken = dict(wide16, magenta=False)
    broken['table'] = wide16['table']
    assert decide(broken, prior)[0] == 'H-witness'
    missing = dict(base_arm, events=[setup, ev('floor-enter', 0)], samples=[torn], z=[[(0, 0, 0, 0)] * 142])
    missing['table'] = classify(missing)
    assert decide(wide16, missing) == ('H-witness', ['no-writer'])
    # Zeros without the ~0.96 cluster are not serial 1. That is a bad log,
    # not an unwritten tile: the known 16:9 store is what makes readback usable,
    # and only after the interleave is actually present.
    zeros_only = blank(0.2, lambda col, y: 0.0 if y < 13 else 1.0)
    unread = dict(base_arm, events=[setup, ev('floor-enter', 0)], samples=[zeros_only], z=[[(0, 0, 0, 0)] * 142])
    unread['table'] = classify(unread)
    assert decide(wide16, unread)[0] == 'H-witness'
    capped = dict(prior, overflow=1)
    capped['table'] = classify(capped)
    assert 'overflow' in decide(wide16, capped)[1]
    # Zeros already present, mid introduced by the triangle: zeros stay unwritten.
    head_zero = blank(0.2, lambda col, y: 0.0 if y < 13 else 1.0)
    mixed = dict(base_arm, events=[setup, ev('enter', 0, zUpd=0, zCmp=0, depthWr=0), tri, floor],
                 samples=[head_zero, torn, torn], z=[[(0, 0, 0, 0)] * 142, rough_z(), rough_z()])
    mixed['table'] = classify(mixed)
    assert mixed['table']['zero_writer'] is None and mixed['table']['mid_writer']['kind'] == 'tri', mixed['table']
    assert decide(wide16, mixed)[0] == 'H-prior-stripe'
    print('selftest ok', flush=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--analyze', action='store_true')
    ap.add_argument('--output-root', type=Path, default=Path('scratch/agent/s6625_depth'))
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    root = args.output_root.resolve()
    if not args.analyze:
        for aspect, tag, width in (('16:9', 'wide16', 796), ('21:9', 'wide21', 1024)):
            (root / tag / 'shader').mkdir(parents=True, exist_ok=True)
            (root / tag / 'depth').mkdir(parents=True, exist_ok=True)
            os.environ['ROGUESQ_FLOOR_SHADER_DIR'] = str(root / tag / 'shader')
            os.environ['ROGUESQ_FLOOR_DEPTH_DIR'] = str(root / tag / 'depth')
            os.environ.pop('ROGUESQ_FLOOR_PIPE_DIR', None)
            base.run_arm(aspect, tag, width, root)
    arms = {}
    for tag, width in (('wide16', 796), ('wide21', 1024)):
        arms[tag] = load_arm(root, tag, width)
    verdict, why = decide(arms['wide16'], arms['wide21'])
    result = dict(
        selects=verdict, why=why,
        arms={tag: dict(
            table={k: public_event(v) if k.endswith('writer') or k == 'floor' else v
                   for k, v in arm['table'].items()},
            magenta=arm['magenta'], floor_store=arm['floor_store'], pix_match=arm['pix_match'],
            crashlines=arm['crashlines'], summary=arm.get('summary'), meta=arm['meta'],
        ) for tag, arm in arms.items()},
    )
    # public_event on floor too; table.floor is an event. Fix writers only.
    for tag, arm in arms.items():
        table = arm['table']
        result['arms'][tag]['table'] = dict(table)
        for key in ('zero_writer', 'mid_writer', 'stripe_writer', 'writer', 'floor'):
            result['arms'][tag]['table'][key] = public_event(table[key])
    (root / 'depth_verdict.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(selects=verdict, why=why,
                          wide21=result['arms']['wide21']['table'].get('writer'),
                          zeros=result['arms']['wide21']['table'].get('zero_writer'),
                          smooth=arms['wide21']['table']['smooth'],
                          pitch=arms['wide21']['table']['pitch'])), flush=True)


if __name__ == '__main__':
    main()
