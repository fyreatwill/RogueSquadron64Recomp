"""Join one GPU target, converted native buffer and swapped RDRAM writeback.

The GPU-uploaded red/green checker is at x/y 32..39, outside floor samples.
Diagnostic captures deliberately alter those 64 pixels; retail is unchanged.
GPU samples follow FbWriteColorCS.Load integer coordinates, without rescaling.
"""
import json
import os
from pathlib import Path
import statistics
import re
import sys
import g1d_floor_inputs as base

ROOT = Path.cwd() / 'scratch/agent/s6622_pipe'


def pixels(meta, raw, stage):
    w = meta['native_width']
    def px(x, y):
        if stage == 'gpu':
            bpp = meta['bpp']
            offset = y * meta['pitch'] + x * bpp
            if bpp == 4:
                return tuple(raw[offset:offset+3])
            return tuple(int.from_bytes(raw[offset+c*2:offset+c*2+2], 'little') / 257 for c in range(3))
        offset = ((y-meta['row_start']) * w + x) * 2
        if stage == 'ram':
            v = (raw[offset ^ 3] << 8) | raw[(offset+1) ^ 3]
        else:
            v = int.from_bytes(raw[offset:offset+2], 'big')
        r, g, b = v >> 11, (v >> 6) & 31, (v >> 1) & 31
        return tuple((c << 3) | (c >> 2) for c in (r,g,b))
    return px


def step(px, w):
    def luma(p):
        return sum(c*v for c,v in zip((.2126,.7152,.0722),p))
    return [sum(abs(luma(px(x,y+1))-luma(px(x,y))) for y in range(180,250))/70 for x in (16,w-17)]


def checker(px):
    good = 0
    for y in range(32,40):
        for x in range(32,40):
            red = ((x//2+y//2)&1)==0
            p = px(x,y)
            good += p[0 if red else 1] >= 248 and p[1 if red else 0] <= 8 and p[2] <= 8
    return good


def analyze(tag):
    folder = ROOT/tag/'pipe'
    rows = []
    log = (ROOT/tag/'run.log').read_text(errors='replace')
    displayed = {int(m[0],16) for m in re.findall(r'\[g1d-join\].*?fb=0x([A-F0-9]+) vi_w=(796|1024) ', log)}
    for fb, source, width in re.findall(r'\[fbdump\].*?fb=0x([A-F0-9]+).*?source=0x([A-F0-9]+) width=(796|1024) height=336 ', log):
        displayed.update((int(fb,16)&0xFFFFFF,int(source,16)))
    metadata = [json.loads(p.read_text()) for p in folder.glob('pipe_*.json')]
    if not metadata:
        raise RuntimeError('no GPU capture metadata: '+tag)
    last_frame = max(m['frame'] for m in metadata)
    final = {}
    for m in metadata:
        if m['address'] in displayed and m['frame'] != last_frame:
            key = (m['frame'],m['address'])
            if key not in final or m['pair'] > final[key]['pair']:
                final[key] = m
    serials = {m['serial'] for m in final.values()}
    for path in sorted(folder.glob('pipe_*.json'),key=lambda p:int(p.stem.split('_')[1])):
        m = json.loads(path.read_text())
        if m['serial'] not in serials:
            continue
        stem = str(path.with_suffix(''))
        if not all(Path(stem+'.'+s).exists() for s in ('gpu','native','ram')):
            continue
        row = dict(m)
        pxs = {}
        for stage in ('gpu','native','ram'):
            pxs[stage] = pixels(m,Path(stem+'.'+stage).read_bytes(),stage)
            row[stage] = step(pxs[stage],m['native_width'])
            row[stage+'_control'] = checker(pxs[stage])
        row['copy_mismatches'] = sum(pxs['native'](x,y)!=pxs['ram'](x,y) for y in range(180,251) for x in (16,m['native_width']-17))
        row['gpu_native_mae'] = sum(abs(a-b) for y in range(180,251) for x in (16,m['native_width']-17) for a,b in zip(pxs['gpu'](x,y),pxs['native'](x,y)))/(142*3)
        rows.append(row)
    if not rows:
        raise RuntimeError('no complete stage captures: '+tag)
    summary = dict(n=len(rows), controls={s:min(r[s+'_control'] for r in rows) for s in ('gpu','native','ram')},
                   steps={s:[statistics.median(r[s][i] for r in rows) for i in (0,1)] for s in ('gpu','native','ram')},
                   copy_mismatches=sum(r['copy_mismatches'] for r in rows),
                   gpu_native_mae=statistics.median(r['gpu_native_mae'] for r in rows))
    # Keep a complete, visibly torn frame when available, with all stages together.
    selected = max(rows,key=lambda r:sum(r['native']))
    stem=folder/f"pipe_{selected['serial']}"
    for stage in ('gpu','native','ram'):
        px=pixels(selected,Path(str(stem)+'.'+stage).read_bytes(),stage)
        w,h=selected['native_width'],selected['row_end']
        rgb=bytearray()
        for y in range(h):
            for x in range(w):
                rgb.extend(round(min(255,max(0,c))) for c in px(x,y))
        (ROOT/tag/(stage+'.ppm')).write_bytes(f'P6\n{w} {h}\n255\n'.encode()+rgb)
    summary['selected']=selected
    (ROOT/tag/'pipe_summary.json').write_text(json.dumps(dict(summary=summary,rows=rows),indent=2)+'\n')
    return summary


def main():
    if '--analyze' not in sys.argv:
        for aspect,tag,w in [('16:9','wide16',796),('21:9','wide21',1024)]:
            folder=ROOT/tag/'pipe'
            folder.mkdir(parents=True,exist_ok=True)
            os.environ['ROGUESQ_FLOOR_PIPE_DIR']=str(folder)
            base.run_arm(aspect,tag,w,ROOT)
    summaries={tag:analyze(tag) for tag in ('wide16','wide21')}
    controls=all(min(s['controls'].values())==64 for s in summaries.values())
    ratios={stage:[summaries['wide21']['steps'][stage][i]/max(.001,summaries['wide16']['steps'][stage][i]) for i in (0,1)] for stage in ('gpu','native','ram')}
    selected='H-witness'
    if controls:
        if min(ratios['gpu'])>2:
            selected='H-raster-single-source'
        elif min(ratios['native'])>2:
            selected='H-convert-single-source'
        elif min(ratios['ram'])>2:
            selected='H-copy-single-source'
    from PIL import Image, ImageDraw
    sheet = Image.new('RGB',(1044,735),'#202020')
    draw = ImageDraw.Draw(sheet)
    for col,tag in enumerate(('wide16','wide21')):
        for row,stage in enumerate(('gpu','native','ram')):
            im = Image.open(ROOT/tag/(stage+'.ppm'))
            im.thumbnail((512,205))
            x,y = 10+col*522,30+row*240
            sheet.paste(im,(x,y))
            draw.text((x,y-20),f'{tag} / {stage} / serial {summaries[tag]["selected"]["serial"]}',fill='white')
    sheet.save('docs/owner_sheet_s6622_pipe.png')
    result=dict(selects=selected,controls=controls,ratios=ratios,arms=summaries)
    (ROOT/'verdict.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
