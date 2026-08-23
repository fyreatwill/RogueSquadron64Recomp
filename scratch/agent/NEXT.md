# NEXT work unit (s2179) — port extract / first-cross word bits vs retail finite

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2178 selected `H-RetailSourceWordFinite`: retail
cinematic first-cross `w_a2p8` (prev=`0x80059F3C`)
and extract `w_a1p20` are 10/10 finite (0 NaN).
The port SIGABRT is `vec3Cross` `NAN_CHECK` f10
(`funcs_4.c:33371`) from jal `0x800A8640`. Ground
truth asked: retail input is not NaN.

Ask the port the same two words, in one build,
before any `NAN_CHECK` skip/allow.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc / transform / extract jal,
disable `NAN_CHECK`, or add a wait/slot guard.

## Competing hypotheses and discriminator

IEEE single: NaN iff `(w & 0x7F800000)==0x7F800000 && (w & 0x007FFFFF)!=0`.
Join on 640 cinematic (`0x00696100`/`0x00696600`).
Always-log NaN; rate-limit finite.

- `H-PortExtractAlreadyNaN`: `[vec3-word-ctl]` fires
  at 640/`0x00696100`; extract `w_a1p20` is NaN bits
  (port source already bad before orthonormalize).
- `H-PortOrthonormalizeMakesNaN`: extract `w_a1p20`
  finite; first-cross `w_a2p8` / f10.u32l is NaN
  (orthonormalize rewrote dest+0x14 to NaN).
- `H-PortF10NotMemWord`: first-cross MEM_W($a2,8)
  finite but f10.u32l is NaN (reload/FPR split).
- `H-PortNoNaNThisPair`: both arms complete or
  640-stall with 0 NaN rows (abort class missed;
  enqueue soak, do not conclude port-finite).

Positive controls: `[vec3-word-ctl]` at 640
including origin `0x00696100`; printed `w=` on
extract and on first-cross (`ra` in
`{0x80059F3C,0x80059F40}` delay-slot). A NaN
always-log is the abort-class control.

## Exact commands

One rebuild. Add diagnostic fprintf only (same
`ROGUESQ_LOG_CUTSCENE_A2_50` / `ROGUESQ_LOG_ALL`
gate as heap0). Put the insert in
`tools/fixup_game_funcs.py` if that script still
owns these sites; otherwise the established
cinematic-probe pattern is a hand-instrument of
generated C (do not put load-bearing logic there).

1. `../N64Recomp/RecompiledFuncs/funcs_13.c` after
   `0x80059D48` `ctx->f0.u32l = MEM_W(ctx->r5, 0X20);`
   log site=extract a0/a1/w=f0.u32l ieee.
2. `../N64Recomp/RecompiledFuncs/funcs_4.c` after
   `0x8001954C` `ctx->f10.u32l = MEM_W(ctx->r6, 0X8);`
   and BEFORE `NAN_CHECK(ctx->f2.fl); NAN_CHECK(ctx->f10.fl);`
   log site=cross a0/a1/a2/ra w_mem=MEM_W($a2,8)
   w_f10=f10.u32l ieee. First-cross =
   `ra` in `{0x80059F3C,0x80059F40}`.
3. Catalog `[vec3-word]` / `[vec3-word-ctl]` in
   `docs/debug-trace-env-vars.md` on the
   `ROGUESQ_LOG_CUTSCENE_A2_50` row.
4. cmake Debug RogueSquadron64Recomp.
5. Same-build concurrent 90s SIGKILL:

    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 \
      ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1 \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh \
      s2179_on 30 12

    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=0 \
      ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1 \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh \
      s2179_off 30 12

Table to `scratch/agent/s2179_vec3_word_port.txt`.
If neither arm aborts and NaN n=0, enqueue a
`=1` soak (do not select port-finite).
