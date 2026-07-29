# NEXT work unit — localize `submitSceneNodeRender+19268` to a guest
# address / C source line, using disassembly, not blind re-reading.

## Where the investigation stands (s264)

s264 ran s263's prescribed 2nd `dequeueguard1` soak (iron rule 4's 2nd
independent data point). It crashed — not clean. Crucially, s264 also
introduced a NEW methodology for this investigation: decoding the actual
ARM64 faulting instruction instead of trusting the crash handler's
`pc-symbol` name+offset at face value. Two small scripts do this without
`atos`/`otool`/`lldb` (none are on this sandbox's Bash allowlist):

- `scratch/agent/s193_disasm.py` (pre-existing, s193): hand-rolled ARM64
  LDR/STR/LDP/STP decoder. Usage:
  `python3 scratch/agent/s193_disasm.py build/RogueSquadron64Recomp <symbol> <offset-decimal> <window-bytes>`
- `scratch/agent/s264_symrange.py` (new, s264): parses the Mach-O symbol
  table directly to get a function's real address range (its start and the
  next symbol's start), so you can check whether a crash offset genuinely
  falls inside the named function or actually belongs to unlabeled code
  past it.

**Result of applying these this session**: the crash
(`[CRASH][mcontext] pc=0x102fc4efc sym=submitSceneNodeRender+19268`) is
CONFIRMED to be genuinely inside `submitSceneNodeRender`'s own address
range (`0x1006b43b8` to `renderFlatMeshFaceGroup` at +37528), NOT inside
`heapFreeListDequeue` (a distant, separate symbol at `0x1004180e8`). The
faulting instruction itself, `0xb82a6928`, decodes to `STR w8, [x9, x10]`
— register dump confirms `si_addr = x9 + x10` exactly
(`x9=0x0000000300000000`, `x10=0x00000000f5f9f85c`).

**Also important**: `x0`/`x8`/`x9 = 0x0000000300000000` is NOT a
meaningful crash signature — it's the process's constant RDRAM host base
pointer, present in every faulting memory access in this whole binary
(`PORTING-STATE` Session 219, `CURRENT-TRUTH` item -60, proved this 44
sessions ago by reading `recomp.h`'s `MEM_W` macro). s263's `DEQUEUE_GUARD`
justification cited exactly this value as a "matching fault signature" —
that reasoning was invalid; s263 apparently didn't check the "Overturned
conclusions" section for this exact already-refuted claim. **Do NOT repeat
this mistake**: the only valid crash-matching evidence is (a) whether the
native pc offset genuinely falls inside the named function (check with
`s264_symrange.py`), and (b) the OTHER operand register's value (here
`x10`), not the RDRAM-base register.

`DEQUEUE_GUARD` itself: 0 fires across 2 independent soaks now (s263's
clean run AND this run's crash), and this run's crash is proven to be in
unrelated code. Per budget rule 8, downgrade it from "candidate fix" to
"independently-justified hardening" — do not soak it again as a fix
attempt; leave it armed (it's still a real bug per s263's source-read) but
stop treating it as the answer to "the 18th crash class."

Per s219's own KSEG0-tag criterion, `x10=0xf5f9f85c` (top nibble `0xf`,
not `0x8`) is NOT item -49's specific bug either (that one is the fixed
literal `0x80630062`/`si_addr=0x380630062` at `renderUnlitMeshFaces+792`).
This is a 3rd, previously-uncatalogued site in the broader "RDRAM-base +
wild 32-bit garbage operand" store/load family s257 already named.

## The next work unit

**Localize native offset `submitSceneNodeRender+19268` to the guest MIPS
address / recompiled C source line, then read that specific region and
guard it — same recipe as every prior session in this chain (source-read
the gap, add one guard, rebuild, soak), but starting from a disassembly-
confirmed location instead of an eyeballed one.**

