# NEXT: G3 cinematic sweep follow-ups
HYPOTHESIS-ID: g3-cinematic-sweep

Done s6792: 81/81 AT THE MOVIES shots paired with retail; spike cull fixed for 640-wide images (notch gone).

Work unit: the thin vertical line at x=320 (screen centre) visible in the 640-wide cinematic window shots
(scratch/s6792/notch_fix_sheet.png, both builds). Hypotheses: H-retail (retail angrylion frame shows it too: two 320-wide
halves/texrect seam in the game), H-rt64 (RT64 seam between two half-screen draws / tile sampling at the 320 split),
H-rdp (port RDP stream differs at x=319/320). Discriminator: render the same shot from retail's dump (oracle angrylion frame)
and compare column 318-322 luminance vs neighbours; then port dump at the aligned frame (tools/g3_cine_sweep.py block/shots
alignment, dumps in scratch/s6792/mov/ and fix/). Second item: TRI shots 48/64 (retail tri median 914/772 vs port 1188/846).
DUR shots (+4 s retail) stay single-source oracle-side unless a port-side cause appears.
