s6301 SIMD-vs-SISD differential fuzz of rsp_vu_impl.hpp (31 elementwise VU ops x 16 element modes, 200k random+edge-biased inputs each).
run.sh builds simd/ and sisd/ variants (Accuracy flags flipped in the copy of rsp_vu.hpp) and diffs per-op state hashes.
Result: 496/496 identical. Positive control: mutating VCL's SISD line 684 makes VCL differ (see PORTING-STATE s6301).
Scope: proves the two independent implementations in ares agree; it is NOT hardware ground truth.
