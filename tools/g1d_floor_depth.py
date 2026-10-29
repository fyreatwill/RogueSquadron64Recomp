"""Name the writer of the striped depth already present at the 21:9 floor sample 0.

One binary, both widths. History runs from depth-target setup through the
first phase>=4 floor submission's sample 0. The floor attachment capture is
unchanged and supplies the magenta and 16:9 ~0.996 controls.
"""
import json
import os
import re
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
    guest_path = depth / 'history.guest'
    guest = load_guest(guest_path, pix['nsample']) if guest_path.exists() else None
    arm = dict(
        events=events, samples=pix['samples'], z=zs, width=width,
        magenta=shader['magenta'], floor_store=shader['floor_store'],
        pix_match=pix_match(hist_enter, shader['enter']),
        overflow=meta.get('overflow', 0), meta=meta, serial=shader['serial'],
        guest=guest,
    )
    arm['table'] = classify(arm)
    arm['copies'], arm['copy_calls'] = load_copies(depth / 'copytoram.jsonl')
    arm['rdram'] = load_events(depth / 'rdram.jsonl') if (depth / 'rdram.jsonl').exists() else []
    writer = arm['table'].get('stripe_writer')
    rec = guest_of(arm, writer) if writer else None
    arm['head_raw'] = rec['rawBe'][:13] if rec and rec.get('rawBe') else None
    if rec is not None and writer is not None and writer['sample'] < len(arm['samples']):
        worst, _endian, _dec, _n = best_decode(rec, arm['samples'][writer['sample']])
        arm['guest_mae'] = worst
    else:
        arm['guest_mae'] = None
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
            'zCmp', 'zUpd', 'depthCmp', 'depthWr', 'faces', 'sample', 'captureZ', 'whole',
            'site', 'rowStart', 'stride', 'guestAddr', 'storeAddr', 'guestCovers', 'guest')
    return {k: ev[k] for k in keys if k in ev}


GUEST_REC = 32 + 48 + 142 * 4 * 2 + 142 * 2 * 2
GUEST_MAGIC = 0x66346627


def load_guest(path, nsample):
    data = path.read_bytes()
    magic, n = struct.unpack_from('<2I', data)
    assert magic == GUEST_MAGIC and n == nsample, (path, magic, n, nsample)
    assert len(data) == 8 + nsample * GUEST_REC, (path, len(data), nsample, GUEST_REC)
    rows = []
    for s in range(nsample):
        base = 8 + s * GUEST_REC
        present, width, height, row_start, stride, address, store_addr, covers = struct.unpack_from('<8I', data, base)
        site = data[base + 32:base + 80].split(b'\0', 1)[0].decode()
        dec = list(struct.unpack_from('<142f', data, base + 80))
        alt = list(struct.unpack_from('<142f', data, base + 80 + 568))
        raw_be = list(struct.unpack_from('<142H', data, base + 1216))
        raw_le = list(struct.unpack_from('<142H', data, base + 1500))
        rows.append(dict(present=present, site=site, width=width, height=height, rowStart=row_start,
                         stride=stride, address=address, storeAddr=store_addr, covers=covers,
                         dec=dec, alt=alt, rawBe=raw_be, rawLe=raw_le))
    return rows


def flat_mae(dec, sample):
    errs = []
    for col in (0, 1):
        for y in range(71):
            g = dec[col * 71 + y]
            if g < 0:
                continue
            errs.append(abs(g - sample[(col, y)][4]))
    if not errs:
        return None, 0
    return max(errs), len(errs)


def as_depth_sample(dec):
    sample = {}
    for col in (0, 1):
        for y in range(71):
            z = dec[col * 71 + y]
            sample[(col, y)] = (0.0, 0.0, 0.0, 1.0, -1.0 if z < 0 else z)
    return sample


def is_guest_stripe(dec):
    return is_stripe(as_depth_sample(dec))


def is_clear_dec(dec):
    vals = [z for z in dec if z >= 0]
    return len(vals) >= 60 and all(abs(z - 1.0) < 1e-3 for z in vals)


def is_smooth_dec(dec):
    if is_clear_dec(dec) or is_guest_stripe(dec):
        return False
    for col in (0, 1):
        colv = [dec[col * 71 + y] for y in range(71)]
        if any(v < 0 for v in colv):
            return False
        if sum(abs(v) < 1e-6 for v in colv[:13]) >= 8:
            return False
        second = [abs(colv[i + 2] - 2 * colv[i + 1] + colv[i]) for i in range(69)]
        if not second or max(second) > 0.02:
            return False
    return True


def best_decode(guest, sample):
    ranked = []
    for name, dec in (('be', guest['dec']), ('le', guest['alt'])):
        worst, n = flat_mae(dec, sample)
        ranked.append((1e9 if worst is None else worst, name, dec, n))
    ranked.sort(key=lambda row: row[0])
    return ranked[0]


def differ_span(dec, sample):
    rows = []
    for y in range(71):
        for col in (0, 1):
            g = dec[col * 71 + y]
            if g < 0:
                continue
            if abs(g - sample[(col, y)][4]) > 0.02:
                rows.append(180 + y)
                break
    if not rows:
        return None
    return [rows[0], rows[-1]]


