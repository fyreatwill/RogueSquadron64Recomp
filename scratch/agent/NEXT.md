# NEXT work unit (s871)

HYPOTHESIS-ID: m3-coalescer-heap-writers

Perform one source-only whole-idiom audit of the coalescer heap-entry state.
Enumerate every generated writer of guest globals `0x801163e4` and
`0x801163e8`, every caller of `coalesceFreeHeapBlocks` at `0x80001430`, and
the complete path from each caller's `a0/a1` source into the two forward
walks. Include all generated aliases and delay-slot duplicates, but do not
build, run, or add a guard.

Competing hypotheses:

- H-init-writer-only: the globals are initialized or mutated only by the
  known boot allocator path; the invalid port entry arrives through caller
  arguments or a separate untracked heap-link writer.
- H-runtime-writer: a later normal game path writes the invalid global state;
  the source inventory identifies that path and its transition conditions.
- H-caller-state: the globals remain valid, but one or more callers source an
  invalid `a0/a1` from a game record or stack state before the coalescer call.
- H-legitimate-transition: every writer/caller path has a valid state-machine
  explanation, so the observed invalid values remain unexplained runtime
  corruption rather than an identifiable legitimate state.

Discriminating measurement: the exhaustive inventory must produce a table of
all writer PCs, written expressions, all callsites, and `a0/a1` provenance.
Only a writer that can reach the observed invalid global values selects
H-runtime-writer; valid globals with an invalid call argument selects
H-caller-state; a complete valid transition table leaves the state
corruption unexplained and keeps H-legitimate unproven. Any missing writer
or caller means the audit is incomplete and no hypothesis may be selected.

Exact commands:

```sh
rg -n -S '801163e4|801163e8|80001430|coalesceFreeHeapBlocks' ../N64Recomp/RecompiledFuncs src tools
rg -n -S '0x801163e4|0x801163e8|0x80001430|80001430' docs PORTING-STATE.md | tail -80
```

Do not add mitigation machinery. If the inventory identifies a new
phase-gateable caller/state boundary, make that the following unit's probe
design; otherwise record the missing boundary explicitly.
