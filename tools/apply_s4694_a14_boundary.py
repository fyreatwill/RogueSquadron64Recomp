"""M5 A14 diagnostic: phase-gated shutdownMusyXVoices call-3 boundary rows.

Adds [a14-enter] (call entry), [a14-scan] (status-scan mismatch iterations at
1,2,3,10^k), [a14-timeout] (10,000,000 scans, observational only -- the loop is
NOT broken) and [a14-return] (loop fell through to 0x8009BD14) rows, all gated
on rs64_phase_ord() >= 3. Pairs with the existing [s4471-b7cc] status-zero
store row and [a14-yield] row (tools/apply_s4296_a14_spin_yield.py).

ORIGIN: no mitigation; read-only logging, no state forced or cleared. Live-tree
patch like s4296 (full regen is broken, REGEN WARNING s4204).
"""
from pathlib import Path

gen = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_26.c"
t = gen.read_text()
if "PATCH: s4694 A14 boundary" in t:
    raise SystemExit("already patched")


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit(f"anchor count {t.count(old)} for {old[:60]!r}")
    t = t.replace(old, new)


FMT = "s0=%02X s1=%02X s2=%02X s3=%02X"
ARGS = ", ".join(
    f"(unsigned)MEM_BU(0, S32(0x80154620u + {i}u * 0x1228u))" for i in range(4)
)

sub(
    "RECOMP_FUNC void shutdownMusyXVoices(uint8_t* rdram, recomp_context* ctx) {\n",
    "static unsigned long g_a14_call = 0, g_a14_it = 0, g_a14_reads = 0; static int g_a14_act = 0; /* PATCH: s4694 A14 boundary */\n"
    "RECOMP_FUNC void shutdownMusyXVoices(uint8_t* rdram, recomp_context* ctx) {\n",
)

ENTRY_ANCHOR = "    // 0x8009BCC4: addiu       $sp, $sp, -0x18\n"
sub(
    ENTRY_ANCHOR,
    "    { /* PATCH: s4694 A14 boundary */\n"
    "        extern uint32_t rs64_phase_ord(void); extern int rogue_current_thread_id(uint8_t*);\n"
    "        ++g_a14_call; g_a14_it = 0; g_a14_reads = 0; g_a14_act = (rs64_phase_ord() >= 3u);\n"
    "        if (g_a14_act) { const char* e = getenv(\"ROGUESQ_A14_YIELD\");\n"
    f'            fprintf(stderr, "[a14-enter] call=%lu phase=%u thr=%d yield=%d a0=%u {FMT}\\n", g_a14_call, rs64_phase_ord(), rogue_current_thread_id(rdram), (e && e[0] == \'0\') ? 0 : 1, (unsigned)ctx->r4, {ARGS}); fflush(stderr); }}\n'
    "    }\n" + ENTRY_ANCHOR,
)

READ_ANCHOR = "L_8009BCF0:\n    // 0x8009BCF0: lui         $at, 0x8015\n"
sub(
    READ_ANCHOR,
    "L_8009BCF0:\n    ++g_a14_reads; /* PATCH: s4694 A14 boundary */\n"
    "    // 0x8009BCF0: lui         $at, 0x8015\n",
)

MISS_ANCHOR = "    if (ctx->r4 != ctx->r5) { /* PATCH: s4296 A14 spin yield */\n"
sub(
    MISS_ANCHOR,
    MISS_ANCHOR
    + "        if (g_a14_act) { unsigned long n = ++g_a14_it; if (n <= 3ul || n == 10ul || n == 100ul || n == 1000ul || n == 10000ul || n == 100000ul || n == 1000000ul || n == 10000000ul) {\n"
    f'            fprintf(stderr, "[a14-scan] call=%lu scans=%lu reads=%lu a0=%u a1=%u {FMT}\\n", g_a14_call, n, g_a14_reads, (unsigned)ctx->r4, (unsigned)ctx->r5, {ARGS});\n'
    '            if (n == 10000000ul) fprintf(stderr, "[a14-timeout] call=%lu scans=%lu\\n", g_a14_call, n);\n'
    "            fflush(stderr); } }\n",
)

RET_ANCHOR = (
    "            goto L_8009BCEC;\n    }\n"
    "    // 0x8009BD14: addu        $a0, $zero, $zero\n"
)
sub(
    RET_ANCHOR,
    "            goto L_8009BCEC;\n    }\n"
    "    if (g_a14_act) { /* PATCH: s4694 A14 boundary */\n"
    f'        fprintf(stderr, "[a14-return] call=%lu scans=%lu reads=%lu {FMT}\\n", g_a14_call, g_a14_it, g_a14_reads, {ARGS}); fflush(stderr); g_a14_act = 0; }}\n'
    "    // 0x8009BD14: addu        $a0, $zero, $zero\n",
)
gen.write_text(t)
print("patched", gen)