def name_input(ev, dec, sample):
    notes = []
    width = ev.get('depthW') or ev.get('colorW') or 0
    if ev.get('stride') and width and ev['stride'] != width * 2:
        notes.append('stride')
    if ev.get('storeAddr') and ev.get('guestAddr') and ev['storeAddr'] != ev['guestAddr']:
        notes.append('lookup-addr')
    best_shift, best = 0, 1e9
    for shift in range(-20, 21):
        err = []
        for col in (0, 1):
            for y in range(71):
                ys = y + shift
                if ys < 0 or ys >= 71:
                    continue
                g = dec[col * 71 + ys]
                if g < 0:
                    continue
                err.append(abs(g - sample[(col, y)][4]))
        if len(err) >= 40:
            worst = max(err)
            if worst < best:
                best, best_shift = worst, shift
    if best_shift != 0 and best <= 1e-3:
        notes.append('viewport-shift-%d' % best_shift)
    else:
        # A boolean discard keeps the cleared 1.0. It cannot paint the zeros.
        notes.append('pixel-texture')
    return notes, best_shift, best


def guest_of(arm, ev):
    if ev is None or ev.get('sample', -1) < 0 or not ev.get('guest'):
        return None
    guests = arm.get('guest')
    if not guests or ev['sample'] >= len(guests):
        return None
    rec = guests[ev['sample']]
    if not rec or not rec.get('present'):
        return None
    return rec


def floor_guest_copies(arm):
    floor = arm['table'].get('floor')
    if floor is None:
        return []
    out = []
    for ev in arm['events']:
        if ev.get('kind') == 'copy-changes' and ev.get('depth') == floor.get('depth') and ev.get('guest') == 1:
            out.append(ev)
    return out


def decide_upload(wide16, wide21):
    bad = list(controls(wide16, wide21))
    detail = {}
    if wide16.get('guest') is None or wide21.get('guest') is None:
        bad.append('guest-file')
    if bad:
        return 'H-witness', bad, detail
    for ev in floor_guest_copies(wide16):
        rec = guest_of(wide16, ev)
        if rec is None or rec.get('covers', 0) < 60:
            bad.append('wide16-guest')
            break
        sample = wide16['samples'][ev['sample']]
        worst, _name, _dec, n = best_decode(rec, sample)
        if n < 60 or worst > 1e-3 or not all_ones(sample):
            bad.append('wide16-guest')
            break
    if bad:
        return 'H-witness', bad, detail
    writer = wide21['table'].get('stripe_writer')
    if writer is None or writer.get('kind') != 'copy-changes':
        return 'H-witness', ['no-stripe-upload'], detail
    rec = guest_of(wide21, writer)
    if rec is None or rec.get('covers', 0) < 60:
        return 'H-witness', ['guest-missing'], detail
    gpu = wide21['samples'][writer['sample']]
    if not is_stripe(gpu):
        return 'H-witness', ['upload-not-stripe'], detail
    worst, endian, dec, n = best_decode(rec, gpu)
    detail = dict(
        site=writer.get('site') or rec.get('site'),
        stride=writer.get('stride', rec.get('stride')),
        guestAddr=writer.get('guestAddr', rec.get('address')),
        storeAddr=writer.get('storeAddr', rec.get('storeAddr')),
        rowStart=writer.get('rowStart', rec.get('rowStart')),
        covers=rec.get('covers'),
        endian=endian, mae=worst, npix=n,
        guest_stripe=is_guest_stripe(dec),
        guest_clear=is_clear_dec(rec['dec']),
        guest_smooth=is_smooth_dec(rec['dec']),
    )
    if n < 60:
        return 'H-witness', ['guest-short'], detail
    if worst <= 1e-3 and is_guest_stripe(dec):
        detail['input'] = 'faithful'
        return 'H-guest', [], detail
    if is_clear_dec(rec['dec']) or is_smooth_dec(rec['dec']) or is_guest_stripe(rec['dec']):
        notes, shift, shift_mae = name_input(writer, rec['dec'], gpu)
        detail['input'] = notes
        detail['shift'] = shift
        detail['shift_mae'] = shift_mae
        detail['rows'] = differ_span(rec['dec'], gpu)
        return 'H-upload', [], detail
    return 'H-witness', ['decode-unrecognized'], detail


ORIGIN = 0x00B56000
STRIDE = 2048
HEAD_YS = list(range(180, 193))


def load_copies(path):
    rows = []
    calls = [0] * 8
    if not path.exists():
        return rows, calls
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        rows.append(rec)
        got = rec.get('calls')
        if isinstance(got, list) and len(got) == 8:
            calls = got
    return rows, calls


def target_phys(x, y):
    return ORIGIN + y * STRIDE + x * 2


def byte_span(rec):
    phys = rec.get('phys')
    width = rec.get('width')
    row0 = rec.get('rowStart')
    row1 = rec.get('rowEnd')
    if not isinstance(phys, int) or phys >= 0xF0000000 or not isinstance(width, int):
        return None
    if not isinstance(row0, int) or not isinstance(row1, int) or row1 <= row0:
        return None
    return phys, phys + (row1 - row0) * width * 2


def covering_word(rec, x, y):
    if rec.get('k') != 'w' or not rec.get('copied'):
        return None
    want = target_phys(x, y)
    for word in rec.get('words') or []:
        same_pixel = word.get('x') == x and word.get('y') == y
        if word.get('phys') == want and (word.get('watch') or same_pixel):
            return word
    span = byte_span(rec)
    if span is not None and span[0] <= want < span[1]:
        return 'missing-word'
    return None


def upload_cutoff(rows):
    for rec in rows:
        if rec.get('k') != 'up' or rec.get('site') != 'state.cpp:2604' or rec.get('width') != 1024:
            continue
        raw = rec.get('rawBe') or []
        if len(raw) >= 13 and all(v == 0 for v in raw[:13]):
            return rec.get('n')
    return None


def call_total(calls):
    return sum(calls) if isinstance(calls, list) else 0


