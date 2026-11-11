#!/usr/bin/env python3
"""s7141: summarise s7122_fidelity frames.csv with --split columns (central 4:3 band vs side bands). usage: s7141_summ.py csv [csv..]"""
import sys, csv, statistics as S
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
for f in sys.argv[1:]:
    r = [x for x in csv.DictReader(open(f)) if int(x['pframe']) > 0]
    print(f, 'frames', len(r))
    for k in ('meand', 'frac_over_T', 'meand_c', 'frac_c', 'meand_s', 'frac_s'):
        v = [float(x[k]) for x in r]
        print('  %-12s med %.4f p90 %.4f max %.4f' % (k, S.median(v), q(v, .9), max(v)))
    print('  frames frac>0.02', sum(float(x['frac_over_T']) > .02 for x in r), '>0.05', sum(float(x['frac_over_T']) > .05 for x in r),
          ' side>0.05', sum(float(x['frac_s']) > .05 for x in r), ' centre>0.05', sum(float(x['frac_c']) > .05 for x in r))
    top = sorted(r, key=lambda x: -float(x['frac_over_T']))[:6]
    print('  top', [(x['swap'], x['frac_over_T'], x['frac_c'], x['frac_s'], x['biggest']) for x in top])
