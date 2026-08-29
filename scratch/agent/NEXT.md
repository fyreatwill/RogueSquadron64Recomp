# NEXT work unit — restore retail source needed for a new M5 boundary

HYPOTHESIS-ID: m5-retail-source-restoration

## Single work unit

Obtain an equivalent generated body or disassembly for the libultra/video
handoff, then select one genuinely unenumerated retail instruction. Until
that source exists, do not build an oracle watch, add a port instrument, or
change audio behavior. The prior candidate set and pending/descriptor census
are exhausted; a repeated candidate is invalid.

## Competing hypotheses

- H-RetailBoundaryFound: the new candidate executes in title or hangar and
  identifies the missing 640-to-1024 publication edge.
- H-RetailBoundaryAbsent: the candidate is live only in the 640 control or
  never executes, so it is not the target handoff.
- H-SourceInsufficient: the available static sources cannot justify a new
  candidate; no instrument should be built.

## Discriminating measurement

The same oracle run, once the missing source is supplied, must show the
whole-RDRAM control, title `1024`, hangar `512`, and candidate-PC hits
phase-keyed by VI origin. Target-phase candidate hits select
H-RetailBoundaryFound; control-only or zero hits select H-RetailBoundaryAbsent;
the present census selected H-SourceInsufficient because no new candidate is
defensible.

## Exact command

```sh
rg -n 'pending|descriptor|osViSetMode|__osViSwapContext|VI_ORIGIN_REG' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  syms docs --glob '!PORTING-STATE.md'
```

Before any build, record a new candidate table and positive-control watch in
this file. The 2026-08-28 census found no candidate; evidence is in
`scratch/agent/s3139_m5_retail_static_census.md`. The next falsifier is a
restored libultra/video generated body or equivalent instruction-level
disassembly that exposes a not-yet-watched pending-to-descriptor edge.
