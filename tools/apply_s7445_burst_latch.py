#!/usr/bin/env python3
"""s7445 class DB: latch the three default-on burst diagnostic prints left in the owner-recipe stderr (scratch/s7444/run.tlog).

  [s4234-ENTRY]  fillSampleStreamRange entry rows (apply_s4234_entryprobe.py + s4278 window), 2101 lines / 257 KB,
                 150 KB in ONE second at t=6.5 s. Investigation (s4234-s4280 sample-stream list) closed long ago.
                 Consumer env: ROGUESQ_S4234_ENTRY=1. rs64_s4234_g (the entry ordinal other probes read) still counts.
  [newbtn]       s577 port-0 controller edge probe (fixup_game_funcs_vendored.py), 791 lines / 84 KB.
                 Consumer env: ROGUESQ_NEWBTN_LOG=1.
  [drain-tick/-slots/-cross/-cursor/-path/-base/-hdr] s1976-s1982 drainAudioAndFinalizeSpeechBuffer sample dumps
                 (fixup_game_funcs_vendored.py), ~480 lines / ~75 KB in one second at t=44.8 s. Diagnostic-only state
                 (s1980 prev_pos/have_sample) is only read inside the same block. Consumer env: ROGUESQ_DRAIN_DUMP=1.
ROGUESQ_G1E_TRIM=0 restores all three (old behaviour). No guest store or control flow changes. Idempotent; runs after
the fixup's s4234/s4278/s577/s1976 patches (listed near the end of RS64 apply list)."""
import pathlib
D = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7445 latch"


def latch(env):
    return ('({ static int on_ = -1; if (on_ < 0) { const char *e_ = getenv("%s"), *g_ = getenv("ROGUESQ_G1E_TRIM"); '
            'on_ = (e_ && e_[0] == \'1\') || (g_ && g_[0] == \'0\'); } on_; }) /* %s */' % (env, MARK))


SITES = [
    ("funcs_24.c", "rs64_s4234_g = s4234_n; if (s4234_n <= 30",
     "rs64_s4234_g = s4234_n; if (%s && (s4234_n <= 30" % latch("ROGUESQ_S4234_ENTRY"),
     ") && s4234_n <= 2000)) fprintf(stderr, \"[s4234-ENTRY]", ") && s4234_n <= 2000))) fprintf(stderr, \"[s4234-ENTRY]"),
    ("funcs_19.c", "        if (((cur | prev | nw) & 0x1000u) ||\n            (port == 0u && (s_newbtn_n < 8 || (s_newbtn_n % 400) == 0))) {",
     "        if (%s && (((cur | prev | nw) & 0x1000u) ||\n            (port == 0u && (s_newbtn_n < 8 || (s_newbtn_n %% 400) == 0)))) {" % latch("ROGUESQ_NEWBTN_LOG"),
     None, None),
    ("funcs_30.c", "            if (s1976_drain_iters <= 8 || (s1976_drain_iters % 100000) == 0) {\n                unsigned gate",
     "            if (%s && (s1976_drain_iters <= 8 || (s1976_drain_iters %% 100000) == 0)) {\n                unsigned gate" % latch("ROGUESQ_DRAIN_DUMP"),
     None, None),
]
n = 0
for fn, old, new, old2, new2 in SITES:
    f = D / fn; t = f.read_text()
    if old not in t:
        print(f"{fn}: already latched" if MARK in t and new.split(" /* ")[0][:40] in t else f"{fn}: anchor MISSING")
        continue
    assert t.count(old) == 1, (fn, t.count(old))
    t = t.replace(old, new, 1)
    if old2:
        assert t.count(old2) == 1, (fn, "tail", t.count(old2)); t = t.replace(old2, new2, 1)
    f.write_text(t); n += 1
print("s7445 sites latched:", n)
