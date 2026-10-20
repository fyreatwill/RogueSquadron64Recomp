Single next work unit (s5625): G1 mission progress. Why only 8 setObjectiveBoolean calls in 420 s unpoked?
Competing hypotheses: (A) lv2_checkComplexObjectives is called every frame but its conditions never become true (world state/AI not advancing); (B) the level script task stops being scheduled (stall in scheduler/thread); (C) it is progressing at game speed and the objectives are simply time-gated (retail would show same).
ONE instrument (extend apply_s5622_objbool_log.py or new apply_s5625): on every setObjectiveBoolean call AND every lv2_checkComplexObjectives entry (count only + every 60th), log VI frame counter and mission-time. Soak x2 as s5625_prog_{a,b}.
Outcomes: entry count keeps rising with no new booleans => A (then dump which condition globals it reads); entry count freezes => B; booleans arrive at fixed mission-times => C (compare with retail oracle timing if reachable).
Positive control: entry counter must be >0 and rising in the first 60 s.
HYPOTHESIS-ID: m6-mission-endurance
