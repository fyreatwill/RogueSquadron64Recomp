"""s7422 (usage: s7422_idem_class_test.py [control rev] [pristine dir]): class CE test for every apply script called twice in a regen
(inline fixer + RS64_REPLAY). Apply once to the pristine N64Recomp file, then interpose a 450 KB foreign block in front of each of the
script's own tagged lines (a later script inserting at the same anchor), then apply again. Fixed (working-tree) copies must add 0;
the control copies from REV (windowed checks) must add >0, which proves the interposer reaches past every old window."""
import importlib.util, os, re, subprocess, sys
REV = sys.argv[1] if len(sys.argv) > 1 else 'd1c50d659'
PRISTINE = sys.argv[2] if len(sys.argv) > 2 else '/tmp/s7420/front'
OLD = '/tmp/s7422_idem_old'; os.makedirs(OLD, exist_ok=True)
FOREIGN = "    { /* PATCH: s7422 interposed */ " + "(void)0; " * 50000 + "}\n"
CASES = [('apply_s5811_ctr1_bt', ['funcs_15.c'], ['PATCH: s5811 ctr1 bt']),
         ('apply_s5812_npc_spawn_class', ['funcs_36.c'], ['PATCH: s5812 spawn class']),
         ('apply_s5813_npc_fate', ['funcs_36.c', 'funcs_8.c'], ['PATCH: s5813 track', 'PATCH: s5813 msg', 'PATCH: s5813 free']),
         ('apply_s5829_teardown_gate', ['funcs_36.c'], ['PATCH: s5829 teardown gate']),
         ('apply_s5887_spawn_nonclass1', ['funcs_36.c'], ['PATCH: s5887 spawn nonclass1 dump']),
         ('apply_s5893_msg5ids', ['funcs_36.c'], ['PATCH: s5893 msg5 per-id']),
         ('apply_s5953_objsnap', ['funcs_35.c'], ['PATCH: s5953 objsnap']),
         ('apply_s5960_objsnap_tick', ['funcs_42.c'], ['PATCH: s5960b objsnap tick'])]
SAFE_BY_ANCHOR = {'apply_s5829_teardown_gate'}
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def interpose(t, tags):
    for tag in tags:
        out, pos = [], 0
        for mt in re.finditer(re.escape(tag), t):
            ls = t.rfind('\n', 0, mt.start()) + 1
            if ls < pos: continue
            out.append(t[pos:ls]); out.append(FOREIGN); pos = ls
        out.append(t[pos:]); t = ''.join(out)
    return t
ok = True
for name, files, tags in CASES:
    open('%s/%s.py' % (OLD, name), 'w').write(subprocess.check_output(['git', 'show', '%s:tools/%s.py' % (REV, name)], text=True))
    for tag, d in (('new', 'tools'), ('old', OLD)):
        m = load('%s/%s.py' % (d, name), name + tag); n1 = n3 = 0
        try:
            for f in files:
                t = open(os.path.join(PRISTINE, f)).read()
                t1, a = m.apply(t); n1 += a
                _, b = m.apply(interpose(t1, tags)); n3 += b
            # s5829 anchors on ANC + the next comment line, which its own insert breaks: the old copy is safe by anchor shape
            exp = (n3 == 0) if tag == 'new' or name in SAFE_BY_ANCHOR else (n3 > 0); res = 'PASS' if exp and n1 > 0 else 'FAIL'
        except AssertionError as e:
            res = 'ERR(assert)'
        ok &= res == 'PASS'
        print('%-30s %s first=%d reapply=%d %s' % (name, tag, n1, n3, res))
print('IDEMPOTENCE-CE', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
