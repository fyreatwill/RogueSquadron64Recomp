# NEXT (s7501)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7500_ey_levels (tools/s7500_ey_recipe.zsh; `s7500_ey_levels ey arm=` rows in scratch/s7500_ey_levels/out.txt):
read=0 ctlA=ok ctlB=ok on L1 dd8 21:9 / L7 / L10 / L12 dd4 -> EY CLOSED 6 levels. read>0 -> read `[s7500] first cls=zread|tex|up` rows first
(that is the work unit). Note: the recipe's fill/draw/tex/up fields were fixed s7500 to parse before ` hooks ` (rerun-safe).

Work unit: class EZ, the writer behind each RT64 checkRAM upload. s7500 hooks counted 37 (L4) / 31 (L15) uploadRAM calls per run: RT64's
checkRAM found a known framebuffer's RDRAM bytes changed since its own hash, and copied those bytes into its GPU image. Something other than
RT64's draws wrote that RAM. Hypotheses: H-ez-cover (another image's RT64 writeback, an s7499 pair) / H-ez-cpu (guest CPU stores: the game
clears or draws into the fb in software, e.g. boot/fade/letterbox) / H-ez-dma (PI/SP DMA into the fb) / H-ez-hash (no real change: the hash
moved because RT64's own writeback did not update RAMHash).
Instrument, ONE build: extend rs64_s7500_up to log every upload (addr, w, siz, diffPx, path, swap, t) plus the bbox of changed bytes (reuse
the s6729 ROGUESQ_LOG_FBUPLOAD bbox code in rt64_framebuffer_manager.cpp uploadRAM), and join it against: the latest s7499 writeback range
(any image) overlapping that bbox since the fb's previous hash, the s6938 G1E_WBW page-protect write trap (or a cheaper guest store sample
over the fb range), and PI/SP DMA destinations (existing DMA hooks in recomp/rsp). Control: ROGUESQ_S7501_CTL pokes one word into a live
fb's RAM from the host once, which must show up as an upload with writer=ctl.
Run: `env XC=ROGUESQ_S7501_EZ=1+ROGUESQ_S7501_CTL=1 zsh tools/s7500_ey_recipe.zsh` (L4 dd1, L15 dd8 21:9), score per writer class.
