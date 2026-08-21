# NEXT work unit (s2159) — A1 named default-blocker census

HYPOTHESIS-ID: m5-image-arm-default-blockers

## Work unit

s2158 selected `H-IsolatedOnlyByEnv`: the only control-flow isolator
that keeps `factor5_ucode_b` opt-in is `get_rsp_microcode`'s
`ROGUESQ_AUDIO_UCODE` branch. `run_task` always calls that pointer;
the env-true wrapper never reaches `musyx_stub`. Do not default the
image arm from that table, move the canary, change canary 10→prefill,
or change `osAiGetStatus_recomp` / `osAiSetNextBuffer_recomp`.

The remaining A1 question is which named reason, if any, still forbids
flipping `s_use_real_audio_ucode`'s default. Next unit is one host-only
table of every sentence in `docs/CURRENT-TRUTH.md`,
`docs/M5-AUDIO-PLAN.md` A1, and the `get_rsp_microcode` M_AUDTASK
comment that claims a reason the image arm must stay opt-in. Classify
each as closed-by-selected-hypothesis, still-open, or policy-comment.
No port build, game run, default-arm, canary, task-exit, or output-route
change.

Positive control: the CURRENT-TRUTH sentence that isolation remains
because the generated task "does not yet satisfy the host task
contract", plus the `get_rsp_microcode` hang-comment about
`waitForMusyXAudioTaskDone`. Both must appear as named rows.

## Competing hypotheses and discriminator

- `H-PolicyOnly`: every previously named host-contract reason to keep
  the arm opt-in is already closed by a selected hypothesis; remaining
  isolation is the env default plus a historical comment.
- `H-ContractOpen`: at least one named host-task-contract clause is
  still unsatisfied (cite the clause and the missing discriminator).
- `H-WaitWedgeStillOpen`: the `waitForMusyXAudioTaskDone` hang comment
  in `get_rsp_microcode` is an untested default-arm risk, not closed by
  s2123/s2125 sampled wait/pump rows.
- `H-CoverageFailure`: a named "keep opt-in" sentence has no matching
  selected hypothesis and no classifiable open discriminator.

The discriminator is one table: every keep-opt-in sentence, its class,
and the selected hypothesis or missing measurement it cites.
All-closed-plus-policy selects `H-PolicyOnly`; one unsatisfied contract
clause selects `H-ContractOpen`; an unclosed hang-comment risk selects
`H-WaitWedgeStillOpen`; an unclassifiable sentence selects
`H-CoverageFailure`. Do not default the image arm from the table.

## Exact commands

    python3 - <<'PY'
    from pathlib import Path
    files = [
        Path('docs/CURRENT-TRUTH.md'),
        Path('docs/M5-AUDIO-PLAN.md'),
        Path('src/main/main.cpp'),
    ]
    needles = [
        'opt-in', 'default', 'ROGUESQ_AUDIO_UCODE',
        'host task contract', 'waitForMusyXAudioTaskDone',
        's_use_real_audio_ucode', 'factor5_ucode_b',
    ]
    for p in files:
        text = p.read_text()
        print(p, 'bytes', p.stat().st_size)
        for n in needles:
            print(' ', n, text.count(n))
    PY

Grep those needles in the three files. Classify each keep-opt-in
sentence. Write `scratch/agent/s2159_image_arm_default_blockers.txt`.

Do not edit `get_rsp_microcode`, `musyx_stub`, `osAiSetNextBuffer_recomp`,
or the default audio arm.
