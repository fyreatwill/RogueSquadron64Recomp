import json, os, sys, pathlib, glob
sys.path.insert(0, 'tools')
import g1d_floor_inputs as b, g1d_row_noise as rn
root = pathlib.Path('scratch/agent/s6692_floorsrc').resolve()
if b.screen_locked(): raise SystemExit('screen locked')
res = {}
for aspect, tag, w in (('16:9', 'wide16', '796'), ('21:9', 'wide21', '1024')):
    s = b.run_arm(aspect, tag, w, root)
    frames = {}
    for p in sorted(glob.glob(str(root / tag / f'fbd/*_w{w}.ppm'))):
        sc = rn.score(*rn.load(p)); frames[os.path.basename(p)] = sc.get('vhf', sc)
    res[tag] = dict(seconds=s['seconds'], crash=s['crashlines'], good=s['good_frames'], frames=frames)
    print(tag, s['seconds'], s['crashlines'], s['good_frames'], len(frames), flush=True)
(root / 'ab.json').write_text(json.dumps(res, indent=2, default=str))
