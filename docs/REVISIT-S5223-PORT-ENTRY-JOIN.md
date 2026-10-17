# Session 5223 port entry-contract join

Question: on the qualified mission origins, does the port enter
`fillSampleStreamRange = 0x8008FAAC` with the same caller and the same
retained-tuple field constraints that session 5203 recorded for retail?

Retail constraint, from the retained 32,768 distinct rows in
`scratch/agent/s5203_retail_entry_range/retail_fixed.log` (not a frequency
sample; 111,686 later novel tuples were dropped): `s0` and `s1` in KSEG0,
`source_byte = MEM_U8(s0+0x22)` in {0x00, 0x01, 0xFF}, `v0` in 1..8, dominant
`prev_pc = 0x800902CC`, and exact `0x800903F0` hits = 0. The port does not
compare `ctx->r31` to retail `ra`. Caller identity is the callsite hook.

## Boot failure, then the qualified run

The first launch, `scratch/agent/s5223_bootcrash/run.log`, SIGSEGVed in about
3 seconds, before `[s5223-armed]`. The faulting PC was `bzero+80` with
`si_addr=0x858`, called from `RT64::GBIManager::GBIManager`. `nm` showed
strong text symbols `_bzero` and `_bcmp`. The rename map had turned the
recompiler's `bzero_recomp` / `bcmp_recomp` into the unsuffixed libc names, and
this iteration's relink of `register_overlays.cpp` was the first link that
exported them. The libc-style call `bzero(ptr, 0x830)` entered the recompiled
function and used the size as a pointer. Restoring the `_recomp` suffixes
leaves `U _bzero` for libSystem and `T _bzero_recomp` / `T _bcmp_recomp`.
The header macros in `register_overlays.cpp` only hide the libc declarations;
they do not stop interposition.

The qualified rerun is `scratch/agent/s5223_port_entry_join/run.log`.
`[s5223-armed] entry-contract-join` fired once. `[phase]` reached title
`origin=0x00790400` at 51.1s (width 1024) and mission `origin=0x00690400` at
98.4s and 297.4s (width 512). `[vi]` also showed `origin=0x00620400`. Hangar
`origin=0x006AB400` did not appear. The driver summary keyed `00690400` and
therefore reported the mission join buckets absent: `%06X` prints `690400`.
The counts below are the last `[s5223-join]` line for each origin, and that
line's entry equals the max entry seen for that origin. No crash marker.

## Last join snapshots

`0x690400` (the `0x00690400` mission origin): entry=78464, c24c=117,
c2cc=78347, c39c=0, c3f0=0, s0_bad=0, s1_bad=0, sb_ok=87, sb_bad=78377,
sb_badptr=0, v0_ok=78464, v0_bad=0. The four callsites sum to entry.

`0x620400`: entry=79264, c24c=124, c2cc=79140, c39c=0, c3f0=0, s0_bad=0,
s1_bad=0, sb_ok=89, sb_bad=79175, sb_badptr=0, v0_ok=79264, v0_bad=0. The
four callsites sum to entry.

Other origins, printed as `origin=0x000000`: entry=180969, c2cc=180855,
c3f0=0, sb_bad=180748. Not used to select.

First three samples on each mission origin had `s1=0x8018C720`, `s0` in
{`0x80195190`, `0x80190E50`}, `v0` in {2, 3}, and `sb` in {0x03, 0xBB}.

## Selection

This selects H-field-diff. Caller structure matches the retained retail
contract, including a zero count at `0x800903F0`, so it refutes
H-port-takes-dead-site, H-port-misses-entry, and H-caller-diff. It refutes
H-entry-contract-shared because `source_byte` at `s0+0x22` is outside
{0x00, 0x01, 0xFF} on 78377/78464 and 79175/79264 mission entries. s0, s1,
and v0 stayed inside the retained set. The retail side of that byte set is
still the capped distinct-row table, so this does not prove retail never
emits 0x03. No guard is authorized.
