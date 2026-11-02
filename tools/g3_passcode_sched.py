# s6786 G3: AP schedule that types a passcode on the PASSCODES letter wheel (centred on A at entry).
# usage: sched.py WORD T0 [STEP] [ENDKEYS]; prints comma-separated <secs>:<key> (port names: left/right/a/down)
import sys
w, t = sys.argv[1], float(sys.argv[2]); step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
end = sys.argv[4] if len(sys.argv) > 4 else ''
cur, ev = 0, []
for ch in w:
    d = ord(ch) - ord('A') - cur
    for _ in range(abs(d)):
        ev.append('%g:%s' % (t, 'right' if d > 0 else 'left')); t += step
    t += 0.3; ev.append('%g:a' % t); t += 1.0; cur = ord(ch) - ord('A')
for k in filter(None, end.split('/')):
    t += 2.0; ev.append('%g:%s' % (t, k))
print(','.join(ev))
