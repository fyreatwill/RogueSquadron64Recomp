# NEXT: complete the RSP callback null-input guard audit
HYPOTHESIS-ID: m3-rsp-entry-null-guard

This iteration is the bounded M3 guard-class change. The audited class is
host-facing RSP callback entry points that accept `rdram` and then dereference
it before the generated ucode can report an error.

Competing hypotheses:

- H-null-is-impossible: the runtime always supplies non-null RDRAM and DMEM;
  the guard is unreachable and should remain a cheap defensive invariant.
- H-null-is-transient: a teardown or failed task can enter the callback with a
  null context; returning `-1` prevents a host crash and lets the caller's
  existing task-failure path handle it.
- H-null-is-game-data: a malformed guest task is the source; callback guards
  cannot explain it and task-field validation is the next class instead.

DISCRIMINATING MEASUREMENT: build the guard and run the existing compile/test
targets. The source audit must show every callback in this class has a null
decision before dereference, while the normal build remains unchanged. A
synthetic null callback test would select H-null-is-transient only if the
runtime exposes one; no production null hit is expected and that absence does
not justify removing the guard.

Planned change: guard `rs64_run_lle_gfx` on both `rdram` and `g_dmem_cur`, and
guard the optional audio-object diagnostic before its first RDRAM read. Build
the Debug target and record whether the production path is unaffected.
