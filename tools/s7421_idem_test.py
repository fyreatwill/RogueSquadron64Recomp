"""s7421 (usage: s7421_idem_test.py [control rev] [pristine dir]): re-apply each windowed-idempotence apply script after a foreign block is interposed at its anchor.
Fixed scripts must add 0 the second time; the HEAD (old) copies must add >0 (control: the bug is real)."""
import importlib.util, os, subprocess, sys
REV = sys.argv[1] if len(sys.argv) > 1 else '20ff19bbc'   # last commit with the windowed checks (control arm)
PRISTINE = sys.argv[2] if len(sys.argv) > 2 else '/tmp/s7420/front'   # pristine N64Recomp output (tools/regen_front.sh)
OLD = '/tmp/s7421_idem_old'; os.makedirs(OLD, exist_ok=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
ok = True
for name, f in [('apply_s5787_objcount_log', 'funcs_35.c'), ('apply_s5790_inline_writer_log', 'funcs_15.c'),
                ('apply_s5791_objwr_bt', 'funcs_15.c'), ('apply_s5809_ctr1_log', 'funcs_15.c')]:
    open('%s/%s.py' % (OLD, name), 'w').write(subprocess.check_output(['git', 'show', '%s:tools/%s.py' % (REV, name)], text=True))
    for tag, d in (('new', 'tools'), ('old', OLD)):
        m = load('%s/%s.py' % (d, name), name + tag)
        args = (m.FILES[f],) if hasattr(m, 'FILES') else ()
        t = open(os.path.join(PRISTINE, f)).read()
        if name == 'apply_s5791_objwr_bt':  # anchors on the s5790 block
            p5790 = load('tools/apply_s5790_inline_writer_log.py', 'p5790' + tag); t, _ = p5790.apply(t, p5790.FILES[f])
        t1, n1 = m.apply(t, *args)
        anc = getattr(m, 'ANCH', "    int c1cs = 0;\n")
        t2 = t1.replace(anc, anc + "    { /* PATCH: s7421 interposed */ " + "(void)0; " * 400 + "}\n")
        _, n3 = m.apply(t2, *args)
        exp = (n3 == 0) if tag == 'new' else (n3 > 0)
        ok &= exp and n1 > 0
        print('%-32s %s first=%d reapply=%d %s' % (name, tag, n1, n3, 'PASS' if exp and n1 > 0 else 'FAIL'))
print('IDEMPOTENCE', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
