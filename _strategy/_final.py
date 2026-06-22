from _run_tail import *
from _assemble import report, pack, THEMES_REC, THEMES_ALT
import json

rec_focal=json.load(open('_focal.json'))
alt_focal=json.load(open('_focal_alt.json'))
rec_prov=json.load(open('_prov_rec.json'))
alt_prov=json.load(open('_prov_alt.json'))

rec_bands={
 'JPN':(4,26,48,60,34,48),'DNK':(344,360,50,62,28,46),'CHE':(28,50,36,48,28,46),
 'NLD':(54,72,54,64,34,50),'ISR':(92,108,46,56,30,46),'ITA':(112,128,42,52,30,48),
 'NZL':(130,146,38,46,30,48),'NOR':(224,244,48,60,28,44),'FRA':(252,266,46,60,30,46),
 'FIN':(286,302,42,54,26,44),'KOR':(316,342,44,58,34,50),
}
alt_bands={
 'JPN':(4,24,46,58,34,48),'DNK':(350,366,48,60,28,44),'CHE':(20,40,36,48,28,46),
 'NLD':(60,80,54,64,32,50),'ISR':(112,130,44,54,30,48),'ITA':(140,158,40,50,30,48),
 'NZL':(164,182,48,60,28,46),'NOR':(206,228,46,60,28,44),'FRA':(246,262,46,60,30,46),
 'FIN':(282,300,42,54,26,44),'KOR':(304,322,44,58,34,52),
}

def best_tail(focal,bands,seeds):
    return _bt(focal,bands,seeds)
def _bt(focal,bands,seeds):
    b=None
    for s in seeds:
        t=fit_tails_vec(focal,bands,seed=s); wn=verify_tails(focal,t)
        if b is None or wn>b[0]: b=(wn,t)
    return b[1]

print('### REC TAILS ###')
rec_tail=best_tail(rec_focal,rec_bands,[1,3,5])
print('### ALT TAILS ###')
alt_tail=best_tail(alt_focal,alt_bands,[1,3,5])

json.dump(rec_tail,open('_tail_rec.json','w'))
json.dump(alt_tail,open('_tail_alt.json','w'))

r=report('RECOMMENDED (spectral-matte)',rec_focal,rec_tail,rec_prov)
a=report('ALTERNATIVE (cartographic-earth)',alt_focal,alt_tail,alt_prov)

out=dict(recommended=pack(rec_focal,rec_tail,rec_prov,THEMES_REC),
         alternative=pack(alt_focal,alt_tail,alt_prov,THEMES_ALT))
json.dump(out,open('_assembled.json','w'),indent=1)
print('\nDONE  rec.PASS=',r['passes'],' alt.PASS=',a['passes'])
