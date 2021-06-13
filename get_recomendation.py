import pandas as pd
import numpy as np
#import mlxtend
import scipy as sp
#import swifter
import os
import gc
import re

from os import listdir
from os.path import isfile, join
import json
import gzip


with gzip.open('./data/dict_sosedi.json.gz', 'r') as d:
     name_to_id =json.load(d)
        
res_assoc = pd.read_csv('./data/res_assoc.csv.gz', sep=';',compression='gzip')
res_assoc['consequents']=res_assoc['consequents'].map(lambda x: set([re.sub("'", '', st) for st in re.sub("[{}]",'', x).split("', ")]))
res_assoc['antecedents']=res_assoc['antecedents'].map(lambda x: set([re.sub("'", '', st) for st in re.sub("[{}]",'', x).split("', ")]))
all_avg = pd.read_csv('./data/train_points_with_prohod.csv', sep=';')

def get_top_k_from_len(d):
    len_d = d.len_ant.unique()
    for i,l in enumerate(len_d):
        if i==0:
            cands = d[d.len_ant==l].sort_values('cum_score', ascending=False)[:50].reset_index(drop=True)
        else:
            cand = d[d.len_ant==l].sort_values('cum_score', ascending=False)[:50].reset_index(drop=True)
            cands= pd.concat([cands, cand],axis=0, ignore_index=True)
    return cands

def get_best_intersec_points(zapros, 
                             name_to_id=name_to_id,
                             res_assoc=res_assoc,
                             day_flag=True,  #FLAG TRUE - day FALSE-Night
                             day_l=0, #low day bound
                             day_u=99999, #up day bound
                             night_l=0, #low night bound
                             might_u=99999  #up night bound
                             ):
    antecedents = res_assoc[res_assoc.consequents.map(lambda x: zapros in x)]

    consequents = res_assoc[res_assoc.antecedents.map(lambda x: zapros in x)]
    
    intersec = {'inter':[], 'id': [], 'cum_score':[], 'consequents':[]}
    
    if len(antecedents.index)>0:
        antecedents = get_top_k_from_len(antecedents)
        aim_cols = 'antecedents'
    elif len(consequents.index)>0:
        antecedents = get_top_k_from_len(consequents)
        aim_cols = 'consequents'
    else:
        aim_cols = 'self'
    
    for k in name_to_id.keys():
        s = set(name_to_id[k]['set_neighbors'])
        
        traf_d = name_to_id[k]['prohod_d']
        traf_n = name_to_id[k]['prohod_n']
        
        if day_flag and traf_d<=day_l and traf_d>=day_u:
            continue
        elif day_flag and traf_d>=day_l and traf_d<=day_u:
            traf = traf_d
        elif day_flag==False and traf_n<=night_l and traf_d>=night_u:
            continue
        elif day_flag==False and traf_d>=night_l and traf_d<=day_u:
            traf = traf_n
        else:
            traf = name_to_id[k]['prohod_all']
        
        if aim_cols == 'self':
            inter = -1*name_to_id[k]['name_neighbors'].count(zapros)
            max_inter = -1*inter
            intersec['consequents'] += [zapros]
        else:
            inter = antecedents[aim_cols].map(lambda x: len(x.intersection(s))).values
            max_inter = inter[np.argmax(inter)]
            intersec['consequents'] += [antecedents.consequents[np.argmax(inter)]]
        
        intersec['id'].append(int(k))
        intersec['inter'].append(max_inter)
        conc = name_to_id[k]['name_neighbors'].count(zapros)
        intersec['cum_score']+= [0.6*traf/1000 + 0.4*max_inter-conc]
        
        
    intersec['id']= np.array(intersec['id'])
    intersec['cum_score'] = np.array(intersec['cum_score'])
    intersec['consequents'] = np.array(intersec['consequents'])
    intersec['inter'] = np.array(intersec['inter'])
    best_id = intersec['id'][np.argsort(-1*intersec['cum_score'])[:20]]

    consec = intersec['consequents'][best_id]
    lat = all_avg.iloc[best_id]['lat'].values
    long = all_avg.iloc[best_id]['long'].values
    
    lat_sosed = [name_to_id[str(k)]['lat_sosed'] for k in best_id] 
    long_sosed = [name_to_id[str(k)]['long_sosed'] for k in best_id] 

    names_conc = [name_to_id[str(k)]['name_neighbors'] for k in best_id]
    
    score = intersec['cum_score'][best_id]
    conc_cnt = [name_to_id[str(k)]['name_neighbors'].count(zapros) for k in best_id]
    
    return {'lat':lat, 'long':long, 
            'concurents_cnt': conc_cnt,
            'lat_concurent':lat_sosed, 
            'long_concurent':long_sosed,
            'name_concurent':names_conc}