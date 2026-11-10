#!/usr/bin/env python3
"""s7064 transition-stall audio wait: host ring of audio-slot drain waits, ROGUESQ_S7064=<out path> (unset = one global test).
Hooks (measurement only, no guest state touched):
  anyAudioSlotActive return (funcs_23.c): rs64_s7064_poll(rdram, idle=v0, caller ra from the saved stack slot)
  deactivateVoice (funcs_24.c): rs64_s7064_deact(rdram, slot idx, ra)
  musyxSynthFrame_s4562_impl entry (funcs_24.c): rs64_s7064_synth(rdram)
Host side (src/main/upstream_compat.cpp) keeps episodes (busy polls until idle), per-episode active-slot masks, per-synth-frame
slot snapshots (136 B each) inside episodes, and deactivate events; dumped as text at exit. Usage: apply_s7064_slotwait.py [dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7064 slotwait"
DECL = ('extern int g_rs64_s7064; extern void rs64_s7064_poll(uint8_t*, unsigned, unsigned); '
        'extern void rs64_s7064_deact(uint8_t*, unsigned, unsigned); extern void rs64_s7064_synth(uint8_t*); /* %s */\n' % TAG)
def patch(fn, edits):
    p = D / fn; t = p.read_text(errors="surrogateescape")
    if TAG in t: print(fn, "already applied"); return
    t = t.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL, 1)
    for head, nxt, old, new in edits:
        i0 = t.index(head); i1 = t.index(nxt, i0 + len(head)); body = t[i0:i1]
        assert body.count(old) == 1, (fn, old[:60], body.count(old))
        t = t[:i0] + body.replace(old, new) + t[i1:]
    p.write_text(t, errors="surrogateescape"); print(fn, "applied", TAG)
A = "RECOMP_FUNC void anyAudioSlotActive(uint8_t* rdram, recomp_context* ctx) {"
patch("funcs_23.c", [(A, "\n;}", "    ctx->r31 = MEM_W(ctx->r29, 0X20);\n",
      "    if (g_rs64_s7064) rs64_s7064_poll(rdram, U32(ctx->r2), U32(MEM_W(ctx->r29, 0X20))); /* %s */\n"
      "    ctx->r31 = MEM_W(ctx->r29, 0X20);\n" % TAG)])
DV = "RECOMP_FUNC void deactivateVoice(uint8_t* rdram, recomp_context* ctx) {"
SY = "RECOMP_FUNC void musyxSynthFrame_s4562_impl(uint8_t* rdram, recomp_context* ctx) {"
patch("funcs_24.c", [
    (DV, "\n;}", "    ctx->r2 = S32(ctx->r4 << 4);\n",
     "    if (g_rs64_s7064) rs64_s7064_deact(rdram, U32(ctx->r4), U32(ctx->r31)); /* %s */\n    ctx->r2 = S32(ctx->r4 << 4);\n" % TAG),
    (SY, "\n", SY, SY + "\n    if (g_rs64_s7064) rs64_s7064_synth(rdram); /* %s */" % TAG)])
