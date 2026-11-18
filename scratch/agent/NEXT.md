# NEXT (s7598)
HYPOTHESIS-ID: guest-sized-allocation-census

Class XC closed s7597 (91 exception sites, 0 open; mods/ scan ELOOP/EACCES boot abort fixed). Class AZ = every host allocation
whose SIZE derives from guest data (guest RAM words, RDP/RSP command fields, VI registers, DMA lengths) in owner-reachable code:
std::vector resize/reserve/assign, new[], malloc/calloc/realloc, std::string(n,..), RT64 texture/framebuffer/buffer creation
(width*height*bpp from SetColorImage/SetTextureImage/LoadBlock/VI width) in src/, librecomp/src, ultramodern/src, lib/rt64/src.
Per site: size source; clamp present?; worst-case bytes from a 32-bit/12-bit guest field; consequence (bad_alloc ->
terminate rc134, multi-GB commit, GPU allocation failure -> null deref).
Hypotheses: H-clamped (every guest-sized allocation has a bound), H-unbounded (a corrupt or unusual guest field drives a
multi-GB alloc -> abort/hang), H-gpu (RT64 texture/target creation from guest dims has no cap and fails on the Metal side).
Tool: tools/s7598_az_census.py --controls (plant an unclamped resize(guest_word) + drop a row; both caught). Runtime witness
for any H-unbounded row: a gated plant lever writing the extreme field, old arm aborts, clamped arm alive, ctl alive
(pattern tools/s7597_xc_witness.zsh, copied folders).
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
