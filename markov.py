#!/usr/bin/python
import cgi
import pandas as pd
import scipy.stats as stats
import csv
import numpy as np
from collections import Counter

fs = cgi.FieldStorage()

all_pat = pd.read_excel('/Users/Confetti/Documents/pathways.xlsx',sheetname='ibc_pos',header=None) #CHANGE

all_paths = {}
for index, row in all_pat.iterrows():
    all_paths[row[1]] = row[0]

all_sites = []
for path in all_paths: #create all_sites generally
    path_temp = str(path).split("|")
    for site in path_temp:
        if site not in all_sites and site != "Left Study" and site !="Living" and site !="Deceased":
            all_sites.append(site)
              
mdict = {}
idict = {}

for site1 in all_sites: 
    for site2 in all_sites: #end up with all combinations of sites
        #concentrating on one transition
        trans = site1 + ' to ' + site2
        usedpaths = []
        patarr = []
        for path in all_paths: #look at each path
            path_temp = str(path).split("|")
            if site1 in path_temp:
                site1_index = [i for i, x in enumerate(path_temp) if x == site1] #get all instances of site1
                for ind in site1_index:
                    if path_temp[ind+1] == site2: #if this path has site1 -> site2 transition
                        ct_site1 = 0.0
                        ct_site2 = 0.0
                        #now looking only at paths of interest
                        path_trunc = "|".join(path_temp[0:ind+2]) #element of transition (+1 to capture ind)
                        path_trunc2 = "|".join(path_temp[0:ind+1])
                        if path_trunc in usedpaths: #skip over if already calculated
                            continue
                        usedpaths = usedpaths + [path_trunc]     
                        for path2 in all_paths: #count all of path_trunc
                            if str(path2).startswith(path_trunc2):
                                ct_site1 = ct_site1 + all_paths[path2] #count site1 number
                                if str(path2).startswith(path_trunc):
                                    ct_site2 = ct_site2 + all_paths[path2]; #count site2 number
                        prob = ct_site2 / ct_site1    #calculate individual transition prob
                        idict[trans + ' of ' + path_trunc] = (prob, ct_site2) 
                        patarr.append(prob) 
        if len(patarr) == 0:  
            continue              
        trans_prob = sum(patarr) / len(patarr)
        patarr_np = np.array(patarr)
        trans_stdev = np.std(patarr_np)
        mdict[trans] = (trans_prob, trans_stdev)
        print trans, trans_prob, trans_stdev
    

#print to csv
mdict_top = Counter(mdict).most_common()
idict_top = Counter(idict).most_common()
marr = []
iarr = []
for path in mdict_top:
    s = path[1][0]
    t = path[1][1]
    u = path[0]
    marr = marr + [[u,s,t]]
for path in idict_top:
    s = path[1][0]
    t = path[1][1]
    u = path[0]
    iarr = iarr + [[u,s,t]]

with open('/Users/Confetti/Documents/Research/markov/markov_ibc_pos.csv', 'wb') as f: #CHANGE
    writer = csv.writer(f, delimiter=',')
    for key in marr:
        writer.writerow(key)

with open('/Users/Confetti/Documents/Research/markov/markov_ind_ibc_pos.csv', 'wb') as f: #CHANGE
    writer = csv.writer(f, delimiter=',')
    for key in iarr:
        writer.writerow(key) 
