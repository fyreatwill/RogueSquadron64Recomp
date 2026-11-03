# NEXT: re-verify the 21:9 owner bundle on the s6858 spill layout (SPILL_HI + RAMTOP 20 when OSMEM>8)
HYPOTHESIS-ID: g1d-spill-layout-219-recheck

Why: s6858 found the dd>1 malloc spill arena (0x80800000-0x80C00000) aliased the 12 MB game heap. 21:9 sets OSMEM_MB=12
itself, so the s6857 21:9+FPS60+dd4 pass (lvl9/lvl17, 12782 spill blocks at 0x808xxxxx) ran on the aliased layout. The fix
moves the spill to 0x81000000 and widens RAMTOP to 20 MB; nobody has run 21:9 on it.
Hypotheses: H-ok (lvl9/lvl17 300 s clean, spill all at 0x81, disc 100% shifted, non-disc 0) / H-ramtop (RAMTOP 20 breaks
something at 1024 width: RT64 read limit, DL pointer guard -> crash or missing geometry) / H-latent (a crash the aliasing had
masked or a different heap-pressure failure now that 4 MB of heap is no longer stolen).
Discriminator: sed s6858 -> s6859 in scratch/s6857/abd.sh and both.sh (keep 21:9, MISSION_WIDTH 1024, SHIFT=256), run
`zsh scratch/s6859/both.sh`; check `grep -a '\[ddbundle\] osmem' run.log` fired, spill address prefixes
(`grep -a '^\[spill\] req' run.log | awk '{print substr($4,1,3)}' | sort | uniq -c` -> only 810/811), crash lines, and
python3 scratch/s6857/tot.py <dir>/zgate.txt (disc textures may relocate; take the top shifted textures and confirm kept 0).
Sheet: tools/owner_sheet_s6856.py <out> lvl9=<fbd>:=6000,9000,12000 lvl17=... (defaults --w 1024 --cx 760).
Outcomes: clean -> close, note in OWNER-OPT-INS that both bundles run on the fixed layout; crash -> backtrace, name writer.
