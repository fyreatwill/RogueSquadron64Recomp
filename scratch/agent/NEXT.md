# NEXT work unit — VI-mode stall: identify osViSetMode(1024) caller

HYPOTHESIS-ID: m5-vi-mode-stall

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

1. Identify the retail osViSetMode physical address:
   From the oracle README, watch VI_WIDTH_REG physical address 0x04400008 for
   writes. The PC attributing the write that changes width to 1024 is the
   osViSetMode body. Alternatively use the oracle's -watchpc on the known
   retail PC for osViSetMode from an existing MAP file.

2. Run the oracle:
   ```
   cd tools/oracle && python3 run_oracle.py \
     --watch-write 0x04400008 \
     --positive-rdram \
     --plugin rice \
     --timeout 90 \
     2>&1 | tee /tmp/retail_osvisetmode.log
   ```
   Expected: see at least one write with value=1024 at ~45s. The writing PC
   is the retail osViSetMode body (or its inlined caller).

3. Run port capture concurrently:
   ```
   cd build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
     ROGUESQ_AUTOPILOT=1 \
     timeout 90 ./RogueSquadron64Recomp ROM.z64 \
     2>&1 | grep "\[osViSetMode" > /tmp/port_osvisetmode.log
   kill %1
   ```

4. Compare: grep /tmp/port_osvisetmode.log for width=1024. Count total calls
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
