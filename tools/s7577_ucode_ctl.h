/* s7577 fold controls, force-included (-include) into every RSP ucode TU by tools/s7577_ucode_ub_census.py.
   Each control's -O2 asm MUST change when its arm's flag defines the UB away; the ucode's own functions must not. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((noinline, used)) int rs64_s7577_ctl_wrapv(int x) { return x + 1 > x; }        /* folds to 1 unless -fwrapv */
__attribute__((noinline, used)) int rs64_s7577_ctl_alias(int *a, float *b) { *a = 1; *b = 2.0f; return *a; } /* folds unless -fno-strict-aliasing */
__attribute__((noinline, used)) int rs64_s7577_ctl_null(int *p) { int v = *p; if (!p) return -1; return v; } /* check deleted unless -fno-delete-null-pointer-checks */
__attribute__((noinline, used)) int rs64_s7577_ctl_u16mul(unsigned short a, unsigned short b) { return (a * b) < 0; } /* int-promoted u16*u16 nsw: folds to 0 unless -fwrapv */
#ifdef __cplusplus
}
#endif
