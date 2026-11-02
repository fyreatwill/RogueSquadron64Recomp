# NEXT: audit every stack-payload sendServiceMessage (s6781 class)
HYPOTHESIS-ID: service-msg-stack-payload-audit

s6781 fixed SELECT GAME panels lost because tickFormatMessageWorker sent a completion that lives on its own stack and
looped before the menu read it (sendServiceMessage 0x80006F78 queues the POINTER, no copy). Fix pattern: host FIFO of
(pointer, value) recorded after the send, substituted at the receiver's load (tools/fixup_menu_worker.py).
Class audit (iron rule: enumerate the whole idiom, classify every site, fix or prove dead):
1. Disassemble main (/tmp/main.s recipe: ROM 0x1000 -> vram 0x80000400) and EVERY overlay from
   rogue_squadron64/roguesquadron.yaml (menu 0x10C2D0, mission 0xA5D30, cinematic 0x137580, ... all at vram 0x800A5130),
   list every jal 0x80006F78 with how $a2 is formed (addiu a2,sp,N = stack payload).
   Seed (main + menu only): 0x8000582C, 0x800058FC (main), 0x800C5880 (menu), 0x800B380C (fixed s6781).
2. Per stack site: who receives (dest worker id in $a1), what the receiver reads and when, and whether the sender can
   reuse the frame first (loops, returns, or blocks on a reply). Sender that blocks on a reply before returning = safe.
3. Live sites: same xtrace marks (tools/fixup_rand_trace.py s6781 block) on the send and the receive load, oracle
   --exec-trace on the same PCs for the retail timing, then the FIFO fix; dead sites: write the proof in the entry.
Hypotheses: H-safe (every other stack send is followed by a blocking reply wait / the receiver copies at once);
H-live (another worker loop reuses its stack payload, e.g. the main-segment pair, possibly behind other menu/debrief
glitches). Discriminating outcome: per site, sender reuse-before-read possible (H-live) or not (H-safe).
Also: fold the s6781_menufifo_lvl1_dd1 soak verdict (expect rc=0, 0 crash, 0 stall).
After the audit: remaining front-end screens vs retail (options, controller settings, records/medals, ERASE GAME).
