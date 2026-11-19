#!/bin/zsh
# s7643 class TS-2: TSan witness binary over the HOST runtime: libultramodern.a, liblibrecomp.a (incl. o1heap) and every
# RogueSquadron64Recomp.dir object (src/main, src/rsp, imgui metal backend), PLUS the s7642 rt64/plume tsan archives
# (run tools/s7642_tsan_rt64_build.sh first). factor5_ucode (generated RSP ucode) and RecompiledFuncs/PatchesLib (guest code)
# stay plain. Output: build/RogueSquadron64Recomp_tsan3. Never replaces the real binary.
set -e
R=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp; B=$R/build; T=$R/scratch/s7643/obj; P=$R/scratch/s7642/obj; mkdir -p $T
[[ -f $P/rt64.a && -f $P/libplume.a ]] || { echo "missing s7642 tsan rt64/plume archives"; exit 2; }
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
python3 - "$B" "$T" > $T/cmds.txt 2> $T/map.txt <<'P'
import json,sys,os
B,T=sys.argv[1:3]
for e in json.load(open(B+'/compile_commands.json')):
    d=e['directory']; c=e['command']; o=c.split(' -o ')[1].split()[0]
    lib=None
    if d==B+'/N64ModernRuntime/ultramodern' and o.startswith('CMakeFiles/ultramodern.dir/'): lib='ultramodern'
    elif d==B+'/N64ModernRuntime/librecomp' and o.startswith('CMakeFiles/librecomp.dir/'): lib='librecomp'
    elif d==B and o.startswith('CMakeFiles/RogueSquadron64Recomp.dir/') and '/factor5_ucode/' not in o: lib='main'
    if not lib: continue
    out=f"{T}/{lib}/{os.path.basename(o)}"
    c=c.replace(' -o '+o, ' -fsanitize=thread -o '+out)
    print(f"cd {d} && {c}")
    if lib=='main': print(f"{o} {out}",file=sys.stderr)
P
rm -rf $T/ultramodern $T/librecomp $T/main; mkdir -p $T/ultramodern $T/librecomp $T/main
echo "TUs: $(wc -l < $T/cmds.txt)"
rm -rf $T/cmd; mkdir -p $T/cmd; split -l 1 $T/cmds.txt $T/cmd/c_
ls $T/cmd/c_* | xargs -P 8 -n 1 sh
cp $B/N64ModernRuntime/ultramodern/libultramodern.a $T/libultramodern.a; cp $B/N64ModernRuntime/librecomp/liblibrecomp.a $T/liblibrecomp.a
(cd $T/ultramodern && ar r $T/libultramodern.a *.o); (cd $T/librecomp && ar r $T/liblibrecomp.a *.o)
ranlib $T/libultramodern.a $T/liblibrecomp.a 2>/dev/null || true
echo "replaced ultramodern=$(ls $T/ultramodern/*.o | wc -l) librecomp=$(ls $T/librecomp/*.o | wc -l) main=$(ls $T/main/*.o | wc -l)"
L=$(cat $B/CMakeFiles/RogueSquadron64Recomp.dir/link.txt)
L=${L//rt64\/src\/contrib\/plume\/libplume.a/$P/libplume.a}
L=${L// rt64\/rt64.a / $P/rt64.a }
L=${L// N64ModernRuntime\/librecomp\/liblibrecomp.a / $T/liblibrecomp.a }
L=${L// N64ModernRuntime\/ultramodern\/libultramodern.a / $T/libultramodern.a }
while read o out; do L=${L// $o / $out }; done < $T/map.txt
L=${L/-o RogueSquadron64Recomp /-fsanitize=thread -o RogueSquadron64Recomp_tsan3 }
print -r -- "$L" > $T/link_cmd.txt
(cd $B && eval $L)
ls -la $B/RogueSquadron64Recomp_tsan3
