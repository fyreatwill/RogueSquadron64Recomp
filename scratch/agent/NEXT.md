# NEXT (s7565)
HYPOTHESIS-ID: compensation-chain-audit

19b CLOSED s7564 (B40 A/B: both settings 6/6 clean; gate-0 default lives only via s4889 dereg + s7476 $a1 fix; owner decides).
Unit: 19c compensation-chain audit, offline, ONE tool. Class: default-on behaviour patches whose trigger is another port deviation
(s4889 fires only because B40 defaults to 0; s7476 repairs s4889's clobber). Enumerate from docs/DEFAULT-ON-LEVERS.md (115 ON
levers) + class GR fixup hunks: for each, read its trigger condition and session ORIGIN line, classify
  RETAIL-GAP (repairs a retail/host behaviour gap), CHAIN (exists because of another port lever/deviation: name the parent),
  DIAG, UNKNOWN. Write tools/s7565_comp_chain.py emitting a table + docs/COMPENSATION-CHAINS.md.
Hypotheses: H-isolated (s4889/s7476 is the only chain) vs H-chains (>=2 more chains; each is an owner-facing simplification:
retail parent setting would retire the child) vs H-unclassifiable (ORIGIN lines too thin -> list them as UNKNOWN, not a zero).
Positive control: the tool must classify s4889 as CHAIN(parent=M5_B40_VALUE) and s7476 as CHAIN(parent=s4889); a planted fake
lever with an ORIGIN naming another lever must appear as CHAIN. Never flip a default; owner decides.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
