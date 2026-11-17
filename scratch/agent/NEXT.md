# NEXT (s7550)
HYPOTHESIS-ID: class-gj-rt64-retained-rdram-addrs

Classes GF-GI CLOSED (s7546-s7549): threads, ultramodern/librecomp retained pointers, src/main statics, injected statics.
Residual host layer: RT64 (lib/rt64/src) keeps RDRAM addresses across frames: framebuffer manager entries (address/width/size),
texture cache keys (TMEM loads keyed by RDRAM address + hash), tile copies, the RDRAM-shadow/VI origin. If the guest frees a
heap block that RT64 still tracks and reuses it, RT64 could copy stale native fb data back into it (write) or serve a stale texture
(read). Writes into guest RAM are the dangerous direction.

Work unit: tools/s7550_gj_census.py (--controls), offline. Enumerate in lib/rt64/src (read-only, NEVER edit lib/ without
export.sh + commit): every member/static that stores an RDRAM address or offset (names like address, addr, rdramAddress, origin,
startAddress; assigned from a DP/RDP command word or VI register) and every site that WRITES host data into rdram through one
(copyNativeToRAM, framebuffer writeback / R2R, memcpy into RDRAM).
Classify: H-percmd (address taken from the current command stream and used within that command/frame), H-frameset (fb registry
rebuilt or validated per frame against the current colour image), H-hash (texture cache entries re-validated by content hash before
use; read-only), H-gated (RENDER_TO_RAM / R2R paths with an env gate: name the default), OPEN (a default-on RDRAM write through an
address retained past the frame without revalidation).
Controls: planted retained-address write -> UNCLASSIFIED; deleted rule; renamed proof -> DRIFT; real tree rc 0.
Hypotheses: H-percmd/H-frameset only; H-hash covers reads; H-stale-write (a default-on writeback into a retained address: then
measure it at runtime with a write watch on the fb registry addresses vs rs_free'd blocks before any fix).
Prior evidence: s7391 fb-cpu-reader census (0 guest loads from a live colour image), s7542 GC census (host writes into guest RAM
from src/main), s7541 late-writeback readers (only RT64 XXH3 + copyRAMToNativeAndChanges).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
