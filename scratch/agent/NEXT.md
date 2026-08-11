# NEXT work unit

HYPOTHESIS-ID: cimg-origin-desync

## Single work unit

**Exact freelist-killer origin freeroll** under the s662 instruments (already
built). Do not expand freelist mitigation. Do not re-run hangar-cluster
probes — those are settled (H-desync-tri SUPPORTED, in_wrap=1).

The loop should consume `scratch/agent/soak_queue/s662_dpcwrap_killer_correlate.sh`
if still queued; else re-run the same recipe in-session.

## Hypotheses (exact killer only — hangar cluster already classified)

| ID | Claim | Killed if |
|----|-------|-----------|
| H-exact-same-class | The historical freelist SETCIMG (`w=1161` `addr=0x1F0D74`) is the same hangar garbage-ring class (in_wrap=1 + garbage prev TRI) | KILLER dump shows in_wrap=0 and a clean allowlist-width prev chain |
| H-exact-legit | The game/ucode genuinely emits those operands on a clean command boundary | KILLER dump shows garbage prev (op 0x09 TRI / non-monotonic) or in_wrap=1 with desync shape |
| H-exact-submit-range | The processRDPLists range that carries the killer is a deferred merge of wrap-adjacent ring bytes | submit sticky (now fixed at real submit_rdp_range) does not contain the killer task address |

## Discriminating measurements (already instrumented — one freeroll)

Arm: `ROGUESQ_LOG_CIMG_RAW=1 ROGUESQ_LOG_CIMG=1 ROGUESQ_LOG_DL_SYNC2=1
ROGUESQ_LOG_FL_ZERO_WATCH=1` + force6/inject as in s662 soak recipe.

Watch for **exact** tags only:
- `[cimg-raw] KILLER` (w=1161 OR addr=0x1F0D74) — must dump with prev ring +
  wrap sticky + submit sticky
- `[set-cimg-full] KILLER`
- `[fb-fl-writeback] ... addrStart=0x1F0D74 w=1161`

Posctrl (same run): `[cimg-raw] OK` must fire early (boot w=320).

## Outcomes

- **A)** KILLER + in_wrap=1 + garbage prev → same class as hangar wilds.
  Next: filter/drop RDP submits that are inside a just-wrapped ring tail, then
  A/B freelist mitigation OFF (expect freelist stomp gone).
- **B)** KILLER + in_wrap=0 + clean prev chain → H-legit / different path.
  Resume writer attribution (oracle + overlay residency at fire time).
- **C)** No exact KILLER in budget → keep recipe queued; do not chase hangar
  wilds again.

## Standing rules

- Exact KILLER only — covers_fl was REFUTED as a tag (s662 false-pos).
- Positive control OK dumps before trusting null KILLER.
- No new freelist mitigation without ORIGIN line.
- If editing lib/: `./submodule-patches/export.sh` + commit same session.
