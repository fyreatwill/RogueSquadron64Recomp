"""s6524: EMPTY fraction (npass==0) of [ret-sum] rows with key>=745, per arm run.log. Usage: s6524_empty_by_arm.py <run.log>..."""
import sys, re
for p in sys.argv[1:]:
    n = e = 0
    for l in open(p, errors="replace"):
        m = re.match(r"\[ret-sum\] key=(\d+) .*npass=(\d+)", l)
        if m and int(m.group(1)) >= 745:
            n += 1; e += int(m.group(2)) == 0
    print(f"{p}: EMPTY {e}/{n} = {100*e/max(n,1):.1f}%")
