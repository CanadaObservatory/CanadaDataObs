from _colour_opt import *
import json

ADJ = set(map(frozenset, [
    ('YT','BC'),('YT','NT'),('NT','BC'),('NT','AB'),('NT','SK'),('NT','NU'),
    ('NU','MB'),('BC','AB'),('AB','SK'),('SK','MB'),('MB','ON'),('ON','QC'),
    ('QC','NL'),('QC','NB'),('NB','NS'),('NB','PE'),('NS','PE'),
]))

def run(tag, hue, Lb, Cb, seeds, iters=160000):
    items=list(hue.keys()); best=None
    for s in seeds:
        hexes,(rep,adjrep)=optimise_fast(items,{},hue,Lb,Cb,ADJ,15,15,cvd_all=False,seed=s,iters=iters)
        norm=rep['normal'][0]
        adjc=min(adjrep['deuteranopia'][0],adjrep['protanopia'][0])
        gcvd=min(rep['deuteranopia'][0],rep['protanopia'][0])
        feas=(norm>=15) and (adjc>=15)
        key=(feas, gcvd if feas else norm+adjc)
        if best is None or key>best[0]: best=(key,hexes,rep,adjrep,norm,adjc,gcvd)
    key,hexes,rep,adjrep,norm,adjc,gcvd=best
    print(f'== {tag} ==  feasible={key[0]}')
    print(f'  normal-all min      {norm:.2f}  {rep["normal"][1]}')
    print(f'  adjacency deut min {adjrep["deuteranopia"][0]:.2f}  {adjrep["deuteranopia"][1]}')
    print(f'  adjacency prot min {adjrep["protanopia"][0]:.2f}  {adjrep["protanopia"][1]}')
    print('  flags',line_flags([hexes[c] for c in items],items))
    for c in items: print('   ',c,hexes[c],[round(x,1) for x in lab2lch(hex2lab(hexes[c]))])
    json.dump(hexes,open(f'_prov_{tag}.json','w'))
    return hexes

# ALTERNATIVE province bands (muted cartographic; bluer spruce, deeper cobalt, reshuffled Atlantic/North)
hue=dict(ON=(28,46),QC=(258,280),BC=(130,150),AB=(66,84),NS=(184,200),
         MB=(28,50),SK=(50,66),NB=(158,178),NL=(200,220),PE=(206,226),
         YT=(236,258),NT=(224,250),NU=(286,320))
Lb=dict(ON=(53,60),QC=(34,43),BC=(36,46),AB=(56,64),NS=(49,58),
        MB=(33,42),SK=(45,53),NB=(38,47),NL=(40,49),PE=(61,68),
        YT=(40,48),NT=(54,61),NU=(48,58))
Cb=dict(ON=(34,52),QC=(34,54),BC=(30,50),AB=(42,62),NS=(26,48),
        MB=(28,50),SK=(40,60),NB=(28,50),NL=(26,46),PE=(30,48),
        YT=(10,26),NT=(8,22),NU=(18,38))
run('alt',hue,Lb,Cb,seeds=[0,1,2,3,4,5,6,7])
