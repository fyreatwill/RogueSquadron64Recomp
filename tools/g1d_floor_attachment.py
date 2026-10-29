"""Pre/post attachment witness for the 21:9 level-select floor columns.

One binary, both widths. Every draw/clear that can touch x=16 and x=w-17,
y=180..250, records actual color and depth before and after it, the fixed
function state Metal received, and the shader outputs already captured for
that draw. A one-pixel magenta clear is the positive control.
"""
import argparse
import json
import os
from pathlib import Path
import statistics
import struct

import g1d_floor_inputs as base

FIELDS = ('key', 'uv', 'smooth', 'shade', 'tex0', 'combiner', 'result', 'alpha',
          'tile', 'dimensions', 'control', 'tex1', 'modes', 'selected', 'zinfo')
RECORD = struct.Struct('<I60f')
PIX = struct.Struct('<5f')
BLEND = {0: 'UNKNOWN', 1: 'ZERO', 2: 'ONE', 3: 'SRC_COLOR', 4: 'INV_SRC_COLOR',
         5: 'SRC_ALPHA', 6: 'INV_SRC_ALPHA', 7: 'DEST_ALPHA', 8: 'INV_DEST_ALPHA',
         9: 'DEST_COLOR', 10: 'INV_DEST_COLOR', 11: 'SRC_ALPHA_SAT', 12: 'BLEND_FACTOR',
         13: 'INV_BLEND_FACTOR', 14: 'SRC1_COLOR', 15: 'INV_SRC1_COLOR', 16: 'SRC1_ALPHA',
         17: 'INV_SRC1_ALPHA'}
CMP = {0: 'UNKNOWN', 1: 'NEVER', 2: 'LESS', 3: 'EQUAL', 4: 'LESS_EQUAL', 5: 'GREATER',
       6: 'NOT_EQUAL', 7: 'GREATER_EQUAL', 8: 'ALWAYS'}


def luma(rgb):
    return (rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722) * 255.0


def near(a, b, tol=2.0):
    return max(abs(a[i] - b[i]) * 255.0 for i in range(3)) <= tol


def step_of(pixels):
    acc = [0.0, 0.0]
    for col in (0, 1):
        for y in range(70):
            acc[col] += abs(luma(pixels[(col, y)]) - luma(pixels[(col, y + 1)]))
    return [acc[0] / 70.0, acc[1] / 70.0]


