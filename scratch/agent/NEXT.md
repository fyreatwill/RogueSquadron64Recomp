# NEXT: locate the RSP op that yields wrong shade integer words in hangar triangles

HYPOTHESIS-ID: hangar-artifact-triage

s4517: port RDP stream (frame 900) vs retail (frame 0, s4516 rdp.bin): every non-triangle command and all tri edge/texture words are byte-identical; shade words (8-23) differ in 588/1249 tris, mostly port 0xFFxx where retail 0x00xx (sign-extended colour byte), e.g. 0xffa1ffa3 vs 0x00a100a3. Tools: scratch/agent/s4517_diff.py, s4517_port_rdp.sh (RS64_RDP_BIN_PORT dump).
Hypotheses: H-A RSP vector accumulator/pack clamp semantics wrong (unsigned vs signed saturate on VSAR/VMACx/VMUDx/VSUBx/VCH family) in the shade path; H-B ucode vertex-colour/light load (LBV/LPV/LUV/LSV sign-vs-zero extension) wrong; H-C DMEM vertex colour bytes differ already at input (data, not op).
Discriminator: pick one differing tri (e.g. frame 900 cmd 66, shade w8 0xffa1ffa3 vs 0x00a100a3), find the vertex input colour bytes in RDRAM/DMEM for the matching vertex on both sides (port: dump DMEM vertex buffer at tri emit; retail: oracle). Input bytes equal => H-A/H-B (op-level: trace the RSP instructions between vertex load and the shade-word emit and look for a clamp/pack op); input bytes differ => H-C. Positive control: a tri with colour < 0x80 must show equal words.
Alternative cheaper split: check whether the port RSP interpreter and the cxd4 retail core disagree on saturate semantics via a unit vector-op test against cxd4 reference for VMACF/VMUDN/VMADH/VSAR with high-bit operands.
