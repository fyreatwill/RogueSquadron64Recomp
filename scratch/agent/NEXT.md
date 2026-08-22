# NEXT work unit (s2171) — catch a failing =1 cinematic with flow probes

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2170 selected `H-NoHangAtN150` on a completing `=1` run.
Table: `scratch/agent/s2170_match_kw_flow_ab.txt`.
Soak `s2171_image_cinematic_flow` is queued to catch the
intermittent failure (`H-CinematicRegress` remains:
s2163 0/5 title, s2167 SIGBUS, s2169 640-stall vs
s2162/s2170 title+hangar).

If SOAK-RESULTS has a new `s2171_image_cinematic_flow`
line, THIS iteration is analysis-only (no rebuild):

- Fail (no 1024, or SIGBUS): read
  `scratch/s73_post_a_scene/s2171_image_cinematic_flow/run.log`
  flow last-n. Select among:
  - `H-HangInsideMatchKw`: matchEntry n has no matching
    return (entry n = return330+return358 + 1) after the
    last logged call.
  - `H-CallerStops`: matchEntry n == returns; further
    entries stop; effectsEntry==effectsRet.
  - `H-EffectsHang`: effectsEntry continues (or
    effectsEntry > effectsRet) while matchEntry stops.
  - `H-CoverageFailure`: no `[match-kw-flow-ctl]` at
    width=640 origin=`0x00696100`.
- Clean (title+hangar): do NOT repeat the same A/B.
  Offline-split existing captures s2169_on (stall) vs
  s2170_on (success) for a named pre-t=21 difference
  (last-guest-pc, audtask count, [CRASH]/SIGBUS,
  match-kw last n, update_screen origin). That uses
  logs already on disk.

If no soak line yet, run the soak yourself with the
exact command below. Do not S32-address, NULL-skip,
re-flip default-on, skip/allow the function, add a
wait/slot guard, or log `$t0`.

## Competing hypotheses and discriminator

Same four as s2170, now on a FAILING `=1` run (the
completing run already refuted them). Positive control:
`[match-kw-flow-ctl]` at width=640 origin=`0x00696100`.

## Exact commands

Queued recipe (loop may already have run it):

    zsh scratch/agent/soak_queue/s2171_image_cinematic_flow.sh

If running in-session instead:

    GAME_EXTRA_ENV='ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_MATCH_KW=1' \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2171_image_cinematic_flow 30 12

Watchdog SIGKILL at 120s. Classify from flow last-n plus
whether VI 1024/512 appear.

Do not flip `get_rsp_microcode`. Do not skip/allow/guard
`matchKeywordWithPriority`. Do not add `$t0`.
