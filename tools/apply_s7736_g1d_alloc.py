"""s7736: replay step for the s6201 [g1d-alloc] probe (ROGUESQ_LOG_G1D_TASK=1, beginFrameDLChunk in funcs_*.c).
The fixer's inline apply_s6201_alloc call runs before the S5798 store form exists, so on a pristine regen it never
matched and the probe died silently (s7735 live-vs-replay getenv diff). This runs it again from RS64_REPLAY after
apply_s5798_recwatch / apply_s6287_ppcount. Idempotent. Usage: apply_s7736_g1d_alloc.py <RecompiledFuncs dir>"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_s6031_far as a
d = sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
hit = 0
for f in sorted(glob.glob(os.path.join(d, "funcs_*.c"))):
    t = open(f).read()
    if "RECOMP_FUNC void beginFrameDLChunk(" not in t:
        continue
    hit += 1
    if "PATCH: s6201 alloc */ static int en" in t:
        print(os.path.basename(f), "s6201 alloc already present"); continue
    t2, n = a.apply_s6201_alloc(t)
    if not n:
        sys.exit(f"apply_s7736_g1d_alloc: anchors missing in {os.path.basename(f)}")
    open(f, "w").write(t2); print(os.path.basename(f), "s6201 alloc x1")
if hit != 1:
    sys.exit(f"apply_s7736_g1d_alloc: beginFrameDLChunk found in {hit} files, want 1")
