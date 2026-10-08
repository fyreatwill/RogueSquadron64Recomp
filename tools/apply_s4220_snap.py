"""s4220: DMEM nz-per-256B snapshot at every label 0x1104..0x1314 of factor5_ucode_b (voice loop + frame end), phase-scoped windows. Env ROGUESQ_LOG_S4220=1.
Idempotent. Also called from fixup_factor5_ucode.py so regen keeps it."""
import re, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]

def patch_rsp():
    rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
    t = rsp.read_text()
    if "rs64_s4220_snap" in t:
        return
    anchor = 'extern "C" void rs64_probe_audio_dma_write(uint8_t* rdram,'
    assert t.count(anchor) == 1
    code = r'''extern "C" void rs64_s4220_snap(uint32_t pc) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4220"); return e && e[0] && e[0] != '0'; }();
    if (!on || !rs64_s4208_active) return;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned long fetches; static bool logging;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; fetches = 0; logging = false; }
    if (pc == 0x1104) { fetches++; logging = (fetches <= 3) || (fetches >= 300 && fetches < 304); }
    if (!logging) return;
    std::fprintf(stderr, "[s4220] phase=%u f=%lu pc=%04X nz:", phase, fetches, pc);
    for (uint32_t c = 0; c < 16; c++) { uint32_t z = 0; for (uint32_t i = 0; i < 256; i++) z += RSP_MEM_BU(0, c * 256 + i) != 0; std::fprintf(stderr, " %u", z); }
    std::fputc('\n', stderr);
}
'''
    rsp.write_text(t.replace(anchor, code + anchor))

def patch_c(cpath):
    s = cpath.read_text()
    if "rs64_s4220_snap" in s:
        return
    out = []
    for line in s.split("\n"):
        out.append(line)
        m = re.match(r"^L_([0-9A-F]{4}):$", line)
        if m and 0x1105 <= int(m.group(1), 16) <= 0x1314:
            out.append(f"    rs64_s4220_snap(0x{m.group(1)});  /* fixup: s4220 snap */")
    s = "\n".join(out)
    s = s.replace('extern "C" void rs64_audio_image_break(uint32_t pc);', 'extern "C" void rs64_s4220_snap(uint32_t pc);\nextern "C" void rs64_audio_image_break(uint32_t pc);', 1)
    # entry snapshot at the fetch point, so fetch-count advances per record
    old = "    rs64_s4210_cmd_rec(r4);  /* fixup: s4210 cmd ring */\n"
    assert old in s
    s = s.replace(old, old + "    rs64_s4220_snap(0x1104);  /* fixup: s4220 snap */\n", 1)
    cpath.write_text(s)

if __name__ == "__main__":
    patch_rsp()
    patch_c(R / "build/factor5_ucode/factor5_ucode_b_recompiled.c")
    print("ok")
