#!/usr/bin/env python3
"""s7528 gap FQ: score overlay-swap func_map eviction from [s7528] census lines.

usage: s7528_evict_score.py DIR tag...      (reads DIR/log_<tag>.txt)
       s7528_evict_score.py --controls OLDLOG NEWLOG
PASS per log: >=1 overlay swap seen (an [s7528] pre line with evicted_secs>=1), every post line has
stale_window_entries=0, every planted ctl probe misses (ctl_hit=0), loaded_sections never grows past the
first overlay load's count, last [s7520-sum] gf_stale=0, no 'Failed to find function'. Exit 0 pass, 1 fail.
--controls: OLDLOG (ROGUESQ_S7528_EVICT=0) must FAIL with stale>0 and ctl_hit=1; NEWLOG must PASS.
"""
import re, sys

def score(path):
    pre = post = swaps = 0; stale = []; hits = 0; probes = 0; loaded = []; gf_stale = None; failed = 0
    for ln in open(path, errors='replace'):
        if ln.startswith('[s7528] pre '):
            pre += 1
            m = re.search(r'evicted_secs=(\d+)', ln)
            if m and int(m.group(1)) >= 1: swaps += 1
        elif ln.startswith('[s7528] post '):
            post += 1
            stale.append(int(re.search(r'stale_window_entries=(\d+)', ln).group(1)))
            loaded.append(int(re.search(r'loaded_sections=(\d+)', ln).group(1)))
            m = re.search(r'ctl_hit=(\d)', ln)
            if m: probes += 1; hits += int(m.group(1))
        elif '[s7520-sum]' in ln:
            m = re.search(r'gf_stale=(\d+)', ln)
            if m: gf_stale = int(m.group(1))
        elif 'Failed to find function' in ln:
            failed += 1
    base = loaded[2] if len(loaded) > 2 else (max(loaded) if loaded else 0)  # boot (2 main) + first overlay
    grow = max(loaded) - base if loaded else 0
    ok = post > 0 and swaps >= 1 and max(stale or [0]) == 0 and hits == 0 and grow == 0 and gf_stale == 0 and failed == 0
    return ok, dict(loads=post, swaps=swaps, stale_max=max(stale or [0]), probes=probes, ctl_hits=hits,
                    loaded_max=max(loaded or [0]), grow=grow, gf_stale=gf_stale, failed=failed)

def main(a):
    if a and a[0] == '--controls':
        ok_old, d_old = score(a[1]); ok_new, d_new = score(a[2])
        c1 = (not ok_old) and d_old['stale_max'] > 0 and d_old['ctl_hits'] > 0
        c2 = ok_new and d_new['probes'] > 0
        print(f"ctl old_must_fail={'PASS' if c1 else 'FAIL'} {d_old}")
        print(f"ctl new_must_pass={'PASS' if c2 else 'FAIL'} {d_new}")
        return 0 if c1 and c2 else 1
    d, tags = a[0], a[1:]; rc = 0
    for t in tags:
        try: ok, info = score(f"{d}/log_{t}.txt")
        except FileNotFoundError: ok, info = False, 'missing log'
        print(f"s7528 {t} {'PASS' if ok else 'FAIL'} {info}")
        rc |= 0 if ok else 1
    print(f"s7528 score={rc}")
    return rc

sys.exit(main(sys.argv[1:]))
