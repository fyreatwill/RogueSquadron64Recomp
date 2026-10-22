"""s5899: for each pair of logged [s5898] lives on the same pr, is the object's rotation basis (+0x28..+0x48) and
position (+0x4c..+0x54) at the next life's start equal to the previous life's end? Usage: python3 -I tools/s5899_life_continuity.py run.log"""
import re, sys
L = []
for l in open(sys.argv[1], errors='replace'):
    m = re.match(r'\[s5898\] life pr=(\w+) n=(\d+) maxd=(\S+) dt_ms=(\S+) diff:(.*?)\| start:(.*)', l)
    if not m: continue
    pr, n, md, dt, d, s = m.groups(); s = [int(x, 16) for x in s.split()]; e = s[:]
    for a, b, c in re.findall(r'\+(\w+):(\w+)>(\w+)', d): e[int(a, 16) // 4] = int(c, 16)
    L.append((pr, s, e))
tot = mat = pos = 0
for i in range(len(L)):
    for j in range(i + 1, len(L)):
        if L[j][0] == L[i][0]:
            tot += 1; mat += L[i][2][10:19] == L[j][1][10:19]; pos += L[i][2][19:22] == L[j][1][19:22]; break
print(f"lives={len(L)} same-pr pairs={tot} basis-continuous={mat} pos-continuous={pos}")
