import csv,sys,statistics as st
for p in sys.argv[1:]:
    r=list(csv.DictReader(open(p)))
    last=max(int(x['pframe']) for x in r)
    for lab,f in (('all',lambda x:True),('ok',lambda x:0<int(x['pframe'])<last)):
        s=[x for x in r if f(x)]
        m=sorted(float(x['meand']) for x in s); fr=sorted(float(x['frac_over_T']) for x in s)
        q=lambda a,p:a[min(len(a)-1,int(p*len(a)))]
        out=[x for x in s if float(x['frac_over_T'])>0.05]
        print(p,lab,len(s),'meand %.2f/%.2f/%.2f'%(q(m,.5),q(m,.9),m[-1]),'frac %.3f/%.3f/%.3f'%(q(fr,.5),q(fr,.9),fr[-1]),'>0.05',len(out),[(x['swap'],x['pframe'],x['frac_over_T']) for x in out][:8])
    if 'frac_c' in r[0]:
        s=[x for x in r if 0<int(x['pframe'])<last]
        print('  centre frac med %.3f side frac med %.3f'%(st.median(float(x['frac_c']) for x in s),st.median(float(x['frac_s']) for x in s)))
