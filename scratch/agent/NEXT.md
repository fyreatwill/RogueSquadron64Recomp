# NEXT: does streamTerrainGridCellsByDistance run inside load_level_hmp on lvl7 dd4? (H-load-race vs H-teardown-zero)
HYPOTHESIS-ID: g1c-dd-phase2
State (s6590): retail desc+4 valid; dd4 CAPX=2 fault sees desc+0/+4 NULL with dims 93x96 already set.
Work unit: patch logs (via fixup script) at load_level_hmp (0x80043DD8 region) entry/exit, the 0x6DC0/0x4 publish stores, loadLevelAssets zeroing, and the first streaming call with desc+4==0, each with VI number; run scratch/agent/s6590_run.sh dd4 and ret. Outcome: streaming call between dims set and publish => load race (find who calls streaming from the other thread/frame, defer it or gate on desc+4!=0); zeroing after publish => find the teardown writer.
