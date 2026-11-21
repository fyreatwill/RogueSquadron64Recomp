#!/bin/zsh
# s7752: build the offline port-ucode task replay (harness) and the angrylion task renderer (rdp_render).
# harness links the live build's factor5_ucode_lean.cpp.o, so rebuild the game first after any ucode fixup edit.
set -e
R=${0:A:h:h:h}; O=${0:A:h}
c++ -std=c++20 -O1 -c $O/harness.cpp -o /tmp/s7752_h.o
c++ /tmp/s7752_h.o $R/build/CMakeFiles/RogueSquadron64Recomp.dir/src/rsp/factor5_ucode_lean.cpp.o -o $O/harness
A=/tmp/s7752_alp; [[ -f $A/n64v16.o ]] || zsh $R/tools/angrylion_replay/build16.sh $A >/dev/null
clang -O2 -I$A/alp/core -I$A/alp $O/rdp_render.c $A/n64v16.o $A/par16.o -lc++ -o $O/rdp_render
echo built $O/harness $O/rdp_render
