from collections import Counter

#!/usr/bin/python

import cgi
import pandas as pd
import scipy.stats as stats
import csv

fs = cgi.FieldStorage()

all_pat = pd.read_excel('/Users/Confetti/Documents/pathways.xlsx',sheetname='mda_breast',header=None) #CHANGE

all_paths = {}
for index, row in all_pat.iterrows():
    all_paths[row[1]] = row[0]

#vars
NUM_PATIENTS = 0
usedpaths = []
local = {}
top_sites = ['Deceased'] 
all_sites = []

for path in all_paths: #create all_sites generally
    path_temp = str(path).split("|")
    for site in path_temp:
        if site not in all_sites and site != "Left Study":
            all_sites.append(site)

#remove patients who left the study at 2nd or 3rd met
for k,v in all_paths.items(): 
    path_temp = str(k).split("|")
    if len(path_temp) < 4 or path_temp[3] == 'Left Study':
        del all_paths[k]

for path in all_paths: #get NUM_PATIENTS value
    NUM_PATIENTS = NUM_PATIENTS + all_paths[path]
    NUM_PATIENTS = float(NUM_PATIENTS)

#remove first mets that each comprise less than 2.5% of patients
for site in all_sites: 
    count = 0.0
    for path in all_paths: #count number of patients with that first met
        path_temp = str(path).split("|")
        if site == path_temp[1]: 
            count = count + all_paths[path]
    perc = count / NUM_PATIENTS
    if perc >= 0.025:
        top_sites.append(site)

for k,v in all_paths.items(): #delete patients taken out b/c of 2.5% rule
    path_temp = str(k).split("|") #includes first and second met sites
    if path_temp[1] not in top_sites or path_temp[2] not in top_sites or path_temp[3] not in top_sites:
        del all_paths[k];

NUM_PATIENTS = 0
for path in all_paths: #update NUM_PATIENTS value
    NUM_PATIENTS = NUM_PATIENTS + all_paths[path]
    NUM_PATIENTS = float(NUM_PATIENTS)
    
###

for thispath in all_paths: #choose first path from paths in excel sheet
    first_ct = 0 #vars
    second_ct = 0
    div = 0

    temp = thispath.split('|')
    
    if thispath in usedpaths: #if you've used this path already (nec bc of truncation)
        continue;
    
    temp = [temp[0], \
        temp[1], temp[2], temp[3]] #truncate to origin and 3 mets
    thispath = "|".join([temp[0], temp[1], temp[2],temp[3]])
    origin = temp[0]
    firstmet = "|".join([origin, temp[1],temp[2]]) 
    
    usedpaths = usedpaths + [thispath] #add path so you won't use it after this    
    
    #counting number of patients for this path
    for path in all_paths: 
        if str(path).startswith(firstmet):
            first_ct = first_ct + all_paths[path]; 
            if str(path).startswith(thispath):
                second_ct = second_ct + all_paths[path];   
        
    div =  float(second_ct) / first_ct
        
    local[thispath] = (div) #enter path in dictionary with value


#now you have a dictionary with all paths paired to all values
#sort by most to least 
c = Counter(local) #make list for odds ratio
top = c.most_common()

loc_arr = [] #change list formatting to write to csv
for path in top:
    s = path[1]
    u = path[0]
    loc_arr = loc_arr + [[u,s]]

with open('/Users/Confetti/Documents/Research/listlocal3step/Local3_Paths_MDA.csv', 'wb') as f: #CHANGE
    writer = csv.writer(f, delimiter=',')
    for key in loc_arr:
        writer.writerow(key)