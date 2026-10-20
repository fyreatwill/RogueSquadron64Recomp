Single next work unit (s5640): fold s5639_vcaller_{a,b} (build already carries the [vcaller] entry log on all 35 playObjectiveVoiceLine1 caller functions + runInMissionFrame control; grep '\[vcaller\]' scratch/agent/m6/<tag>/run.log).
Splits: control runInMissionFrame absent -> instrument invalid (rebuild check); control present + zero vcaller lines -> A/C (script triggers never fire; trace upward from a caller's table/event dispatcher; try oracle at mission start); some vcaller lines but no [voiceln] playObjectiveVoiceLine1 -> B (read the early-out gate in that caller); both -> look downstream (sound start / MusyX).
Then: read the first caller seen, find who invokes the zero-count ones (jalr tables).
HYPOTHESIS-ID: g2-voice-never-requested
