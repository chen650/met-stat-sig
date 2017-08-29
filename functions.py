# -*- coding: utf-8 -*-

import time
import numpy as np
import pandas as pd
import pykov as pk
import itertools
import psycopg2
import psycopg2.extras
import scipy.stats as stats 
#from pandas.io.sql import read_sql_query

min_met_days = 30

###############################################################################
###############################################################################

def get_patients(demographic, select_statement, primary):
    all_times = ['Start']
    start_time = time.time()
    all_times.append(time.time() - start_time)
    try:
        conn = psycopg2.connect(host='4db.usc.edu',database='test_msg',user='kuhn')
        pcur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except:
        print "Unable to connect to database."

    all_times.append('Time to connect to database:')
    all_times.append(time.time() - start_time)
    select_statement = select_statement + " WHERE (primary_cancer = '" + primary + "')"
    if demographic != "":
        demographic = demographic[1:len(demographic)-1]
        demographic = demographic.replace('},{', '}|{')
        demographic = demographic.split('|')

        for demo in demographic:
            group = demo.split('"')[3]
            selections = (demo.split('['))[1].split(']')[0]
            selections = selections.replace('"', '')
            selections = selections.split(',')
            sub_selections = {}
            
            if (selections != ['']) and (group in ['age', 'bmi', 'tumor_size', 'alb', 'ceam', 'ebl', 'cci', 'comorbidity']):
                for count in range(len(selections)):
                    age_range = selections[count].split('-')
                    sub_selections[count] = "(" + group + " >= " + age_range[0] + " AND " + group + " < " + age_range[1] + ")"

            if (selections != ['']) and (group in ['dx_hospital', 'ethnicity', 'sex', 'histology', 'her2', 'er', 'pr', 'nuclear_grade', 'clinical_stage', 'histology_grade', 'asa', 'lvi', 'clinical_t', 'clinical_n', 'pathologic_t', 'pathologic_n', 'neo_adj_chemo', 'adj_chemo']):
                for count in range(len(selections)):
                    sub_selections[count] = "(" + group + " = '" + selections[count] + "')"

            if (selections != ['']):
                temp_select = ''
                temp_select = temp_select + "(" + sub_selections[0]
                if len(sub_selections) > 1:
                    for count in range(len(sub_selections)-1):
                        temp_select = temp_select + " OR " + sub_selections[count+1]
                temp_select = temp_select + ")"
                select_statement = select_statement + " AND " + temp_select
    all_times.append('Time to complete SELECT statement from demographics:')
    all_times.append(time.time() - start_time)

    #all_pat = []
    try:
        #all_pat = read_sql_query(select_statement, conn, coerce_float=True, params=None)
        pcur.execute(select_statement)
        all_times.append('Time to execute SELECT statement:')
        all_times.append(time.time() - start_time)
        prow = pcur.fetchall()
        all_times.append('Time to fetchall() into variables:')
        all_times.append(time.time() - start_time)
        all_pat = pd.DataFrame([i.copy() for i in prow])
        all_times.append('Time to convert to pandas dataframe:')
        all_times.append(time.time() - start_time)
    except:
        print "Improper SELECT statement."
    
    return all_pat, all_times

###############################################################################
###############################################################################

def get_patient_paths(patient, time_delta, path, use_groups=True, include_censored=True):
    time_delta_yrs = time_delta * 365.25

    # groups all mets that are within a certain time delta (min_met_days)
    last_met_days = -30
    for pid, pat in patient.iterrows():
        if (not pd.isnull(pat['met_id_days_from_dx'])):
            if (pat['met_id_days_from_dx']-last_met_days) <= min_met_days:
                patient.set_value(pid, 'met_id_days_from_dx', last_met_days)
            last_met_days = pat['met_id_days_from_dx']
    if use_groups:
        patient = patient.sort_values(['met_id_days_from_dx', 'met_order_groups'], ascending=[True, True])
    else:
        patient = patient.sort_values(['met_id_days_from_dx', 'met_order'], ascending=[True, True])

    # appends all mets that occur within a desired time to the path
    for pid, pat in patient.iterrows():
        if (not pd.isnull(pat['met_id_days_from_dx'])):
            if (pat['met_id_days_from_dx'] <= time_delta_yrs):
                if use_groups:
                    path = "|".join([path, pat['met_group']])
                else:
                    path = "|".join([path, pat['met_name']])

    if (not pd.isnull(pat['death_days_from_dx'])):
        if (pat['death_days_from_dx'] <= time_delta_yrs):
            # appends Deceased to end of path if death occurs within time frame
            path = "|".join([path, 'Deceased'])
        else:
            path = "|".join([path, 'Living'])
    elif (not pd.isnull(pat['last_followup_days_from_dx'])):
        if (pat['last_followup_days_from_dx'] <= time_delta_yrs):
            # appends Left Study to end of path if patient left study within timeframe and including censored patients
            if include_censored:
                path = "|".join([path, 'Left Study'])
            else:
                return None
        else:
            path = "|".join([path, 'Living'])
    else:
        # appends Living to end of path otherwise
        path = "|".join([path, 'Living'])

    return path