def decide_ram(wide16, wide21):
    bad = list(controls(wide16, wide21))
    detail = {}
    if call_total(wide16.get('copy_calls')) <= 0 or call_total(wide21.get('copy_calls')) <= 0:
        bad.append('copy-count')
    head = wide21.get('head_raw')
    if not isinstance(head, list) or len(head) < 13 or any(v != 0 for v in head[:13]):
        bad.append('head-raw')
    mae = wide21.get('guest_mae')
    if mae is None or mae > 1e-3:
        bad.append('gpu-match')
    if bad:
        return 'H-witness', bad, detail
    rows = wide21.get('copies') or []
    cutoff = upload_cutoff(rows)
    if cutoff is None:
        return 'H-witness', ['upload-marker'], detail
    last = {}
    logger_bad = False
    for rec in rows:
        if rec.get('k') != 'w' or rec.get('n', 0) >= cutoff:
            continue
        for y in HEAD_YS:
            got = covering_word(rec, 16, y)
            if got in ('missing-word', 'mismatch'):
                logger_bad = True
            elif got is not None:
                last[y] = (rec, got)
    if logger_bad:
        return 'H-witness', ['word-layout'], detail
    records = []
    seen = set()
    fffc = 0
    for y in HEAD_YS:
        if y not in last:
            continue
        rec, _word = last[y]
        key = rec.get('n')
        if key in seen:
            continue
        seen.add(key)
        words = rec.get('words') or []
        fffc += sum(1 for w in words if w.get('rawBe') == 0xFFFC)
        records.append(dict(
            n=key, width=rec.get('width'), phys=rec.get('phys'),
            rowStart=rec.get('rowStart'), rowEnd=rec.get('rowEnd'), copied=rec.get('copied'),
        ))
    zeros = sum(1 for y in last if last[y][1].get('rawBe') == 0)
    detail = dict(
        cutoff=cutoff, covered=len(last), zeros=zeros, nonzero=len(last) - zeros, fffc=fffc,
        records=records, calls=wide21.get('copy_calls'), calls16=wide16.get('copy_calls'),
        head=[None if y not in last else last[y][1].get('rawBe') for y in HEAD_YS],
    )
    if not last:
        return 'H-unwritten', [], detail
    if len(last) == 13 and zeros == 13:
        return 'H-writeback', [], detail
    if len(last) == 13 and zeros == 0:
        return 'H-later-zero', [], detail
    return 'H-split', [], detail


def b4_zero(rec):
    return str(rec.get('b4', '')).upper() in ('00000000', '0X00000000')


def same_host(a, b):
    host = a.get('host')
    if host and host == b.get('host') and host not in ('0x0', '0'):
        return True
    return a.get('eq') == 1 and b.get('eq') == 1


def head_raw(rec):
    cols = {}
    for col in rec.get('cols') or []:
        if col.get('in'):
            cols[(col.get('x'), col.get('y'))] = col.get('raw')
    vals = []
    for y in HEAD_YS:
        raw = cols.get((16, y))
        if not isinstance(raw, int) or raw < 0:
            return None
        vals.append(raw)
    return vals


def last_cover_n(copies, cutoff):
    last = None
    for rec in copies or []:
        if rec.get('k') != 'w' or not isinstance(rec.get('n'), int) or rec['n'] >= cutoff:
            continue
        got = covering_word(rec, 16, 180)
        if isinstance(got, dict):
            last = rec['n']
    return last


def classify_sites(sites, cutoff, copies):
    if cutoff is None:
        return 'H-witness', ['upload-marker'], {}
    bs = [r for r in sites or [] if r.get('k') == 'b' and isinstance(r.get('n'), int) and r['n'] < cutoff]
    if not bs:
        return 'H-witness', ['site-b'], {}
    store = max(bs, key=lambda r: r['n'])
    writes = [r for r in sites or [] if r.get('k') == 'a' and isinstance(r.get('n'), int) and r['n'] < store['n']]
    if not writes:
        return 'H-witness', ['site-a'], {}
    write = max(writes, key=lambda r: r['n'])
    detail = dict(
        a_n=write.get('n'), b_n=store.get('n'), cutoff=cutoff, wn=write.get('wn'),
        a_count=sum(1 for r in sites or [] if r.get('k') == 'a'),
        b_count=sum(1 for r in sites or [] if r.get('k') == 'b'),
        a_host=write.get('host'), b_host=store.get('host'),
        a_rdram=write.get('rdram'), b_rdram=store.get('rdram'),
        a_eq=write.get('eq'), b_eq=store.get('eq'),
        a_phys0=write.get('phys0'), b_phys0=store.get('phys0'),
        a_native=write.get('native'), a_swap=write.get('swap'), a_raw=write.get('raw'),
        a_b4=write.get('b4'), b_raw=store.get('raw'), b_b4=store.get('b4'),
        a_fl=write.get('fl'), same_host=int(same_host(write, store)),
    )
    cover = last_cover_n(copies, cutoff)
    detail['cover_n'] = cover
    if cover is None or write.get('wn') != cover:
        return 'H-witness', ['pair'], detail
    native = write.get('native')
    raw = write.get('raw')
    swap = write.get('swap')
    if not isinstance(native, int) or native < 0:
        return 'H-witness', ['native-missing'], detail
    if native == 0:
        return 'H-witness', ['native-zero'], detail
    if raw == 0:
        if not isinstance(swap, int) or swap < 0:
            return 'H-witness', ['swap-missing'], detail
        detail['step'] = 'byteswap' if swap == 0 else 'after-byteswap'
        return 'H-swap', [], detail
    b_head = head_raw(store)
    detail['b_head'] = b_head
    if b4_zero(store) and not same_host(write, store):
        return 'H-alias', [], detail
    if b_head is not None and all(v == 0 for v in b_head) and same_host(write, store):
        return 'H-between', [], detail
    if b_head is not None and all(v == 0 for v in b_head):
        return 'H-alias', [], detail
    if isinstance(store.get('raw'), int) and store['raw'] != 0 and same_host(write, store):
        return 'H-after-store', [], detail
    return 'H-witness', ['unmatched'], detail


