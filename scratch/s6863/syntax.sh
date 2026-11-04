#!/bin/zsh
cd "$(dirname "$0")/../.."
F=build/CMakeFiles/RecompiledFuncs.dir/flags.make
D=$PWD/../N64Recomp/scratch_s6863_replay; O=$PWD/scratch/s6863
grep -E '^C_(FLAGS|DEFINES|INCLUDES) *=' $F | sed 's/^[^=]*= *//' | tr '\n' ' ' > $O/cc.rsp
echo " -I$D -fsyntax-only -w" >> $O/cc.rsp
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
mkdir -p $O/syn; rm -f $O/syn/*
cat > $O/one.sh <<'X'
#!/bin/zsh
f=$1; b=${f:t}; cc @$2/cc.rsp $f > $2/syn/$b.out 2>&1; echo "$? $b" >> $2/syn/rc.txt
X
cp $D/funcs_0.c $O/ctl_broken.c; echo 'this is not C;' >> $O/ctl_broken.c
ls $D/*.c $O/ctl_broken.c | xargs -P 6 -n1 -I{} zsh $O/one.sh {} $O
echo "files $(wc -l < $O/syn/rc.txt)  nonzero $(grep -vc '^0 ' $O/syn/rc.txt)"; grep -v '^0 ' $O/syn/rc.txt | head
grep -h -E 'error:' $O/syn/*.out | sed 's/.*scratch_s6863_replay.//' | cut -c1-180 | head -20
