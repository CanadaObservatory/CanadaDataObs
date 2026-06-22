from _colour_opt import *
import json, itertools

FOCAL_ORDER=['CAN','USA','DEU','AUS','GBR','SWE']
TAIL_ORDER=['JPN','FRA','ITA','KOR','NLD','CHE','NOR','DNK','FIN','ISR','NZL']
PROV_ORDER=['ON','QC','BC','AB','NS','MB','SK','NB','NL','PE','YT','NT','NU']
PRIORITY={'ON','QC','BC','AB','NS'}
ADJ=set(map(frozenset,[('YT','BC'),('YT','NT'),('NT','BC'),('NT','AB'),('NT','SK'),
 ('NT','NU'),('NU','MB'),('BC','AB'),('AB','SK'),('SK','MB'),('MB','ON'),('ON','QC'),
 ('QC','NL'),('QC','NB'),('NB','NS'),('NB','PE'),('NS','PE')]))

def grpmin(codes,hexes,modes=MODES):
    out={}
    for m in modes:
        mm=1e9;wp=None
        for a,b in itertools.combinations(codes,2):
            d=ciede2000(cvd_lab(hexes[a],m),cvd_lab(hexes[b],m))
            if d<mm:mm=d;wp=(a,b)
        out[m]=(mm,wp)
    return out

def adjmin(hexes):
    out={}
    for m in ['deuteranopia','protanopia']:
        mm=1e9;wp=None
        for fs in ADJ:
            a,b=tuple(fs)
            d=ciede2000(cvd_lab(hexes[a],m),cvd_lab(hexes[b],m))
            if d<mm:mm=d;wp=(a,b)
        out[m]=(mm,wp)
    return out

def tailmin_vs_focal(tails,focal):
    wn=1e9;wnp=None
    for tc in tails:
        for fc in focal:
            d=ciede2000(hex2lab(tails[tc]),hex2lab(focal[fc]))
            if d<wn:wn=d;wnp=(tc,fc)
    return wn,wnp

def report(name,focal,tails,prov):
    print(f'\n========== {name} ==========')
    fm=grpmin(FOCAL_ORDER,focal)
    print('FOCAL-6 mutual:')
    for m in MODES: print(f'   {m:13s} {fm[m][0]:6.2f}  {fm[m][1]}')
    pm=grpmin(PROV_ORDER,prov)
    print('PROVINCES (13) mutual:')
    for m in MODES: print(f'   {m:13s} {pm[m][0]:6.2f}  {pm[m][1]}')
    am=adjmin(prov)
    print('PROVINCE ADJACENCY (17 pairs):')
    for m in ['deuteranopia','protanopia']: print(f'   {m:13s} {am[m][0]:6.2f}  {am[m][1]}')
    wn,wnp=tailmin_vs_focal(tails,focal)
    print(f'TAIL vs FOCAL (normal): {wn:.2f}  {wnp}')
    allhex={**focal,**tails,**prov}
    fl=line_flags(list(allhex.values()),list(allhex.keys()))
    print('LINE FLAGS:',fl if fl else 'none')
    # PASS gate
    gate=(fm['normal'][0]>=15 and fm['deuteranopia'][0]>=15 and fm['protanopia'][0]>=15
          and pm['normal'][0]>=15
          and am['deuteranopia'][0]>=15 and am['protanopia'][0]>=15
          and wn>=15 and not fl)
    print('PASS:',gate)
    return dict(focal=fm,prov=pm,adj=am,tailvsfocal=(wn,wnp),flags=fl,passes=gate)

def pack(focal,tail,prov,themes):
    countries=[{'code':c,'hex':focal[c].upper(),'tier':'focal'} for c in FOCAL_ORDER]
    countries+=[{'code':c,'hex':tail[c].upper(),'tier':'tail'} for c in TAIL_ORDER]
    provinces=[{'code':c,'hex':prov[c].upper(),'priority':c in PRIORITY,'theme':themes[c]} for c in PROV_ORDER]
    return dict(countries=countries,provinces=provinces)

THEMES_REC=dict(ON='terracotta',QC='cobalt',BC='spruce',AB='wheat-gold',NS='sea-teal',
 MB='russet-earth',SK='ochre-clay',NB='petrol-green',NL='deep-blue-teal',PE='aqua',
 YT='slate',NT='arctic-blue-grey',NU='violet-grey')
THEMES_ALT=THEMES_REC.copy()