def load_records(path):
    data = path.read_bytes()
    assert len(data) % RECORD.size == 0, path
    out = []
    for values in RECORD.iter_unpack(data):
        slot = values[0]
        fields = {name: values[1 + i * 4:5 + i * 4] for i, name in enumerate(FIELDS)}
        fields.update(slot=slot, col=(slot % 142) // 71, y=(slot % 71), order=slot // 142)
        out.append(fields)
    return out


def load_pix(path):
    data = path.read_bytes()
    magic, nsample, width, fmt = struct.unpack_from('<4I', data)
    assert magic == 0x66346624, path
    body = data[16:]
    assert len(body) == nsample * 142 * PIX.size, (path, len(body), nsample)
    samples = []
    for s in range(nsample):
        pix = {}
        for i, values in enumerate(PIX.iter_unpack(body[s * 142 * PIX.size:(s + 1) * 142 * PIX.size])):
            pix[(i // 71, i % 71)] = values
        samples.append(pix)
    return dict(samples=samples, width=width, fmt=fmt, nsample=nsample)


def factor(code, src, dst, src1):
    name = BLEND.get(code, 'UNKNOWN')
    table = {'ZERO': 0.0, 'ONE': 1.0, 'SRC1_ALPHA': src1, 'INV_SRC1_ALPHA': 1.0 - src1,
             'SRC_ALPHA': src[3], 'INV_SRC_ALPHA': 1.0 - src[3], 'DEST_ALPHA': dst[3],
             'INV_DEST_ALPHA': 1.0 - dst[3]}
    return table.get(name)


def predict_blend(op, src, dst, src1):
    if not op['blend']:
        return src[:3]
    s = factor(op['src'], src, dst, src1)
    d = factor(op['dst'], src, dst, src1)
    if s is None or d is None or BLEND.get(op['opb']) != 'ADD':
        return None
    return tuple(min(1.0, max(0.0, s * a + d * b)) for a, b in zip(src[:3], dst[:3]))


def depth_pass(op, z, depth):
    name = CMP.get(op['depthCmp'], 'UNKNOWN')
    if name == 'ALWAYS':
        return True
    if name == 'NEVER':
        return False
    if name == 'LESS':
        return z < depth
    if name == 'LESS_EQUAL':
        return z <= depth + 1e-6
    if name == 'GREATER':
        return z > depth
    if name == 'GREATER_EQUAL':
        return z >= depth - 1e-6
    if name == 'EQUAL':
        return abs(z - depth) < 1e-5
    if name == 'NOT_EQUAL':
        return abs(z - depth) >= 1e-5
    return True


def cpu_mismatch(op):
    if op['kind'] != 'tri' or not op['ff']:
        return []
    expect = dict(
        blend=1 if op['alphaBlend'] or op['cvgAdd'] else 0,
        src=16 if op['alphaBlend'] else 2,
        dst=17 if op['alphaBlend'] else 1,
        opb=1,
        srcA=2,
        dstA=2 if op['cvgAdd'] else 1,
        opa=1,
        mask=15,
        depthEn=1 if op['zCmp'] or op['zUpd'] else 0,
        depthWr=1 if op['zUpd'] else 0,
        depthCmp=2 if op['zCmp'] else 8,
        msc=1,
    )
    return [key for key, value in expect.items() if op[key] != value]


def inside(op, col, y, width):
    x = 16 if col == 0 else width - 17
    return op['x0'] <= x < op['x1'] and op['y0'] <= y < op['y1']


def simulate(op, pre, frags):
    color = pre[:4]
    depth = pre[4]
    if op['kind'] in ('fill', 'control'):
        if frags is None:
            return None
        return (op['cr'], op['cg'], op['cb'], op['ca'], depth)
    if op['kind'].startswith('dither'):
        return None
    if op['kind'] != 'tri':
        return None
    if not frags:
        return pre
    if not op['ff']:
        return None
    wrote = False
    for frag in sorted(frags, key=lambda item: item['order']):
        z = frag['zinfo'][0]
        if not depth_pass(op, z, depth):
            continue
        rgb = predict_blend(op, frag['result'], color, frag['zinfo'][2])
        if rgb is None:
            return None
        color = (rgb[0], rgb[1], rgb[2], frag['result'][3])
        if op['depthWr']:
            depth = z
        wrote = True
    if not wrote:
        return pre
    return color + (depth,)


def scene_table(meta, ops, pix, records):
    samples = pix['samples']
    width = pix['width']
    assert pix['nsample'] == len(ops) + 1
    by_pixel = {}
    zmagic = 0
    checker = 0
    for rec in records:
        by_pixel.setdefault((rec['order'], rec['col'], rec['y']), []).append(rec)
        if abs(rec['zinfo'][3] - 6624.0) < 1e-3:
            zmagic += 1
        x = 16 if rec['col'] == 0 else width - 17
        red = ((x // 2 + rec['y'] // 2) & 1) == 0
        want = (1, 0, 0, 1) if red else (0, 1, 0, 1)
        checker += near(rec['control'], want, 1.0)
    control = ops[0]
    changed = samples[1][(0, 0)]
    other = samples[1][(1, 0)]
    initial = samples[0][(1, 0)]
    control_ok = (control['kind'] == 'control' and near(changed, (1, 0, 1), 2.0)
                  and near(other, initial, 2.0) and not meta['overflow'])
    binding_ok = all(op['colorTex'] == meta['colorTex'] and op['depthTex'] == meta['depthTex'] for op in ops)
    tri_ops = [op for op in ops if op['kind'] == 'tri']
    ff_ok = all(op['ff'] for op in tri_ops)
    mismatches = {}
    for op in tri_ops:
        for key in cpu_mismatch(op):
            mismatches[key] = mismatches.get(key, 0) + 1
    final = samples[-1]
    final_step = step_of(final)
    initial_step = step_of(samples[0])
    # Floor draws are the triangle ops that actually shaded a floor-fmt texel.
    floor_ids = set()
    for rec in records:
        if int(rec['tile'][3]) == 4 and int(rec['dimensions'][3]) == 0:
            for op in tri_ops:
                if op['face0'] <= rec['order'] < op['face0'] + op['faces']:
                    floor_ids.add(op['id'])
    torn = []
    classes = {'rejected': 0, 'later': 0, 'mismatch': 0, 'shader': 0, 'matched': 0, 'uncovered': 0}
    later_kinds = {}
    sim_err = []
    for col in (0, 1):
        for y in range(70):
            if abs(luma(final[(col, y)]) - luma(final[(col, y + 1)])) <= 15.0:
                continue
            for yy in (y, y + 1):
                key = (col, yy)
                if key in torn:
                    continue
                torn.append(key)
    if not torn:
        torn = [(col, y) for col in (0, 1) for y in range(71)]
    for col, y in torn:
        floor_op = None
        frags = []
        for op in ops:
            if op['id'] not in floor_ids:
                continue
            got = []
            for order in range(op['face0'], op['face0'] + op['faces']):
                got.extend(by_pixel.get((order, col, y), []))
            if got:
                floor_op = op
                frags = got
        if floor_op is None:
            classes['uncovered'] += 1
            continue
        pre = samples[floor_op['id']][(col, y)]
        post = samples[floor_op['id'] + 1][(col, y)]
        pred = simulate(floor_op, pre, frags)
        if pred is None or not near(post, pred, 3.0):
            classes['mismatch'] += 1
            if pred is not None:
                sim_err.append(max(abs(post[i] - pred[i]) for i in range(3)) * 255.0)
            continue
        classes['matched'] += 1
        if near(post, pre, 2.0):
            classes['rejected'] += 1
        winning = max(frags, key=lambda item: item['order'])
        if not near(post, winning['result'], 3.0) and not near(post, pre, 2.0):
            classes['shader'] += 1
        later = None
        for op in ops:
            if op['id'] <= floor_op['id']:
                continue
            if not near(samples[op['id'] + 1][(col, y)], samples[op['id']][(col, y)], 2.0):
                later = op['kind']
        if later and not near(final[(col, y)], post, 2.0):
            classes['later'] += 1
            later_kinds[later] = later_kinds.get(later, 0) + 1
    n = max(1, len(torn))
    return dict(control_ok=control_ok, binding_ok=binding_ok, ff_ok=ff_ok, zmagic=zmagic,
                checker=checker, records=len(records), mismatches=mismatches,
                final_step=[round(v, 2) for v in final_step],
                initial_step=[round(v, 2) for v in initial_step],
                torn=len(torn), classes=classes, later_kinds=later_kinds,
                sim_mae=round(statistics.mean(sim_err), 3) if sim_err else 0.0,
                ops=len(ops), tri=len(tri_ops), floor_draws=len(floor_ids),
                rejected_frac=classes['rejected'] / n, later_frac=classes['later'] / n,
                mismatch_frac=classes['mismatch'] / n)


def choose(wide16, wide21):
    def bad(arm):
        return not (arm and arm['control_ok'] and arm['binding_ok'] and arm['ff_ok'] and arm['zmagic'] == arm['records'] and arm['checker'] == arm['records'])
    if bad(wide16) or bad(wide21):
        return 'H-witness'
    if max(wide16['final_step']) > 12 or max(wide21['final_step']) < 20:
        return 'unresolved'
    if wide21['mismatches']:
        return 'H-fixed-function'
    if wide21['mismatch_frac'] >= 0.5:
        return 'H-fixed-function'
    if wide21['later_frac'] >= 0.5:
        return 'H-later-writer'
    if wide21['rejected_frac'] >= 0.5 and max(wide21['initial_step']) >= 20:
        return 'H-late-test'
    if wide21['rejected_frac'] >= 0.5:
        return 'H-late-test'
    if max(wide21['initial_step']) >= 20 and wide21['rejected_frac'] >= 0.5:
        return 'H-prior-writer'
    return 'unresolved'


def selftest():
    def pix(step, base=0.2):
        out = {}
        for col in (0, 1):
            for y in range(71):
                v = base + (y % 2) * step
                out[(col, y)] = (v, v, v, 1, 0.5)
        return out
    smooth = pix(0.01)
    torn = pix(0.25, 0.2)
    # Rejected floor: shader ran, attachment unchanged, initial already torn.
    samples = [torn, torn, torn]
    ops = [
        dict(id=0, kind='control', cr=1, cg=0, cb=1, ca=1, x0=16, y0=180, x1=17, y1=181,
             colorTex=1, depthTex=2, blend=0, src=2, dst=1, opb=1, srcA=2, dstA=1, opa=1,
             mask=15, depthEn=0, depthWr=0, depthCmp=8, msc=1, ff=1, alphaBlend=0, cvgAdd=0,
             zCmp=0, zUpd=0, face0=0, faces=0),
        dict(id=1, kind='tri', colorTex=1, depthTex=2, blend=1, src=16, dst=17, opb=1,
             srcA=2, dstA=1, opa=1, mask=15, depthEn=1, depthWr=1, depthCmp=2, msc=1, ff=1,
             alphaBlend=1, cvgAdd=0, zCmp=1, zUpd=1, face0=0, faces=1),
    ]
    # Control pixel must change. Patch sample 1 at (0,0) only.
    samples = [dict(torn), dict(torn), dict(torn)]
    samples[1][(0, 0)] = (1, 0, 1, 1, 0.5)
    rec = []
    for col in (0, 1):
        for y in range(71):
            rec.append(dict(order=0, col=col, y=y, tile=(0, 0, 0, 4), dimensions=(0, 0, 0, 0),
                            control=(1, 0, 0, 1) if ((16 if col == 0 else 1007) // 2 + y // 2) & 1 == 0 else (0, 1, 0, 1),
                            result=(0.2, 0.2, 0.2, 1), zinfo=(0.9, 1, 1, 6624)))
    # depth 0.9 fails LESS against 0.5, so post stays pre. Prediction equals pre.
    meta = dict(overflow=0, colorTex=1, depthTex=2)
    # The control sample is not actually magenta-only in sample 0->1 for this
    # hand-built torn image except (0,0). other column sample 1 equals sample 0.
    table = scene_table(meta, ops, dict(samples=samples, width=1024, fmt=11, nsample=3), rec)
    assert table['control_ok'] and table['rejected_frac'] > 0.9, table
    smooth_samples = [dict(smooth), dict(smooth), dict(smooth)]
    smooth_samples[1][(0, 0)] = (1, 0, 1, 1, 0.5)
    for col in (0, 1):
        for y in range(71):
            # Depth test passes and replace-blend writes the smooth shader color.
            smooth_samples[2][(col, y)] = (0.2, 0.2, 0.2, 1, 0.2)
    rec_ok = []
    for col in (0, 1):
        for y in range(71):
            rec_ok.append(dict(order=0, col=col, y=y, tile=(0, 0, 0, 4), dimensions=(0, 0, 0, 0),
                               control=(1, 0, 0, 1) if ((16 if col == 0 else 779) // 2 + y // 2) & 1 == 0 else (0, 1, 0, 1),
                               result=(0.2, 0.2, 0.2, 1), zinfo=(0.2, 1, 1, 6624)))
    ops_ok = [dict(ops[0]), dict(ops[1], blend=0, src=2, dst=1, alphaBlend=0, zCmp=1, depthCmp=2)]
    # blend disabled means replace. depth 0.2 < 0.5 passes LESS.
    wide16 = scene_table(meta, ops_ok, dict(samples=smooth_samples, width=796, fmt=11, nsample=3), rec_ok)
    wide21 = scene_table(meta, ops, dict(samples=samples, width=1024, fmt=11, nsample=3), rec)
    assert choose(wide16, wide21) == 'H-late-test', (choose(wide16, wide21), wide16['final_step'], wide21['classes'])
    print('selftest ok', flush=True)


def analyze_arm(root, tag):
    folder = root / tag / 'shader'
    rows = []
    for path in sorted(folder.glob('shader_*.ops.json')):
        ops_meta = json.loads(path.read_text())
        pix_path = path.with_suffix('').with_suffix('.pix')
        # shader_N.ops.json -> shader_N.pix and shader_N.records
        stem = path.name[:-len('.ops.json')]
        pix = load_pix(folder / f'{stem}.pix')
        records = load_records(folder / f'{stem}.records')
        if pix['nsample'] != len(ops_meta['ops']) + 1 or len(records) < 142:
            continue
        for i, op in enumerate(ops_meta['ops']):
            op['id'] = i
        table = scene_table(ops_meta, ops_meta['ops'], pix, records)
        table['serial'] = ops_meta['serial']
        rows.append(table)
    assert rows, f'no attachment scenes: {tag}'
    picked = max(rows, key=lambda row: max(row['final_step']))
    summary = dict(n=len(rows), picked=picked,
                   control_ok=all(row['control_ok'] for row in rows),
                   binding_ok=all(row['binding_ok'] for row in rows),
                   ff_ok=all(row['ff_ok'] for row in rows))
    (root / tag / 'attachment_summary.json').write_text(json.dumps(dict(summary=summary, rows=rows), indent=2) + '\n')
    return picked | summary


def sheet(root, arms, verdict):
    from PIL import Image, ImageDraw
    out = Image.new('RGB', (1100, 280), '#202020')
    draw = ImageDraw.Draw(out)
    draw.text((10, 8), verdict, fill='white')
    for col, (tag, arm) in enumerate(arms.items()):
        folder = root / tag / 'shader'
        stem = folder / f"shader_{arm['picked']['serial']}"
        meta_path = folder / f"shader_{arm['picked']['serial']}.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        target = next(item for item in meta['snapshots'] if item['name'] == 'target')
        import g1d_floor_pipe as pipe
        px = pipe.pixels(dict(target, native_width=meta['width']), stem.with_suffix('.target').read_bytes(), 'gpu')
        image = Image.new('RGB', (meta['width'], meta['height']))
        image.putdata([tuple(round(c) for c in px(x, y)) for y in range(meta['height']) for x in range(meta['width'])])
        image.thumbnail((520, 220))
        x = 10 + col * 540
        out.paste(image, (x, 36))
        draw.text((x, 250), f"{tag} steps {arm['picked']['final_step']} {arm['picked']['classes']}", fill='white')
    out.save(root / 'owner_sheet_attachment.png')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--analyze', action='store_true')
    ap.add_argument('--output-root', type=Path, default=Path('scratch/agent/s6624_attachment'))
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    root = args.output_root.resolve()
    if not args.analyze:
        for aspect, tag, _w in (('16:9', 'wide16', 796), ('21:9', 'wide21', 1024)):
            (root / tag / 'shader').mkdir(parents=True, exist_ok=True)
            os.environ['ROGUESQ_FLOOR_SHADER_DIR'] = str(root / tag / 'shader')
            os.environ.pop('ROGUESQ_FLOOR_PIPE_DIR', None)
            base.run_arm(aspect, tag, 796 if tag == 'wide16' else 1024, root)
    arms = {tag: analyze_arm(root, tag) for tag in ('wide16', 'wide21')}
    verdict = choose(arms['wide16']['picked'], arms['wide21']['picked'])
    result = dict(selects=verdict, arms={tag: arm['picked'] for tag, arm in arms.items()})
    (root / 'attachment_verdict.json').write_text(json.dumps(result, indent=2) + '\n')
    sheet(root, arms, verdict)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
