// s7359 class AJ standalone control for src/main/rs64_apf.h.
//   (1) equivalence: for in-range values the old `o += snprintf(b + o, sizeof b - o, ...)` idiom and rs64_apf produce the same
//       bytes (the [s7030]/[s7046]/[s7233] row shapes at the measured dd8 magnitudes);
//   (2) positive control: with values whose %.1f text no longer fits (20 x 1e30 into char[400], the s7030 hist row) the OLD
//       idiom passes the end -> ASan stack-buffer-overflow when built with -DOLD_OVERFLOW; rs64_apf truncates, offset == cap-1.
// build/run: clang++ -std=c++17 -fsanitize=address -g -I src/main tools/s7359_apf_ctl.cpp -o /tmp/s7359_ctl && /tmp/s7359_ctl
//            clang++ ... -DOLD_OVERFLOW ... && /tmp/s7359_ctl_old   (must abort with "stack-buffer-overflow")
#include "rs64_apf.h"
#include <cstring>
static int fail = 0;
template <class F> static void row(const char* name, size_t, F f) { f(); (void)name; }
int main() {
    const double mid[20] = {186.6, 448.8, 695.9, 913.7, 1068.1, 1035.9, 1005.9, 982.9, 956.4, 900.4, 790.6, 677.4, 472.0, 51.5, 10.0, 0.4, 0, 0, 0, 0.3};
    { char a[400], b[400]; int oa = 0, ob = 0;
      for (int i = 0; i < 20; i++) oa += snprintf(a + oa, sizeof a - oa, "%s%.1f", i ? "," : "", mid[i]);
      for (int i = 0; i < 20; i++) ob = rs64_apf(b, sizeof b, ob, "%s%.1f", i ? "," : "", mid[i]);
      const bool ok = oa == ob && !strcmp(a, b); fail |= !ok; printf("equiv s7030-row  len %d/%d %s\n", oa, ob, ok ? "PASS" : "FAIL"); }
    { char a[300], b[300]; int oa = 0, ob = 0;   // 32 x %.2f fractions (s7046 eyeedge), measured max 159 B
      for (int i = 0; i < 32; i++) oa += snprintf(a + oa, sizeof a - oa, "%s%.2f", i ? "," : "", i == 8 ? 0.99 : 0.0);
      for (int i = 0; i < 32; i++) ob = rs64_apf(b, sizeof b, ob, "%s%.2f", i ? "," : "", i == 8 ? 0.99 : 0.0);
      const bool ok = oa == ob && !strcmp(a, b) && oa == 159; fail |= !ok; printf("equiv s7046-row  len %d/%d %s\n", oa, ob, ok ? "PASS" : "FAIL"); }
    { char b[400]; int ob = 0;                    // truncation: offset clamps, string stays terminated
      for (int i = 0; i < 20; i++) ob = rs64_apf(b, sizeof b, ob, "%s%.1f", i ? "," : "", 1e30);
      const bool ok = ob == 399 && strlen(b) == 399; fail |= !ok; printf("clamp 20x1e30    off %d strlen %zu %s\n", ob, strlen(b), ok ? "PASS" : "FAIL"); }
    { char b[8]; int ob = rs64_apf(b, sizeof b, 100, "x");  // offset already past the end (caller bug) -> no write past b
      const bool ok = ob == 7 && b[7] == 0; fail |= !ok; printf("clamp off>cap    off %d %s\n", ob, ok ? "PASS" : "FAIL"); }
#ifdef OLD_OVERFLOW
    { char b[400]; int o = 0;                     // the old idiom on the same input: o passes 400, sizeof b - o wraps
      for (int i = 0; i < 20; i++) o += snprintf(b + o, sizeof b - o, "%s%.1f", i ? "," : "", 1e30);
      printf("old idiom survived?! o=%d\n", o); return 3; }
#endif
    printf("%s\n", fail ? "CTL FAIL" : "CTL PASS"); return fail;
}
