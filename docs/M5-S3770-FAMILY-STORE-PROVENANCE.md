# M5 s3770 — family internal-store provenance

Session 3770 ran one regeneration-safe store census in concurrent image and
silent arms, with the retail oracle in the same work unit.

The oracle whole-RDRAM positive control fired (77,858 writes) and reached
title 1024 @ 0x00790400 and hangar 512 @ 0x006AB400. It independently
executed the retail family PCs: 0x80007670 (300), 0x8001E2C0 (19),
0x8001FACC (19), 0x8001FADC (19), 0x8001FAE4 (18),
0x8001FAEC (18), 0x8001FAF0 (19), 0x8001FAF8 (18), and
0x8001FBE4 (18).

Both port arms reached both target VIs, emitted all three family store
controls, and matched the census. Phase-bucket rows were:

| Family | Title | Hangar | Target-range rows |
|---|---:|---:|---:|
| S (rs_strncpy) | 256 | 256 | 0 |
| L (loadTextureToMemory) | 256 | 256 | 0 |
| I (initTextureLUTAndAllocBuffers) | 256 | 0 | 0 |

S/L destinations were alternate object addresses such as 0x80165E98 and
0x80165D5E, not the title (0x80178C80..0x80178F80) or hangar
(0x801797B0..0x80179A48) buffers. I's title stores were setup/table
destinations such as 0x80128EF0..0x80128F08; it had no hangar-phase store
bucket. The value field was retained; no write or audio gate was changed.

This selects H-M5-FamilyStoresAlternateLegitimateObject for the measured S/L
store destinations and H-M5-FamilyAbsentTargetEdge for I. It does not yet
prove that the alternate objects are legitimate or explain the route/object
identity mismatch. The next discriminator must join those alternate
destinations to the clear-associated object and route identity.

ORIGIN: the writer PCs and values are legitimate asset/setup stores; this
instrument only observes their effective destinations and values.
