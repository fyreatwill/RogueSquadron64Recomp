"""Compare level-select floor fill words and shade alpha at 796/1024 width.

One instrumented binary, phase-driven route, last-floor samples at x=16
and x=w-17, rows 180..250. Reject verdicts unless framebuffer row steps,
prior color-input controls and a synthetic alpha/fill checker all pass.
"""
import json, os, pathlib, plistlib, re, subprocess, time

ROOT = pathlib.Path.cwd()
EXPECT_W = {'wide16': 796, 'wide21': 1024}
EXPECT = {
    'wide16': dict(dI=45.21, dL=2.95, dT=4.59),
    'wide21': dict(dI=42.15, dL=2.96, dT=4.97),
}
BL = 'cyc0f0(CC*CCA+MEM*MEMA)|(CC*CCA+MEM*MEMA)'
CC = '(T0-0)*SHADE+0'
SAMPLES = 142
COL = 71


def screen_locked():
    data = plistlib.loads(subprocess.check_output(['/usr/sbin/ioreg', '-n', 'Root', '-d1', '-a']))

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in ('CGSSessionScreenIsLocked', 'IOConsoleLocked') and value is True:
                    return True
                if walk(value):
                    return True
        elif isinstance(node, list):
            return any(walk(item) for item in node)
        return False

    return walk(data)


def read_ppm(path):
    raw = path.read_bytes()
    if not raw.startswith(b'P6\n'):
        raise SystemExit(f'not a ppm: {path}')
    i = 3
    while raw[i:i + 1] == b'#':
        i = raw.index(b'\n', i) + 1
    nl = raw.index(b'\n', i)
    w, h = (int(x) for x in raw[i:nl].split())
    i = raw.index(b'\n', nl + 1) + 1
    pix = raw[i:]
    if len(pix) < w * h * 3:
        raise SystemExit(f'short ppm {path}: {len(pix)} < {w * h * 3}')
    return w, h, pix


