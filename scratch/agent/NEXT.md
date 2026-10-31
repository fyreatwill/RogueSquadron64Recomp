# G1(d): level7 ordinary named target health/route qualification
HYPOTHESIS-ID: g1-coverage-cd

ONE bounded ordinary-only adapter/analyzer change and one corrected unlocked
flight. s6684 qualifies the original static contract; no live target admission
yet. Target20_Dest_Tanks_01 DAT+05D0 subtype0x14, nominal detail0HP50,
effect(20,1,0,0,0,1). Preserve level3..6 helpers and all retail defaults.

Hypotheses:
H-registered: original name lookup finds a valid owned registered CBB0 victim;
API10 dispatches message5CF88, store6CFE8 subtracts10, survives, returns agree.
H-fallback: name exists but slotFFFF/unowned; do NOT issue damage because the
fallback effect is eager. Admission evidence identifies this boundary.
H-route: lookup/ownership is valid but actual detail/health/gates/message chain
differs; capture all keys at once, classify the first divergence.
DISCRIMINATOR: one exact epoch/slot/gen/node/NPC/DAT/detail/message/API sequence
through original health store and both API/getter returns. Same-run owned
mark-all controls and actual changing objective-getter values are required;
heartbeat or branch entry is not a null control. No lethal request, direct
health/counter stores, stage completion or mission win. Health must exceed10
and actual live detail must be observed before ordinary admission.

Ground truth/checks first:
    python3 tools/g1_dat_inventory.py --level 7 --check-level7 --mutation-check-level7 --output scratch/agent/s6685_level7_contract.json
Read docs/G1-OBJECTIVE-RESPONSE.md s6684 and bounded original hook windows.
Extend existing tools/apply_s6657_objective_response.py and
 tools/g1_objective_response_run.py (currently --level choices stop at6).
Use the existing level3/6 original named API and free-list/ownership patterns,
not generic TELE or raw pointer-shaped candidate counts. Hook lv7 callback
801044E0; DAT base/name lookup -> selected05D0; handler8006CBB0/message5CF88,
health store6CFE8; original getters20/30/40/99. Collect every identity/gate,
pre/post health, message pointer, request/return and objective value in one
build. Keep level7 lethal and generic TELE hard-disabled. Phase/flight-gate
all counters/budgets. Add complete/missing-link/wrong-route/FFFF fixtures.

Then (only after --level7 and fixtures exist):
    python3 tools/g1_objective_response_run.py --self-test
    python3 tools/fixup_game_funcs.py
    cmake --build build --target RogueSquadron64Recomp -j6
    /usr/sbin/ioreg -n Root -d1 | rg CGSSessionScreenIsLocked
    python3 tools/g1_objective_response_run.py s6685_lvl7_ordinary --level 7
Runner verifies unlock and launch manifest, watchdogs and SIGKILLs itself.
Do not run a key-driven route if locked. No repeat coverage/crash-hunt hold.
Check adapter idempotence/hook-free replay, all6 manifest hashes, saved lvl3..6
analyzer results and static contracts. If first admission misses ownership,
report that exact edge; no claim of target absence or objective null.
Record Session6685, update truth/objective docs, NEXT/STATUS/OUTCOME and make
a NEW iter commit. No new queued-soak verdicts through s6684.
