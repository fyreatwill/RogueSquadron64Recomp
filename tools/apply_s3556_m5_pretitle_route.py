#!/usr/bin/env python3
from pathlib import Path
import re

path = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
text = path.read_text()
marker = "/* PATCH: s3556 pretitle rs_malloc route table */"
if marker in text:
    raise SystemExit("s3556 patch already present; regenerate before reapplying")
start = text.index("RECOMP_FUNC void rs_malloc(")
next_match = re.search(r"\nRECOMP_FUNC void ", text[start + 1:])
end = start + 1 + next_match.start() if next_match else len(text)
region = text[start:end]

entry = """    { /* PATCH: s3556 pretitle rs_malloc route table */
        static int en = -1;
        static unsigned n = 0;
        if (en < 0) { const char* e = getenv(\"ROGUESQ_LOG_PRETITLE_MUSYX\"); en = (e && e[0] && e[0] != '0') ? 1 : 0; }
        if (en) {
            extern uint32_t rs64_phase_ord(void);
            unsigned phase = rs64_phase_ord();
            if (phase >= 3 && (n < 64 || (n % 256) == 0)) {
                fprintf(stderr, \"[pret-myx] edge=entry n=%u phase=%u size=0x%08X flags=0x%08X ra=0x%08X\\n\", n, phase, U32(ctx->r4), U32(ctx->r5), U32(ctx->r31));
                fflush(stderr);
            }
            if (phase >= 3) n++;
        }
    }
"""
needle = "    // 0x80001ACC: addiu       $sp, $sp, -0x38\n"
if region.count(needle) != 1:
    raise SystemExit(f"entry anchor count={region.count(needle)}")
region = region.replace(needle, entry + needle, 1)

pre = """    { /* PATCH: s3556 pretitle rs_malloc route table */
        extern uint32_t rs64_phase_ord(void);
        uint32_t phase = rs64_phase_ord();
        if (phase >= 3) fprintf(stderr, \"[pret-myx] edge=pre-recv phase=%u q=0x%08X msg=0x%08X block=0x%08X size=0x%08X flags=0x%08X\\n\", phase, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17));
    }
"""
needle = "    rs64_m5_frequency_caller(rdram, ctx, 0x80001B04u); /* PATCH: s3438 frequency caller */\n"
if region.count(needle) != 1:
    raise SystemExit(f"pre-recv anchor count={region.count(needle)}")
region = region.replace(needle, pre + needle, 1)

post = """    { /* PATCH: s3556 pretitle rs_malloc route table */
        extern uint32_t rs64_phase_ord(void);
        uint32_t phase = rs64_phase_ord();
        if (phase >= 3) fprintf(stderr, \"[pret-myx] edge=post-recv phase=%u result=0x%08X size=0x%08X flags=0x%08X\\n\", phase, U32(ctx->r2), U32(ctx->r16), U32(ctx->r17));
    }
"""
needle = "    after_0:\n    // 0x80001B0C: addiu       $v0, $s0, 0xF\n"
if region.count(needle) != 1:
    raise SystemExit(f"post-recv anchor count={region.count(needle)}")
region = region.replace(needle, "    after_0:\n" + post + "    // 0x80001B0C: addiu       $v0, $s0, 0xF\n", 1)

read = """    { /* PATCH: s3556 pretitle rs_malloc route table */
        extern uint32_t rs64_phase_ord(void);
        uint32_t phase = rs64_phase_ord();
        if (phase >= 3) fprintf(stderr, \"[pret-myx] edge=heap-read phase=%u heap=0x%08X size=0x%08X flags=0x%08X aligned=0x%08X\\n\", phase, U32(ctx->r2), U32(ctx->r16), U32(ctx->r17), U32(ctx->r16));
    }
"""
needle = "    ctx->r2 = MEM_W(ctx->r2, -0X104);\n"
if region.count(needle) != 1:
    raise SystemExit(f"heap-read anchor count={region.count(needle)}")
region = region.replace(needle, needle + read, 1)

ret = """    { /* PATCH: s3556 pretitle rs_malloc route table */
        extern uint32_t rs64_phase_ord(void);
        uint32_t phase = rs64_phase_ord();
        if (phase >= 3) fprintf(stderr, \"[pret-myx] edge=return phase=%u value=0x%08X ra=0x%08X\\n\", phase, U32(ctx->r2), U32(ctx->r31));
    }
"""
needle = "    // 0x80001C90: jr          $ra\n"
if region.count(needle) != 1:
    raise SystemExit(f"return anchor count={region.count(needle)}")
region = region.replace(needle, ret + needle, 1)
text = text[:start] + region + text[end:]
path.write_text(text)
print("patched funcs_0.c s3556 x5")
