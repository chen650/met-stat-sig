#!/usr/bin/python

import cgi
import pandas as pd
from functions import get_patients
from functions import get_patient_paths
from functions import order_mets_and_groups
import scipy.stats as stats

fs = cgi.FieldStorage()
'''
demographics = fs.getvalue('demographics')
primary = fs.getvalue('primary')
time_delta = fs.getvalue('time_delta')
time_delta = int(time_delta)
time_range = fs.getvalue('range')
time_range = int(time_range)
include_censored = fs.getvalue('censored')
include_censored = bool(include_censored)
'''

#temporary values
primary = 'Breast'
time_delta = 20;
include_censored = bool(0);

select_statement = """SELECT p.uuid, m.met_name, m.met_group, 
                    (CASE
                    WHEN met_id_days_from_dx is null THEN
                    met_id_date - dx_date
                    ELSE 
                    met_id_days_from_dx
                    END) met_id_days_from_dx, 
                    (CASE
                    WHEN last_followup_days_from_dx is null THEN
                    last_followup_date - dx_date
                    ELSE 
                    last_followup_days_from_dx
                    END) last_followup_days_from_dx, 
                    (CASE
                    WHEN death_days_from_dx is null THEN
                    death_date - dx_date
                    ELSE
                    death_days_from_dx
                    END) death_days_from_dx 
                    FROM patient p 
                    LEFT OUTER JOIN mets m ON p.uuid = m.uuid 
                    LEFT OUTER JOIN """ + primary.lower() + """ c ON m.uuid = c.uuid 
                    LEFT OUTER JOIN therapy t ON c.uuid = t.uuid """

all_pat = pd.read_csv('/Users/Confetti/Downloads/angela_data.csv')

all_pat = all_pat.sort_values(['uuid', 'met_id_days_from_dx'], ascending=[True, True])
all_pat = order_mets_and_groups(all_pat, primary)
subset = all_pat.drop_duplicates('uuid')

all_paths = {}
for pid, pat in subset.iterrows():
    temp_pat = all_pat[all_pat.uuid == pat.uuid]
    pat_path = get_patient_paths(temp_pat, time_delta, primary, use_groups=True, include_censored=True)
    if pd.isnull(pat_path):
        pass
    elif all_paths.has_key(pat_path):
        all_paths[pat_path] += 1
    else:
        all_paths[pat_path] = 1

totalSum = sum(all_paths.values())
all_paths = sorted(all_paths.items(), key=lambda x: x[1], reverse=True)

"""
# print out results
print "Content-type: text/html\n"
for path in all_paths:
    print "['" + str(path[0]) + "','" + str(path[1]) + "']"

print "BREAK"
print "Spatiotemporal Times"
for val in all_times:
	print val
"""

"""
1) choose path w/ 1st and 2nd met site
    * for path in all_paths:
        met sites = str(path[0]), count = path[1]
2) iterate through all other 1st met sites to get each p of fisher
3) average p vals
4) display
"""

all_sites = ['Bone','Contra Breast','LN (reg)','Chest Wall', \
    'Lung/pleura','LN (dist)','Liver','Thyroid','Brain', 'Ipsi Breast', \
    'Ab Wall','Kidney/Adrenal','Other','Pancreas','Muscles','Cervix', \
    'Skin','Ovary','Other CNS','Eye','Pericardium','Bladder','Head and Neck', \
    'Uterus','Parotid','Stomach','Colorectal','Intestine','Spleen', 'Vagina', \
    'Aorta','Esophagus','Gallbladder','Pharynx','Living']

NUM_PATIENTS = 4181.0
thispath_ct1 = 0
thispath_ct2 = 0
thatpath_ct1 = 0
thatpath_ct2 = 0
psum = 0 
psumadj = 0
orsum = 0
orsumadj = 0

thispath = ('Breast|Bone|Brain')
thispath_temp = thispath.split('|')
origin = thispath_temp[0]
thispath_firstmet = "|".join([thispath_temp[0], thispath_temp[1]]) 
secondmet = thispath_temp[2]

#counting number of patients for this path
for path in all_paths:
    if str(path[0]).startswith(thispath_firstmet):
        thispath_ct1 = thispath_ct1 + path[1]; 
        if str(path[0]).startswith(thispath):
            thispath_ct2 = thispath_ct2 + path[1]; 

for site in all_sites: #iterating thru all met sites
    thatpath = "|".join([origin,site,secondmet]) #choose comparison path
    thatpath_firstmet = "|".join([origin,site])      
    for path in all_paths:
        if str(path[0]).startswith(thatpath_firstmet):
            thatpath_ct1 = thatpath_ct1 + path[1]; 
            if str(path[0]).startswith(thatpath):
                thatpath_ct2 = thatpath_ct2 + path[1]; 
    thatperc = (thatpath_ct1 / NUM_PATIENTS) 
    table = [[thispath_ct2, thispath_ct1-thispath_ct2], [thatpath_ct2, thatpath_ct1-thatpath_ct2]]
    oddsratio, pvalue = stats.fisher_exact(table)
    print "Comparing with ", thatpath, " gives a pvalue of ", pvalue,\
        " and an odds ratio of ", oddsratio
    p_adj = thatperc * pvalue
    or_adj = thatperc * oddsratio
    print "Comparing with ", thatpath, " gives an adjusted pvalue of ", p_adj, \
        "and an adjusted odds ratio of ", or_adj;
    psumadj = p_adj + psumadj
    orsumadj = or_adj + orsumadj
    psum = pvalue + psum
    orsum = oddsratio + orsum

p_avg = psum / len(all_sites)
or_avg = orsum / len(all_sites)
p_avg_adj = psumadj / len(all_sites)
or_avg_adj = orsumadj / len(all_sites)
print "Average p-value: ", p_avg
print "Average odds ratio: ", or_avg
print "Average adjusted p-value: ", p_avg_adj
print "Average adjusted odds ratio: ", or_avg_adj
