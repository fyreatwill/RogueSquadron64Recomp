// s7365 class AP two-arm control: s7096_fwd_cover.cpp fwd() held `Rng& r = pend[i]` across pend.push_back(tail) and then read
// r.hi (heap-use-after-free when push_back reallocates). Arm "pre" = the old order (must trip ASan), "post" = the landed order
// (decide/erase on r before the push; must run clean). Usage: ap_ctl fwd pre|post
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
struct Rng { uint32_t lo, hi, off; };
static int c_fwd(bool post) {
    std::vector<Rng> pend; pend.reserve(2);
    pend.push_back({0, 100, 0}); pend.push_back({200, 300, 0});        // size == capacity: the next push reallocates
    uint32_t p = 210, hi = 220;
    for (size_t i = 0; i < pend.size(); i++) {
        Rng& r = pend[i];
        if (p < r.lo || p >= r.hi) continue;
        const uint32_t n = (hi - p < r.hi - p) ? hi - p : r.hi - p;
        Rng tail{p + n, r.hi, r.off + (p + n - r.lo)}; r.hi = p;
        if (!post) {
            if (tail.hi > tail.lo) pend.push_back(tail);
            if (r.hi <= r.lo) pend.erase(pend.begin() + i);             // r dangles here
        } else {
            const bool rdead = r.hi <= r.lo;
            if (rdead) pend.erase(pend.begin() + i);
            if (tail.hi > tail.lo) pend.push_back(tail);
        }
        break;
    }
    printf("fwd size=%zu [%u,%u) [%u,%u) [%u,%u)\n", pend.size(), pend[0].lo, pend[0].hi, pend[1].lo, pend[1].hi, pend[2].lo, pend[2].hi);
    return 0;
}
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    const bool post = !strcmp(argv[2], "post");
    if (!strcmp(argv[1], "fwd")) return c_fwd(post);
    return 2;
}