def finish_rdram(upload_verdict, ram_verdict, ram, sites, copies):
    if upload_verdict != 'H-guest' or ram_verdict != 'H-later-zero':
        return 'H-witness', ['control', upload_verdict, ram_verdict], {}
    cutoff = upload_cutoff(copies)
    selects, why, detail = classify_sites(sites, cutoff, copies)
    if selects == 'H-witness':
        return selects, why, detail
    head = (ram or {}).get('head') or []
    if not head or head[0] != detail.get('a_native'):
        return 'H-witness', ['native-mismatch'], detail
    return selects, why, detail


def classify_writers(sites, prior, detail):
    writers = [r for r in sites or [] if r.get('k') == 'writer' and r.get('class') != 'ownership']
    controls = {}
    for cls in ('guest', 'host'):
        controls[cls] = [r for r in writers if r.get('target') == 0x1FF0020
                         and r.get('class', '').startswith(cls)
                         and r.get('before', 0) != 0 and r.get('after') == 0]
    if not all(controls.values()):
        return 'H-witness', ['writer-controls'], dict(controls=controls)
    if prior != 'H-between':
        return 'H-witness', ['writer-transition', prior], dict(controls=controls)
    rows = [r for r in writers if r.get('target') == 0xBB0020
            and detail['a_n'] < r['n'] < detail['b_n']
            and r['phys'] < 0xBB0024 and r['phys'] + r['len'] > 0xBB0020]
    changed = [r for r in rows if r.get('before', 0) != 0 and r.get('after') == 0]
    out = dict(controls=controls, rows=rows, zero_writers=changed)
    if not changed:
        return 'H-uncovered', ['no-intersecting-zero-transition'], out
    if any(r['class'] == 'guest-delayed' for r in changed):
        return 'H-uncovered', ['delayed-store-needs-post-witness'], out
    classes = {r['class'].split('-')[0] for r in changed}
    if len(classes) != 1:
        return 'H-uncovered', ['multiple-writer-classes'], out
    return ('H-guest-store' if 'guest' in classes else 'H-host-write'), [], out


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

    def dec_from(fn):
        out = [-1.0] * 142
        for col in (0, 1):
            for y in range(71):
                out[col * 71 + y] = fn(col, y)
        return out

    def grec(dec, alt=None):
        return dict(present=1, site='state.cpp:2604', covers=71, stride=2048, address=1, storeAddr=1,
                    rowStart=0, width=1024, height=339, dec=dec, alt=dec if alt is None else alt)

    ramp = lambda col, y: 0.0 if y < 13 else (0.964 if col == 0 else 1.0)
    ramp_dec = dec_from(ramp)
    gpu_ramp = blank(0.2, ramp)
    w16 = dict(wide16, guest=[])
    upload = ev('copy-changes', 1, guest=1, site='state.cpp:2604', stride=2048, guestAddr=1, storeAddr=1, depth='0xfloor')
    floor_u = ev('floor-enter', 2, depth='0xfloor', zCmp=0, zUpd=0, depthWr=0, captureZ=0)
    guest_arm = dict(base_arm, events=[setup, clear, upload, floor_u], samples=[one, gpu_ramp, gpu_ramp],
                     z=[[(0, 0, 0, 0)] * 142] * 3, guest=[None, grec(ramp_dec), None])
    guest_arm['table'] = classify(guest_arm)
    assert decide_upload(w16, guest_arm)[0] == 'H-guest', decide_upload(w16, guest_arm)
    clear_guest = dict(guest_arm, guest=[None, grec(dec_from(lambda col, y: 1.0)), None])
    clear_guest['table'] = guest_arm['table']
    got = decide_upload(w16, clear_guest)
    assert got[0] == 'H-upload' and 'pixel-texture' in got[2]['input'], got
    stride_guest = dict(clear_guest, events=[setup, clear, ev('copy-changes', 1, guest=1, site='state.cpp:2604', stride=1280, guestAddr=1, storeAddr=9, depth='0xfloor'), floor_u])
    stride_guest['table'] = classify(stride_guest)
    got = decide_upload(w16, stride_guest)
    assert got[0] == 'H-upload' and 'stride' in got[2]['input'] and 'lookup-addr' in got[2]['input'], got
    le_guest = dict(guest_arm, guest=[None, grec(dec_from(lambda col, y: 0.2), ramp_dec), None])
    le_guest['table'] = guest_arm['table']
    got = decide_upload(w16, le_guest)
    assert got[0] == 'H-guest' and got[2]['endian'] == 'le', got
    bare = dict(guest_arm, events=[setup, clear, ev('copy-changes', 1, guest=0, depth='0xfloor'), floor_u], guest=[None, None, None])
    bare['table'] = classify(bare)
    assert decide_upload(w16, bare)[1] == ['guest-missing']
    noise = dec_from(lambda col, y: 0.2 if y % 2 == 0 else 0.55)
    noisy = dict(guest_arm, guest=[None, grec(noise, noise), None])
    noisy['table'] = guest_arm['table']
    assert decide_upload(w16, noisy)[0] == 'H-witness'
    assert decide_upload(dict(w16, guest=None), guest_arm)[1] == ['guest-file']

    def ram_arm(base, head, calls, copies, mae=0.0):
        arm = dict(base)
        arm['head_raw'] = head
        arm['guest_mae'] = mae
        arm['copy_calls'] = calls
        arm['copies'] = copies
        return arm

    def pix(x, y, raw):
        return dict(x=x, y=y, rawBe=raw, phys=ORIGIN + y * STRIDE + x * 2)

    def wide_rec(n, raw_of):
        words = []
        for y in list(HEAD_YS) + [200]:
            for x in (16, 1024 - 17):
                words.append(pix(x, y, raw_of(x, y)))
        return dict(k='w', n=n, siz=2, width=1024, phys=ORIGIN, rowStart=0, rowEnd=339,
                    copied=1, calls=[0, 0, 8, 0, 0, 0, 0, 0], words=words)

    def up(n):
        return dict(k='up', n=n, site='state.cpp:2604', width=1024, rawBe=[0] * 26,
                    calls=[0, 0, 8, 0, 0, 0, 0, 0])

    calls = [0, 0, 8, 0, 0, 0, 0, 0]
    left0 = lambda x, y: 0 if y <= 192 and x == 16 else (0xFFFC if y == 200 else 0x9E40)
    w16r = ram_arm(wide16, [1] * 13, [0, 0, 4, 0, 0, 0, 0, 0], [])
    wrote0 = ram_arm(prior, [0] * 13, calls, [wide_rec(1, lambda x, y: 0xFFFC), wide_rec(2, left0), up(3)])
    got = decide_ram(w16r, wrote0)
    assert got[0] == 'H-writeback' and got[2]['fffc'] >= 1 and got[2]['covered'] == 13, got
    later = ram_arm(prior, [0] * 13, calls, [wide_rec(1, lambda x, y: 0xFFFC), up(2)])
    assert decide_ram(w16r, later)[0] == 'H-later-zero', decide_ram(w16r, later)
    after = ram_arm(prior, [0] * 13, calls, [up(1), wide_rec(2, lambda x, y: 0)])
    assert decide_ram(w16r, after)[0] == 'H-unwritten', decide_ram(w16r, after)
    other = ram_arm(prior, [0] * 13, calls, [
        dict(k='w', n=1, copied=1, width=796, phys=0x1000, rowStart=0, rowEnd=336, words=[], calls=calls),
        up(2)])
    assert decide_ram(w16r, other)[0] == 'H-unwritten'
    assert decide_ram(w16r, ram_arm(prior, [0] * 13, [0] * 8, []))[0] == 'H-witness'
    assert decide_ram(w16r, ram_arm(prior, [0] * 13, calls, [wide_rec(2, left0)]))[1] == ['upload-marker']
    # A 447-row color write at 0xB20000 covers depth 0xB56000 at a different image y.
    # Image y=180 of that write is not the depth pixel. Only the absolute phys counts.
    overlap_words = [dict(x=16, y=y, rawBe=0, phys=target_phys(16, y), watch=1) for y in HEAD_YS]
    overlap_words.append(dict(x=16, y=200, rawBe=0xFFFC, phys=target_phys(16, 200), watch=1))
    overlap = dict(k='w', n=1, siz=2, width=1024, phys=0xB20000, rowStart=0, rowEnd=447,
                   copied=1, calls=calls, words=overlap_words)
    assert byte_span(overlap)[0] <= target_phys(16, 180) < byte_span(overlap)[1]
    got = decide_ram(w16r, ram_arm(prior, [0] * 13, calls, [overlap, up(2)]))
    assert got[0] == 'H-writeback' and got[2]['fffc'] == 1, got
    decoy_words = [dict(x=16, y=180, rawBe=0, phys=0xB20000 + 180 * 2048 + 32)]
    decoy = dict(k='w', n=1, siz=2, width=1024, phys=0xB20000, rowStart=0, rowEnd=447,
                 copied=1, calls=calls, words=decoy_words)
    assert decide_ram(w16r, ram_arm(prior, [0] * 13, calls, [decoy, up(2)]))[1] == ['word-layout']

    def rcol(x, y, raw, native=-1, swap=-1):
        return {'x': x, 'y': y, 'in': 1, 'raw': raw, 'native': native, 'swap': swap}

    def rsite(k, n, host, raw, native=-1, swap=-1, b4=None, wn=0, head=None):
        cols = []
        for x in (16, 1007):
            for y in list(HEAD_YS) + [200]:
                val = head if head is not None and x == 16 and y in HEAD_YS else raw
                cols.append(rcol(x, y, val, native if k == 'a' else -1, swap if k == 'a' else -1))
        if b4 is None:
            b4 = '00000000' if raw == 0 else '4C9F0000'
        return dict(k=k, n=n, wn=wn, host=host, rdram='0x10', eq=1 if host == '0xA' else 0,
                    b4=b4, raw=raw, native=native, swap=swap, fl=0, phys0=1, cols=cols)

    cover = wide_rec(4, lambda x, y: 0x9F4C)
    copies = [cover, up(9)]
    ram = dict(head=[0x9F4C] * 13)
    base_sites = [
        rsite('a', 5, '0xA', 0, native=0x9F4C, swap=0, wn=4),
        rsite('b', 8, '0xA', 0, head=0),
    ]
    got = finish_rdram('H-guest', 'H-later-zero', ram, base_sites, copies)
    assert got[0] == 'H-swap' and got[2]['step'] == 'byteswap', got
    after = [
        rsite('a', 5, '0xA', 0, native=0x9F4C, swap=0x9F4C, wn=4),
        rsite('b', 8, '0xA', 0, head=0),
    ]
    got = finish_rdram('H-guest', 'H-later-zero', ram, after, copies)
    assert got[0] == 'H-swap' and got[2]['step'] == 'after-byteswap', got
    alias = [
        rsite('a', 5, '0xA', 0x9F4C, native=0x9F4C, swap=0x9F4C, wn=4),
        rsite('b', 8, '0xB', 0, head=0),
    ]
    assert finish_rdram('H-guest', 'H-later-zero', ram, alias, copies)[0] == 'H-alias'
    between = [
        rsite('a', 5, '0xA', 0x9F4C, native=0x9F4C, swap=0x9F4C, wn=4),
        rsite('b', 8, '0xA', 0, head=0),
    ]
    assert finish_rdram('H-guest', 'H-later-zero', ram, between, copies)[0] == 'H-between'
    later = [
        rsite('a', 5, '0xA', 0x9F4C, native=0x9F4C, swap=0x9F4C, wn=4),
        rsite('b', 8, '0xA', 0x9F4C, b4='4C9F0000'),
    ]
    assert finish_rdram('H-guest', 'H-later-zero', ram, later, copies)[0] == 'H-after-store'
    mismatch = [
        rsite('a', 5, '0xA', 0x9F4C, native=0x1111, swap=0x9F4C, wn=4),
        rsite('b', 8, '0xA', 0, head=0),
    ]
    assert finish_rdram('H-guest', 'H-later-zero', ram, mismatch, copies)[1] == ['native-mismatch']
    assert finish_rdram('H-guest', 'H-later-zero', ram, [], copies)[1] == ['site-b']
    assert finish_rdram('H-upload', 'H-later-zero', ram, between, copies)[0] == 'H-witness'
    wc = [dict(k='writer', n=1, target=0x1FF0020, before=0x78, after=0,
               **{'class': c}) for c in ('guest-delayed', 'host')]
    d = dict(a_n=10, b_n=20)
    for cls, verdict in [('guest-exact', 'H-guest-store'), ('host', 'H-host-write')]:
        row = dict(k='writer', n=15, target=0xBB0020, phys=0xBB0020, len=4,
                   before=0x9EC49ECC, after=0, **{'class': cls})
        assert classify_writers(wc+[row], 'H-between', d)[0] == verdict
        row['before'] = 0
        assert classify_writers(wc+[row], 'H-between', d)[0] == 'H-uncovered'
        row['before'] = 1
        row['n'] = 21
        assert classify_writers(wc+[row], 'H-between', d)[0] == 'H-uncovered'
    delayed = dict(k='writer', n=15, target=0xBB0020, phys=0xBB0020, len=4,
                   before=1, after=0, **{'class': 'guest-delayed'})
    assert classify_writers(wc+[delayed], 'H-between', d)[1] == ['delayed-store-needs-post-witness']
    assert classify_writers(wc[:1], 'H-between', d)[1] == ['writer-controls']
    assert classify_writers(wc, 'H-swap', d)[1] == ['writer-transition', 'H-swap']
    own_selftest()
    print('selftest ok', flush=True)


