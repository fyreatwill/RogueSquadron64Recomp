# NEXT: G1d step 24 - parameterise the 8 MB pointer-range guards (RS64_RAM_TOP)
HYPOTHESIS-ID: g1d-widescreen
Known (s6131): 12 MB pool is built (head 0x80B20000); crash = our own `< 0x80800000u` guards (1011 in funcs_*.c, 442 in funcs_3.c; 28 tools/*.py; ~107 in src/main) treating >8 MB pointers as NULL.
Hypotheses: H-guards (lifting all bounds lets OSMEM=12 boot), H-more (further 8 MB assumptions: 0x7FFFFF masks, RT64/ucode addresses, game's own 24-bit DL masks) appear after.
Work: add `extern uint32_t rs64_ram_top;` + `#define RS64_RAM_TOP rs64_ram_top` to a header all funcs include, define it in recomp.cpp (default 0x80800000, = 0x80000000+mb*1MB after ROGUESQ_OSMEM_MB), then sed `0x80800000u`->`RS64_RAM_TOP` inside tools/fixup_game_funcs_vendored.py's final pass (and the tools/apply_*.py generators that emit it, 28 files; also fix s6098 walk bound). Regen order make_elf->N64Recomp->fixup->cmake. lib/ edit => export.sh + commit.
Test: env XENV_EXTRA="ROGUESQ_OSMEM_MB=12 " HOLD_S=15 LEVEL=1 TAG_SUFFIX=x zsh scratch/agent/g1_level_coverage_common.zsh (control: OSMEM unset still boots). Then 21:9 at 12 MB.
