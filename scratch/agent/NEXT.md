# NEXT (s7356): idiom-class audit - class AG, unchecked host allocation / mapping / file-open results
HYPOTHESIS-ID: host-unchecked-resource-result
Context: s7355 closed class AF (crash reporter async-signal safety; strsignal removed, per-thread sigaltstack, ctx-scan clamp;
arms in scratch/s7355/arms.zsh, census tools/s7355_sighandler_census.py, ground truth tools/s7355_sighandler_ctl.cpp).
A crash now ALWAYS reports: re-run scratch/s7355/arms.zsh after any change to the sigaction lambda in main.cpp.
Idiom (class AG): in host C++ we own (src/, lib/N64ModernRuntime/{librecomp,ultramodern}/src, lib/rt64/src/{hle,rhi}/ our patched
files only), a result of malloc/calloc/realloc/new(nothrow)/mmap/fopen/popen/SDL_Create*/dup used without a null / MAP_FAILED /
<0 check. Hazard: a resource failure (low memory at dd8 px8, fd exhaustion from log files, a missing file) becomes a wild
deref far from its cause instead of a named error.
Hypotheses: H-safe (every site checks or the use is itself guarded), H-diag (unchecked sites only in env-gated diagnostics),
H-unchecked (a default-on path derefs an unchecked result: fix with a named fail-fast message).
Method: tools/s7356_unchecked_census.py: enumerate call sites of the allocator/open set; for each, find the assigned variable and
look for a check (if (!x) / x == nullptr / x == MAP_FAILED / x < 0 / x != nullptr) before the first deref within the function;
classify CHECKED / D (dead or _WIN32) / G (env-gated) / B (default-on unchecked) / ?. Controls: planted unchecked malloc (B),
checked twin (CHECKED), gated twin (G).
Second line: for each B, a runtime arm that forces the failure (e.g. DYLD interpose or an env knob that makes the alloc fail) and
shows the pre-fix crash vs the post-fix named error. Then 260 s dd8 smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7356_dd8 ''`.
Exit: PORTING-STATE s7356, CURRENT-TRUTH item 27u -> closed/fixed, commit.
