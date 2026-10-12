#!/usr/bin/env python3
"""Make the existing voice handoff probes phase-attributable.

This is a diagnostic fixup for the generated funcs_24.c snapshot.  It keeps
the named render-call witness only in the title and hangar VI buckets and
adds the phase identity to every retained row.
"""
from pathlib import Path

path = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
text = path.read_text()
mark = "PATCH: s4690 external-entry phase attribution"
if mark in text:
    print("already applied")
    raise SystemExit(0)

start = text.index("/* PATCH: s4534 voice a3 callsite.")
end = text.index("/* PATCH: s4537 init-voice store census.", start)
block = text[start:end]

old = """    if (!on) return;
    uint32_t d = (uint32_t)a3;
"""
new = """    if (!on) return;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    uint32_t phase = rs64_phase_ord();
    uint32_t vi_width = rs64_vi_committed_width();
    uint32_t vi_origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((vi_width == 1024u && vi_origin == 0x00790400u) ||
          (vi_width == 512u && vi_origin == 0x006AB400u))) return;
    uint32_t d = (uint32_t)a3;
"""
if block.count(old) != 1:
    raise SystemExit(f"phase anchor count: {block.count(old)}")
block = block.replace(old, new, 1)

old = '"[s4534-jal] kind=arm site=%s pc=0x%08X s1=0x%08X raw34=0x%08X raw_ok=%d a3=0x%08X a1=0x%08X\\n",\n            site, pc, s32, raw, raw_ok, d, (uint32_t)a1);'
new = '"[s4534-jal] kind=arm phase=%u width=%u origin=0x%06X site=%s pc=0x%08X s1=0x%08X raw34=0x%08X raw_ok=%d a3=0x%08X a1=0x%08X\\n",\n            phase, vi_width, vi_origin, site, pc, s32, raw, raw_ok, d, (uint32_t)a1);'
if block.count(old) != 1:
    raise SystemExit(f"arm format count: {block.count(old)}")
block = block.replace(old, new, 1)

old = '"[s4534-jal] kind=%s site=%s pc=0x%08X s1=0x%08X raw34=0x%08X raw_ok=%d a3=0x%08X a1=0x%08X\\n",\n        bad ? "bad" : "ctl", site, pc, s32, raw, raw_ok, d, (uint32_t)a1);'
new = '"[s4534-jal] kind=%s phase=%u width=%u origin=0x%06X site=%s pc=0x%08X s1=0x%08X raw34=0x%08X raw_ok=%d a3=0x%08X a1=0x%08X\\n",\n        bad ? "bad" : "ctl", phase, vi_width, vi_origin, site, pc, s32, raw, raw_ok, d, (uint32_t)a1);'
if block.count(old) != 1:
    raise SystemExit(f"row format count: {block.count(old)}")
block = block.replace(old, new, 1)

block = block.replace("/* PATCH: s4534 voice a3 callsite. Diagnostic only. */",
                      "/* PATCH: s4534 voice a3 callsite. Diagnostic only. " + mark + " */", 1)
path.write_text(text[:start] + block + text[end:])
print("applied")