WATCH = 0x00BB0020
OUTSIDE = (0x00BB5FDE, 0x00BB6020, 0x00BB67DE)
FB_PTRS = tuple(0x801163D8 + 4 * i for i in range(9))


def own_fields(row):
    return {k: int(v, 16) for k, v in re.findall(
        r'(?:^|;)([0-9A-F]{8})=([0-9A-F]{8})(?=;|$)', row.get('caller') or '')}


def byte_covers(phys, length, addr):
    return phys <= addr < phys + length


def parse_fb(api):
    m = re.search(r'fb=([0-9A-Fa-f]+)-([0-9A-Fa-f]+),w=(\d+),h=(\d+)', api or '')
    if not m:
        return None
    return dict(start=int(m.group(1), 16), end=int(m.group(2), 16),
                w=int(m.group(3)), h=int(m.group(4)))


def named_fb(fields, fb_start):
    want = fb_start & 0x1FFFFFFF
    return [p for p in FB_PTRS if (fields.get(f'{p:08X}') or 0) & 0x1FFFFFFF == want and fields.get(f'{p:08X}')]


def outside_hits(events, lo, hi):
    found = {}
    for addr in OUTSIDE:
        hits = []
        for r in events:
            n = r.get('n', -1)
            if not (lo < n < hi):
                continue
            if (r.get('class') in ('guest-exact', 'host') and r.get('target') == addr
                    and r.get('before') != r.get('after')):
                hits.append(dict(n=n, cls=r['class'], api=r.get('api'), pc=r.get('pc'),
                                  before=r.get('before'), after=r.get('after')))
            elif (r.get('class') == 'ownership' and r.get('api') in ('malloc', 'clear')
                    and byte_covers(r.get('phys', 0), r.get('len', 0), addr)):
                hits.append(dict(n=n, cls='ownership', api=r['api'], phys=r['phys'], len=r['len']))
        found[f'{addr:08X}'] = hits[:8]
    return found


