# NEXT work unit (s1142)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Perform one bounded static audit of the regeneration/input path for the
coalesced `0x80077AC0`/`0x80077AF0` range. Do not build or run the game.
Locate where the distinct `npcPowerGeneratorUpdate` boundary is lost and name
the smallest durable correction that will regenerate two host functions.

```sh
rg -n 'forwardToNpcGeneratorSpawn|npcPowerGeneratorUpdate|80077AC0|80077AF0|77680|789FC' . /Users/williambuckley/Documents/Tools/N64Recomp --glob '!funcs_*.c' --glob '!PORTING-STATE.md' --glob '!*.log'
rg -n 'fixup_game_funcs|recomp_overlays|single_file_output|function.*table|symbols|syms' tools patches *.toml CMakeLists.txt
```

Competing hypotheses and the discriminating measurement:

- H-input-merged: the source/config function table itself presents one
  merged range, so the durable fix is in the generator input or symbol-map
  generation.
- H-fixup-merged: the source table is split but `fixup_game_funcs.py` or a
  post-generation transform merges/relabels the functions; the correction is
  in that transform.
- H-generator-bug: the source and generated symbol tables are split, but
  N64Recomp emits one host body; the correction belongs in N64Recomp or its
  invocation, not a game guard.

The discriminating measurement is the first representation in the
regeneration chain whose range omits the split at `0x80077AF0`, followed by
the concrete generated invocation/output that coalesces the body. Record the
representation, range, and correction. Do not hand-edit generated C or add a
runtime mitigation.
