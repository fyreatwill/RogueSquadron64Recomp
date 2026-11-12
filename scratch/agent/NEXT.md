# NEXT (s7210): field-mode census — which screens draw with the RDP scissor field bit, and is each presented as model G?
HYPOTHESIS-ID: field-mode-census
Context: s7209 closed Elite Rogues (4:3): RT64 ignores the Set Scissor field/odd bits (drawCall.scissorMode read only by the debugger),
so it presents a progressive render (angrylion NOFIELD=1 replay, model G) instead of the hardware weave. Unknown: whether any OTHER
screen (boot logos, attract, crawls, cutscenes, menus at 16:9 owner recipe) uses field mode, and whether at 16:9 (WIDE paths, 796/1024 fb)
the progressive draw still lines up.
Hypotheses: H-only-ER (Elite Rogues is the only field-mode screen -> census closes the class); H-more-prog (other screens use it and
present as G: same verdict, list them); H-more-break (a field-mode screen at 16:9 presents rows offset/doubled -> G loses, fix).
Discriminator, offline first then ONE run: grep existing .cap streams for Set Scissor (op 0x2D) with w1 bit 25 set (write a tiny
census script over scratch/s7141/*.cap and scratch/s7124/... if any caps remain; else ONE owner-recipe 16:9 boot->menu->L17->ER run
with G5B_FRAME_EVERY=1 FROM=0 and PRESENT_RING), list field-mode swap ranges by cimg/width, replay them NOFIELD, score
tools/s7183_parity.py GDIR=. Disk: 136 GB free, ~20 GB per 3 min capture: keep spans short, delete raws after scoring.
Outcomes: no other field-mode swaps -> H-only-ER, close; G picked with symmetric rows -> H-more-prog, close; G loses -> H-more-break, fix.
