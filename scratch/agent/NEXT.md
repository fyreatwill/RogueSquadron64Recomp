# NEXT work unit (s1971) — audit generated branch-and-link `$ra` consumers

HYPOTHESIS-ID: mips-link-register-lowering-audit

## What s1970 settled

The complete generated tree has three direct callers of
`filterVoiceSampleBlock`. Static code says its indexed selector read is the
fixed arithmetic `$ra + 0xD4 + $a0`; caller-owned source/output spans are 26
and 40 bytes. The corrected LLE-solo hangar run reached
`updateVoiceChannelParamsLarge` at `0x8009D740` after the hangar controls. The
same-run control fired, source `0x8011C748` and output `0x8011C7B0` were valid,
but the call and callee-entry rows both had `$ra=0`, table `0x000000D4`, and a
SIGBUS followed at the invalid byte read. Static intended link is
`0x8009D748`. H-filter-local-range is selected for this edge; no guard was
added. The first run without the proven LLE-solo environment stalled at 640
and was correctly classified as recipe failure.

## Single next work unit

Audit the whole generated idiom class in which a direct host call is reached
from `bgezal`/`bltzal`, or a callee consumes `$ra` as a data-pointer base.
Enumerate every site in `RecompiledFuncs/`, classify the intended link writer
and the first post-call `$ra` consumer, then build one regeneration-safe batch
probe that records expected link PC, actual `ctx->r31`, callee, and derived
address/range. Do not repair one site or add a skip until the class is
classified.

## Competing hypotheses and discriminator

- **H-link-lost:** N64Recomp's direct host-call lowering leaves `ctx->r31`
  unchanged for link-producing calls. Selecting evidence is multiple
  independent `bgezal`/`bltzal` or `$ra`-consumer sites with actual RA not equal
  to the guest link PC, while their static link writers are valid.
- **H-link-preserved:** the runtime or generated wrapper writes the guest link
  elsewhere, and the filter row is an isolated caller/context anomaly.
  Selecting evidence is every audited site having actual RA equal to its
  guest link or a documented equivalent before its consumer.
- **H-legitimate-data:** a non-link RA value is intentional for a subset of
  calls. Selecting evidence is a site whose static control flow proves the
  value is not used as a guest-PC/data base, while the failing filter site is
  the only range-invalid consumer.
- **H-other-corruption:** RA is correct at the call boundary but changes before
  the consumer, or the derived address is invalid despite a correct RA.
  Selecting evidence is a same-site entry/consumer mismatch with a valid link
  writer.

The discriminator is one static census plus one run carrying every selected
site in one build. Positive controls must include the whole-RDRAM retail oracle
control already established in s1970, the port's hangar phase/control row, and
at least one generated site with a known non-data `$ra` use. A null before
VI=512 is unevaluable.

## Exact commands

Read `tools/oracle/README.md` and `docs/F5-UCODE-REFERENCE.md` before any new
instrument. Enumerate first:

```sh
rg -n -U -g 'funcs_*.c' 'bgezal|bltzal|addu\s+\$at,\s+\$ra|addiu\s+\$[^,]+,\s+\$ra' ../N64Recomp/RecompiledFuncs
rg -n 'jal|bgezal|bltzal|ctx->r31' ../N64Recomp/RecompiledFuncs/funcs_27.c
```

Put the complete site table and probes in `../N64Recomp/fixup_game_funcs.py`,
then regenerate in this order:

```sh
python3 ../rogue_squadron64/tools/make_elf.py
cd ../N64Recomp && ./build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py
cd ../RogueSquadron64Recomp
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from the build with the proven route, phase-gated and SIGKILL-watched:

```sh
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_M4_Y8000_WIDTH=512 \
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_MIPS_LINK_AUDIT=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1971_mips_link_audit 180 2
```

Expected split: repeated `actual_ra != expected_link` selects H-link-lost;
all links matching selects H-link-preserved; a statically intentional
non-link site selects H-legitimate-data; a valid call link followed by a
changed/invalid consumer value selects H-other-corruption. Do not interpret
any row unless the hangar control and positive row fire in the same run.