###############################################################################
###############################################################################

def order_mets_and_groups(all_pat, primary):
    met_order = all_pat['met_name'].value_counts().keys()
    met_order_groups = all_pat['met_group'].value_counts().keys()

    all_pat['met_order'] = pd.Categorical(all_pat['met_name'], categories=met_order, ordered=True)
    all_pat['met_order_groups'] = pd.Categorical(all_pat['met_group'], categories=met_order_groups, ordered=True)

    return all_pat

###############################################################################
###############################################################################

def build_markov_chain(all_pat, primary, use_groups=True, include_censored=True, separator='|'):
    subset = all_pat.drop_duplicates('uuid')
    all_paths = []
    for pid, pat in subset.iterrows():
        temp_pat = all_pat[all_pat.uuid == pat.uuid]
        pat_path = get_all_paths(temp_pat, primary, use_groups)
        all_paths.extend([pat_path])

    # Modify paths from nested list of lists to flattened list with separator
    tot_paths = []
    for path in all_paths:
        if path:
            tot_paths.extend(equivalent_traj(path, separator))
            tot_paths.extend(separator)
    tot_paths.pop()

    # Build Markov Chain (Wrapper to pykov)
    p, P = pk.maximum_likelihood_probabilities(tot_paths, separator=separator)
    return p, P

def get_all_paths(patient, primary, use_groups=True):
    # groups all mets that are within a certain time delta (min_met_days)
    last_met_days = 0
    temp_path = []
    path = []
    path.extend(primary)
    for pid, pat in patient.iterrows():
        if (not pd.isnull(pat['met_id_days_from_dx'])):
            if (pat['met_id_days_from_dx']-last_met_days) <= min_met_days:
                if use_groups:
                    temp_path.extend([pat['met_group']])
                else:
                    temp_path.extend([pat['met_name']])
            else:
                if temp_path:
                    path.extend([temp_path])
                last_met_days = pat['met_id_days_from_dx']
                temp_path = []
                if use_groups:
                    temp_path.extend([pat['met_group']])
                else:
                    temp_path.extend([pat['met_name']])
    if (not pd.isnull(pat['met_id_days_from_dx'])):
        if (pat['met_id_days_from_dx']-last_met_days) <= min_met_days:
            path.extend([temp_path])

    if (not pd.isnull(pat['death_days_from_dx'])):
        # appends Deceased to end of path if death occurs within time frame
        path.extend([['Deceased']])

    return path

def equivalent_traj(trajectory, separator='|'):
    #traj = list(trajectory)
    if not isinstance(trajectory, (list, tuple)):
        print 'traj input must be a list or tuple'
        return trajectory

    # extract probable states from trajectory
    prob_states = []
    for i in range(len(trajectory)):
        if isinstance(trajectory[i], (list, tuple, np.ndarray)):
            prob_states.append((i, trajectory[i]))

    # return traj if the trajectory is deterministic
    if not prob_states:
        return trajectory

    # finds all combinations of probablistic states
    states = [i for i in itertools.product(*[state for j, state in prob_states])]
    num_traj = len(states)  # Number of equivalent trajectories

    # Populate equivalent trajectories with the unique combinations of probablistic states
    eq_trajs = []
    for n in range(num_traj):
        temp_traj = list(trajectory)
        for p in range(len(states[n])):
            temp_traj[prob_states[p][0]] = states[n][p]
        eq_trajs.extend(temp_traj)
        eq_trajs.extend(separator)
    eq_trajs.pop()
    return eq_trajs
