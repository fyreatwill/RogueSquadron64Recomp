# NEXT work unit (s1143)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Apply the smallest input correction identified in s1142: make the companion
symbol input emit `npcPowerGeneratorUpdate` at `0x80077AF0` in the main `.text`
section, then run the required regeneration chain and verify the split. Do not
hand-edit generated C and do not run the game in this work unit.

```sh
rg -n 'npcPowerGeneratorUpdate|80077AF0' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py
cd /Users/williambuckley/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
objdump -t /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf | rg -i '80077ac0|80077af0|80078e3c'
rg -n 'void npcPowerGeneratorUpdate|void forwardToNpcGeneratorSpawn|80077AF0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_18.c
```

Expected discriminating outcomes:

- PASS: ELF shows `forwardToNpcGeneratorSpawn` size `0x30` and a distinct
  `npcPowerGeneratorUpdate` symbol at `0x80077AF0`; generated C has two host
  functions. This validates the input correction.
- FAIL: ELF still omits `0x80077AF0`; the source ownership/input fix was not
  applied or `make_elf.py` still rejects it. Stop before running the game and
  inspect only that mapping.