def outer_dy(path):
    w, h, pix = read_ppm(path)
    xs = list(range(0, w // 3)) + list(range((2 * w) // 3, w))
    if h < 251 or not xs:
        return None
    acc = 0.0
    n = 0
    for y in range(180, 250):
        o0 = y * w * 3
        o1 = (y + 1) * w * 3
        for x in xs:
            p0 = o0 + x * 3
            p1 = o1 + x * 3
            l0 = pix[p0] * 0.2126 + pix[p0 + 1] * 0.7152 + pix[p0 + 2] * 0.0722
            l1 = pix[p1] * 0.2126 + pix[p1 + 1] * 0.7152 + pix[p1 + 2] * 0.0722
            acc += abs(l0 - l1)
            n += 1
    return round(acc / n, 2) if n else None


def column_step(path, xs):
    w, h, pix = read_ppm(path)
    if h < 251:
        return None
    out = []
    for x in xs:
        if x < 0 or x >= w:
            return None
        acc = 0.0
        n = 0
        for y in range(180, 250):
            p0 = (y * w + x) * 3
            p1 = ((y + 1) * w + x) * 3
            l0 = pix[p0] * 0.2126 + pix[p0 + 1] * 0.7152 + pix[p0 + 2] * 0.0722
            l1 = pix[p1] * 0.2126 + pix[p1 + 1] * 0.7152 + pix[p1 + 2] * 0.0722
            acc += abs(l0 - l1)
            n += 1
        out.append(round(acc / n, 2) if n else None)
    return out


def grab(line, pat, cast=float):
    m = re.search(pat, line)
    return cast(m.group(1)) if m else None


def parse_frame(line):
    if not line.startswith('[floor-tex] why='):
        return None
    keys = (
        ('nFs', r'\bnFs=(\d+)', int),
        ('nFw', r'\bnFw=(\d+)', int),
        ('fw', r'\bfw=([A-F0-9]+)', lambda x: int(x,16)),
        ('dF', r'\bdF=([-\d.]+)', float),
        ('nFp', r'\bnFp=(\d+)', int),
        ('dA', r'\bdA=([-\d.]+)', float),
        ('nAa', r'\bnAa=(\d+)', int),
        ('cca', r'\bcca=(\S+)', str),
        ('ccaN', r'\bccaN=(\d+)', int),
        ('why', r'why=([A-Za-z0-9_-]+)', str),
        ('w', r'\bw=(\d+)', int),
        ('floor_frac', r'floor_frac=([-\d.]+)', float),
        ('other_frac', r'other_frac=([-\d.]+)', float),
        ('dT', r'\bdT=([-\d.]+)', float),
        ('npair', r'npair=(\d+)', int),
        ('badw', r'badw=(\d+)', int),
        ('dL', r'\bdL=([-\d.]+)', float),
        ('nL', r'\bnL=(\d+)', int),
        ('nS', r'\bnS=(\d+)', int),
        ('cc', r'\bcc=(\S+)', str),
        ('dI', r'\bdI=([-\d.]+)', float),
        ('nI', r'\bnI=(\d+)', int),
        ('untex', r'\buntex=([-\d.]+)', float),
        ('bl', r'\bbl=(\S+)', str),
        ('x0', r'\bx0=([-\d.]+)', float),
        ('x1', r'\bx1=([-\d.]+)', float),
        ('lastF', r'lastF=([-\d.]+)', float),
        ('lastO', r'lastO=([-\d.]+)', float),
        ('lastR', r'lastR=([-\d.]+)', float),
        ('lastN', r'lastN=([-\d.]+)', float),
        ('nF', r'\bnF=(\d+)', int),
        ('nO', r'\bnO=(\d+)', int),
        ('nR', r'\bnR=(\d+)', int),
        ('nZ', r'\bnZ=(\d+)', int),
        ('both', r'\bboth=([-\d.]+)', float),
        ('touchR', r'touchR=([-\d.]+)', float),
        ('touchU', r'touchU=([-\d.]+)', float),
        ('over', r'\bover=([-\d.]+)', float),
        ('nFL', r'\bnFL=(\d+)', int),
        ('nOL', r'\bnOL=(\d+)', int),
        ('nRL', r'\bnRL=(\d+)', int),
        ('nFR', r'\bnFR=(\d+)', int),
        ('nOR', r'\bnOR=(\d+)', int),
        ('nRR', r'\bnRR=(\d+)', int),
    )
    out = {}
    for name, pat, cast in keys:
        out[name] = grab(line, pat, cast)
    if out['nF'] is None:
        return None
    return out


def rel(a, b):
    hi = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / hi


def agrees(a, b):
    return rel(a, b) <= 0.25


def pool(frames):
    kept = [f for f in frames
            if f and f['why'] == 'frame' and (f['floor_frac'] or 0) >= 0.90
            and (f['npair'] or 0) >= 100 and f.get('dL') is not None
            and f.get('dI') is not None and f.get('nF') is not None
            and f.get('bl') and None not in (f['nF'], f['nO'], f['nR'], f['nZ'])
            and (f['nF'] + f['nO'] + f['nR'] + f['nZ']) == SAMPLES]
    if not kept:
        return None

    def wmean(key, weight):
        den = sum(f[weight] or 0 for f in kept)
        if not den:
            return None
        return sum((f[key] or 0) * (f[weight] or 0) for f in kept) / den

    def mean(key):
        return sum(f[key] or 0 for f in kept) / len(kept)

    n = len(kept)
    den = SAMPLES * n
    nF = sum(f['nF'] for f in kept)
    nO = sum(f['nO'] for f in kept)
    nR = sum(f['nR'] for f in kept)
    nZ = sum(f['nZ'] for f in kept)

    def col(key):
        return sum(f[key] for f in kept) / (COL * n)

    return dict(
        nframes=n,
        nFs=sum(f['nFs'] or 0 for f in kept),
        nFw_max=max(f['nFw'] or 0 for f in kept),
        fw=sorted({f['fw'] for f in kept}),
        dF=wmean('dF','nFp'), dA=wmean('dA','nAa'),
        nAa=sum(f['nAa'] or 0 for f in kept),
        cca=sorted({f['cca'] for f in kept if f['cca']}),
        ccaN_max=max(f['ccaN'] or 0 for f in kept),
        npair=sum(f['npair'] for f in kept),
        nL=sum(f['nL'] or 0 for f in kept),
        floor_frac=mean('floor_frac'),
        untex=mean('untex'),
        dT=wmean('dT', 'npair'),
        dL=wmean('dL', 'nL'),
        dI=wmean('dI', 'nI'),
        badw=sum(f['badw'] or 0 for f in kept),
        cc=kept[0]['cc'] if len({f['cc'] for f in kept}) == 1 else 'mixed',
        bl=kept[0]['bl'] if len({f['bl'] for f in kept}) == 1 else 'mixed',
        x0=kept[0]['x0'],
        x1=kept[0]['x1'],
        x0_n=len({f['x0'] for f in kept}),
        x1_n=len({f['x1'] for f in kept}),
        lastF=nF / den, lastO=nO / den, lastR=nR / den, lastN=nZ / den,
        both=mean('both'), touchR=mean('touchR'), touchU=mean('touchU'), over=mean('over'),
        lastFL=col('nFL'), lastOL=col('nOL'), lastRL=col('nRL'),
        lastFR=col('nFR'), lastOR=col('nOR'), lastRR=col('nRR'),
        nF=nF, nO=nO, nR=nR, nZ=nZ,
    )


def controls(arm):
    why = []
    if arm.get('dy180') is None:
        why.append('dy-missing')
    if arm.get('selftest_ok') != 1:
        why.append('selftest')
    p = arm.get('pool')
    if not p:
        why.append('no-pool')
        return why
    if p['nframes'] < 20:
        why.append('short')
    if p['badw'] != 0:
        why.append('badw')
    if (p['floor_frac'] or 0) < 0.90:
        why.append('floor-frac')
    if (p['both'] or 0) < 0.90:
        why.append('overlap')
    tag = arm.get('arm')
    exp = EXPECT[tag]
    if p['dI'] is None or not agrees(p['dI'], exp['dI']):
        why.append('dI')
    if p['dL'] is None or not agrees(p['dL'], exp['dL']):
        why.append('dL')
    if p['dT'] is None or not agrees(p['dT'], exp['dT']):
        why.append('walker-dT')
    if p['cc'] != CC:
        why.append('cc')
    if p['bl'] != BL:
        why.append('blender')
    if p.get('x0') is None or abs(p['x0'] - 16.0) > 0.05 or p.get('x0_n') != 1:
        why.append('x0')
    expect_x1 = EXPECT_W[tag] - 17
    if p.get('x1') is None or abs(p['x1'] - expect_x1) > 0.05 or p.get('x1_n') != 1:
        why.append('x1')
    if abs((p['lastF'] + p['lastO'] + p['lastR'] + p['lastN']) - 1.0) > 0.001:
        why.append('last-sum')
    if p['touchR'] >= 0.50 and (p['over'] + p['lastR']) < (p['touchR'] - 0.05):
        why.append('rect-stamp')
    el, er = arm.get('edge_l'), arm.get('edge_r')
    if el is None or er is None:
        why.append('edge-missing')
    elif tag == 'wide16' and not (el < 12 and er < 12):
        why.append('edge-px')
    elif tag == 'wide21' and not (el > 30 and er > 30):
        why.append('edge-px')
    dy = arm.get('dy180')
    if dy is not None:
        if tag == 'wide16' and not dy < 12:
            why.append('dy')
        if tag == 'wide21' and not dy > 18:
            why.append('dy')
    return why


def decide(a, b):
    out = dict(fail16=controls(a), fail21=controls(b))
    for arm in (a,b):
        p=arm['pool']
        if not p or p['nFs'] != SAMPLES*p['nframes'] or p['nAa'] != 140*p['nframes'] or not p['cca']:
            out['fail16' if arm['arm']=='wide16' else 'fail21'].append('alpha-fill-incomplete')
        if arm.get('alpha_fill_control') != 1:
            out['fail16' if arm['arm']=='wide16' else 'fail21'].append('alpha-fill-selftest')
    out['arms']=[a,b]
    if out['fail16'] or out['fail21']:
        out['selects']='instrument-fail'
        return out
    p,q=a['pool'],b['pool']
    if q['nFw_max']>1 or q['dF']>2*p['dF']:
        out['selects']='H-mem'
    elif p['nFw_max']==q['nFw_max']==1 and (q['dA']>2*p['dA'] or p['cca']!=q['cca']):
        out['selects']='H-alpha'
    elif p['nFw_max']==q['nFw_max']==1 and agrees(p['dA'],q['dA']) and p['cca']==q['cca']:
        out['selects']='H-pipe-single-source'
    else:
        out['selects']='unresolved'
    return out


def arm_from_text(tag, text, dy=None):
    frames = [parse_frame(line) for line in text.splitlines() if line.startswith('[floor-tex] why=')]
    frames = [f for f in frames if f]
    self_ok = sum(1 for line in text.splitlines() if line.startswith('[floor-i4] selftest ok '))
    ctl=[f for f in frames if f['why']=='selftest-alpha-fill']
    ctl_ok=int(len(ctl)==1 and ctl[0]['nFw']==2 and ctl[0]['nFs']==142
               and ctl[0]['nAa']==140 and ctl[0]['dA']==64 and abs(ctl[0]['dF']-255)<0.01)
    return dict(arm=tag, dy180=dy, pool=pool(frames), selftest_ok=self_ok,
                alpha_fill_control=ctl_ok,
                edge_l=None, edge_r=None)


def frame_line(w, last, touchR=1.0, touchU=0.0, over=None, both=1.0, dI=None, dL=None, dT=None, bl=BL):
    exp_tag = 'wide16' if w == 796 else 'wide21'
    exp = EXPECT[exp_tag]
    if dI is None:
        dI = exp['dI']
    if dL is None:
        dL = exp['dL']
    if dT is None:
        dT = exp['dT']
    nF = min(SAMPLES, max(0, int(round(last[0] * SAMPLES))))
    nO = min(SAMPLES - nF, max(0, int(round(last[1] * SAMPLES))))
    nR = min(SAMPLES - nF - nO, max(0, int(round(last[2] * SAMPLES))))
    nZ = SAMPLES - nF - nO - nR
    if over is None:
        over = touchR if last[2] < 0.5 else 0.0
    # Left column gets the floor share, right the rect share, so a pooled
    # split is visible per column in the selftest without a second formula.
    nFL, nFR = nF // 2, nF - nF // 2
    nOL, nOR = nO // 2, nO - nO // 2
    nRL, nRR = nR // 2, nR - nR // 2
    return (
        f"[floor-tex] why=frame w={w} floor_frac=1.0000 other_frac=0.0000 multi_frac=0.0100 "
        f"dT={dT:.4f} dTl=1 dTr=1 npair=140 maxdT=4 jump4=0 jump8=0 "
        f"tex=1..2 badw=0 spill=0 dS=3.9 dL={dL:.4f} nS=140 nL=140 "
        f"cc={CC} omL=00552230 ccn=1 n0=140 n1=0 cc2=- om2=00000000 "
        f"dI={dI:.4f} nI=140 iLo=0 iHi=255 untex=1.0000 bl={bl} blu=cyc3f1(CC*0+CC*1)|(CC*0+CC*1) "
        f"x0=16.00 x1={w - 17:.2f} "
        f"lastF={nF / SAMPLES:.4f} lastO={nO / SAMPLES:.4f} lastR={nR / SAMPLES:.4f} lastN={nZ / SAMPLES:.4f} "
        f"nF={nF} nO={nO} nR={nR} nZ={nZ} "
        f"both={both:.4f} touchR={touchR:.4f} touchU={touchU:.4f} over={over:.4f} "
        f"nFL={nFL} nOL={nOL} nRL={nRL} nFR={nFR} nOR={nOR} nRR={nRR}"
    )


def selftest():
    line=frame_line(796,(1.0,0.0,0.0))+' nFs=142 nFw=1 fw=00010001 dF=0 nFp=140 dA=0 nAa=140 cca=(0-0)*0+SHADE ccaN=1'
    f=parse_frame(line)
    assert f['nFs']==142 and f['nFw']==1 and f['dA']==0 and f['cca']=='(0-0)*0+SHADE',f
    assert pool([f])['fw']==[0x00010001]
    def arm(tag):
        w=EXPECT_W[tag]
        line=frame_line(w,(1.0,0.0,0.0))+' nFs=142 nFw=1 fw=00010001 dF=0 nFp=140 dA=0.08 nAa=140 cca=(0-0)*0+0 ccaN=1'
        frames=[parse_frame(line)]*25
        return dict(arm=tag, pool=pool(frames), selftest_ok=1,
                    alpha_fill_control=1, dy180=8 if w==796 else 25,
                    edge_l=6 if w==796 else 45, edge_r=6 if w==796 else 45)
    a,b=arm('wide16'),arm('wide21')
    assert decide(a,b)['selects']=='H-pipe-single-source'
    b['pool']['nFw_max']=2
    assert decide(a,b)['selects']=='H-mem'
    b=arm('wide21');b['pool']['dA']=1
    assert decide(a,b)['selects']=='H-alpha'
    b=arm('wide21');b['pool']['cca']=['(0-0)*0+1']
    assert decide(a,b)['selects']=='H-alpha'
    b=arm('wide21');b['alpha_fill_control']=0
    assert decide(a,b)['selects']=='instrument-fail'
    print('selftest ok: parser, H-mem, H-alpha, H-pipe, rejected control',flush=True)


def run_arm(aspect, tag, width_expect, output_root=None):
    assert not screen_locked(), 'screen locked'
    out = (pathlib.Path(output_root) if output_root else ROOT / 'scratch/agent/s6620_alpha') / tag
    fbd = out / 'fbd'
    fbd.mkdir(parents=True, exist_ok=True)
    base = dict(
        ROGUESQ_OVL2C_DROP='0', ROGUESQ_SPIN_YIELD='1', ROGUESQ_LLE_FORCE='1',
        ROGUESQ_LLE_UNGATED='1', ROGUESQ_LLE_SOLO='1', ROGUESQ_STUB_MISSING_FUNCS='1',
        ROGUESQ_LOG_PHASE='1', ROGUESQ_AUDIO_UCODE='1',
        ROGUESQ_LOG_FB_FLIP_RANGE='1', ROGUESQ_FB_DUMP_EVERY='50',
        ROGUESQ_FB_DUMP_VI='1', ROGUESQ_FB_DUMP_TAIL_ROWS='0',
        PROBE_PHASE_WIDTH='512', PROBE_PHASE_TIMEOUT='240',
        PROBE_KEYS_FROM_PHASE='1', PROBE_LEAVE_OK='1',
        ROGUESQ_OSMEM_MB='12', ROGUESQ_ASPECT=aspect,
        ROGUESQ_LOG_FLOOR='1',
    )
    base['ROGUESQ_AUTOPILOT'] = ','.join(
        f'{10 + 4 * i}:{"start" if i % 2 == 0 else "z"}' for i in range(300))
    env = os.environ.copy()
    for key in ('ROGUESQ_HUD_ANCHOR', 'ROGUESQ_HUD_ANCHOR_AUTO', 'ROGUESQ_SHIFT_REGION',
                'ROGUESQ_LOG_REGION', 'ROGUESQ_DRAW_DISTANCE', 'ROGUESQ_DD_UNSAFE'):
        env.pop(key, None)
    env.update(base)
    env['ROGUESQ_FB_DUMP_DIR'] = str(fbd)
    start = time.monotonic()
    offset = 0
    pending = ''
    reason = 'timeout'
    got_dump = False
    good_frames = 0
    log_path = out / 'run.log'
    with log_path.open('wb') as log:
        proc = subprocess.Popen(
            [str(ROOT / 'build/RogueSquadron64Recomp')],
            cwd=str(ROOT / 'build'), env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            while time.monotonic() - start < 240 and proc.poll() is None:
                time.sleep(0.25)
                with log_path.open(errors='replace') as reader:
                    reader.seek(offset)
                    chunk = reader.read()
                    offset = reader.tell()
                lines = (pending + chunk).split('\n')
                pending = lines.pop()
                for line in lines:
                    if line.startswith('[floor-tex] why=frame') and 'nF=' in line and 'dI=' in line:
                        frac = grab(line, r'floor_frac=([-\d.]+)')
                        npair = grab(line, r'npair=(\d+)', int)
                        if frac is not None and frac >= 0.90 and npair and npair >= 100:
                            good_frames += 1
                    if f'width={width_expect}' in line and 'height=336' in line and '[fbdump]' in line:
                        got_dump = True
                if got_dump and good_frames >= 50:
                    reason = 'tex+dump'
                    time.sleep(0.6)
                    break
        finally:
            alive = proc.poll() is None
            if alive:
                proc.kill()
            rc = proc.wait()
    text = log_path.read_text(errors='replace')
    parsed = arm_from_text(tag, text)
    crash = sum(text.count(tok) for tok in ('[CRASH]', '[ABORT]', 'SIGSEGV', 'SIGBUS'))
    ppms = sorted(fbd.glob(f'fb_*_w{width_expect}.ppm'))
    picked = None
    best = None
    for ppm in ppms:
        m = re.search(r'fb_(\d+)_', ppm.name)
        if not m:
            continue
        n = int(m.group(1))
        dist = abs(n - 1400)
        if best is None or dist < best:
            best = dist
            picked = ppm
    dy = outer_dy(picked) if picked else None
    edge = column_step(picked, (16, int(width_expect) - 17)) if picked else None
    parsed['dy180'] = dy
    parsed['edge_l'] = edge[0] if edge else None
    parsed['edge_r'] = edge[1] if edge else None
    summary = dict(
        arm=tag, aspect=aspect, expect=width_expect,
        seconds=round(time.monotonic() - start, 1),
        alive_at_end=int(alive), rc=rc, stop=reason,
        good_frames=good_frames,
        crashlines=crash, dy180=dy,
        edge_l=parsed['edge_l'], edge_r=parsed['edge_r'],
        dy_ppm=str(picked.relative_to(ROOT)) if picked else None,
        selftest_ok=parsed['selftest_ok'], alpha_fill_control=parsed['alpha_fill_control'],
        pool=parsed['pool'],
        fail=controls(parsed),
    )
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (out / 'tex.txt').write_text('\n'.join(
        line for line in text.splitlines()
        if line.startswith('[floor-tex]') or line.startswith('[floor-cc]')
        or line.startswith('[floor-i4]')) + '\n')
    print(json.dumps({k: summary[k] for k in summary if k != 'pool'}), flush=True)
    print(json.dumps(summary['pool']), flush=True)
    return summary


def main():
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--selftest':
        selftest()
        return
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--rescore':
        root = ROOT / 'scratch/agent/s6620_alpha'
        arms = []
        for tag in ('wide16', 'wide21'):
            text = (root / tag / 'tex.txt').read_text(errors='replace')
            summary = json.loads((root / tag / 'summary.json').read_text())
            arm = arm_from_text(tag, text, summary.get('dy180'))
            arm['alpha_fill_control'] = summary.get('alpha_fill_control')
            arm['edge_l'] = summary.get('edge_l')
            arm['edge_r'] = summary.get('edge_r')
            arms.append(arm)
        verdict = decide(arms[0], arms[1])
        (root / 'verdict.json').write_text(json.dumps(verdict, indent=2) + '\n')
        print(json.dumps(verdict), flush=True)
        return
    assert not screen_locked(), 'screen locked'
    arms = [
        run_arm('16:9', 'wide16', '796'),
        run_arm('21:9', 'wide21', '1024'),
    ]
    verdict = decide(
        dict(arm='wide16', alpha_fill_control=arms[0]['alpha_fill_control'], dy180=arms[0]['dy180'], pool=arms[0]['pool'],
             selftest_ok=arms[0]['selftest_ok'], edge_l=arms[0]['edge_l'], edge_r=arms[0]['edge_r']),
        dict(arm='wide21', alpha_fill_control=arms[1]['alpha_fill_control'], dy180=arms[1]['dy180'], pool=arms[1]['pool'],
             selftest_ok=arms[1]['selftest_ok'], edge_l=arms[1]['edge_l'], edge_r=arms[1]['edge_r']),
    )
    out = ROOT / 'scratch/agent/s6620_alpha'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'verdict.json').write_text(json.dumps(verdict, indent=2) + '\n')
    print(json.dumps(verdict), flush=True)


if __name__ == '__main__':
    main()
