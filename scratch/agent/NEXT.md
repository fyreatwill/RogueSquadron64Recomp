# NEXT (s7491)
HYPOTHESIS-ID: m3-store-path-coverage

Step 0 note: CURRENT-TRUTH is ~59.4 KB, close to the 60 KB maintenance trigger. Check wc -c first.

Fold first: soak s7490_zmemcpy_levels (L1 dd8 21:9, L7/L10/L12 dd4; tools/s7490_zmemcpy_recipe.zsh on the build with the PatchesLib hooks).
score=0 + zplant DETECTED on all arms -> EO host-memcpy CLOSED for 6 levels. Also grep the logs for rows with fn=rs64_find_body: any
uaf-store/uaf-load/slack-store row there is the first in-flight datum from the DL-finder patch hooks (loc=F/R = real; chase it).

Work unit (class EP, the last host-store class): OS-call host stores through guest pointers (census Part B, tools/s7490_hostwrite_census.py):
osRecvMesg *msg out + mq fields, osSendMesg/JamMesg msg slot, osCreateMesgQueue, osContGetReadData/Query/Init pad structs, save_read
(pi.cpp:359), IoMesg (pi.cpp:722), osCreateThread OSThread fields.
1. Route each through rs64_s7475_store (as s7490 did for zmemcpy, fn=os_<name>) behind the bitmap test. Most sites are under lib/
   (ultramodern mesgqueue.cpp, librecomp cont.cpp/pi.cpp): run ./submodule-patches/export.sh and commit the patches in the same session.
2. Control: a ZPLANT-style plant on the msg-out pointer of the next osRecvMesg whose destination is inside a live canary block.
3. Rerun tools/s7490_zmemcpy_recipe.zsh style, LV="4:4 15:8" HOLD=220.
Hypotheses: H-ep-clean (no OS-call store lands in a free block) / H-mesg-uaf (a freed message buffer or queue is written by the host
scheduler) / H-ep-none (every Part B destination is static .bss: then say so with a destination-range histogram and close).
If EP closes clean, the M3 heap-audit store/load series is DONE: take the ITERATION 3c ladder's next rung.
