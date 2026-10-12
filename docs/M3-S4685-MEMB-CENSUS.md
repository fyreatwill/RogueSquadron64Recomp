# M3 s4685 — backward non-self zero-offset `MEM_B` census

The external generated tree was scanned at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs` with
`tools/census_memb.py`. The parser scan and an independent broad regex scan
both found 35 direct `MEM_B(ctx->rN, 0)` loads in 9 files. Of these, 22 are
inside a backward edge and 12 are non-self source/destination register sites.
The remaining 10 loop sites are self-register loads and 13 direct loads are
outside a backward loop.

All 12 non-self sites are scalar or packed-field consumers:

| Sites | Function(s) | Use | Classification |
|---:|---|---|---|
| 1 | `initGridLayerFromLevelData` | signed byte compared with a limit | scalar field |
| 1 | `selectGridCellTileVariant` | signed byte compared with a table limit; same address is then read unsigned | scalar/table field |
| 1 | `emitGridCellTileStripDiagonal` | signed vertex/mesh byte used in arithmetic | scalar geometry field |
| 1 | `menuControllerInput` | signed input byte tested, then unsigned value incremented/stored | scalar input field |
| 2 | `renderFlatMeshFaceGroup`, `renderUnlitMeshFaces` | signed bytes shifted and packed into a render word | packed scalar fields |
| 5 | `bcopy_recomp` | source bytes copied while source/destination pointers advance | byte-copy data; pointer is not reconstructed |
| 2 | `streamTerrainGridCellsByDistance` | signed terrain bytes compared and used as thresholds | scalar terrain fields |

The `bcopy_recomp` sites are the only candidates whose surrounding code
advances a pointer, but the loaded byte is copied to the destination and is
never used to form an address. No candidate is a pointer reconstruction, and
no named writer publishes an invalid pointer at any candidate. The allocator
and free-list anchor scan found the existing `rs_malloc`/free-list controls;
none is implicated by this class.

Result: H-MEMB-bounded. This is static/source-only evidence; no runtime probe,
guard, or mitigation is authorized. A future runtime arm would require a new
site-specific symptom and the existing allocator/free-list positive controls.
