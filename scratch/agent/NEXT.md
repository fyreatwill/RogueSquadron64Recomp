# NEXT work unit — identify the upstream route blocker before target phase

HYPOTHESIS-ID: m5-audio-route-upstream-boundary

## Single work unit

Use one new independent retail-grounded/static handoff audit to find the first
divergence before VI 1024. The paired qualification in Session 3124 passed
same-run controls and showed both image and silent arms stopping at VI 640, so
the audio/task table is still unevaluable. Do not change behavior.

## Competing hypotheses

- H-UpstreamPortStop: both arms stop at the same pre-target boundary, so the
  blocker precedes the audio/task table.
- H-ImageSpecificStop: image dispatch changes the boundary or terminal state,
  implicating image-task handling.
- H-RouteInstrumentationGap: controls show target progress while the current
  phase marker misses it, requiring a marker/consumer correction.

## Discriminating measurement

In one bounded audit/run, independently attributed guest PCs or a newly watched
handoff must split the hypotheses: identical image/silent stop boundary selects
H-UpstreamPortStop; an arm-specific boundary selects H-ImageSpecificStop; a
live target-phase control without a phase marker selects H-RouteInstrumentationGap.

## Exact commands

1. Ask/inspect the independent retail handoff boundary before adding port
   instrumentation; choose one unenumerated pre-640-to-1024 handoff.
2. Build all arms and controls together, run from `build/`, and kill with
   SIGKILL. Require the same-run positive control to fire.
3. Record the first divergent guest PC/phase and select exactly one hypothesis.
