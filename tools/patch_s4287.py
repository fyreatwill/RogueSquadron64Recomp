#!/usr/bin/env python3
# s4287: wrap-flush restore-from-shadow becomes default-on (ROGUESQ_WRAP_RESTORE=0 disables),
# shadow cap default 0x2000, and the per-range liveSave vector is reused (thread_local).
# Requires s4286 patch applied. Idempotent.
p = 'src/rsp/dpc_bridge.cpp'
s = open(p).read()
if 's4287' in s:
    raise SystemExit('already patched')
a = '''const char *e = std::getenv("ROGUESQ_WRAP_RESTORE"); return e && *e && *e != '0'; }();'''
assert s.count(a) == 1
s = s.replace(a, '''const char *e = std::getenv("ROGUESQ_WRAP_RESTORE"); return !(e && *e == '0'); }(); /* s4287: default on */''')
b = 'std::vector<uint8_t> liveSave;'
assert s.count(b) == 1
s = s.replace(b, 'static thread_local std::vector<uint8_t> liveSave; /* s4287: reuse, no per-range alloc */')
c = ': 0x400u; }(); /* s4286 */'
assert s.count(c) == 1
s = s.replace(c, ': 0x2000u; }(); /* s4286, s4287: default 0x2000 */')
open(p, 'w').write(s)
