# NEXT: why do dd4 stream-function calls return empty with a non-empty window (span-table filters)
HYPOTHESIS-ID: g1c-dd8-limit
s6493: empty lists (20% dd4) are not early-out/pool/spanbound/nonode. Cells are rejected by the span-table filters in streamTerrainGridCellsByDistance (0x80042D64 equal-sentinel beq; 0x80042D90/DA8 +3/+4 byte compares vs table 0x80130DB0).
Hypotheses: H-spanoverflow (signed-byte table can't hold dd4 extents / footprint rasterizer writes wrong rows), H-footprint (window words 0x80132DB0..BC from s6036/s6037 mismatch the table's row origin), H-camera (empties only at certain poses, a real geometry effect).
Do: scout the writer of table 0x80130DB0 (who fills rows/bytes from the footprint polygon, row origin, byte meaning). Then on empty calls ([streamcum] extension) log window words 0x80132DB0/B4/B8/BC and the first rows of the table; compare with a non-empty dd4 call and a dd1 call. Re-run scratch/agent/s6493_streamcum.sh (rename tag). Outcome: whether table bytes are out of range/wrapped on empty calls.

## RESUME (s6494)
tools/apply_s6493b_empty_dump.py exists but has NOT been applied/built/run. Next: `python3 tools/apply_s6493b_empty_dump.py` (after apply_s6493_stream_cum.py), rebuild (DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build), re-run scratch/agent/s6493_streamcum.sh with ROGUESQ_FORFACE_LOG=1 at dd4 and dd1, compare [streamdump] EMPTY vs ok rows: are table bytes out of range/wrapped or window words mismatched on empties? Fold the patch into the fixup scripts if it must survive regen.
