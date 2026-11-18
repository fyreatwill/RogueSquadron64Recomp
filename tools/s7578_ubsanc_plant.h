/* s7578: force-included into every C TU of the build_ubsanc arm (tools/build_ubsanc.sh). Positive control for the runtime
 * signed-overflow witness over the generated game C: with ROGUESQ_S7578_PLANT=1, the first constructor to run does one
 * INT_MAX + 1 in a RecompiledFuncs-flag TU, so UBSan must print "s7578_ubsanc_plant.h:... signed integer overflow". */
#include <stdlib.h>
#include <stdio.h>
#include <limits.h>
__attribute__((weak)) int rs64_s7578_plant_done;
static void __attribute__((constructor, used)) rs64_s7578_plant(void) {
    const char* e = getenv("ROGUESQ_S7578_PLANT");
    if (!e || (e[0] < '1' || e[0] > '4') || rs64_s7578_plant_done) return;
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
    volatile int x = INT_MAX; int y = x + (e[0] - '0');
    fprintf(stderr, "[s7578-plant] fired y=%d\n", y);
}
