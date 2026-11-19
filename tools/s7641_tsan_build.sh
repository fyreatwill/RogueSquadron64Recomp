#!/bin/zsh
# s7641: TSan witness binary. Only plume_metal.cpp is instrumented (both sides of the drawable-index race live there);
# everything else links uninstrumented. Output: build/RogueSquadron64Recomp_tsan. Never replaces the real binary.
set -e
R=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp; B=$R/build; T=$R/scratch/s7641/tsan; mkdir -p $T  # ignored scratch; rerun to rebuild
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
CMD=$(python3 -c "
import json;cc=json.load(open('$B/compile_commands.json'))
print([e['command'] for e in cc if e['file'].endswith('/plume_metal.cpp')][0])")
CMD=${CMD/-o CMakeFiles\/plume.dir\/plume_metal.cpp.o/-fsanitize=thread -o $T/plume_metal.cpp.o}
(cd $B/rt64/src/contrib/plume && eval $CMD)
cp $B/rt64/src/contrib/plume/libplume.a $T/libplume.a
(cd $T && ar r libplume.a plume_metal.cpp.o && ranlib libplume.a 2>/dev/null)
L=$(cat $B/CMakeFiles/RogueSquadron64Recomp.dir/link.txt)
L=${L//rt64\/src\/contrib\/plume\/libplume.a/$T/libplume.a}
L=${L/-o RogueSquadron64Recomp /-fsanitize=thread -o RogueSquadron64Recomp_tsan }
(cd $B && eval $L)
ls -la $B/RogueSquadron64Recomp_tsan
