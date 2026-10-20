Single next work unit (s5638): fold s5637_voiceln_{a,b,c} soaks. For each log, grep [voiceln] and [objbool] id=0x64; table per run: did sayWhoaHim_v0x1FC fire, at what t relative to 0x64, and the ra of the playObjectiveVoiceLine1 caller (identify the dispatcher from ra).
Hypotheses: (A) voice line stepped by timer/proximity, fail separate; (B) line follows a damage/kill event that is the real fail cause; (C) bool 7 only read by the checker as a gate.
Outcomes: 0x1FC fires in failing runs only, shortly before 0x64 -> B/C, trace ra caller; fires in all runs -> A (not discriminating for fail); never fires in a failing run -> bool 7 set elsewhere (dynamic id).
Control: playObjectiveVoiceLine1 must log at least once per run, else the instrument is dead. Related: G2 (no dialogue audio).
HYPOTHESIS-ID: m6-mission-endurance
