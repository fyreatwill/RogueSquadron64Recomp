# NEXT: reach hangar (VI 512) under default flags
HYPOTHESIS-ID: wild-setcimg-writeback
s4550: 175 s run, fix arms odd=0, control odd=60 (pre-hangar only; vi_width=512 never logged). Next: find an autopilot/probe.sh key route that logs vi_width=512 (see s4548 probe.sh), rerun s4550_hangar.sh with that route + default vs control; odd>0 in default hangar => separate hangar writer.
