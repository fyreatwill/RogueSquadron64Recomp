# NEXT: reach hangar (VI 512) under default flags
HYPOTHESIS-ID: wild-setcimg-writeback
s4551: early autopilot (3:start,...) reaches title, then arms A/C die at musyxSynthFrame+5436 (parked list-walk onto bad next, s4457) before VI 512. Late autopilot (s4550) never reached 512 in 175 s.
Work unit: run the late-route recipe (scratch/agent/s4550_hangar.sh) with sleep 420 and arms A and C only (B control already positive twice); success = vi_width=512 count >0 in A, then compare odd (s4284-odd) in the 512 phase. If still no 512 or crash at +5436 again, stop the hangar-reach line and go to M5/M3 per the strategic priority list instead.
Outcomes: odd=0 in 512 => closes s4287 Q1; odd>0 => separate hangar writer; no 512 => hangar unreachable without addressing +5436.
