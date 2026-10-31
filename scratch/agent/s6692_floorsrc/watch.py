import json, os, sys, pathlib, glob
sys.path.insert(0, 'tools')
import g1d_floor_inputs as b, g1d_row_noise as rn
root = pathlib.Path('scratch/agent/s6692_floorsrc/watch').resolve()
if b.screen_locked(): raise SystemExit('screen locked')
W = {'wide21': 'B70078,BD80C8,BEC708,BFA400', 'wide16': 'B9C670,BE0F28,BF8B00,BFE238'}
for aspect, tag, w in (('16:9', 'wide16', '796'), ('21:9', 'wide21', '1024')):
    d = root / tag / 'depth'; d.mkdir(parents=True, exist_ok=True)
    os.environ['ROGUESQ_FLOOR_DEPTH_DIR'] = str(d); os.environ['ROGUESQ_FLOOR_WATCH'] = W[tag]
    s = b.run_arm(aspect, tag, w, root)
    fr = {os.path.basename(p): rn.score(*rn.load(p)).get('vhf') for p in sorted(glob.glob(str(root / tag / f'fbd/*_w{w}.ppm')))}
    print(tag, s['seconds'], s['crashlines'], fr, flush=True)
