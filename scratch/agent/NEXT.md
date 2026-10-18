# Next work unit: offline - find what ends mission 1 so a soak can reach results
Plume thread closed (s5463: 16/16 titles clean). M6 mission-hold endurance closed. Gap: no recipe reaches mission end/results (s5445).
Hypotheses: H1 end needs objective kills/ally survival (flight keys alone cannot); H2 end is a timer/trigger reachable by holding in a region; H3 a debug/cheat path (applyCheatCodeFromInput, S4486 audit) can force it.
Discriminator: in generated code, find writers of the mission-state variable that precedes the results scene (origin transition after post_results seen in m6_post_late soaks; grep s5420-s5449 notes for the scene ids) and name the condition. Output docs/M6-MISSION-END-TRIGGER.md (NEW doc) with the exact condition per hypothesis. Then, only if H3, queue one soak.
HYPOTHESIS-ID: m6-mission-end-trigger
