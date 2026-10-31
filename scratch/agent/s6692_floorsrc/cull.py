import json, os, sys, pathlib, glob
sys.path.insert(0, 'tools')
import g1d_floor_inputs as b, g1d_row_noise as rn
root = pathlib.Path('scratch/agent/s6692_floorsrc/cull').resolve()
if b.screen_locked(): raise SystemExit('screen locked')
res = {}
for tag, env in (('cull0', {'ROGUESQ_CULL_SPIKE': '0', 'ROGUESQ_LOG_SPIKE': '1'}), ('cull1', {'ROGUESQ_CULL_SPIKE': '1', 'ROGUESQ_LOG_SPIKE': '1'})):
    os.environ.update(env)
    r = root / tag
    s = b.run_arm('21:9', 'wide21', '1024', r)
    frames = {}
    for p in sorted(glob.glob(str(r / 'wide21/fbd/*_w1024.ppm'))):
        sc = rn.score(*rn.load(p)); frames[os.path.basename(p)] = sc.get('vhf', sc)
    res[tag] = dict(seconds=s['seconds'], crash=s['crashlines'], frames=frames)
    print(tag, json.dumps(res[tag]), flush=True)
(root / 'cull.json').write_text(json.dumps(res, indent=2, default=str))
