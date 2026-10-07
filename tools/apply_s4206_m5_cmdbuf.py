"""M5 Step 9d: extend the s4205 record census with volume-field and referenced-buffer hashes.

Diagnostic only (ROGUESQ_LOG_M5_CMDLIST / ROGUESQ_LOG_ALL). After render returns, per phase:
records with a nonzero halfword at +0x58/+0x5A (candidate volume, 0x4000 in dumped records),
and for the pointers at rec+0x2C, +0x40, +0x78, +0x7C the count of records whose first 0x100
bytes are nonzero. Positive control: ptr_ok counts valid pointers and the s4205 rec_nz/ctl_nz
columns stay nonzero in the same run.
"""
from pathlib import Path

OLD = "    if (n <= 3 || (n % 512ul) == 0) {\n        fprintf(stderr, \"[m5-cmdlist]"
NEW = r'''    { /* PATCH: s4206 cmdbuf */
        static unsigned long vol58_nz, bufptr_ok[4], buf_nz[4], pn;
        static uint32_t pk = 0xFFFFFFFFu;
        if (pk != phase) { pk = phase; vol58_nz = pn = 0; for (i = 0; i < 4; ++i) bufptr_ok[i] = buf_nz[i] = 0; }
        if (rec >= 0x80000000u && rec < 0x807FFF78u) {
            gpr r = (gpr)(int32_t)rec;
            static const unsigned offs[4] = {0x2C, 0x40, 0x78, 0x7C};
            ++pn;
            if (MEM_HU(0x58, r) || MEM_HU(0x5A, r)) ++vol58_nz;
            for (unsigned k = 0; k < 4; ++k) {
                uint32_t p = (uint32_t)MEM_W(offs[k], r);
                if (p >= 0x80000000u && p < 0x807FFF00u) {
                    ++bufptr_ok[k];
                    unsigned bz = 0;
                    for (unsigned j = 0; j < 0x100; ++j) if (MEM_BU(j, (gpr)(int32_t)p)) ++bz;
                    if (bz) ++buf_nz[k];
                }
            }
        }
        if (n <= 3 || (n % 512ul) == 0)
            fprintf(stderr, "[m5-cmdbuf] phase=%u n=%lu pn=%lu vol58_nz=%lu ptr_ok=%lu/%lu/%lu/%lu buf_nz=%lu/%lu/%lu/%lu\n",
                    phase, n, pn, vol58_nz, bufptr_ok[0], bufptr_ok[1], bufptr_ok[2], bufptr_ok[3],
                    buf_nz[0], buf_nz[1], buf_nz[2], buf_nz[3]);
    }
'''
MARK = "PATCH: s4206 cmdbuf"

if __name__ == "__main__":
    p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
    t = p.read_text()
    if MARK in t:
        print("s4206 already present")
    else:
        assert t.count(OLD) == 1, t.count(OLD)
        p.write_text(t.replace(OLD, NEW + OLD, 1))
        print("s4206 patched")
