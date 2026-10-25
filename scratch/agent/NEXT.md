# G1d: does reinterpretTileRecord (framebuffer-as-texture) feed the title garbage rect? (w900 title phase)
HYPOTHESIS-ID: g1d-widescreen
s6232: upload-time TMEM bytes are clean for 99/100 photo tiles, yet garbage rect still draws (fix_03.png). So garbage is not TMEM-upload content.
Hypotheses: H-fbreinterp (rect samples a framebuffer-derived texture via lib/rt64 hle/rt64_framebuffer_manager.cpp reinterpretTileRecord, line ~450, because widened fb range overlaps photo tile source); H-up167 (the one noisy upload, first 64x32, is the rect's texture); H-cache (hash collision picks a wrong cached texture).
Discriminator: one build logging per reinterpretTileRecord call (tile addr, fb addr/width/height, hash, frame) + per-draw texture hash for rect texrects (screen x<=0x240,y>=0x2A0 at w900). Hits at rect tile addrs -> H-fbreinterp (then relocate/shrink fb range; export.sh+commit). Zero hits and rect hash == up_167 hash h98bb35b7e7c80445 -> H-up167, find its source. Else H-cache.
Run: zsh scratch/agent/s6232_run.sh 900 (copy to s6233); decode with scratch/agent/s6232_sheet.py (python3 -I). Game cwd build/.
