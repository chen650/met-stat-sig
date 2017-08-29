#!/usr/bin/python

import cgi
import pandas as pd
import scipy.stats as stats
import csv

fs = cgi.FieldStorage()

f = open('/Users/Confetti/Documents/Research/site2/site2_ibc_neg.docx','w')

all_pat = pd.read_excel('/Users/Confetti/Documents/pathways.xlsx',sheetname='ibc_neg',header=None) #CHANGE

all_paths = {}
for index, row in all_pat.iterrows():
    all_paths[row[1]] = row[0]

path_temp = str(all_paths.keys()[0]).split("|")
origin = path_temp[0]

for path in all_paths: #create all_sites generally
    path_temp = str(path).split("|")
    if origin == '':
        origin = path_temp[0]

all_sites = []
for path in all_paths: #create all_sites generally
    path_temp = str(path).split("|")
    for site in path_temp:
        if site not in all_sites and site != "Left Study" and site !="Living" and site !="Deceased":
            all_sites.append(site)

####

"""
given met X as first met, what is the probability of a certain site met Y next
given met X as first met, what is the probability of met Y at any point afterwards
given met X as first met, what is the probability of never getting subsequent met Y after

"""

for site1 in all_sites:
    for site2 in all_sites:
        metx = site1
        given = 0
        event_next = 0
        event_ever = 0
        event_never = 0
        next_path = "|".join([origin, metx, site2])
        given_path = "|".join([origin,metx])

        for thispath in all_paths:
            temp = thispath.split("|")
            if not str(thispath).startswith(given_path):
                continue
    
            given = given + all_paths[thispath]
     
            if str(thispath).startswith(next_path):
                event_next = event_next + all_paths[thispath]
            if site2 in temp:
                event_ever = event_ever + all_paths[thispath]

        print 'Given: ', given
        if given != 0:
            p_next = float(event_next) / given
            p_ever = float(event_ever) / given
            p_never = 1 - p_ever

            print 'Given ', metx, 'as first met'
            print 'Probability of ', site2, ' next: ', p_next
            print 'Probability of ', site2, ' at any point after: ', p_ever
            print 'Probability of never having ', site2, ' after: ', p_never
            print ''
        
            f.write('Given '+ metx+ ' as first met\n')
            f.write('Probability of '+ site2+ ' next: '+ str(p_next)+'\n')
            f.write('Probability of '+ site2+ ' at any point after: '+str(p_ever)+'\n')
            f.write('Probability of never having '+ site2+ ' after: '+str(p_never)+'\n')
            f.write('\n')
        """
        ignoring paths with met Y before met X
        given met X at any point, what is the probability of met Y next
        given met X at any point, what is the probability of met Y at any point afterwards
        given met X at any point, what is the probability of never getting subsequent met Y
        """

        given2 = 0
        event2_next = 0
        event2_ever = 0
        event2_never = 0

        for thispath in all_paths:
    
            temp = thispath.split("|")
    
            if not metx in temp: 
                continue
    
            metx_i = temp.index(metx)
            if site2 in temp[0:metx_i]:
                continue
    
            given2 = given2 + all_paths[thispath]   
    
            if temp[metx_i+1] == site2:
                event2_next = event2_next + all_paths[thispath]    

            if site2 in temp[metx_i+1:len(temp)]:
                event2_ever = event2_ever + all_paths[thispath]    

        if given2 != 0:
            p2_next = float(event2_next) / given2
            p2_ever = float(event2_ever) / given2
            p2_never = 1 - p2_ever

            print 'Ignoring paths with ', site2, ' before ', metx
            print ''
            print 'Probability of ', site2, 'next: ', p2_next
            print 'Probability of ', site2, ' at any point after: ',p2_ever
            print 'Probability of never ', site2, ' after: ',p2_never
            print ''
        
            f.write('Ignoring paths with '+ site2+ ' before ' + metx + '\n')
            f.write('Given ' + metx + ', probability of '+ site2+ ' next: '+ str(p2_next)+'\n')
            f.write('Given ' + metx + ', probability of '+ site2+ ' at any point after: '+str(p2_ever)+'\n')
            f.write('Given ' + metx + ', probability of never '+ site2+ ' after: '+ str(p2_never)+'\n')
            f.write('\n')
        
f.close()
