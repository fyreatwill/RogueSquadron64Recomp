#!/bin/zsh
# s7160: after tools/s7141_post.zsh, rescore one level with the refit capture rect (default 0,10,370,217, the L0/L12 fit),
# print summary + 8 row bands + worst-swap neighbours (duplicate pframe = frame-match lag), write the owner sheet (worst, median, p20).
# usage: s7160_fit_post.zsh <dir> <name> [rect] [sheet.png]   e.g. s7160_fit_post.zsh scratch/s7160 L3
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=$1; N=$2; R=${3:-0,10,370,217}; T=$(echo $R | tr , _); O=$D/${N}_f$T; SH=${4:-docs/owner_sheet_${D:t}_${N}_fidelity.png}
python3 tools/s7122_fidelity.py score $D/$N.raw $D/$N.idx $D/${N}r $O --rect $R --split 46,322 > $O.log 2>&1 || { tail -3 $O.log; exit 1; }
echo "rect $R"; python3 tools/s7157_fsum.py $O.frames.csv | tail -2
S=$(python3 - $O <<'PY'
import csv, sys, collections
o = sys.argv[1]; r = list(csv.DictReader(open(o + '.frames.csv'))); v = [float(x['meand']) for x in csv.DictReader(open(o + '.rows.csv'))]
n = len(v); print('bands', ' '.join('%.2f' % (sum(v[i*n//8:(i+1)*n//8]) / len(v[i*n//8:(i+1)*n//8])) for i in range(8)), file=sys.stderr)
c = collections.Counter(x['pframe'] for x in r); print('dup pframes', sum(k - 1 for k in c.values()), file=sys.stderr)
s = sorted(r, key=lambda x: float(x['frac_over_T'])); m = len(s)
for w in s[-3:][::-1]: print('worst swap %s pframe %s frac %s frac_c %s dup %d' % (w['swap'], w['pframe'], w['frac_over_T'], w['frac_c'], c[w['pframe']] - 1), file=sys.stderr)
print(','.join(s[i]['swap'] for i in (m - 1, m // 2, m // 5)))
PY
)
env SHEET_RECT=$R SHEET_LABEL=16:9 python3 tools/s7156_sheet.py $D/$N.raw $D/${N}r $O.frames.csv $SH $S
