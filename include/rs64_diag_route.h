#ifndef RS64_DIAG_ROUTE_H
#define RS64_DIAG_ROUTE_H
// s7447 class DD: force-included (CMakeLists RS64_DIAG_ROUTE_SRC) into the hand-written src/main + src/rsp C++ sources so
// their ~1450 direct fprintf / std::fprintf sites go through rs64_diag_fprintf (src/main/main.cpp) like the generated C
// does since s7432 (include/rsp_dpc_macros.h). Default (ROGUESQ_DIAG_QUIET unset) is byte-identical output: the router
// just vfprintf's. ROGUESQ_DIAG_QUIET=1 now drops these too (crash/abort/fatal/SIG/ERROR/assert formats always pass).
// Function-like macro: `using ::fprintf;` in <cstdio> is untouched; std::fprintf(...) resolves via the using below.
// Opt out per build: -DRS64_DIAG_ROUTE=OFF at configure time.
#include <cstdio>
extern "C" int rs64_diag_fprintf(FILE* f, const char* fmt, ...);
namespace std { using ::rs64_diag_fprintf; }
#define fprintf(...) rs64_diag_fprintf(__VA_ARGS__)
#endif
