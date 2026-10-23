# G3 retail pixel oracle (s5963)

Rice/Glide64 leave the RDRAM framebuffer empty (s4506), so retail pixels were unobtainable.
Fix: angrylion-rdp-plus (software RDP, renders into RDRAM) built as an m64p video plugin
at /Users/williambuckley/Documents/Tools/g3_angrylion (clone of github.com/ata4/angrylion-rdp-plus,
`cmake ../src -DCMAKE_POLICY_VERSION_MINIMUM=3.5 && make`; builds clean on macOS, outside the repo).
Recipe: scratch/agent/s5963_angry_fb.sh (oracle + cxd4 LLE RSP + angrylion, --fb-dump at hangar).
Convert: `python3 -I scratch/agent/s4506_fb_png.py hangar6.bin 6AB400 6A0000 512 440 out.png`
(use the dump taken AFTER the VI origin settles; the 2.0 s dump caught the other buffer 0x656800).
Positive control: title dump at 790000 is all zeros (wrong buffer, origin was 0x790400/0x790800) while
hangar has 238k nonzero words, so RDRAM writes are live. Reference frame: docs/g3_retail_hangar_oracle.png.
First comparison (single-source): retail pillar rails are dark; port frame s4642_viext/f_003_004.6.png
shows bright white vertical stubs at pillar edges => genuine port defect, not by-design lighting.
