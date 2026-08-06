# NEXT work unit

## s389 recap

Picked up the M3 idiom-class-audit strategic-priority item fresh (no live thread was open). Candidate
search tallied `[CRASH][last-guest-pc]` across ~24 recent soaks in `scratch/agent/soak_results/*.log` and
found `0x800ad0dc` (`pc-symbol=findLookupEntryByKey+1864`) recurring at n=2, previously dismissed twice
(s359, s370) as off-target noise for unrelated threads. Investigation (delegated to a read-only Explore
agent) found the pc-symbol attribution itself was wrong — the address is actually inside
`hangarInitialize`/`static_5_800AB658`, a large already-heavily-patched function, at a fixed-global store,
not a hash-table dereference (same failure mode as the long-catalogued `0x8000b650` staleness). Pivoted:
`findLookupEntryByKey` and 2 siblings share the exact unguarded table-base-pointer idiom already fixed for
their sibling `setLookupEntryField5ByKey` (s260). Enumerated the whole "Lookup" struct-family (6
functions: 2 pre-guarded/out-of-class, 4 newly guarded this session), applied guards reusing the s260
KSEG0-range+hi-word template with per-function bail semantics matched to each one's own control flow,
verified via the standard byte-identical-except-intended-diff regen protocol + clean build + 3 soaks (2
hit unrelated already-catalogued crash families, 1 fully clean 304s hold with the full VI phase timeline).
0 guard fires in any soak — a proactive/defensive fix, not a response to reproducing corruption. Full
detail: `PORTING-STATE.md` Session 389, `docs/CURRENT-TRUTH.md` item -239.

## This iteration's work unit: M3 idiom-class audit, next cycle

Per the standing strategic-priority order (M5 fully closed s376; sanctioned tooling backport fully closed
s386-388; this session's Lookup-family idiom class now closed too), the next work unit is another **fresh**
M3 systematic idiom-class audit, same model as s282-288 and s389: grep-enumerate a whole idiom class,
classify every site, guard or prove dead, close the class. Do NOT reactively chase a single breadcrumb.

### Step 1 — find a live candidate (do this first, it's cheap)

s389 fully mined the `soak_results/*.log` population that existed at its start (the s355-369 M5 Step 5
guard-hunting arc's own verify pairs, plus the s379/s386/s388 manual batch-verification soaks). That
population is now exhausted for this purpose — every recurring `last-guest-pc` in it has been triaged
(either already-catalogued/closed, confirmed stale-symbol noise, or turned into this session's fix).
Before repeating the same tally:

1. Check whether the loop's soak queue has drained any NEW recipes since s389 started (this session queued
   none itself, but the loop may have run something else in the gap) — `tail -20
   scratch/agent/SOAK-RESULTS.md` and diff against what this NEXT.md already knows about.
2. If nothing new: queue a few fresh general-purpose soaks (not a targeted verify pair for a specific
   guard — a broad, unbiased soak_queue/*.sh recipe with a long `HOLD_S` and every standing guard env var
    armed, same shape as `run_s327waitpump.sh`) to generate NEW crash population to tally, since the old
   population is drained. 2-4 recipes, `HOLD_S=300`+, is enough to get a fresh sample without spending a
   whole session babysitting them — the loop drains up to 2 per gap.
3. Once fresh data exists (this session's queued soaks, or whatever the loop already ran), tally
   `last-guest-pc` recurrence the same way s389 did, remembering the `0x8000b650`
   (`beginFrameDLChunk`-stale) and now `0x800ad0dc` (`findLookupEntryByKey`-stale,
   really-`hangarInitialize`) lessons: a pc-symbol name is NOT reliable evidence of which function a crash
   is really in — always confirm against the generated source's own `RECOMP_FUNC`/`// 0x...` address
   comments before trusting a symbol name, especially for any address that hasn't been confirmed in-range
   before.
4. Pick ONE idiom class with the most evidence density as this session's target, or — if the soak
   population stays too thin/scattered to identify one — fall back to a proactive sweep: pick a struct
   family or function cluster already known to share an idiom (grep `fixup_game_funcs.py` for existing
   guard clusters — `HANGARLIST_GUARD`, `SCENE_NODE_CACHE`, `COMPOSE_NPC_GUARD` families, etc. — and check
   each family's OWN sibling functions for the same unguarded pattern, the same move that worked this
   session for the Lookup family).

### Step 2 — grep-enumerate and classify

Follow the s282-288/s389 model: grep the full idiom pattern across all of `RecompiledFuncs/`, produce one
line per site with file/function/address, classify each as (a) already guarded, (b) needs a guard, (c)
provably dead code, or (d) needs more investigation. Enumerate the WHOLE class before writing any patch,
then batch the guards into one patch set with one regen-diff-build-soak verification cycle.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (unchanged — this is iteration 2 of the standing M3-idiom-class-audit
work mode; the slug tracks the audit MODE, not a single class, since each closed class hands off to the
next one under the same strategic-priority item).
