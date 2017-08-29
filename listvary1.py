

from collections import Counter

#!/usr/bin/python

import cgi
import pandas as pd
import scipy.stats as stats
import csv

fs = cgi.FieldStorage()

all_pat = pd.read_excel('/Users/Confetti/Documents/pathways.xlsx',sheetname='bladder',header=None) #CHANGE

all_paths = {}
for index, row in all_pat.iterrows():
    all_paths[row[1]] = row[0]

#vars
NUM_PATIENTS = 0
usedpaths = []
or_adj_pair = {}
or_pair = {}
top_sites = ['Deceased'] 
all_sites = []

for path in all_paths: #create all_sites generally
    path_temp = str(path).split("|")
    for site in path_temp:
        if site not in all_sites and site != "Left Study":
            all_sites.append(site)

#remove patients who left the study at 1st 2nd or 3rd met
for k,v in all_paths.items(): 
    path_temp = str(k).split("|")
    if len(path_temp) < 4 or path_temp[3] == 'Left Study':
        del all_paths[k]

for path in all_paths: #get NUM_PATIENTS value
    NUM_PATIENTS = NUM_PATIENTS + all_paths[path]
    NUM_PATIENTS = float(NUM_PATIENTS)

#make list of first mets that each comprise less than 2.5% of patients
for site in all_sites: #check for all sites
    count = 0.0
    for path in all_paths: #count number of patients with that first met
        path_temp = str(path).split("|")
        if site == path_temp[1]: 
            count = count + all_paths[path]
    perc = count / NUM_PATIENTS
    if perc >= 0.025:
        top_sites.append(site)

#delete patients taken out b/c of 2.5% rule
#includes first, second, and third met sites
for k,v in all_paths.items(): 
    path_temp = str(k).split("|") 
    if path_temp[1] not in top_sites or path_temp[2] not in top_sites or path_temp[3] not in top_sites:
        del all_paths[k];

NUM_PATIENTS = 0
for path in all_paths: #update NUM_PATIENTS value
    NUM_PATIENTS = NUM_PATIENTS + all_paths[path]
    NUM_PATIENTS = float(NUM_PATIENTS)

#######
for thispath in all_paths: #choose first path from paths in excel sheet
    thispath_ct1 = 0 #vars
    thispath_ct2 = 0
    thatpath_ct1 = 0
    thatpath_ct2 = 0
    orsum = 0
    psum = 0
    orsumadj = 0
    psumadj = 0
    or_avg = 0
    p_avg = 0
    or_avg_adj = 0
    p_avg_adj = 0
    
    thispath_temp = thispath.split('|')
    
    if thispath in usedpaths: #if you've used this path already
        continue;
    
    thispath_temp = [thispath_temp[0], \
        thispath_temp[1], thispath_temp[2], thispath_temp[3]] #truncate to origin and 3 mets
    thispath = "|".join([thispath_temp[0], thispath_temp[1], thispath_temp[2], thispath_temp[3]])
    origin = thispath_temp[0]
    thispath_firstmet = "|".join([origin, thispath_temp[1],thispath_temp[2]]) 
    secondmet = thispath_temp[2] #used to hold 2 constant while varying 1
    thirdmet = thispath_temp[3]
    
    usedpaths = usedpaths + [thispath] #add path so you won't use it after this    
    
    #counting number of patients for this path
    for path in all_paths: #necessary bc you want to ignore later mets
        path_temp = path.split('|')
        if str(path).startswith(thispath_firstmet):
            thispath_ct1 = thispath_ct1 + all_paths[path]; #counts all w/ first and 2nd met
            if str(path).startswith(thispath):
                thispath_ct2 = thispath_ct2 + all_paths[path]; #counts specific path  
    if thispath_ct1-thispath_ct2 <= 0: #throws out inf. ORs (when 2nd met = 100% chance)
        continue;  
    
    for site in top_sites: #iterating thru all met sites to choose comparison path
        thatpath = "|".join([origin,site,secondmet,thirdmet]) #choose comparison path
        thatpath_firstmet = "|".join([origin,site,secondmet])      
        for path in all_paths: #counting number of patients for comparison path
            if str(path).startswith(thatpath_firstmet):
                thatpath_ct1 = thatpath_ct1 + all_paths[path]; 
                if str(path).startswith(thatpath):
                    thatpath_ct2 = thatpath_ct2 + all_paths[path]; 

        if thatpath_ct2 > 0:
            table = [[thispath_ct2, thispath_ct1-thispath_ct2], \
                [thatpath_ct2, thatpath_ct1-thatpath_ct2]]
            oddsratio, pvalue = stats.fisher_exact(table)
            thatperc = thatpath_ct1 / NUM_PATIENTS
            or_adj = thatperc * oddsratio
            p_adj = thatperc * pvalue
            orsumadj = or_adj + orsumadj
            psumadj = p_adj + psumadj
            orsum = oddsratio + orsum
            psum = pvalue + psum

    #final values for this path
    or_avg = orsum / len(top_sites)
    p_avg = psum / len(all_sites)
    or_avg_adj = orsumadj / len(top_sites)
    p_avg_adj = psumadj / len(all_sites)

    or_adj_pair[thispath] = (or_avg_adj, p_avg_adj) #enter path in dictionary with value
    or_pair[thispath] = (or_avg, p_avg)

"""
#now you have a dictionary with all paths paired to all values
#sort by most to least 
or_c = Counter(or_pair) #make list for odds ratio
or_top = or_c.most_common()
or_adj_c = Counter(or_adj_pair) #make list for adj odds ratio
or_adj_top = or_adj_c.most_common()

or_arr = [] #change list formatting to write to csv
or_adj_arr = []
for path in or_top:
    s = path[1][0]
    t = path[1][1]
    u = path[0]
    or_arr = or_arr + [[u,s,t]]
    
for path in or_adj_top:
    s = path[1][0]
    t = path[1][1]
    u = path[0]
    or_adj_arr = or_adj_arr + [[u,s,t]]

with open('/Users/Confetti/Documents/Research/listvary1/Vary1_OR_Paths_Bladder.csv', 'wb') as f: #CHANGE
    writer = csv.writer(f, delimiter=',')
    for key in or_arr:
        writer.writerow(key)

with open('/Users/Confetti/Documents/Research/listvary1/Vary1_AOR_Paths_Bladder.csv', 'wb') as f: #CHANGE
    writer = csv.writer(f, delimiter=',')
    for key in or_adj_arr:
        writer.writerow(key)
"""