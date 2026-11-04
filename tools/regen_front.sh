#!/bin/zsh
# s6870: make_elf -> N64Recomp into a scratch dir. make_elf sizes every function up to the next symbol, so data after a
# function's real end gets decoded as code; tools/func_sizes.txt feeds N64Recomp the real size through [[input.function_sizes]].
# Never touches the live tree or the sibling repos' files.
# usage: tools/regen_front.sh <out dir> [sizes file]   (sizes file "none": plain ELF sizes, the baseline)
cd "$(dirname "$0")/.." || exit 2
R=$PWD/..; O=${1:A}; Z=${2:-$PWD/tools/func_sizes.txt}
[ -n "$1" ] && [ ! -e "$O" ] || { echo "usage: $0 <new out dir> [sizes file|none]"; exit 2; }
W=$O.work; rm -rf $W; mkdir -p $O $W/build
(cd $R/rogue_squadron64 && cp -R rogue_squadron.z64 symbol_files tools $W/) || exit 2
(cd $W && python3 tools/make_elf.py > make_elf.log 2>&1) || { echo "regen_front: make_elf failed"; exit 1; }
sed -e "s#^elf_path = .*#elf_path = \"$W/build/roguesquadron.elf\"#" -e "s#^output_func_path = .*#output_func_path = \"$O\"#" \
    -e "s#^relocatable_sections_path = \"#relocatable_sections_path = \"$R/N64Recomp/#" $R/N64Recomp/rogue_squadron.toml > $W/cfg.toml
if [ "$Z" != none ]; then
  print 'function_sizes = [' >> $W/cfg.toml
  while read -r n s; do print "    { name = \"$n\", size = $s },"; done < $Z >> $W/cfg.toml
  print ']' >> $W/cfg.toml
fi
$R/N64Recomp/build/N64Recomp $W/cfg.toml > $W/n64recomp.log 2>&1 || { echo "regen_front: N64Recomp failed (see $W/n64recomp.log)"; exit 1; }
echo "regen_front: ok, $(ls $O | wc -l | tr -d ' ') files, $(cat $O/funcs_*.c | wc -l | tr -d ' ') lines"
