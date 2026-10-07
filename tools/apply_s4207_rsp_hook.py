"""s4207: call rs64_s4207_after_audtask right after ucode_func in librecomp rsp.cpp (mirrored by submodule-patches)."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = p.read_text()
if "rs64_s4207_after_audtask" in t:
    print("already")
else:
    old = ("    RspExitReason exit_reason = ucode_func(rdram, task->t.ucode);\n"
           "    g_audio_dma_probe = previous_audio_probe;\n")
    assert t.count(old) == 1
    t = t.replace(old, old + "    if (is_audio_task) { rs64_s4207_after_audtask(rdram, static_cast<int>(exit_reason)); }\n")
    d = 'extern "C" uint32_t rs64_phase_ord();'
    assert t.count(d) == 1
    t = t.replace(d, d + '\nextern "C" void rs64_s4207_after_audtask(uint8_t* rdram, int exit_reason);')
    p.write_text(t)
    print("patched")
