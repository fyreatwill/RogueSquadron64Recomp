#!/usr/bin/env python3
"""s7354 class AE: summarise ThreadSanitizer reports from a build_tsan run (tools/build_tsan.sh).
usage: s7354_tsan_report.py <run.log or tsan log files...> [--frames N]
Groups reports by (kind, sorted pair of first in-repo frames), prints count, location (global name / heap), threads and
the first N repo frames of each access. The planted control (ROGUESQ_S7354_RACE_CTL=1, s7354_race_ctl_var in main.cpp)
must appear as a row or the run's null is void (iron rule 1).
Classes in HAND (key substring -> class, reason):
  B      default-on race on a host global / member (defect)      D/G  diag-only / env-gated path
  BENIGN race on a value whose torn/stale read cannot change behaviour (monotonic counter read for logging, etc.)
  EXT    race inside a system / third-party library frame we do not own (SDL, Metal, libdispatch)
  CTL    the planted control
exit 1 if any group is unclassified or B."""
import re, sys, collections
HAND = [  # (substring of group key, class, reason) -- filled from the s7354 run review
    ("s7354_race_ctl", "CTL", "planted control"),
    # SEM = guest-thread handoff through moodycamel::LightweightSemaphore (mach semaphore_t), which TSan does not model:
    # tools/s7354_sem_ctl.cpp `sem` arm reports a race on a correctly synchronised handoff (1 report), `mutex` arm 0.
    ("osRecvMesg mesgqueue.cpp", "SEM", "guest mq in RDRAM, both sides guest threads serialised by the ultramodern run-one scheduler"),
    ("osRecvMesg_recomp", "SEM", "guest mq in RDRAM, both sides guest threads (run-one scheduler)"),
    ("osSendMesg_recomp", "SEM", "guest mq in RDRAM, both sides guest threads (run-one scheduler)"),
    ("osCreateThread threads.cpp", "SEM", "creator fills OSThread, new guest thread reads it after the start semaphore"),
    ("stack of thread T13", "SEM", "gfx thread signals the init semaphore on T13's stack; T13 waits on it before reusing the frame"),
    ("thread.h:213", "SEM", "same: std::thread ctor reuses the stack slot of the waited-on init semaphore"),
    ("g_recomp_rdram_for_wp_raw", "BENIGN", "one 8-byte aligned publish of the rdram base before any guest code; diag poll threads read it"),
    ("rt64_present_queue.cpp:1075", "BENIGN", "swapChainRate: aligned u32 pacing hint, changed only on window move/resize (present thread under its mutex), gfx thread reads stale-or-new"),
    ("plume_metal.cpp", "EXT", "Metal completion-handler block: copied on the present thread, run on Metal's internal queue (uninstrumented system HB)"),
    ("data race on vptr", "EXT", "same Metal completion-handler block (vptr of the captured object)"),
    ("'events_context'", "FIX", "s7354: VI cur/next flip in vi_thread_func now under message_mutex (+ dummy VI, osViGet*Framebuffer)"),
    ("'sample_rate'", "FIX", "s7354: audio.cpp sample_rate -> std::atomic<uint32_t>"),
    ("osViSwapBuffer_recomp upstream_compat.cpp:1298", "D", "ROGUESQ_FB_HASH (m6 harness default) hashes the guest framebuffer while RT64 fullSync copies native->RAM"),
]
ARGS = [a for i, a in enumerate(sys.argv[1:]) if not a.startswith("--") and sys.argv[i] != "--frames"]
NF = 3
if "--frames" in sys.argv: NF = int(sys.argv[sys.argv.index("--frames") + 1])
FR = re.compile(r"^\s+#\d+\s+(\S+)\s+(\S+?)(?::(\d+))?(?::\d+)?\s*(?:\(|$)")
def frames(lines):
    out = []
    for l in lines:
        m = FR.match(l)
        if not m: break
        fn, loc = m.group(1), m.group(2)
        if "tsan" in loc or "sanitizer_common" in loc: continue
        out.append(f"{fn} {loc.split('/')[-1]}{':' + m.group(3) if m.group(3) else ''}")
    return out
groups = collections.OrderedDict(); total = 0
for f in ARGS:
    text = open(f, errors="replace").read().splitlines()
    i = 0
    while i < len(text):
        if "WARNING: ThreadSanitizer:" not in text[i]: i += 1; continue
        kind = text[i].split("ThreadSanitizer:")[1].split("(pid")[0].strip()
        j = i + 1; acc = []; loc = ""; thr = []
        while j < len(text) and not text[j].startswith("SUMMARY: ThreadSanitizer"):
            l = text[j]
            m = re.match(r"\s+(?:Previous |Atomic )*(?:[Ww]rite|[Rr]ead)\s+of size (\d+).*?by (thread T\d+|main thread)", l)
            if m: acc.append((l.strip().split(" at ")[0], m.group(2), frames(text[j + 1:j + 40])))
            if "Location is" in l: loc = l.strip()
            if l.strip().startswith("Thread T") and "created by" in l: thr.append(l.strip()[:120])
            j += 1
        top = tuple(sorted({(a[2][0] if a[2] else "?") for a in acc}))
        key = (kind, top)
        g = groups.setdefault(key, {"n": 0, "acc": acc, "loc": loc, "thr": thr})
        g["n"] += 1; total += 1
        i = j + 1
bad = 0
print(f"reports {total}, groups {len(groups)}")
for (kind, top), g in groups.items():
    keytxt = kind + " " + " | ".join(top) + " " + g["loc"]
    cls = next(((c, r) for s, c, r in HAND if s in keytxt), ("?", ""))
    if cls[0] in ("?", "B"): bad += 1
    print(f"\n[{cls[0]}] x{g['n']} {kind}  {g['loc'][:160]}  {cls[1]}")
    for a in g["acc"]:
        print(f"   {a[0][:60]} by {a[1]}: " + "  <-  ".join(a[2][:NF]))
    for t in g["thr"][:2]: print("   " + t)
sys.exit(1 if bad else 0)
