#!/usr/bin/env python3
"""s7624 G6c step 3: per-frame stand-in flicker scorer.

ROGUESQ_STANDINS=frame turns stand-ins on in alternate submit calls; ROGUESQ_STANDINS_DUMP=a:b:n dumps every swap in window 1
(toggling) and window 2 (forced off, same run). A stand-in that the game really draws shows as FLICKER: pixel p where frame k
differs from the mean of its neighbours k-1 and k+1 while those two agree. Camera motion between consecutive frames is roughly
linear, so it changes a-vs-c as much as b-vs-mean and is rejected by the |a-c| test; parity flicker is not.

usage: s7624_flicker_score.py LOG FBDIR [--mask out.png] [--control]
  LOG   game stderr with [standins-fb] n=.. win=.. on=.. lines
  FBDIR the ROGUESQ_FB_DUMP_DIR (fb_<n>_w<w>.ppm)
  --control  synthetic positive control: paint a 6x6 +90 square into alternate window-2 frames and require the scorer to find it.
Prints one line per window: frames, triplets, flicker px (sum, per triplet), top/bottom-half split, label alternation.
"""
import re, sys, glob, os, array

T = 40  # luma threshold for "differs"


def read_ppm(path):
    with open(path, 'rb') as f:
        data = f.read()
    parts, i = [], 0
    while len(parts) < 4:
        while data[i:i + 1].isspace():
            i += 1
        if data[i:i + 1] == b'#':
            while data[i:i + 1] != b'\n':
                i += 1
            continue
        j = i
        while not data[j:j + 1].isspace():
            j += 1
        parts.append(data[i:j])
        i = j
    i += 1
    w, h = int(parts[1]), int(parts[2])
    px = data[i:i + w * h * 3]
    luma = array.array('h', ((299 * px[k] + 587 * px[k + 1] + 114 * px[k + 2]) // 1000 for k in range(0, w * h * 3, 3)))
    return w, h, luma


def flicker(fr):
    """fr: list of (w, h, luma) in swap order -> (per-triplet counts, accumulated mask or None)."""
    counts, acc = [], None
    for k in range(1, len(fr) - 1):
        (wa, ha, a), (wb, hb, b), (wc, hc, c) = fr[k - 1], fr[k], fr[k + 1]
        if not (wa == wb == wc and ha == hb == hc):
            counts.append(0)
            continue
        if acc is None:
            acc = array.array('i', bytes(4 * wb * hb))
        n = 0
        for q in range(wb * hb):
            av, cv = a[q], c[q]
            if abs(av - cv) < T // 2 and abs(2 * b[q] - av - cv) > 2 * T:
                n += 1
                acc[q] += 1
        counts.append(n)
    return counts, acc


def main():
    log, fbdir = sys.argv[1], sys.argv[2]
    mask_out = sys.argv[sys.argv.index('--mask') + 1] if '--mask' in sys.argv else None
    control = '--control' in sys.argv
    files = {int(re.search(r'fb_(\d+)_w', os.path.basename(p)).group(1)): p
             for p in glob.glob(os.path.join(fbdir, 'fb_*_w*.ppm')) if 'tail' not in p}
    wins = {1: [], 2: []}
    for line in open(log, errors='replace'):
        m = re.search(r'\[standins-fb\] n=(\d+) win=(\d+) on=(-?\d+) call=(\d+)', line)
        if m and int(m.group(2)) in wins and int(m.group(1)) in files:
            wins[int(m.group(2))].append((int(m.group(1)), int(m.group(3)), int(m.group(4))))
    out = {}
    for w, rows in wins.items():
        rows.sort()
        fr = [read_ppm(files[n]) for n, _, _ in rows]
        if control and w == 2:
            for k in range(0, len(fr), 2):
                fw, fh, l = fr[k]
                l = array.array('h', l)
                for y in range(20, 26):
                    for x in range(40, 46):
                        l[y * fw + x] = min(255, l[y * fw + x] + 90)
                fr[k] = (fw, fh, l)
        counts, acc = flicker(fr)
        labels = ''.join(str(o) for _, o, _ in rows)
        alt = sum(1 for i in range(1, len(rows)) if rows[i][1] != rows[i - 1][1])
        dcall = sorted({rows[i][2] - rows[i - 1][2] for i in range(1, len(rows))})
        fw, fh = (fr[0][0], fr[0][1]) if fr else (0, 0)
        top = sum(acc[: (fh // 2) * fw]) if acc else 0
        bot = sum(acc[(fh // 2) * fw:]) if acc else 0
        tot = sum(counts)
        print(f"win={w} frames={len(fr)} size={fw}x{fh} triplets={len(counts)} flicker_px={tot} per_triplet={tot / max(1, len(counts)):.1f} "
              f"top_half={top} bottom_half={bot} label_alternations={alt}/{max(0, len(rows) - 1)} call_steps={dcall[:6]} "
              f"labels={labels[:40]}")
        out[w] = (tot, acc, fr)
        if control and w == 2:
            ctl = sum(acc[y * fw + x] for y in range(20, 26) for x in range(40, 46)) if acc else 0
            need = 36 * max(1, len(counts)) // 3
            print(f"control: painted 36 px in alternate frames, found in-square {ctl} (need >= {need}) -> {'PASS' if ctl >= need else 'FAIL'}")
    if mask_out and out.get(1) and out[1][1]:
        acc, fr = out[1][1], out[1][2]
        fw, fh, base = fr[len(fr) // 2]
        thr = max(2, len(fr) // 6)
        rgb = bytearray()
        hot = 0
        for q in range(fw * fh):
            if acc[q] > thr:
                rgb += b'\xff\x00\xff'; hot += 1
            else:
                v = max(0, min(255, base[q])); rgb += bytes((v, v, v))
        with open(mask_out, 'wb') as f:
            f.write(b'P6\n%d %d\n255\n' % (fw, fh) + bytes(rgb))
        print(f"mask: {mask_out} hot_px={hot} (accumulated > {thr} triplets)")


if __name__ == '__main__':
    main()
