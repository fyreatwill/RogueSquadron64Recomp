# NEXT: G3 - align retail and port RDP frames on the Available Craft page, find the state that differs

HYPOTHESIS-ID: g3-render-fidelity

Done s5964: retail r12.png (Available Craft) vs port s4642 frame: white stubs are port-only. Census (scratch/agent/s5964_oth.py) shows retail othermode-lo 0x552078 where port has 0x552038 (image_read_en bit 0x40) - but frames were not page-aligned.
Competing: H-rdp-imgread (port lacks image_read_en on those tris, ucode/DL emits different rendermode), H-tex, H-dl.
Work unit: (1) from s5964r/rdp.log pick the width-512 sync whose t~=50 s (matching dump h12/h13 phase); census that frame vs the port frame captured at the Available Craft page (s5964p run.log phase ord); (2) list tri states present in only one; (3) test: in rt64 force image_read_en on the 0x552038 tris within one run (toggle in-run) and see whether white stubs vanish. Positive control: toggle must change visible blend on some tri.
Do not do aim/steer work.
