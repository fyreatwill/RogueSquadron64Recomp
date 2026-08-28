# NEXT work unit — restore oracle prerequisites for VI-mode discriminator

HYPOTHESIS-ID: m5-vi-mode-stall

## Single work unit

Build or install the debugger-enabled mupen64plus core and Rice video plugin
required by `tools/oracle/README.md`, then rerun the retail-vs-port VI-mode
discriminator. Do not add another port instrument until the retail arm has a
positive whole-RDRAM control and reaches title/hangar.

## Competing hypotheses after prerequisites are repaired

- H-TitleOsViNotCalled: retail calls `osViSetMode(1024)` but the corresponding
  port caller never executes.
- H-TitleOsViCalledWrongMode: the caller executes in port but supplies a mode
  whose width is not 1024.
- H-TitleOsViSuppressed: port logs a width-1024 call but the VI register is
  blocked or overwritten before route preparation.

## Discriminating measurement

One oracle run and one port run, with all controls armed. The oracle must
show whole-RDRAM positive-control hits, VI 640→1024, and the writer PC for
the width-1024 VI-register change. The port must show its complete
`osViSetMode` call table, including caller/site and width. Retail width-1024
plus port zero width-1024 selects H-TitleOsViNotCalled; the same caller with a
wrong port width selects H-TitleOsViCalledWrongMode; a port width-1024 call
without the corresponding VI transition selects H-TitleOsViSuppressed.

## Background

Session 3054 (checkpoint) established from the s3053 run.log that the port
issues exactly 4 osViSetMode calls in a 30-second AUTOPILOT run:
  - #1  line 42:   width=320  site=initVideoSubsystem
  - #2  line 1242: width=2    site=swapBufferWithViMode (corrupt data)
  - #3  line 1249: width=640  site=initVideoSubsystem
  - #4  line 1342: width=640  site=applyPendingViChanges

The game never calls osViSetMode(width=1024). The route predicate at
`src/main/main.cpp:1376–1380` fires only when `rs64_vi_committed_width()==1024`
(title) or `==512` (hangar). Older successful runs confirm "vi_width=1024
(was 640) origin=0x00790400 at 45.3s" is the correct title transition.
All sessions 3040–3053 returned H-MeasurementInsufficient because the route
predicate is structurally unreachable without the 1024 VI mode.

## Competing hypotheses

- H-TitleOsViNotCalled: the retail caller of osViSetMode(1024) never executes
  in port AUTOPILOT runs — the game state machine stalls upstream.
- H-TitleOsViCalledWrongMode: the caller executes in port but passes a mode
  struct whose comRegs.width ≠ 1024 (mode pointer or struct corruption).
- H-TitleOsViSuppressed: the call is made correctly but the VI register write
  is blocked or overwritten before the route reads it.

## Discriminating measurement

One retail oracle run + one port AUTOPILOT run, concurrently:

**Retail oracle:**
Use the mupen64plus oracle (`tools/oracle/README.md`). Watch physical addresses
for the osViSetMode function entry (identify from the retail MAP or by watching
VI_WIDTH_REG writes at 0x04400008 in the RDRAM-mapped I/O). Arm the
whole-RDRAM positive control. The target is the execution PC immediately before
VI_WIDTH_REG becomes 1024 in retail. Log all executions of that watch,
recording caller + VI width argument. Use Rice plugin.

**Port:**
`osViSetMode_recomp` already logs unconditionally; run a 90-second AUTOPILOT
capture and count: how many osViSetMode calls fire, and are any width=1024?
Also log the `site` (caller symbol) field already present in the output.

**Comparison table (one row per osViSetMode call):**
| runtime | call# | width | site/caller |
|---------|-------|-------|-------------|
Retail: expected 1024 call near t=45s.
Port: expected 0 calls with width=1024 (per s3053 data).

H-TitleOsViNotCalled is selected if retail shows ≥1 width=1024 call and port
shows 0; this rules out H-Suppressed (call never made, so suppression is
moot). H-TitleOsViCalledWrongMode is selected if port shows a call from the
same site as retail but with wrong width. H-TitleOsViSuppressed is selected if
port shows a width=1024 call but the VI register doesn't update.

## Exact next commands

1. From the repo root, repair the documented oracle dependencies:
   ```
   tools/oracle/build_core.sh
   tools/oracle/build.sh
   ```
   Confirm the debugger-enabled core and Rice plugin paths before running.

2. Identify the retail osViSetMode physical address:
   From the oracle README, watch VI_WIDTH_REG physical address 0x04400008 for
   writes. The PC attributing the write that changes width to 1024 is the
   osViSetMode body. Alternatively use the oracle's -watchpc on the known
   retail PC for osViSetMode from an existing MAP file.

3. Run the oracle:
   ```
   tools/oracle/build/rs64_oracle \
     --core <debugger-enabled-libmupen64plus.dylib> \
     --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
     --secs 90 \
     --watch-write 0x0:0x800000 \
     --watch-write 0x04400008:0x0440000c \
     --vi-trace \
     --video <mupen64plus-video-rice.dylib> \
     --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
     > /tmp/retail_osvisetmode.log 2>&1
   ```
   Expected: the whole-RDRAM watch fires, and at least one VI-register write
   changes width to 1024. The writing PC is the retail osViSetMode body (or
   its inlined caller).

4. Run port capture concurrently:
   ```
   cd build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
     ROGUESQ_AUTOPILOT=1 \
     ./RogueSquadron64Recomp > /tmp/port_osvisetmode.log 2>&1
   ```
   Run it under a watchdog that sends SIGKILL after 90 seconds, then:
   ```
   grep "\[osViSetMode" /tmp/port_osvisetmode.log
   ```

5. Compare: grep /tmp/port_osvisetmode.log for width=1024. Count total calls
   and widths. Compare against retail.

## Exit criterion

The work unit is done when the comparison table has at least one retail
osViSetMode(1024) observation with PC attribution, and the port log shows
the call count + width distribution. This selects exactly one of the three
H-... hypotheses above.

## Iron rules for this unit

- Retain the whole-RDRAM positive control in the oracle run.
- Do not re-run the DP-event, ProducerMark, or action-order watches —
  those are downstream of the stall and give no new information.
- The osViSetMode_recomp logging is already unconditional; no build needed
  for the port capture.
- If a build IS needed for oracle instrumentation, follow make_elf.py →
  N64Recomp → fixup_game_funcs.py → cmake before running.
