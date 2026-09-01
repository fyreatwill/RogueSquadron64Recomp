# M5 Session 3515 — retail route qualification for mixer boundary

The independent retail oracle ran before any port build or new instrument, with
a whole-RDRAM write control and the driven Rice route used for the hangar
comparison. The control reached 10,000 callbacks and was removed; the run then
reached title (1024 VI) and the 512 hangar at about 38.4 seconds.

Retail `musyxMixActiveVoices` entry `0x80090E04` fired 12 times in the hangar
bucket. The known `fillSampleStreamRange` PC at `0x8000B650` had no hits.
This keeps the retail mixer boundary qualified but does not explain the port's
pre-title failure; no port arm was run in this unit.

ORIGIN: independent retail execution capture; no game state, audio state,
selector value, task field, or output was rewritten or skipped.

Evidence: `scratch/agent/s3515_oracle_route/oracle.log`.
