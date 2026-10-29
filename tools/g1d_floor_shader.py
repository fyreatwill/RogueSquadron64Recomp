"""Capture actual per-primitive GPU fragment fields and their bound textures.

Independent RDP varying semantics:
https://www.libretro.com/index.php/parallel-rdp-how-the-upscaled-rendering-works/
This is a runtime witness, not an independent implementation of the GPU/RDP.
"""
import argparse
import json
import os
from pathlib import Path
import statistics
import struct

import g1d_floor_inputs as base
import g1d_floor_pipe as pipe

FIELDS = ('key', 'uv', 'smooth', 'shade', 'tex0', 'combiner', 'result', 'alpha',
          'tile', 'dimensions', 'control', 'tex1', 'modes', 'selected')
RECORD = struct.Struct('<I56f')


def records(path):
    data = path.read_bytes()
    assert len(data) % RECORD.size == 0, path
    out = []
    for values in RECORD.iter_unpack(data):
        slot = values[0]
        fields = {name: values[1+i*4:5+i*4] for i, name in enumerate(FIELDS)}
        fields.update(slot=slot, col=(slot % 142)//71, y=180+slot%71, order=slot//142)
        out.append(fields)
    return out


def luma(rgb):
    return sum(c*w for c,w in zip(rgb, (.2126,.7152,.0722)))


def row_step(pixels):
    return [statistics.mean(abs(luma(pixels[(col,y+1)])-luma(pixels[(col,y)]))
                            for y in range(180,250)) for col in (0,1)]


def texture_gray(meta, raw):
    if meta['bpp'] not in (4,8):
        return None
    px = pipe.pixels(dict(meta, native_width=meta['width']), raw, 'gpu')
    return max(max(px(x,y))-min(px(x,y)) for y in range(meta['height']) for x in range(meta['width']))


def analyze_arm(root, tag):
    folder = root/tag/'shader'
    rows = []
    for path in sorted(folder.glob('shader_*.json')):
        meta = json.loads(path.read_text())
        rs = records(path.with_suffix('.records'))
        last = {}
        control_good = 0
        for r in rs:
            x = 16 if r['col']==0 else meta['width']-17
            red = ((x//2+r['y']//2)&1)==0
            control_good += all(abs(a-b)<1e-5 for a,b in zip(r['control'], (1,0,0,1) if red else (0,1,0,1)))
            key = (r['col'],r['y'])
            if key not in last or r['order'] > last[key]['order']:
                last[key] = r
        if len(last) != 142:
            continue
        snaps = {s['name']: s for s in meta['snapshots']}
        target = snaps['target']
        px = pipe.pixels(dict(target,native_width=meta['width']), path.with_suffix('.target').read_bytes(), 'gpu')
        steps = {field:row_step({key:tuple(v*255 for v in r[field][:3]) for key,r in last.items()})
                 for field in ('smooth','shade','tex0','combiner','result')}
        steps['target'] = row_step({key:px(16 if key[0]==0 else meta['width']-17,key[1]) for key in last})
        textures = {int(r['tile'][1]) for r in last.values()}
        snap_gray = {idx:texture_gray(snaps[f'tex_{idx}'], path.with_suffix(f'.tex_{idx}').read_bytes())
                     for idx in textures if f'tex_{idx}' in snaps}
        def mae(field):
            return statistics.mean(abs(max(0,min(1,v))*255-p)
                for key,r in last.items() for v,p in zip(r[field][:3],px(16 if key[0]==0 else meta['width']-17,key[1])))
        raw_wrap = sum(any(abs(a-b)>.5 for a,b in zip(r['selected'][:3],r['shade'][:3])) for r in last.values())
        texture_sample_chroma=max(max(r['tex0'][:3])-min(r['tex0'][:3]) for r in last.values())
        row = dict(meta, records=len(rs), control_good=control_good, steps=steps,
                   shader_target_mae=mae('result'), combiner_target_mae=mae('combiner'),
                   sample_chroma=texture_sample_chroma, wrapped_pixels=raw_wrap,
                   texture_ids=sorted(textures), snapshot_gray=snap_gray,
                   all_textures_captured=all(f'tex_{idx}' in snaps or f'tmem_{idx}' in snaps for idx in textures))
        ctl=snaps['control']; cpx=pipe.pixels(dict(ctl,native_width=8),path.with_suffix('.control').read_bytes(),'gpu')
        row['control_snapshot']=sum(all(abs(a-b)<1 for a,b in zip(cpx(x,y),(255,0,0) if ((x//2+y//2)&1)==0 else (0,255,0))) for y in range(8) for x in range(8))
        rows.append(row)
    assert rows, f'no full 142-pixel shader witnesses: {tag}'
    summary = dict(n=len(rows), control_good=all(r['records']==r['control_good'] and r['control_snapshot']==64 for r in rows),
                   steps={field:[statistics.median(r['steps'][field][i] for r in rows) for i in (0,1)] for field in rows[0]['steps']},
                   max_sample_chroma=max(r['sample_chroma'] for r in rows),
                   wrapped_pixels=statistics.median(r['wrapped_pixels'] for r in rows),
                   shader_target_mae=statistics.median(r['shader_target_mae'] for r in rows),
                   combiner_target_mae=statistics.median(r['combiner_target_mae'] for r in rows),
                   textures_captured=all(r['all_textures_captured'] for r in rows),
                   max_snapshot_chroma=max((v for r in rows for v in r['snapshot_gray'].values() if v is not None),default=None))
    summary['selected']=max(rows,key=lambda r:sum(r['steps']['target']))
    (root/tag/'shader_summary.json').write_text(json.dumps(dict(summary=summary,rows=rows),indent=2)+'\n')
    return summary


def sheet(root, arms):
    from PIL import Image, ImageDraw
    out=Image.new('RGB',(1044,800),'#202020'); d=ImageDraw.Draw(out)
    for col,(tag,arm) in enumerate(arms.items()):
        m=arm['selected']; folder=root/tag/'shader'; stem=folder/f"shader_{m['serial']}"
        sm=next(s for s in m['snapshots'] if s['name']=='target')
        px=pipe.pixels(dict(sm,native_width=m['width']),stem.with_suffix('.target').read_bytes(),'gpu')
        im=Image.new('RGB',(m['width'],m['height'])); im.putdata([tuple(round(c) for c in px(x,y)) for y in range(m['height']) for x in range(m['width'])]); im.thumbnail((512,220))
        x=10+col*522;out.paste(im,(x,30)); d.text((x,8),f"{tag} frame {m['frame']} pair {m['pair']} target",fill='white')
        rs=records(stem.with_suffix('.records'));last={}
        for r in sorted(rs,key=lambda r:r['order']):last[(r['col'],r['y'])]=r
        for j,field in enumerate(('smooth','shade','tex0','combiner','result')):
            strip=Image.new('RGB',(142,71))
            strip.putdata([tuple(round(max(0,min(255,v*255))) for v in last[(c//71,y)][field][:3]) for y in range(180,251) for c in range(142)])
            y=270+j*104;out.paste(strip.resize((284,71)),(x,y));d.text((x,y-17),field,fill='white')
    out.save(root/'owner_sheet_shader.png')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--analyze',action='store_true');ap.add_argument('--output-root',type=Path,default=Path('scratch/agent/s6623_shader'))
    args=ap.parse_args();root=args.output_root.resolve()
    if not args.analyze:
        for aspect,tag,w in [('16:9','wide16',796),('21:9','wide21',1024)]:
            for sub in ('shader','pipe'):(root/tag/sub).mkdir(parents=True,exist_ok=True)
            os.environ['ROGUESQ_FLOOR_SHADER_DIR']=str(root/tag/'shader')
            os.environ['ROGUESQ_FLOOR_PIPE_DIR']=str(root/tag/'pipe')
            base.run_arm(aspect,tag,w,root)
    arms={tag:analyze_arm(root,tag) for tag in ('wide16','wide21')}
    controls=all(a['control_good'] and a['textures_captured'] for a in arms.values())
    ratios={f:[arms['wide21']['steps'][f][i]/max(.001,arms['wide16']['steps'][f][i]) for i in (0,1)] for f in arms['wide16']['steps']}
    verdict='H-witness'
    if controls:
        if arms['wide21']['max_sample_chroma']>.05: verdict='H-binding-single-source'
        elif min(ratios['result'])>2 and arms['wide21']['shader_target_mae']<12: verdict='H-shader-single-source'
        elif min(ratios['target'])>2 and max(ratios['result'])<1.5: verdict='H-backend-single-source'
        else:verdict='unresolved'
    result=dict(selects=verdict,controls=controls,ratios=ratios,arms=arms)
    (root/'shader_verdict.json').write_text(json.dumps(result,indent=2)+'\n');sheet(root,arms)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
