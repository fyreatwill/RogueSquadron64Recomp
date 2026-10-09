# Next work unit (s4470): M5-AUDIO-PLAN step 7 - status-03 service reaping

HYPOTHESIS-ID: m5-status03-service-reaping

Step 5 is closed (s4101). Start from soak s4104_m5_status03_service_reaping_fixed (Hroute-invalid: control=1 but retail/port title+hangar all 0; port crash spTaskSchedulerThread+9632). First find why the route never reached title (boring-first: stale recipe/ROM path/env), fix it, then run the retail-vs-port status-03 worker writer table in one run.
Hypotheses: (A) recipe route/env bug; (B) a genuine port crash before title on this build; (C) valid route, reaping worker never enters in port.
Discriminator: does port reach title 1024 with the fixed recipe? Y -> measure worker entry/store-zero; N -> crash is the unit.
