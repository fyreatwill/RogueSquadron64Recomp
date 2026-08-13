# NEXT work unit (identify the late E9 span-counting path)

HYPOTHESIS-ID: m3-rdp-parser-condition

Perform one bounded source audit; do not build or run. Reconcile the bridge's
8-byte E9 candidate scan with RT64's length-respecting parser and the new
condition join, including the single residual unassociated slot from s851.
Read only bounded source windows around the listed symbols and record an
exhaustive address/range table in the session ledger.

Competing hypotheses and discriminator:

- H-span-intended: parser command lengths intentionally consume the bridge's
  interior E9 bytes as inline payload.
- H-span-mismatch: the parser spans are real, but bridge and parser use
  different physical/range interpretations.
- H-residual-range: the residual is a deferred/synthetic range or stale
  submit-label case.
- H-pending-residual: the residual is completed through a split-command
  pending lifecycle not represented by the aggregate.

Discriminator: source control flow must account for all three address classes
(direct, span, residual) and prove whether the bridge and parser use identical
physical byte selection and submit-range identity. A complete interior-byte
proof selects H-span-intended; a mapping mismatch selects H-span-mismatch; a
synthetic/deferred label edge selects H-residual-range; a split-command edge
selects H-pending-residual. No behavior or mitigation change.

Exact commands:

1. `rg -n "rs64_count_submitted_e9|MEM_B|emitted_addrs|submit_rdp_range|rs64_dpc_record_submit" src/rsp/dpc_bridge.cpp`
2. `rg -n "commandWordLengths|pendingCommandRemainingBytes|rs64_e9prov_condition|processRDPLists|cmdLength" lib/rt64/src/hle/rt64_interpreter.cpp lib/rt64/src/hle/rt64_rdp.cpp`
3. Read at most 60-line windows around every hit and compare the bridge scan,
   parser byte load, command span, pending continuation, and synthetic submit
   path. Do not run a second capture.
