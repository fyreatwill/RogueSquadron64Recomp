# Regression harness

One run, every phase, one machine-readable verdict. Replaces the per-session
routine of hand-writing `PROBE_KEYS`, running `probe.sh` once per phase, and
eyeballing a contact sheet.

    tools/regress.sh <outdir> [seconds]     # run + capture, then score
    tools/regress_score.py <outdir> [--baseline v.json] [--label name]

`regress_score.py` exits 1 on FAIL, so it can gate an unattended
edit → run → compare loop.

## Recording a baseline

    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_STUB_MISSING_FUNCS=1 \
    REGRESS_KEYS="1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a" \
    REGRESS_LABEL=baseline \
    tools/regress.sh scratch/baseline 120

Then check a change against it:

    REGRESS_BASELINE=scratch/baseline/verdict.json \
    tools/regress.sh scratch/try-something 120

## Key schedule is phase-relative

`REGRESS_KEYS="<width>@<sec>[:<key>] ..."` — `<sec>` counts from the moment that
VI width is first entered, not from boot. Width `0` means boot-relative.

This is the fix for the session-22 failure: absolute key times fire during the
cinematic because the Factor 5 logo has been seen anywhere from 18 s to 48 s.
Key names are the `probe.sh` set (`start a b z up down left right su sd sl sr
cup cdown cleft cright l r`); a bare `<sec>` means Start.

## Two halves, different requirements

| half | what it reports | needs |
|---|---|---|
| log | phase timeline + entry times, crash point, distinct `[missing-func]`, `defer-drop` total, aborts | nothing — works from any shell |
| visual | per-phase content fraction and distinct-colour count | Screen Recording permission for the calling process |

## Preflight (session 25)

`regress.sh` probes both capabilities before launching the game — about a
second, against a full run's budget — records the result in `env.txt`, and
refuses a driven run it cannot actually drive:

    preflight: input=ok visual=denied

- `REGRESS_ALLOW_UNDRIVEN=1` — run the key schedule anyway.
- `REGRESS_REQUIRE_VISUAL=1` — refuse to run at all if capture is unavailable,
  instead of silently producing a log-only verdict.

**`AXIsProcessTrusted` (`winctl trusted`) is necessary but not sufficient.**
Session 25 had two driven runs take the undriven route while `winctl trusted`
still answered `yes` and windowed capture had just started failing. The TCC
grant was still held; the missing piece was a usable GUI session, without which
`winctl activate` cannot front the game, SDL never has a focused window, and
posted keys are dropped although `CGEventPostToPid` reports success. So the
**windowed-capture probe gates driven runs too**. Probe capture first when
planning a session: if it fails, the hangar is unreachable and only log-only
work is possible.

`screencapture -l<windowid>` fails with "could not create image from window"
when the caller lacks Screen Recording permission. The runner detects this on
the first frame, says so loudly, and continues in log-only mode; the scorer
reports `visual: unavailable` and still produces a verdict from the log half.
Grant the permission (System Settings → Privacy & Security → Screen Recording)
to the terminal you want visual scoring from.

Synthetic input has the same shape of problem but fails **silently**:
`winctl key` uses `CGEventPostToPid`, which returns success and does nothing
without Accessibility permission. The scorer therefore checks whether the game
reacted — if a key schedule fired and no VI transition followed within 10 s, it
warns that input may not have landed. Measured on 2026-07-25: two runs whose
keys "fired" with exit 0 both followed the undriven path (512 at origin
`0x690400`, the outdoor scene) instead of the driven one (`0x6AB400`, hangar).

## Measurement rules baked in

- **Sampled counters are read from their index, not their line count.**
  `[defer-drop #N]` prints only the first 32 events then every 64th
  (`src/rsp/dpc_bridge.cpp:1381`), so counting lines measures the sampler. The
  scorer takes `max(N)`. Verified: a log with 34 tag lines reports 128.
- **Only frames that exist on disk are counted.** The runner never reports
  attempts as captures — that is what made `window_burst.sh` read a dead
  window as "60/60 content".
- **Phases under 3 frames are reported, not judged.** A content fraction over
  two frames is noise.
- **Phase-reached checks come from the game's `[phase]` log lines**, not from
  the frames, so they still work when capture is unavailable.

## Failure thresholds

| check | level |
|---|---|
| baseline reached a VI width this run never did | FAIL |
| content fraction dropped > 0.25 for a matched phase | FAIL |
| median distinct colours fell below 50 % of baseline | FAIL |
| new `[missing-func]` addresses | FAIL |
| new aborts / asserts / GPU-OOM / unhandled-jump | FAIL |
| process died where baseline completed | FAIL |
| **key schedule fired but nothing reacted** | **FAIL** (s25 — the run took the undriven route, so its phases are not the ones requested; scoring that PASS is the `window_burst.sh` mistake again) |
| phase reached at > 2× the baseline time | WARN |
| `defer-drop` more than doubled | WARN |

## Files

- `tools/regress.sh` — run, drive, capture, hand off to the scorer.
- `tools/regress_score.py` — score frames, parse the log, write `verdict.json`,
  diff a baseline. Reuses `stats()` from `tools/frames.py` for the content
  judgement rather than reimplementing it.
- `<outdir>/verdict.json` — the artifact to keep as a baseline.

Python needs Pillow; the scorer re-execs itself into `scratch/venv/bin/python3`
automatically, or set `REGRESS_PYTHON`.
