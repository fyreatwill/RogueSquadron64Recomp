# NEXT work unit

HYPOTHESIS-ID: cimg-origin-desync

## Why this replaces the freelist-mitigation thread

Sessions 640-659 landed four layers of mitigation for the framebuffer writeback
that stomps the heap freelist — `SKIP_WILD_W`, `SKIP_FL_HDR`, `ALLOW_FL_HDR`,
`FL_HDR_RESTORE`, now an expand-restore/hole-punch in the previous NEXT.md —
without once establishing **why a colour image is set at `0x1F0D74` with
`w=1161 siz=3`**. Every one of those iterations passed the ADVANCED contract.

1161 is not a width this game is known to use; the measured set is 320, 512,
640, 1024 (a render-to-texture target need not match a VI width, so treat that
as suggestive, not conclusive). And per `docs/F5-UCODE-REFERENCE.md` (new),
**no Factor 5 handler in GLideN64's shipped HLE of this microcode computes a
colour-image command at all** — SETCIMG reaches the RDP only as a raw command
passed through from the display list. So nothing in the ucode's own logic is
in the business of producing those operands, and if they are a misread of the
stream, the entire mitigation stack is guarding against our own parse.

Do NOT continue expanding the restore until this is settled.

## Hypotheses

| ID | Claim | Killed if |
|----|-------|-----------|
| H-desync-tri | Our RDP-stream walk mis-steps a variable-length triangle command and reads coefficient data as a SETCIMG | the killer command is present at a command-aligned offset in the raw stream |
| H-desync-inline | Our LLE ucode mis-advances the DL pointer on one of the six inline-data commands (MoveMem +16, TriGen +32, Tri +16 conditional on `w0 & 2`, TexrectGen +16, SetOtherMode_*_EX +8) and emits garbage downstream | the DL PC advance matches the reference table at every command in the failing task |
| H-legit | The retail game really does set a colour image there | (note: the oracle has now shown the game DOES own and write `0x1F3CC0`, so "that memory is spare" is dead. This hypothesis is about the SETCIMG operands, which is a separate question) |

## Discriminating measurements (one build, one run, plus one oracle run)

1. **Raw-stream check.** At the site that decodes the killer SETCIMG, dump the
   64 bytes of RDP stream preceding it plus the byte offset from the last
   known-good command boundary. If the killer sits at a boundary that follows
   an unbroken decode chain, H-desync-tri dies. If the preceding command is a
   triangle, print its computed length against its flag bits.
2. **PC-advance audit.** For one failing gfx task, log every F5 command opcode
   and the DL PC delta our LLE ucode actually takes, and diff against the
   reference table in `docs/F5-UCODE-REFERENCE.md`. Any mismatch is the bug.
3. **Oracle.** `tools/oracle/` runs the retail ROM under mupen64plus with
   memory watches — see its README. It can now be driven into the hangar
   (`--press 6:start,11:start,...,56:start`; hangar = VI 512 @ `0x6ab400`
   from 38.4s, holds for the rest of the run).

   **MEASURED, and it changes this item (2026-08-10, logs in
   `~/Documents/Tools/rs64-oracle/`):**

   - `hangar_fl_hdr.log` — the retail game **DOES write physical `0x1F3CC0`**:
     624 writes over 150 s, first at 26.1 s, from a repeating unrolled
     sequence at PCs `0x800C7F08 / 7F34 / 7F5C / 7F84 / 7FAC / 7FD4 / 7FFC /
     801C`. So that address is live game-owned allocator memory, not spare
     RAM — which means ANY host-side write there (RT64's framebuffer
     writeback) is unambiguously corruption of a structure the game maintains.
   - `hangar_freelist.log` — the surrounding 64 KB takes 3,514,738 writes with
     the hangar schedule.
   - Every earlier "0 hits" result was a PHASE ARTIFACT: undriven runs take
     zero writes in that entire region because they never leave the attract
     loop. Do not cite those nulls.

   **Attribution caveat, learned the hard way here.** Looking `0x800C7FF8` up
   in the decomp gives `playNpcStateChangeEffect`, and
   `tools/overlay_symbol_probe.py` confirms it is a genuine function start —
   *in the mission overlay*. In the menu overlay the same VRAM is not a
   function start at all. Overlays alias these addresses, so a PC is only
   nameable together with the overlay resident at that moment. Naming the
   writer means first establishing residency at t=26.1 s (title phase).

## Outcomes

- **A)** A decode desync is found → fix it, then A/B whether the freelist stomp
  disappears with ALL four mitigation layers off. If it does, delete them.
- **B)** The stream decodes cleanly and the command is really emitted by our
  ucode → the fault is upstream in the recompiled ucode; take H-desync-inline
  to the specific command.
- **C)** Both refuted → the command is game behaviour after all; record that
  explicitly with its evidence, and only then resume mitigation work.

## Standing rules for this work unit

- Positive control before any null (iron rule 1) — that rule caught a false
  negative in the oracle itself on its first run.
- Build all three arms in one iteration (iron rule 13).
- If you land any skip/allow/guard/restore, the session entry needs an
  `ORIGIN:` line (iron rule 11, enforced by the Stop gate).
