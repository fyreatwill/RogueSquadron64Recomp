#!/bin/zsh
# s7642 class TS: TSan witness binary over ALL of RT64 (rt64.a non-shader TUs) + plume (libplume.a). Shader blob .c files are
# data only and stay uninstrumented. Output: build/RogueSquadron64Recomp_tsan2. Never replaces the real binary.
set -e
R=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp; B=$R/build; T=$R/scratch/s7642/obj; mkdir -p $T
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
python3 - "$B" "$T" > $T/cmds.txt <<'P'
import json,sys,re,os
B,T=sys.argv[1:3]
for e in json.load(open(B+'/compile_commands.json')):
    d=e['directory']; c=e['command']; o=c.split(' -o ')[1].split()[0]
    lib=None
    if d==B+'/rt64' and o.startswith('CMakeFiles/rt64.dir/src/'): lib='rt64'
    elif d==B+'/rt64/src/contrib/plume': lib='plume'
    if not lib: continue
    out=f"{T}/{lib}/{os.path.basename(o)}"
    c=c.replace(' -o '+o, ' -fsanitize=thread -o '+out)
    print(f"cd {d} && {c}")
P
mkdir -p $T/rt64 $T/plume
echo "TUs: $(wc -l < $T/cmds.txt)"
rm -rf $T/cmd; mkdir -p $T/cmd; split -l 1 $T/cmds.txt $T/cmd/c_
ls $T/cmd/c_* | xargs -P 8 -n 1 sh
cp $B/rt64/rt64.a $T/rt64.a; cp $B/rt64/src/contrib/plume/libplume.a $T/libplume.a
(cd $T/rt64 && ar r $T/rt64.a *.o) ; (cd $T/plume && ar r $T/libplume.a *.o); ranlib $T/rt64.a $T/libplume.a 2>/dev/null || true
echo "replaced rt64=$(ls $T/rt64/*.o | wc -l) plume=$(ls $T/plume/*.o | wc -l)"
L=$(cat $B/CMakeFiles/RogueSquadron64Recomp.dir/link.txt)
L=${L//rt64\/src\/contrib\/plume\/libplume.a/$T/libplume.a}
L=${L// rt64\/rt64.a / $T/rt64.a }
L=${L/-o RogueSquadron64Recomp /-fsanitize=thread -o RogueSquadron64Recomp_tsan2 }
(cd $B && eval $L)
ls -la $B/RogueSquadron64Recomp_tsan2
