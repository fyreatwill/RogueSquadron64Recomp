# G1d: intersect RT64 writebacks with the wide scan-out fb (title)
HYPOTHESIS-ID: g1d-widescreen
s6243: all-phase skip blanks the wide title frame (control OK); ph4-only skip leaves noise below y~255 -> garbage = undrawn fb RAM aliasing, filled by RT64 writeback/draw output, not a draw.
One build, one run (wide w900 title, s6242_run.sh recipe): log every rt64_writeback / copyNativeToRAM (phase, phys addr, len, w, h) AND the VI scan-out origin+width per phase 4-5 title frames; compute offline the overlap with [origin, origin+0xC4E00). Outcomes: a writeback range covers fb offset >=0x70800 -> H-alias confirmed, writer = that image; then relocate/shrink that image or the fb (do NOT drop writeback). No overlap -> noise from guest-side write; use lldb write-watch on the fb tail (positive control: whole-fb watch fires).
Positive control: arm SKIPPH=-1 'all' in same session must blank (done s6243).
