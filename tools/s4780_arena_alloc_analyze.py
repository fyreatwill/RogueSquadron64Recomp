import re, sys
LO, HI = 0x80179400, 0x8017B000
first = None
ev = []
for n, l in enumerate(open(sys.argv[1], errors='replace'), 1):
    if first is None and l.startswith('[s4779-unhooked]'):
        first = n
    m = re.match(r'\[rs-malloc\] ptr=0x([0-9A-F]+) size=(\d+) flags=(0x[0-9A-F]+)', l)
    if m:
        p, s = int(m[1], 16), int(m[2])
        ev.append((n, 'M', p, s))
        continue
    m = re.match(r'\[rs-free\] ptr=0x([0-9A-F]+)', l)
    if m:
        ev.append((n, 'F', int(m[1], 16), 0))
    m = re.match(r'\[phase\]|.*phase=', l)
print('first unhooked line', first)
print('total malloc', sum(e[1] == 'M' for e in ev), 'free', sum(e[1] == 'F' for e in ev))
for n, k, p, s in ev:
    if k == 'M' and p < HI and p + s > LO:
        print(('BEFORE' if n < first else 'AFTER '), n, 'M', hex(p), s, 'end', hex(p + s))
    if k == 'F' and LO - 0x20000 <= p < HI:
        print(('BEFORE' if n < first else 'AFTER '), n, 'F', hex(p))
