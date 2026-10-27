# NEXT: G3c(a) fold s6355 red-haze control
HYPOTHESIS-ID: g3c-owner-visual

s6354 showed pcr (col=sp+0x74,row=sp+0x44) is the valid AA74 pair. Open question: does writing vertex rgb at AA74 change rendered terrain? Soak s6355_g3c_r2_redctl (arms ctl: R2=0,1 red haze; mid: 18..26 red haze), dirs scratch/agent/m6/g1_lvl1s6355_{ctl,mid}.
1. Find frames with terrain (python scan for r>b+8 fraction; skip explosion frames; convert with `sips -s format png`), view ctl.
2. ctl terrain red => write site live: view mid, far-edge frames: is edge faded smooth? Run tools/g3c_edge_score.py ctl/mid. Build owner contact sheet.
3. ctl terrain NOT red => AA74 r4 colour is not the terrain colour (decode which store feeds the vertex shade, or fade the DL vertex after it is built); do not tune radii further.
