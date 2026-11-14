#include <cmath>
#include <cstdio>
#include <limits>
static int oldb(float dd) { int b = (int)(dd / 8.0f); if (b > 16) b = 16; return b; }
static int newb(float dd) { return dd < 128.0f ? (int)(dd / 8.0f) : 16; }
int main(int argc, char**) {
    volatile float nan = std::numeric_limits<float>::quiet_NaN(), inf = INFINITY, big = 3e10f;
    float cs[] = {0.f, 7.9f, 8.f, 127.9f, 128.f, 135.f, 1000.f, big, inf, nan};
    int bad = 0;
    for (float d : cs) { int n = newb(d); if (n < 0 || n > 16) bad++; printf("dd=%g old=%d new=%d\n", d, oldb(d), n); }
    for (float d = 0.f; d < 200.f; d += 0.37f) if (oldb(d) != newb(d)) { bad++; printf("finite mismatch %g\n", d); }
    printf("bad=%d\n", bad); return bad;
}
