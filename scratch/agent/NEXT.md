# NEXT: BLOCKED on retail RDP source (see scratch/agent/BLOCKED.md, s4513)

HYPOTHESIS-ID: hangar-artifact-triage

If a human supplies an LLE RSP+RDP plugin, run the oracle with --rsp and take the RDP histogram below. Otherwise do an M5/M3 item or port-only characterisation.

HYPOTHESIS-ID: hangar-artifact-triage

s4512: DL inputs (root, 13 children, texture) are identical; op04 "vertex" blobs are DL scratch (tools/agent_blob_dlscan.py), so input-side diffing is exhausted without F5Rogue source.
Hypotheses: H1 renderer/ucode emits different RDP triangles from identical DLs (counts/types differ); H3 RDP stream equal, defect is in rasterizer/VI/colour-image handling (width/format); H2 hidden vertex-source data differs (unlocated).
Discriminator: per-task RDP command histogram (cmd id 0x08-0x0F tris, 0x24/0x25 rects, 0x37 fill, 0x3D/0x3F set tex/cimg with addr+width) at the first VI-512 task, both sides (oracle: mupen RDP plugin command dump or a RDRAM read of the RDP list from DPC_START..END; port: the LLE ucode's RDP out buffer). Positive control: title VI 1024 task histogram must be non-empty on both sides.
Outcomes: tri counts differ => H1, trace ucode path; equal and SETCIMG width differs => H3 right-edge column; all equal => H3 raster.