def decide_ownership(events):
    own = [r for r in events if r.get('class') == 'ownership']
    reads = []
    for r in own:
        if str(r.get('api', '')).startswith('depth-read'):
            fb = parse_fb(r.get('api'))
            if fb and fb['start'] <= WATCH < fb['end']:
                reads.append((r, fb))
    pairs = []
    for m in own:
        if m.get('api') != 'malloc' or not byte_covers(m.get('phys', 0), m.get('len', 0), WATCH):
            continue
        clear = next((c for c in own if c.get('api') == 'clear' and c['n'] > m['n']
                      and c.get('phys') == m.get('phys') and c.get('len') == m.get('len')), None)
        if clear:
            pairs.append((m, clear))
    base = dict(mallocs=sum(r.get('api') == 'malloc' for r in own),
                clears=sum(r.get('api') == 'clear' for r in own),
                reads=len(reads), pairs=len(pairs))
    if not any(r.get('api') == 'malloc' and byte_covers(r.get('phys', 0), r.get('len', 0), WATCH) for r in own):
        return dict(selects='no-overlap', why='no malloc range contains 0xBB0020', **base)
    if not pairs:
        return dict(selects='instrument-fail', why='malloc covers 0xBB0020 but no matching clear', **base)
    chosen = None
    for m, c in pairs:
        later = [(r, fb) for r, fb in reads if r['n'] > c['n']]
        store = next((r for r in events if r.get('class') == 'guest-exact' and r.get('target') == WATCH
                      and r.get('after') == 0 and m['n'] <= r.get('n', -1) <= c['n'] + 8), None)
        if later and store:
            chosen = (m, c, later[0][0], later[0][1], store)
    if chosen is None and pairs and not reads:
        return dict(selects='no-depth-upload', why='zlib clear covers 0xBB0020 but no later depth upload does', **base)
    if chosen is None:
        return dict(selects='incomplete', why='missing the clear store or a later covering depth-read', **base)
    m, c, read, fb, store = chosen
    if not (fb['start'] <= read.get('phys', -1) < fb['end']):
        return dict(selects='H-address', why='depth-read address is outside the recorded fb interval',
                    fb=fb, read_phys=read.get('phys'), **base)
    named_set = [r for r in own if r.get('api') == 'setzimg' and r['n'] < read['n']
                 and (r.get('phys', 0) & 0x1FFFFFFF) == (fb['start'] & 0x1FFFFFFF)]
    if not named_set:
        return dict(selects='H-address', why='no SETZIMG before the upload names this fb', fb=fb, **base)
    freed = [r for r in own if r.get('api') in ('free', 'free-entry') and m['n'] < r['n'] < read['n']
             and r.get('phys') == m.get('phys')]
    names = named_fb(own_fields(m), fb['start']) or named_fb(own_fields(c), fb['start'])
    names_read = named_fb(own_fields(read), fb['start'])
    common = dict(fb=fb, malloc_phys=m['phys'], malloc_len=m['len'], malloc_n=m['n'],
                  clear_n=c['n'], read_n=read['n'], setzimg_n=named_set[-1]['n'],
                  named_ptrs=[f'{p:08X}' for p in (names or names_read)], freed=len(freed),
                  workload=read.get('api'), outside=outside_hits(events, m['n'], read['n']), **base)
    # A later free of the zlib window does not release the framebuffer. Stale means
    # the reservation no longer named this image when the malloc returned.
    if names or names_read:
        return dict(selects='H-live-overlap',
                    why='guest framebuffer pointer still names this depth image when the overlapping malloc returns',
                    **common)
    if freed:
        return dict(selects='H-stale-target',
                    why='the overlapping malloc was freed before the upload and the reservation did not name the image',
                    **common)
    return dict(selects='H-stale-target',
                why='zlib block overlaps a depth upload whose reservation pointers no longer name it', **common)


