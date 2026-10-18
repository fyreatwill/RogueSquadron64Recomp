#!/usr/bin/env python3
"""Derive scratch/agent/m6_objc_dump.sh from m6_bp_trans.sh: break on checkComplexObjectives /
setHudEnableBit4 and dump the objective counter table (0x80138060), the words lv0_checkComplexObjectives
reads (0x8010B690..), the float table (0x8010C9F8), the event mask (0x8010C9E0) and the float consts."""
src = open("scratch/agent/m6_bp_trans.sh").read()
src = src.replace(
    'echo "breakpoint set -r requestMissionTransitionMode"; echo "breakpoint set -r beginMissionEndTransition"; echo "breakpoint set -r requestSpeechResponseMode"',
    'echo "breakpoint set -r checkComplexObjectives"; echo "breakpoint set -r setHudEnableBit4"; echo "breakpoint set -r requestMissionTransitionMode"')
src = src.replace('echo "watchpoint set expression -w write -s 4 -- $((ad+0x10CA20))"; ', '')
dumps = "".join('echo "memory read -s4 -fx -c %d $((ad+%s))"; ' % (n, a) for n, a in
                [(16, "0x138060"), (8, "0x10B690"), (8, "0x10C9F8"), (4, "0x10C9E0"), (4, "0xA9554"), (4, "0xA9574")])
old = "echo 'bt 8'; echo 'expression -- (unsigned)ctx->r4'; echo continue;"
assert old in src
src = src.replace(old, "echo 'bt 2'; " + dumps + "echo continue;")
open("scratch/agent/m6_objc_dump.sh", "w").write(src)
