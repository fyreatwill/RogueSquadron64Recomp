# NEXT work unit (s2475) — patch the generator gap at the traverseSceneGraph→converter callsite

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

The multi-session caller-boundary walk (s2466–s2473) traced the zero `r31` to:
- Runtime zero-initializes `recomp_context ctx{}` in `run_thread_function`; no
  `r31` init, no `thread_create_callback` registered for this game.
- The JAL at `0x800155E4` in `traverseSceneGraphRecursive` calls
  `convertMat3x4ToN64Mtx` but the generator lowered it WITHOUT writing
  `ctx->r31 = 0x800155EC` (the PC+8 return address). The continuation is
  modeled as host control flow only (`after_4:`).
- The converter's first body instruction (`0x80018D84: addu $t9, $ra, $zero`)
  copies `ctx->r31` into `ctx->r25`, and the terminal instruction dispatches
  via `LOOKUP_FUNC(ctx->r25)`. A zero `ctx->r31` → `get_function(0)` → abort.

This is a generator convention gap: the generator never writes `ctx->r31` for
direct JAL calls (return semantics are host-only). The converter body depends
on the guest `$ra` value, so it requires the callsite to explicitly write
`ctx->r31` before the call.

WRITER: JAL at `0x800155E4` in `traverseSceneGraphRecursive`.
LEGITIMATE VALUE: `0x800155EC` (the MIPS PC+8 return address the JAL would
have placed in `$ra` in retail). This is not a mitigation — it is the correct
return address the JAL must supply.

## Competing hypotheses

- H-GeneratorGap: The generator never writes `ctx->r31` for direct JAL calls.
  The fix is a `fixup_game_funcs.py` patch adding
  `ctx->r31 = 0x800155EC;` immediately before the converter call at
  `funcs_4.c:~21451`. This allows the converter to dispatch back to the correct
  continuation in `traverseSceneGraphRecursive`, and the pre-target abort is
  resolved.
- H-DelaySlotExplanation: The delay slot at `0x800155E8` has an instruction
  that modifies the return address register (e.g., `move $ra, $t5`) and that
  explains why the generator did NOT write a conventional `ctx->r31`. If so,
  the legitimate value is whatever the delay slot would produce, not `0x800155EC`.
- H-WrongContinuation: Writing `ctx->r31 = 0x800155EC` is correct but the
  converter dispatches to `traverseSceneGraphRecursive`'s `after_4:` only once;
  subsequent uses of `ctx->r31` elsewhere in the call chain pick up
  `0x800155EC` and cause a different abort (H-GeneratorGap selected but
  incomplete; needs additional callsite patches).

## Discriminating measurement

1. **Static: verify the delay slot** — disassemble the two MIPS words at
   `0x800155E4..0x800155EC` from the ROM (or read `funcs_4.c` around line
   21451 to see if there is any `ctx->r31 =` or `ctx->r25 =` in the delay
   slot). If the delay slot modifies `$ra`, H-DelaySlotExplanation is selected.
   If the delay slot is irrelevant (e.g., `nop` or an `$a0` load), H-GeneratorGap
   is confirmed as the sole explanation.

2. **Patch and build** — add `ctx->r31 = 0x800155EC;` in `fixup_game_funcs.py`
   immediately before the converter call. Run the full regen cycle
   (`fixup_game_funcs.py` on the existing generated output then `cmake`/build).
   Run with the established route + `ROGUESQ_LOG_M5_PRETARGET=1`. If the run
   reaches past the converter call without aborting in `get_function(0)`,
   H-GeneratorGap is selected. If a different abort occurs, classify it.

3. **Retain the retail positive control** before trusting any change in port
   behavior. Whole-RDRAM watch must fire (threshold ≥ 10,000 callbacks) and
   VI must reach hangar width 512 at origin `0x006AB400`.

## Commands

```sh
# Step 1: find the exact callsite line in the generated funcs_4.c
cd /Users/williambuckley/Documents/Tools/N64Recomp
grep -n "convertMat3x4ToN64Mtx(rdram, ctx)" RecompiledFuncs/funcs_4.c | head -5
# Read ~5 lines before/after that line to see the delay slot in the generated output

# Step 2: check for delay slot ctx->r31 or ctx->r25 write
# If none found, identify the correct return label (after_4 or after_N)
# and confirm 0x800155EC is the right address

# Step 3: add patch to fixup_game_funcs.py (anchor on funcs_4.c near the call)
# Insert: ctx->r31 = 0x800155EC;
# immediately before: convertMat3x4ToN64Mtx(rdram, ctx);

# Step 4: apply fixup + build
python3 fixup_game_funcs.py
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j$(sysctl -n hw.ncpu) 2>&1 | tail -20

# Step 5: oracle (always first)
cd /Users/williambuckley/Documents/Tools/rs64-oracle
mupen64plus --plugin mupen64plus-video-rice.dylib \
  --set "Core[R4300Emulator]=1" \
  --set "Core[SaveState]=0" \
  tools/oracle/rice_hold_start.lua \
  /path/to/rogue_squadron.z64 2>&1 | tee /tmp/oracle_s2475.log

# Step 6: port run (from build/)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build
env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1 \
    ./RogueSquadron 2>&1 | tee /tmp/port_s2475.log &
sleep 60; kill -9 %1 2>/dev/null || true

# Write audit to scratch/agent/s2475_m5_converter_callsite_fix/audit.md
```

## Expected outcomes

- If H-GeneratorGap: the run reaches past the converter call; the pre-target
  abort at `get_function(0)` no longer fires; the resolver positive control
  (`0x8009123C`) still fires; a new (different) boundary may appear.
- If H-DelaySlotExplanation: the delay slot encodes a nonstandard value;
  compute the correct `ctx->r31` to write and repeat.
- If H-WrongContinuation: the converter dispatches correctly once but a
  different abort appears; document the new boundary.

In all cases: retail whole-RDRAM control must pass; no audio gate, output
remap, task-data, or dispatch change is authorized beyond this callsite patch.

ORIGIN (for the patch):
Writer = JAL at virtual address 0x800155E4 in traverseSceneGraphRecursive.
Legitimate value = 0x800155EC (PC+8, the standard MIPS JAL link register value).
This is not a guard or mitigation — it writes the correct return address that
the recompiler convention omits for direct JAL-to-named-function calls.
