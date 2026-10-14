#!/usr/bin/env python3
"""s4878: registerSiCallback(a0==0x8009123C) when the callback table 0x8011A8A4 already holds the synth entry -> return 1 (as a
successful register) without a second copy. Equals retail's net dereg->register state: the boot-time teardown (0x8008ECxx) skips its
dereg because the force-zero gate stubs leave 0x800A0F50==0, so cycle 1's reapplyAudioConfig register is unmatched (+1 copy, synth 2x/VI).
ORIGIN: unmatched register named at s4875 (gate byte 0x800A0F50==0 at first teardown; retail 1). Arm env ROGUESQ_S4875_DEDUP=1 (default off).
Counter: [s4878] dedup-skip n=. Idempotent; wired into fixup_game_funcs_vendored.py's apply list."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
s = p.read_text()
M = "PATCH: s4878 synth dedup"
if M not in s:
    hdr = 'RECOMP_FUNC void registerSiCallback(uint8_t* rdram, recomp_context* ctx) {\n'
    assert s.count(hdr) == 1
    body = ('    { /* ' + M + ' */ static int s_d = -1; static unsigned s_n; if (s_d < 0) { const char* e = getenv("ROGUESQ_S4875_DEDUP"); s_d = (e && e[0] && e[0] != 48) ? 1 : 0; }\n'
            '      if (s_d && (unsigned)ctx->r4 == 0x8009123Cu && ((unsigned)MEM_W(0X0, (int32_t)0x8011A8A4) == 0x8009123Cu || (unsigned)MEM_W(0X4, (int32_t)0x8011A8A4) == 0x8009123Cu || (unsigned)MEM_W(0X8, (int32_t)0x8011A8A4) == 0x8009123Cu || (unsigned)MEM_W(0XC, (int32_t)0x8011A8A4) == 0x8009123Cu)) {\n'
            '        fprintf(stderr, "[s4878] dedup-skip n=%u ra=0x%08X\\n", ++s_n, (unsigned)ctx->r31); ctx->r2 = 1; return; } }\n')
    s = s.replace(hdr, hdr + body, 1)
    p.write_text(s)
print("ok")
