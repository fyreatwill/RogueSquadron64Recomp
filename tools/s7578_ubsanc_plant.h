/* s7578: force-included into every C TU of the build_ubsanc arm (tools/build_ubsanc.sh). Positive control for the runtime
 * signed-overflow witness over the generated game C: with ROGUESQ_S7578_PLANT=1, the first constructor to run does one
 * INT_MAX + 1 in a RecompiledFuncs-flag TU, so UBSan must print "s7578_ubsanc_plant.h:... signed integer overflow". */
#include <stdlib.h>
#include <stdio.h>
#include <limits.h>
#include <stdint.h>
#include <stddef.h>
__attribute__((weak)) int rs64_s7578_plant_done;
__attribute__((weak, noinline, nonnull)) void rs64_s7583_nn(const char* p) { (void)p; }
static void __attribute__((constructor, used)) rs64_s7578_plant(void) {
    const char* e = getenv("ROGUESQ_S7578_PLANT");
    if (!e || (e[0] < '1' || (e[0] > '6' && e[0] != 'u')) || rs64_s7578_plant_done) return;
    rs64_s7578_plant_done = 1;
    if (e[0] == '2') { /* s7579 bounds control: one-past-end index on a fixed array (build_ubsanb, -fsanitize=bounds) */
        static int a[4]; volatile int idx = 4; volatile int r = a[idx & 7]; (void)r; /* read, no store: &7 keeps idx==4 */
        fprintf(stderr, "[s7579-plant] fired idx=%d\n", idx); return; }
    if (e[0] == '3') { /* s7580 shift control: exponent >= width (build_ubsans, -fsanitize=shift) */
        volatile int sh = 40; volatile unsigned r = 1u << sh; (void)r;
        fprintf(stderr, "[s7580-plant3] fired sh=%d\n", sh); return; }
    if (e[0] == '4') { /* s7580 alignment control: misaligned u32 load (build_ubsans, -fsanitize=alignment) */
        static _Alignas(8) unsigned char buf[16]; volatile unsigned char* vp = buf + 1;
        volatile unsigned r = *(const unsigned*)(const void*)vp; (void)r;
        fprintf(stderr, "[s7580-plant4] fired off=1\n"); return; }
    if (e[0] == '5') { /* s7582 pointer-overflow control: char* near the top of the address space plus 16 wraps
                        * (build_ubsanp, -fsanitize=pointer-overflow: "addition of unsigned offset ... overflowed") */
        volatile uintptr_t z = (uintptr_t)0 - 4; char* volatile p = (char*)z; volatile size_t off = 16;
        char* volatile q = p + off; (void)q;
        fprintf(stderr, "[s7582-plant5] fired\n"); return; }
    if (e[0] == '6') { /* s7583 residual-UB controls, all recoverable kinds at once (build_ubsanr): divide by zero,
                        * float->int out of range, invalid bool load, clz(0), nonnull arg = NULL, VLA bound 0 */
        volatile int d = 0; volatile int q = 7 / (d | 0); (void)q;
        volatile float f = 1e20f; volatile int fi = (int)f; (void)fi;
        volatile unsigned char bb = 2; _Bool bv; __builtin_memcpy(&bv, (const void*)&bb, 1); volatile int bi = bv ? 1 : 0; (void)bi;
        volatile unsigned z0 = 0; volatile int c = __builtin_clz(z0); (void)c;
        const char* volatile np = 0; rs64_s7583_nn(np);
        volatile int vn = 0; { int vla[vn]; (void)vla; }
        fprintf(stderr, "[s7583-plant6] fired\n"); return; }
    if (e[0] == 'u') { /* s7583 unreachable control (NOT recoverable: aborts at the constructor) */
        volatile int k = 1; if (k) __builtin_unreachable(); return; }
    volatile int x = INT_MAX; int y = x + (e[0] - '0');
    fprintf(stderr, "[s7578-plant] fired y=%d\n", y);
}
