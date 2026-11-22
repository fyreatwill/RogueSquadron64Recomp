#!/usr/bin/env python3
"""s7672 G6c stand-in -> real object handoff scorer. Reads [s7672-ho] rows (ROGUESQ_STANDINS_LOG=1).
A handoff counts when it is the item's first life in the log, it ended by spawn, and the stand-in was accepted no more than 2 frames
before the spawn (spawn_f - last_si <= 2; held stand-ins give negative values) - i.e. the object was on screen as a stand-in.
blink = frames with neither stand-in nor real object accepted = real_add - last_si - 1 when > 0; overlap = frames with both.
Rows split by odd= (ROGUESQ_S7672_HOLD=odd holds only odd-index stand-ins: even rows are the same-run control and must still blink;
with no odd= field every row is one group).
s7674: rows with si_off= (tools/apply_s7674_bucket_vt.py) also get a cull-class line per group: held stand-in culls by our own view-test
exit (off = box/behind/side, far, novt = cached reject, the game tests each object on alternate frames, vtpass) and the real object's
rejects while waited for. A held si_vtpass > 0 = a culled held stand-in that was not off-screen (rc 1).
s7799 (dd2): a held si_far is legitimate when the item sits beyond far*dd (the stand-in's own widened far, >= the retail far), and
then its real object is far-rejected too. rc 1 only for a held item with si_far > re_far ("far_viol": the stand-in far-culled more
often than its real object at the narrower retail far, i.e. the widened far is broken). At dd4 si_far was 0 (s7674); at dd2 L1 it is
179, all on items with re_far >= si_far (4 never drawn at the intro hold, 1 near the dd2 edge). Usage: s7672_handoff_score.py log [log...]; rc 1 if a held group has a blink > 1 frame."""
import sys, re, collections
rc = 0
for log in sys.argv[1:]:
    seen = set(); grp = collections.defaultdict(list); cls = collections.defaultdict(collections.Counter)
    for ln in open(log, errors="replace"):
        if "[s7672-ho]" not in ln: continue
        d = dict(re.findall(r"(\w+)=(\S+)", ln)); it = ln.split("item ")[1].split()[0]
        first = it not in seen; seen.add(it)
        if first and "si_off" in d:
            for k in ("held", "held_ok", "si_off", "si_far", "si_novt", "si_vtpass", "re_rej", "re_off", "re_far", "re_novt", "re_vtpass"): cls[d.get("odd", "all")][k] += int(d[k])
            cls[d.get("odd", "all")]["far_viol"] += int(int(d["si_far"]) > int(d["re_far"]))
        sb = int(d["si_before_spawn"]); 
        if not first or sb == -9999 or sb > 2 or int(d["real_add"]) < 0: continue
        if d["end"] not in ("spawned", "none"): continue
        grp[d.get("odd", "all")].append((max(int(d["gap"]), 0), int(d["overlap"]), int(d["real_add"]) - int(d["spawn_f"]), float(d["dpos"])))
    for k in sorted(grp):
        r = grp[k]; bl = [x[0] for x in r]; ov = [x[1] for x in r]
        n_bl = sum(1 for b in bl if b > 1)
        print(f"{log.split('/')[-1]} odd={k} handoffs={len(r)} blink>1={n_bl} blink_max={max(bl)} blink_med={sorted(bl)[len(bl)//2]} "
              f"overlap_max={max(ov)} cull_after_spawn_med={sorted(x[2] for x in r)[len(r)//2]} dpos_max={max(x[3] for x in r):.2f}")
        if k == "1" and n_bl: rc = 1
    for k in sorted(cls):
        c = cls[k]; print(f"{log.split('/')[-1]} odd={k} classes " + " ".join(f"{x}={c[x]}" for x in c))
        if k == "1" and (c["far_viol"] or c["si_vtpass"]): rc = 1
sys.exit(rc)