def own_row(api, n, phys, length, caller='', **extra):
    row = dict(k='writer', n=n, **{'class': 'ownership'}, pc=0, phys=phys, len=length,
               target=WATCH, before=0, after=0, api=api, caller=caller)
    row.update(extra)
    return row


def own_selftest():
    fb = 'depth-read:pair=1,workload=9,present=3,fb=00B56000-00C00000,w=1024,h=340'
    snap = '801163D8=80B56000;801163DC=00000000;'
    store = dict(k='writer', n=12, **{'class': 'guest-exact'}, pc=0x800078EC, phys=WATCH,
                 len=1, target=WATCH, before=0x9F4C, after=0, api='scalar', caller='')
    live = [
        own_row('setzimg', 5, 0xB56000, 1024),
        own_row('malloc', 10, 0xBADB50, 0x8000, snap),
        store,
        own_row('clear', 13, 0xBADB50, 0x8000, snap),
        own_row('setzimg', 14, 0xB56000, 1024),
        own_row(fb, 20, 0xB56000, 0xAA000),
    ]
    assert decide_ownership(live)['selects'] == 'H-live-overlap'
    stale = [
        own_row('setzimg', 5, 0xB56000, 1024),
        own_row('malloc', 10, 0xBADB50, 0x8000, '801163D8=80C10000;'),
        store,
        own_row('clear', 13, 0xBADB50, 0x8000, '801163D8=80C10000;'),
        own_row(fb, 20, 0xB56000, 0xAA000),
    ]
    assert decide_ownership(stale)['selects'] == 'H-stale-target'
    freed = stale + [own_row('free', 15, 0xBADB50, 0)]
    assert decide_ownership(freed)['selects'] == 'H-stale-target'
    live_freed = live + [own_row('free', 16, 0xBADB50, 0, snap)]
    assert decide_ownership(live_freed)['selects'] == 'H-live-overlap'
    assert decide_ownership(live_freed)['freed'] == 1
    alien = [
        own_row('setzimg', 5, 0xA00000, 1024),
        own_row('malloc', 10, 0xBADB50, 0x8000, snap),
        store,
        own_row('clear', 13, 0xBADB50, 0x8000, snap),
        own_row(fb, 20, 0xB56000, 0xAA000),
    ]
    assert decide_ownership(alien)['selects'] == 'H-address'
    assert decide_ownership([own_row('setzimg', 1, 0xB56000, 1024)])['selects'] == 'no-overlap'
    assert decide_ownership([
        own_row('malloc', 10, 0xBADB50, 0x8000, snap), store,
        own_row('clear', 13, 0xBADB50, 0x8000, snap),
    ])['selects'] == 'no-depth-upload'
    moved = outside_hits([
        dict(k='writer', n=11, **{'class': 'host'}, target=0xBB6020, before=1, after=2, api='native-swap', pc=0),
    ], 10, 20)
    assert moved['00BB6020'] and not moved['00BB67DE']


