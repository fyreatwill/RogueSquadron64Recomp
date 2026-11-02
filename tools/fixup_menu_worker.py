#!/usr/bin/env python3
"""s6781 G3: menu-overlay image worker completion ids (SELECT GAME slot panels).

The worker (0x800B3650) posts each completion with sendServiceMessage (0x800B380C) as a pointer to a message on ITS OWN
STACK (sp+0x10, request id at +0x14), then frees the request and loops; the menu poll (0x800B3FD8) receives one message
per frame and reads id byte +0x17 (0x800B4004). Retail jobs take ~60 VI (oracle s6781), so each completion is read
before the next one rewrites the slot. The port's worker finishes jobs ~1 VI apart, so two queued pointers both read the
later id and the earlier slot (inset / left emblem panel) waits forever in state 0.
Fix: after a successful send, record (message pointer, id) in a host FIFO (rs64_menu_worker_sent); after the menu's
lbu, replace $v0 with the id recorded for that pointer (rs64_menu_worker_recv). No guest memory or scheduling change;
each received completion carries the id it was sent with, as on hardware. ROGUESQ_MENU_WORKER_FIFO=0 = old behaviour.
Idempotent. Usage: fixup_menu_worker.py <RecompiledFuncs dir>"""
import pathlib, sys

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
TAG = "/* PATCH: s6781 menu worker ids */"
sent = "    rs64_menu_worker_sent(rdram, (const uint64_t*)&ctx->r0); " + TAG + "\n"
recv = "    ctx->r2 = rs64_menu_worker_recv((uint32_t)ctx->r3, (uint32_t)ctx->r2); " + TAG + "\n"
decl = ("extern void rs64_menu_worker_sent(const uint8_t* rdram, const uint64_t* gpr); extern uint64_t rs64_menu_worker_recv(uint32_t msg, uint32_t v0); "
        + TAG + "\n")
lbu = "    // 0x800B4004: lbu         $v0, 0x17($v1)\n    ctx->r2 = MEM_BU(ctx->r3, 0X17);\n"
done = 0
for p in sorted(base.glob("funcs_*.c")):
    s = p.read_text()
    if "// 0x800B380C: jal         0x80006F78" not in s or lbu not in s:
        continue
    done += 1
    if TAG in s:
        print(f"[s6781] menu worker ids already in {p.name}")
        continue
    # after_N label numbering can drift between regens: match on the PC comments around it.
    i = s.find("    // 0x800B380C: jal         0x80006F78\n")
    j = s.find("    // 0x800B3814: jal         0x80001C98\n", i)
    if i < 0 or j < 0 or j - i > 600 or "sendServiceMessage(rdram, ctx);" not in s[i:j]:
        sys.exit("s6781 menu worker ids: send anchor not found")
    k = s.rfind("    after_", i, j)
    if k < 0:
        sys.exit("s6781 menu worker ids: after_ label not found")
    k = s.index("\n", k) + 1
    s = s[:k] + sent + s[k:]
    if s.count(lbu) != 1:
        sys.exit("s6781 menu worker ids: lbu anchor not unique")
    s = s.replace(lbu, lbu + recv)
    s = s.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
    p.write_text(s)
    print(f"[s6781] menu worker ids added to {p.name}")
if done != 1:
    sys.exit(f"s6781 menu worker ids: worker found in {done} files (expected 1)")
