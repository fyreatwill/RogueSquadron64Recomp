/* s7253: direct host clock probe for timing arms. s7249-s7252 inferred CPU throttling from the power source (pmset), but
   battery is necessary, not sufficient (s7252: 11-09 battery runs were 1.00-1.05x AC, 11-12 afternoon 1.36-1.44x).
   This measures it: a fixed dependent integer chain (xorshift + mul, no memory traffic) on a USER_INTERACTIVE thread
   (P-core), REPS repetitions, prints the MIN ms (min rejects preemption by other load; a clock cap raises every rep).
   usage: s7253_clkprobe [iters_millions=60] [reps=7]   -> "clk_ms=<min> med=<median> reps=<n> iters=<M>M"
   Ratio vs the AC baseline (tools/s7253_clkprobe.base) is the throttle factor; the harness logs it as clk=. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <mach/mach_time.h>
static int cmpd(const void *a, const void *b){ double x = *(const double *)a, y = *(const double *)b; return x < y ? -1 : x > y; }
int main(int argc, char **argv){
  long M = argc > 1 ? atol(argv[1]) : 60; int R = argc > 2 ? atoi(argv[2]) : 7; if (R < 1) R = 1; if (R > 64) R = 64;
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  mach_timebase_info_data_t tb; mach_timebase_info(&tb);
  double ms[64]; volatile uint64_t sink = 0;
  for (int r = 0; r < R; r++) {
    uint64_t x = 0x9E3779B97F4A7C15ull + (uint64_t)r, t0 = mach_absolute_time();
    for (long i = 0; i < M * 1000000L; i++) { x ^= x << 13; x ^= x >> 7; x ^= x << 17; x *= 0x2545F4914F6CDD1Dull; }
    uint64_t t1 = mach_absolute_time(); sink += x;
    ms[r] = (double)(t1 - t0) * tb.numer / tb.denom / 1e6;
  }
  qsort(ms, R, sizeof ms[0], cmpd);
  printf("clk_ms=%.2f med=%.2f reps=%d iters=%ldM\n", ms[0], ms[R / 2], R, M);
  return sink == 1; /* keep the chain live */
}
