# NEXT work unit (s2090)

HYPOTHESIS-ID: m5-voice-output-base-provenance

## Work unit

Perform one bounded generated-source/companion-symbol crosswalk for the
off-lattice retail writer `0x80090C80`, comparing its computed destination
base and caller role with the lattice writer `0x800921E8`. This is a source
semantics audit, not a port change and not a repeat soak. Record the base
load, index arithmetic, destination field, and caller for both exact stores.
Use the qualified s2089 oracle table as the retail address/value input, and
do not add a new runtime witness until this crosswalk chooses a branch.

## Competing hypotheses and discriminator

- **H-VoiceBaseMismatch** — the `0x80090C80` source path is rooted at the
  `0x801496F8` voice pointer and its generated `+0x34` destination should be
  on the same `0x88` lattice; the retail off-lattice rows then indicate a
  source/retail field or index mismatch.
- **H-AlternateStructure** — `0x80090C80` computes its destination from a
  different song/channel structure, so its off-lattice destinations are
  legitimate and the prior voice-array attribution was wrong.
- **H-ReallocatedVoiceBase** — the source path is voice-rooted, but the
  contemporaneous pointer/base used by this path is not the sampled
  `0x801496F8` entry; a source-level alternate publisher or base load must be
  identified.
- **H-OracleWriterMismatch** — the generated instruction address or post-store
  attribution does not correspond to the source store under test; the exact
  instruction and physical destination calculation must disagree before this
  branch is admissible.

The discriminator is one crosswalk table covering both writers: if
`0x80090C80` loads `0x801496F8` and forms `base + index*0x88 + 0x34`, select
H-VoiceBaseMismatch; if it loads the command/channel root at another symbol
and stores at that structure's `+0x34`, select H-AlternateStructure; if it
uses a second voice-base publisher, select H-ReallocatedVoiceBase; if neither
source instruction nor physical address matches the oracle row, select
H-OracleWriterMismatch. A missing source/companion mapping is unevaluable.

## Exact commands

```sh
rg -ni -C 8 -- "80090c80|800921e8|0x34|801496f8|80149750|voice" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt

rg -n -C 20 -- "0x80090C80|0X80090C80|0x800921E8|0X800921E8" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c

sed -n '7632,7830p' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c

rg -ni -C 12 -- "musyxKeyOnVoice|musyxInitVoiceFromSample|801496f8|80149750" \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Before any future instrument build, require the crosswalk to identify the
writer's base root and field role. Do not rewrite a field, remove a guard, or
change task/output behavior from this result alone.
