# NEXT (s7557)
HYPOTHESIS-ID: class-gq-default-on-levers

GP CLOSED s7556 (tools/s7556_gp_census.py rc 0, controls 9/9): every guest time consumer uses the host unit; FPS60 dt linear.
GQ asks: does every DEFAULT-ON behaviour change the port makes to the game (env lever read with a `!(e && e[0]=='0')`-style
default, or an unconditional fixup) have (1) a working =0 retail switch, (2) a row in docs/OWNER-OPT-INS.md or CURRENT-TRUTH
naming it, and (3) a qualifying session? Owner rule: no default flips without the owner - a default-on lever nobody listed is
exactly what the owner cannot see.
Static census, tools/s7557_gq_census.py:
- enumerate every getenv("ROGUESQ_*") under src/, lib/N64ModernRuntime/*/src, lib/rt64 patches and tools/fixup_*.py emitted code;
  classify the default from the parse expression (on when unset / off when unset / value default), and whether it changes guest-
  visible state (guest RAM write, control flow of generated code, RDP/present output) or is diagnostic-only (log/counter).
- join each default-on behaviour lever with docs (OWNER-OPT-INS.md, CURRENT-TRUTH, FPS60-FIXES.md) and with PORTING-STATE (grep
  the name for the qualifying session).
Hypotheses: H-listed (every default-on behaviour lever has =0 + a doc row + a session) / H-unlisted (a default-on lever with no
doc row: list it for the owner) / H-no-switch (a default-on change with no =0 path: add one).
Controls (--controls): planted default-on getenv with no doc row -> H-unlisted; planted diag-only getenv -> not a lever; planted
lever whose =0 branch is missing -> H-no-switch; coverage: CULL_SPIKE (default on, owner 2026-10-31) and S7402_CLOCKFIX appear.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
