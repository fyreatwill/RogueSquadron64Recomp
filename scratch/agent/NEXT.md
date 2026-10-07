# Next work unit: requalify the M5 source-construction predecessor route

HYPOTHESIS-ID: m5-source-construction-predecessor-route

Use one rebuilt canonical real-audio/LLE/ungated/solo/spin-yield port and the
independent retail oracle. The new discriminator is route validity at the
port's known `musyxSynthFrame+3828` / guest PC `0x80001B08` boundary: a port
run that reaches hangar without this crash may be compared at the s4139
source-construction tuple; a pre-hangar crash or missing hangar gate is
H-route-invalid and must not be interpreted as a writer null.

Competing hypotheses and discriminator:

- H-source-context-split: both arms pass whole-RDRAM/title/hangar controls and
  the phase-keyed source-construction tuple differs between retail and port.
- H-source-context-match: both arms pass the same controls and the tuple
  matches at the measured source-construction boundary.
- H-route-invalid: either positive control or target phase is absent, or the
  port hits the known pre-hangar `musyxSynthFrame+3828` boundary.

Before building, verify the existing s4139 source-context probe and its
positive-control env vars in the tracked debug catalog. Build once. Run the
retail oracle first with whole-RDRAM and title/hangar controls, then run the
canonical port from `build/` with the same phase gates. Do not change guest
behavior, audio waits, caps, predicates, slot state, or host writeback.

Expected outcome: a qualified paired tuple comparison selects split or match;
any missing gate or known pre-hangar crash selects H-route-invalid.
