# Next work unit: name the writer of the garbage SetColorImage words (s4271)

HYPOTHESIS-ID: m5-audio-destub-sequence

Context (s4270): RT64's tracked fb set growth is garbage colour-image sets starting t=14.09 s (hangar entry): odd widths 1..1217, unaligned addrs (0x001CFFFF, 0x002C0395, 0x0068A2A6...). Sane before. Retail fbs: 320x224/640x480/640x340 at aligned addresses.

Hypotheses:
- A: the F5 LLE ucode emits these (inline-data pointer advance / DL walk mismatch, per docs/F5-UCODE-REFERENCE.md).
- B: our RDP front end (RT64 rdp / LLE bridge) misparses a valid command.
- C: the DL in RDRAM itself is corrupt (a guest writer, port-only).

Discriminating measurement (ONE build, ONE run): at the first creation with an address not 8-byte aligned (FramebufferManager::get() callers, rt64_state.cpp:1224), dump the raw 64-bit RDP words (+/-8 around the SetColorImage), the DL/RDP source address and task ordinal. Control: the same dump of the first sane SetColorImage (t~0) must show a well-formed word. Then compare with the oracle (tools/oracle/README.md) at hangar entry.
Outcomes: garbage word present in the RDP buffer at an aligned position -> ucode/DL producer (A or C: check RDRAM DL source for the same bytes); RDP buffer fine but decoded wrongly -> B.
Run: env-prefixed, from build/, SIGKILL ~20 s; scratch/agent/s4270_fbnames.sh is the template. Any lib/ edit => export.sh + commit.
