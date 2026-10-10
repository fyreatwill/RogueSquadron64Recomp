# NEXT: M3 idiom audit of musyxSynthFrame list walks
HYPOTHESIS-ID: m5-audio-destub
Generated code: /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c (musyxSynthFrame vram 0x8009123C size 0x660; walk at 0x80091368..0x80091380 is a countdown list, head lw -0x6650(0x8015)).
Unit: grep-enumerate every `lw next` + deref loop in musyxSynthFrame/musyxMixActiveVoices, classify each, and add a log-only "next outside 0x80000000..0x80800000" probe at 0x80091378 (positive control: a probe with range 0..~0 must fire) that records the node address and the previous node, to name the corrupt-link writer. Do not re-run s4553 arms.