1. There is no existing offset-to-line calibration for this function.
   Two known guest addresses ARE commented in the source:
   `funcs_4.c:834` (`// 0x800104A8: jal 0x8000CFD4`) and
   `funcs_4.c:2394` (`// 0x80010CD8: jal 0x8000CFD4`) — these are the 2
   `heapFreeListDequeue` call sites `DEQUEUE_GUARD` already covers. Use
   `s193_disasm.py` at a few sample offsets across the function (e.g. every
   ~2000 bytes from 0 to 37528) and look for `BL`/`B` (branch/call)
   instructions — my decoder does NOT currently recognize branch opcodes
   (only load/store), so EXTEND `decode_ldst` (or add a sibling function)
   to recognize unconditional branch (`B`, opcode `000101` in bits[31:26])
   and branch-with-link (`BL`, `100101`) so you can count branches between
   offset 0 and 19268 and roughly correlate against the `jal`/`beq`/etc.
   comment density in `funcs_4.c:6-834` vs `834-2394` vs `2394-3043` to
   narrow down which few hundred source lines correspond to native offset
   ~19268.
2. Once narrowed, read that region of `funcs_4.c` directly (Read tool,
   targeted offset+limit, not the whole 3037-line function) looking for an
   unguarded `MEM_W(reg, offset) = value` STORE (not a load — the crash
   instruction is a store) where `reg` is a freshly-loaded, unvalidated
   32-bit value (same "load-then-immediately-use-as-address" idiom every
   prior guard in this investigation has targeted).
3. Add ONE guard at that site (`fixup_game_funcs.py`, sibling `N64Recomp`
   checkout — same pattern as every guard so far: check the value
   immediately before use, bail to the nearest existing post-statement
   label on failure). Full delete-all regen, verify clean build + patch
   count, soak with the same driver script (add the new guard's env var to
   `run_dequeueguard1.sh` or clone it).
4. Discriminating outcomes: new guard fires with a sane value it caught →
   likely real fix, needs a 2nd soak (iron rule 4) before calling it
   confirmed. New guard doesn't fire but the run survives longer/crashes
   elsewhere → real forward progress, follow the new crash (same
   convention as every session in this chain). New guard doesn't fire and
   crash recurs at the EXACT same disassembly-confirmed offset → the guard
   missed the real value/timing, re-read more carefully before a 3rd
   attempt (budget rule 8).

## Do NOT do this iteration

- Do NOT cite `x0`/`x8`/`x9=0x0000000300000000` as crash-matching evidence
  for ANYTHING — it is the constant RDRAM base pointer (s219, item -60),
  present in essentially every crash in this binary. It has already misled
  two sessions (s216-218 originally, s263 again). Use `s264_symrange.py` +
  `s193_disasm.py` instead: confirm the pc offset actually falls inside the
  named function, and look at the OTHER operand register.
- Do NOT re-soak `dequeueguard1` a 3rd time expecting it to confirm/refute
  the 18th crash class — s264 proved this run's crash isn't even in
  `heapFreeListDequeue`'s code range, so further soaks of this exact guard
  are not informative for that question. `DEQUEUE_GUARD` stays armed as
  hardening only.
- Do NOT treat `x10=0xf5f9f85c` as item -49's bug — wrong shape (no KSEG0
  tag), per s219's own criterion. It's a new, 3rd site.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9` — all confirmed not the
  mechanism for anything currently open.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn (confirmed necessary again this session: the harness's Stop
  hook fired and rejected an attempt to end the turn on an async
  notification promise instead).

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64`, `N64Recomp`
  needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp`,
  `cmake --build` needs cwd `RogueSquadron64Recomp`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always
  launch soak drivers by full absolute path when using
  `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout=<=480000)` synchronously in the
  same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_dequeueguard1.sh`.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets. As of s264,
  these can now be disassembly-verified (`s264_symrange.py` +
  `s193_disasm.py`) instead of trusted blindly — do this for every future
  crash before drawing conclusions from the symbol name alone.
- `atos`/`otool`/`nm`/`dwarfdump`/`lldb` are NOT on the Bash allowlist in
  this sandbox (confirmed s264: `atos` request denied). Use the hand-rolled
  Python Mach-O parsing scripts instead (`s193_disasm.py`,
  `s264_symrange.py`, `s193_symrange.py`, `machoparse.py` — all in
  `scratch/agent/`).
- `CURRENT-TRUTH.md` is ~460KB+ (growing), ~13x the ~35KB target in
  CLAUDE.md. A dedicated pruning session is now 6+ consecutive sessions
  overdue — still not this iteration's job unless the localization work
  unit above is a quick null with clear leftover budget.