def ownership_table(root, rdram_detail):
    import re
    report = {}
    for tag in ('wide16', 'wide21'):
        path = root / tag / 'depth' / 'rdram.jsonl'
        events = load_events(path)
        own = [r for r in events if r.get('class') == 'ownership']
        if not own:
            continue
        def fields(row):
            return {k: int(v, 16) for k, v in re.findall(r'(?:^|;)([0-9A-F]{8})=([0-9A-F]{8})(?=;|$)', row['caller'])}
        transitions = []
        prior = None
        for row in own:
            if row['api'] != 'metadata':
                continue
            f = fields(row)
            state = tuple(f.get(k) for k in ('8010FEFC', '801163D8', '801163DC', '801163E4'))
            if state != prior:
                transitions.append(dict(n=row['n'], pc=row['pc'], state=state, snapshot=row))
                prior = state
        readins = [r for r in own if r['api'].startswith('depth-read')]
        bs = [r for r in events if r.get('k') == 'b']
        first_b = bs[0] if bs else None
        prev_a = [r for r in events if r.get('k') == 'a' and first_b and r['n'] < first_b['n']]
        lo = rdram_detail.get('a_n', prev_a[-1]['n'] if prev_a else 0) if tag == 'wide21' else 0
        hi = rdram_detail.get('b_n', first_b['n'] if first_b else float('inf')) if tag == 'wide21' else float('inf')
        allocs = [r for r in own if r['api'] == 'malloc' and
                  r['phys'] < 0xBB67E0 and r['phys'] + r['len'] > 0xBB0020]
        changes = [r for r in events if r.get('class') in ('guest-exact', 'host') and
                   r.get('target') in (0xBB0020, 0xBB6020, 0xBB5FDE, 0xBB67DE) and
                   r.get('before') != r.get('after') and lo < r['n'] < hi]
        owners = []
        for alloc in allocs:
            last = readins[0]['n'] if readins else max(r['n'] for r in events)
            releases = [r for r in own if alloc['n'] < r['n'] <= last and
                        ((r['api'] in ('free-entry', 'free') and r['phys'] == alloc['phys']) or
                         (r['api'] == 'metadata' and r['phys'] == 0x10FEFC and
                          fields(r).get('8010FEFC') == 0))]
            owners.append(dict(allocation=alloc, releases=releases[:2]))
        commands = []
        for read in readins:
            candidates = [r for r in own if r['api'] == 'setzimg' and r['n'] < read['n'] and r['phys'] == read['phys']]
            commands.append(dict(read=read, command=candidates[-1] if candidates else None))
        verdict = decide_ownership(events)
        verdict['outside_window'] = outside_hits(events, lo if lo else -1, hi if hi != float('inf') else 10**12)
        log = root / tag / 'run.log'
        if log.exists():
            kept = [line for line in log.read_text(errors='replace').splitlines()
                    if line.startswith(('[fballoc]', '[g1d-carve]', '[g1d-drop]'))]
            verdict['reservation'] = kept[-24:]
        report[tag] = dict(transitions=transitions, owners=owners, readins=commands,
                           changed_words=changes, phase_window=[lo, hi if hi != float('inf') else None],
                           verdict=verdict)
    (root / 'ownership_table.json').write_text(json.dumps(report, indent=2) + '\n')
    (root / 'ownership_verdict.json').write_text(json.dumps(
        {tag: report[tag]['verdict'] for tag in report if 'verdict' in report[tag]}, indent=2) + '\n')


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--analyze', action='store_true')
    ap.add_argument('--output-root', type=Path, default=Path('scratch/agent/s6626_guest'))
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
    upload_verdict, upload_why, detail = decide_upload(arms['wide16'], arms['wide21'])
    ram_verdict, ram_why, ram = decide_ram(arms['wide16'], arms['wide21'])
    verdict, why, rdram = finish_rdram(
        upload_verdict, ram_verdict, ram, arms['wide21'].get('rdram'), arms['wide21'].get('copies'))
    writer_verdict, writer_why, writers = classify_writers(arms['wide21'].get('rdram'), verdict, rdram)
    result = dict(
        selects=verdict, why=why, rdram=rdram, writer_selects=writer_verdict, writer_why=writer_why, writers=writers, ram_selects=ram_verdict, ram_why=ram_why,
        ram=ram, upload_selects=upload_verdict,
        upload_why=upload_why, upload=detail,
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
    ownership_table(root, rdram)
    print(json.dumps(dict(selects=verdict, why=why, rdram=rdram, writer_selects=writer_verdict, writer_why=writer_why, writers=writers, ram_selects=ram_verdict, ram=ram, upload_selects=upload_verdict,
                          upload=detail,
                          wide21=result['arms']['wide21']['table'].get('stripe_writer'),
                          smooth=arms['wide21']['table']['smooth'],
                          pitch=arms['wide21']['table']['pitch'])), flush=True)


if __name__ == '__main__':
    main()
