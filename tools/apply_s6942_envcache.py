#!/usr/bin/env python3
"""s6942 G1e: the s857 slot-dispatcher trace (slotDispatcherIter, funcs_8.c) called getenv twice before and twice after every slot call,
about 4 lookups per object per frame: 333 of the game thread's 350 __findenv_locked samples in the s6941 xctrace (scratch/s6941/T.xml,
CALLER=__findenv_locked tools/g1e_xt_leaves.py). Both lookups are cached on first use; trace behaviour is unchanged (env is read once at
first call instead of every call; nothing in the port sets these env vars after start). Idempotent. Usage: apply_s6942_envcache.py [dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6942 envcache"
f = D / "funcs_8.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = ('        const char* e = getenv("ROGUESQ_LOG_SLOT_DISPATCH");\n'
     '        const char* p = getenv("ROGUESQ_SLOT_DISPATCH_PHASE_MIN");\n')
n = t.count(A)
assert n == 2, n
B = ('        static int s6942_i; static const char *s6942_e, *s6942_p; /* ' + TAG + ' */\n'
     '        if (!s6942_i) { s6942_e = getenv("ROGUESQ_LOG_SLOT_DISPATCH"); s6942_p = getenv("ROGUESQ_SLOT_DISPATCH_PHASE_MIN"); s6942_i = 1; }\n'
     '        const char* e = s6942_e;\n'
     '        const char* p = s6942_p;\n')
t = t.replace(A, B)
f.write_text(t, errors="surrogateescape"); print("applied", TAG, n)
