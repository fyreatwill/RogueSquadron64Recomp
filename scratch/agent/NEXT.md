# NEXT: port-side RDP histogram at hangar VI 512, compare to retail (s4514 rdp.log)

HYPOTHESIS-ID: hangar-artifact-triage

Retail reference now exists (scratch/agent/s4514/rdp.log; raw in ~/Documents/Tools/rs64-oracle/s4514_rdp_hangar512.bin).
Retail hangar frame: ~1244 tris (0x0D x275, 0x0F x969), settile 55, loadblk 24, loadtlut 7, settimg 31, setcimg 2, fillrect 1, ~205 KB.
Task: emit the same per-full-sync histogram from the port (hook near rs64_dpc_defer_end / rs64_dpc_get_task_range in
src/main/main.cpp ~5863; parse the committed RDP range from RDRAM with the cmd-length table from tools/oracle/rdplog/rdplog.c).
Positive control: port title VI 1024 must be non-empty (retail: texrect~161, settile~342, loadblk~158, setcimg 3 per sync).
Outcomes: tri counts/types differ => H1 (ucode/renderer path; diff command streams offline); equal counts but SETCIMG width/addr
or settile/tex formats differ => H3 (colour image/VI); all equal => H3 raster (RT64). Compare first sync at VI 512 only.
