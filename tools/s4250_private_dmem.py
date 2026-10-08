#!/usr/bin/env python3
"""s4250: give the audio SP-task path a private DMEM so it need not take g_lle_task_mutex.

Idempotent. Rewrites bare `dmem[`/`dmem +` accesses to the thread-local pointer
`g_dmem_cur` (default = gfx storage `dmem`), and in run_task swaps the pointer to
`dmem_audio` for M_AUDTASK when ROGUESQ_AUDIO_PRIVATE_DMEM is set (then skips the lock).
"""
import re, sys
R = "/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/"
files = ["lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp",
         "lib/N64ModernRuntime/librecomp/src/rsp.cpp",
         "src/rsp/dpc_bridge.cpp", "src/main/main.cpp"]
pat = re.compile(r'(?<![\w.>])(?<!uint8_t )dmem(?=\s*(\[|\+))')
for f in files:
    s = open(R + f).read()
    o = s
    s = pat.sub('g_dmem_cur', s)
    s = re.sub(r"^[ \t]*extern uint8_t (g_dmem_cur|dmem)\[\];.*\n", lambda m: m.group(0) if m.group(1) == "dmem" and f.endswith("rsp.hpp") else "", s, flags=re.M)
    s = s.replace('std::memset(dmem, 0, 0xFC0)', 'std::memset(g_dmem_cur, 0, 0xFC0)')
    if f.endswith('rsp.hpp') and 'g_dmem_cur' in s and 'inline thread_local uint8_t* g_dmem_cur' not in s:
        s = s.replace('using RspUcodeFunc = RspExitReason(uint8_t* rdram, uint32_t ucode_addr);\n',
          'using RspUcodeFunc = RspExitReason(uint8_t* rdram, uint32_t ucode_addr);\n\n'
          '// s4250: `dmem` is the gfx storage; audio SP tasks may run on a private copy.\n'
          'extern uint8_t dmem[];\nextern uint8_t dmem_audio[];\n'
          'inline thread_local uint8_t* g_dmem_cur = dmem;\n', 1)
    if f.endswith('rsp.cpp') and 'dmem_audio' not in s:
        s = s.replace('uint8_t dmem[0x1000];\n', 'uint8_t dmem[0x1000];\nuint8_t dmem_audio[0x1000];\n', 1)
        old = s[s.index('    struct DmemGuard {'):s.index('    } dmem_guard;\n') + len('    } dmem_guard;\n')]
        new = '''    // s4250: private audio DMEM (ROGUESQ_AUDIO_PRIVATE_DMEM=1) -> no shared-dmem lock.
    static const bool s_private_audio_dmem = [] {
        const char* e = std::getenv("ROGUESQ_AUDIO_PRIVATE_DMEM");
        return e && e[0] && e[0] != '0';
    }();
    const bool use_private_dmem = s_private_audio_dmem && task->t.type == M_AUDTASK;
    struct DmemGuard {
        bool priv;
        explicit DmemGuard(bool p) : priv(p) {
            if (priv) { g_dmem_cur = dmem_audio; g_s4248_lock_wait_us = 0; return; }
            auto lt0 = std::chrono::steady_clock::now();
            if (rs64_dmem_lock) rs64_dmem_lock();
            g_s4248_lock_wait_us = (uint32_t)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - lt0).count();
        }
        ~DmemGuard() { if (priv) { g_dmem_cur = dmem; return; } if (rs64_dmem_unlock) rs64_dmem_unlock(); }
    } dmem_guard(use_private_dmem);
'''
        s = s.replace(old, new, 1)
    if s != o:
        open(R + f, 'w').write(s); print("patched", f)
