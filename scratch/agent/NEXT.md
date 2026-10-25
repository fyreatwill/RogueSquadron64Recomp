# NEXT: G1d step 45 - anchor HUD x at +0x18 of the element block, find the list-walk consumer
HYPOTHESIS-ID: g1d-widescreen
s6152: element block x/y = +0x18/+0x1C (scale = +0x24/+0x28); initHudStruct is a message-switch handler (a1 = msg 1..12, table 0x800A6458).
Work unit: (1) offline: read buildHudAmmoReadout (0x800B8380) and updateMenuPerFrame (0x800BB8B4/0x800BB918) and readers of list head *(s4)+8 to find the draw-time consumer. (2) Add a fixup-script hook that adds aspect_shift*side to the float at element+0x18 (side by x<160) at the position stores 0x800C01B4 etc. and at the consumer; positive control: ring+disc+ally+counter all shift in one 16:9 lvl1 frame vs scratch/agent/m6/s6149b baseline. Re-verify the +0x18 claim with a mark-arm (ROGUESQ_HUD_MARKPC at pc 800c01b4) before building on it.

s6153 update: offline scan found no float-pair HUD consumer (see PORTING-STATE s6153). Next: add a load-side hook (or lldb read watchpoint on one element x address, e.g. radar disc) in a single flight run to get the reader PC, then anchor there. Positive control: watch on a known-read address fires.
HYPOTHESIS-ID: g1d-widescreen
