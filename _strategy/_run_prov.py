from _colour_opt import *
import json, sys

ADJ = set(map(frozenset, [
    ('YT','BC'),('YT','NT'),('NT','BC'),('NT','AB'),('NT','SK'),('NT','NU'),
    ('NU','MB'),('BC','AB'),('AB','SK'),('SK','MB'),('MB','ON'),('ON','QC'),
    ('QC','NL'),('QC','NB'),('NB','NS'),('NB','PE'),('NS','PE'),
]))

def run(tag, hue, Lb, Cb, seeds, iters=90000):
    items=list(hue.keys())
    best=None
    for s in seeds:
        hexes,(rep,adjrep)=optimise_fast(items,{},hue,Lb,Cb,ADJ,
                                    normal_floor=15,cvd_floor=15,cvd_all=False,
                                    seed=s,iters=iters)
        # score: feasibility first (normal min & adjacency cvd min), then global cvd min
        norm=rep['normal'][0]
        adjc=min(adjrep['deuteranopia'][0],adjrep['protanopia'][0])
        gcvd=min(rep['deuteranopia'][0],rep['protanopia'][0])
        feas = (norm>=15) and (adjc>=15)
        key=(feas, gcvd if feas else norm+adjc)
        if best is None or key>best[0]:
            best=(key,hexes,rep,adjrep,norm,adjc,gcvd)
    key,hexes,rep,adjrep,norm,adjc,gcvd=best
    print(f'== {tag} ==  feasible={key[0]}')
    print(f'  normal-all min      {norm:.2f}  {rep["normal"][1]}')
    print(f'  deut-all  min      {rep["deuteranopia"][0]:.2f}  {rep["deuteranopia"][1]}')
    print(f'  protan-all min     {rep["protanopia"][0]:.2f}  {rep["protanopia"][1]}')
    print(f'  adjacency deut min {adjrep["deuteranopia"][0]:.2f}  {adjrep["deuteranopia"][1]}')
    print(f'  adjacency prot min {adjrep["protanopia"][0]:.2f}  {adjrep["protanopia"][1]}')
    print('  flags',line_flags([hexes[c] for c in items],items))
    for c in items: print('   ',c,hexes[c],[round(x,1) for x in lab2lch(hex2lab(hexes[c]))])
    json.dump(hexes,open(f'_prov_{tag}.json','w'))
    return hexes

# RECOMMENDED province bands (Okabe/spectral-matte regional themes)
hue=dict(ON=(20,44),QC=(255,282),BC=(130,152),AB=(76,94),NS=(184,202),
         MB=(28,52),SK=(52,68),NB=(155,174),NL=(200,222),PE=(206,228),
         YT=(232,256),NT=(228,260),NU=(286,320))
Lb=dict(ON=(52,59),QC=(40,50),BC=(36,46),AB=(56,64),NS=(49,58),
        MB=(34,43),SK=(45,53),NB=(38,47),NL=(40,49),PE=(59,67),
        YT=(43,50),NT=(58,66),NU=(44,55))
Cb=dict(ON=(36,56),QC=(36,58),BC=(30,52),AB=(42,64),NS=(28,50),
        MB=(28,52),SK=(40,62),NB=(30,52),NL=(26,48),PE=(22,44),
        YT=(10,26),NT=(10,26),NU=(18,38))
run('rec',hue,Lb,Cb,seeds=[0,1,2,3,4,5],iters=160000)
