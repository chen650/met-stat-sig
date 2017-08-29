#!/usr/bin/python

import cgi
import pandas as pd
import scipy.stats as stats
import csv

fs = cgi.FieldStorage()

all_pat = pd.read_excel('/Users/Confetti/Documents/pathways.xlsx',sheetname='all_breast',header=None) #CHANGE

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
given met X as first met, what is the probability of bone met next
given met X as first met, what is the probability of bone met at any point afterwards
given met X as first met, what is the probability of never getting subsequent bone met

"""

for site in all_sites:
    metx = site
    print 'You have chosen ', metx, ' as the first met site'
    given = 0
    event_next = 0
    event_ever = 0
    event_never = 0
    next_path = "|".join([origin, metx, 'Bone'])
    given_path = "|".join([origin,metx])

    for thispath in all_paths:
        temp = thispath.split("|")
        if not str(thispath).startswith(given_path):
            continue
    
        given = given + all_paths[thispath]
     
        if str(thispath).startswith(next_path):
            event_next = event_next + all_paths[thispath]
        if 'Bone' in temp:
            event_ever = event_ever + all_paths[thispath]

    print 'Given: ', given
    if given != 0:
        p_next = float(event_next) / given
        p_ever = float(event_ever) / given
        p_never = 1 - p_ever

    print 'Probability of Bone next: ', p_next
    print 'Probability of Bone at any point after: ',p_ever
    print 'Probability of never Bone after: ',p_never
    print ''

    """
    ignoring paths with bone before met X
    given met X at any point, what is the probability of bone met next
    given met X at any point, what is the probability of bone met at any point afterwards
    given met X at any point, what is the probability of never getting subsequent bone met
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
        if 'Bone' in temp[0:metx_i]:
            continue
    
        given2 = given2 + all_paths[thispath]   
    
        if temp[metx_i+1] == 'Bone':
            event2_next = event2_next + all_paths[thispath]    

        if 'Bone' in temp[metx_i+1:len(temp)]:
            event2_ever = event2_ever + all_paths[thispath]    

    print 'Given: ', given2
    if given2 != 0:
        p2_next = float(event2_next) / given2
        p2_ever = float(event2_ever) / given2
    p2_never = 1 - p2_ever

    print 'Ignoring paths with Bone before chosen met'
    print ''
    print 'Probability of Bone next: ', p2_next
    print 'Probability of Bone at any point after: ',p2_ever
    print 'Probability of never Bone after: ',p2_never
    print ''