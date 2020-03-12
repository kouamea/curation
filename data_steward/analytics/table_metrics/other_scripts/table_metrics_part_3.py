# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from google.cloud import bigquery

client = bigquery.Client()

# %load_ext google.cloud.bigquery

# %reload_ext google.cloud.bigquery

# +
#######################################
print('Setting everything up...')
#######################################

import warnings

warnings.filterwarnings('ignore')
import pandas_gbq
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.lines import Line2D

import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib as mpl

import matplotlib.pyplot as plt
# %matplotlib inline

import os
import sys
from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
import time

DATASET = ''

plt.style.use('ggplot')
pd.options.display.max_rows = 999
pd.options.display.max_columns = 999
pd.options.display.max_colwidth = 999

from IPython.display import HTML as html_print


def cstr(s, color='black'):
    return "<text style=color:{}>{}</text>".format(color, s)


print('done.')

# +
dic = {
    'src_hpo_id': [
        "saou_uab_selma", "saou_uab_hunt", "saou_tul", "pitt_temple",
        "saou_lsu", "trans_am_meyers", "trans_am_essentia", "saou_ummc",
        "seec_miami", "seec_morehouse", "seec_emory", "uamc_banner", "pitt",
        "nyc_cu", "ipmc_uic", "trans_am_spectrum", "tach_hfhs", "nec_bmc",
        "cpmc_uci", "nec_phs", "nyc_cornell", "ipmc_nu", "nyc_hh",
        "ipmc_uchicago", "aouw_mcri", "syhc", "cpmc_ceders", "seec_ufl",
        "saou_uab", "trans_am_baylor", "cpmc_ucsd", "ecchc", "chci", "aouw_uwh",
        "cpmc_usc", "hrhc", "ipmc_northshore", "chs", "cpmc_ucsf", "jhchc",
        "aouw_mcw", "cpmc_ucd", "ipmc_rush"
    ],
    'HPO': [
        "UAB Selma", "UAB Huntsville", "Tulane University", "Temple University",
        "Louisiana State University",
        "Reliant Medical Group (Meyers Primary Care)",
        "Essentia Health Superior Clinic", "University of Mississippi",
        "SouthEast Enrollment Center Miami",
        "SouthEast Enrollment Center Morehouse",
        "SouthEast Enrollment Center Emory", "Banner Health",
        "University of Pittsburgh", "Columbia University Medical Center",
        "University of Illinois Chicago", "Spectrum Health",
        "Henry Ford Health System", "Boston Medical Center", "UC Irvine",
        "Partners HealthCare", "Weill Cornell Medical Center",
        "Northwestern Memorial Hospital", "Harlem Hospital",
        "University of Chicago", "Marshfield Clinic",
        "San Ysidro Health Center", "Cedars-Sinai", "University of Florida",
        "University of Alabama at Birmingham", "Baylor", "UC San Diego",
        "Eau Claire Cooperative Health Center", "Community Health Center, Inc.",
        "UW Health (University of Wisconsin Madison)",
        "University of Southern California", "HRHCare",
        "NorthShore University Health System", "Cherokee Health Systems",
        "UC San Francisco", "Jackson-Hinds CHC", "Medical College of Wisconsin",
        "UC Davis", "Rush University"
    ]
}

site_df = pd.DataFrame(data=dic)
site_df

# +
######################################
print('Getting the data from the database...')
######################################

site_map = pd.io.gbq.read_gbq('''
    select distinct * from (
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_visit_occurrence`
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_care_site`
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_condition_occurrence`  
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_device_exposure`

    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_drug_exposure`
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_location`         
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_measurement`         
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_note`        
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_observation`         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_person`        
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_procedure_occurrence`         
         
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_provider`
         
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_specimen`
    
    UNION ALL
    SELECT
            DISTINCT(src_hpo_id) as src_hpo_id
    FROM
         `{}._mapping_visit_occurrence`   
    )     
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(site_map.shape[0], 'records received.')
# -

site_df = pd.merge(site_map, site_df, how='outer', on='src_hpo_id')

site_df

# # All temporal data points should be consistent such that end dates should NOT be before a start date.

# ## Visit Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        COUNT(*) AS total,
        sum(case when (t1.visit_start_datetime>t1.visit_end_datetime) then 1 else 0 end) as wrong_date
    FROM
       `{}.visit_occurrence` AS t1

    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df

# ### Visit Occurrence Table By Site

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total_rows,
        sum(case when (t1.visit_start_datetime>t1.visit_end_datetime) then 1 else 0 end) as wrong_date_rows
    FROM
       `{}.visit_occurrence` AS t1
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_visit_occurrence`)  AS t2
    ON
        t1.visit_occurrence_id=t2.visit_occurrence_id
    GROUP BY
        1
    ORDER BY
        3
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_date_rows'] / temporal_df['total_rows'], 1)
temporal_df

visit_occurrence = temporal_df.rename(
    columns={"succes_rate": "visit_occurrence"})
visit_occurrence = visit_occurrence[["src_hpo_id", "visit_occurrence"]]
visit_occurrence = visit_occurrence.fillna(100)
visit_occurrence

total_wrong = temporal_df['wrong_date_rows'].sum()
total_wrong

total_row = temporal_df['total_rows'].sum()
percent = round(100 - 100 * (total_wrong / (total_row)), 1)
percent

# ## Condition Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        COUNT(*) AS total,
        sum(case when (t1.condition_start_datetime>t1.condition_end_datetime) then 1 else 0 end) as wrong_date
    FROM
       `{}.condition_occurrence` AS t1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df

# +
# print("success rate for condition_occurrence is: ",round(100-100*(temporal_df.iloc[0,1]/temporal_df.iloc[0,0]),1))
# -

# ### Condition Occurrence Table By Site

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total_rows,
        sum(case when (t1.condition_start_datetime>t1.condition_end_datetime) then 1 else 0 end) as wrong_date_rows
    FROM
       `{}.condition_occurrence` AS t1
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_condition_occurrence`)  AS t2
    ON
        t1.condition_occurrence_id=t2.condition_occurrence_id
    GROUP BY
        1
    ORDER BY
        3
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_date_rows'] / temporal_df['total_rows'], 1)
temporal_df

condition_occurrence = temporal_df.rename(
    columns={"succes_rate": "condition_occurrence"})
condition_occurrence = condition_occurrence[[
    "src_hpo_id", "condition_occurrence"
]]
condition_occurrence = condition_occurrence.fillna(100)
condition_occurrence

total_wrong = temporal_df['wrong_date_rows'].sum()
total_wrong

total_row = temporal_df['total_rows'].sum()
percent = round(100 - 100 * (total_wrong / (total_row)), 1)
percent

# ## Drug Exposure Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        COUNT(*) AS total,
        sum(case when (t1.drug_exposure_start_datetime>t1.drug_exposure_end_datetime) then 1 else 0 end) as wrong_date
    FROM
       `{}.drug_exposure` AS t1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df

# +
# print("success rate for drug_exposure is: ",round(100-100*(temporal_df.iloc[0,1]/temporal_df.iloc[0,0]),1))
# -

# ### Drug Exposure Table By Site

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total_rows,
        sum(case when (t1.drug_exposure_start_datetime>t1.drug_exposure_end_datetime) then 1 else 0 end) as wrong_date_rows
    FROM
       `{}.drug_exposure` AS t1
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_drug_exposure`)  AS t2
    ON
        t1.drug_exposure_id=t2.drug_exposure_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_date_rows'] / temporal_df['total_rows'], 1)
temporal_df

drug_exposure = temporal_df.rename(columns={"succes_rate": "drug_exposure"})
drug_exposure = drug_exposure[["src_hpo_id", "drug_exposure"]]
drug_exposure = drug_exposure.fillna(100)
drug_exposure

total_wrong = temporal_df['wrong_date_rows'].sum()
total_wrong

total_row = temporal_df['total_rows'].sum()
percent = round(100 - 100 * (total_wrong / (total_row)), 1)
percent

# ## Device Exposure Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        COUNT(*) AS total,
        sum(case when (t1.device_exposure_start_datetime>t1.device_exposure_end_datetime) then 1 else 0 end) as wrong_date
    FROM
       `{}.device_exposure` AS t1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df

print("success rate for device is: ",
      round(100 - 100 * (temporal_df.iloc[0, 1] / temporal_df.iloc[0, 0]), 1))

# ### Device Exposure Table By Site

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total_rows,
        sum(case when (t1.device_exposure_start_datetime>t1.device_exposure_end_datetime) then 1 else 0 end) as wrong_date_rows
    FROM
       `{}.device_exposure` AS t1
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_device_exposure`)  AS t2
    ON
        t1.device_exposure_id=t2.device_exposure_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_date_rows'] / temporal_df['total_rows'], 1)
temporal_df

device_exposure = temporal_df.rename(columns={"succes_rate": "device_exposure"})
device_exposure = device_exposure[["src_hpo_id", "device_exposure"]]
device_exposure = device_exposure.fillna(100)
device_exposure

total_wrong = temporal_df['wrong_date_rows'].sum()
total_wrong

total_row = temporal_df['total_rows'].sum()
percent = round(100 - 100 * (total_wrong / (total_row)), 1)
percent

temporal_df

# ## Temporal Data Points - End Dates Before Start Dates

# +

succes_rate = pd.merge(visit_occurrence,
                       condition_occurrence,
                       how='outer',
                       on='src_hpo_id')
succes_rate = pd.merge(succes_rate, drug_exposure, how='outer', on='src_hpo_id')
succes_rate = pd.merge(succes_rate,
                       device_exposure,
                       how='outer',
                       on='src_hpo_id')
succes_rate = pd.merge(succes_rate, site_df, how='outer', on='src_hpo_id')
succes_rate = succes_rate.fillna("No Data")
succes_rate
# -

succes_rate.to_csv("data\end_before_begin.csv")

# # No data point exists beyond 30 days of the death date. (Achilles rule_id #3)

# ## Visit Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(visit_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.visit_occurrence` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_visit_occurrence`)  AS t3
    ON
        t1.visit_occurrence_id=t3.visit_occurrence_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

# - main reason death date entered as default value ("1890")

visit_occurrence = temporal_df.rename(
    columns={"succes_rate": "visit_occurrence"})
visit_occurrence = visit_occurrence[["src_hpo_id", "visit_occurrence"]]
visit_occurrence = visit_occurrence.fillna(100)
visit_occurrence

# ## Condition Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(condition_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.condition_occurrence` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_condition_occurrence`)  AS t3
    ON
        t1.condition_occurrence_id=t3.condition_occurrence_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

condition_occurrence = temporal_df.rename(
    columns={"succes_rate": "condition_occurrence"})
condition_occurrence = condition_occurrence[[
    "src_hpo_id", "condition_occurrence"
]]
condition_occurrence = condition_occurrence.fillna(100)
condition_occurrence

# ## Drug Exposure Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(drug_exposure_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.drug_exposure` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_drug_exposure`)  AS t3
    ON
        t1.drug_exposure_id=t3.drug_exposure_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

drug_exposure = temporal_df.rename(columns={"succes_rate": "drug_exposure"})
drug_exposure = drug_exposure[["src_hpo_id", "drug_exposure"]]
drug_exposure = drug_exposure.fillna(100)
drug_exposure

# ## Measurement Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(measurement_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.measurement` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_measurement`)  AS t3
    ON
        t1.measurement_id=t3.measurement_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

measurement = temporal_df.rename(columns={"succes_rate": "measurement"})
measurement = measurement[["src_hpo_id", "measurement"]]
measurement = measurement.fillna(100)
measurement

# ## Procedure Occurrence Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(procedure_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.procedure_occurrence` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_procedure_occurrence`)  AS t3
    ON
        t1.procedure_occurrence_id=t3.procedure_occurrence_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

procedure_occurrence = temporal_df.rename(
    columns={"succes_rate": "procedure_occurrence"})
procedure_occurrence = procedure_occurrence[[
    "src_hpo_id", "procedure_occurrence"
]]
procedure_occurrence = procedure_occurrence.fillna(100)
procedure_occurrence

# ## Observation Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(observation_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.observation` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_observation`)  AS t3
    ON
        t1.observation_id=t3.observation_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

observation = temporal_df.rename(columns={"succes_rate": "observation"})
observation = observation[["src_hpo_id", "observation"]]
observation = observation.fillna(100)
observation

# ## Device Exposure Table

# +
######################################
print('Getting the data from the database...')
######################################

temporal_df = pd.io.gbq.read_gbq('''
    SELECT
        src_hpo_id,
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(device_exposure_start_date, death_date, DAY)>30) then 1 else 0 end) as wrong_death_date
    FROM
       `{}.device_exposure` AS t1
    INNER JOIN
        `{}.death` AS t2
        ON
            t1.person_id=t2.person_id
    INNER JOIN
        (SELECT
            DISTINCT * 
        FROM
             `{}._mapping_device_exposure`)  AS t3
    ON
        t1.device_exposure_id=t3.device_exposure_id
    GROUP BY
        1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
temporal_df.shape

print(temporal_df.shape[0], 'records received.')
# -

temporal_df['succes_rate'] = 100 - round(
    100 * temporal_df['wrong_death_date'] / temporal_df['total'], 1)
temporal_df

device_exposure = temporal_df.rename(columns={"succes_rate": "device_exposure"})
device_exposure = device_exposure[["src_hpo_id", "device_exposure"]]
device_exposure = device_exposure.fillna(100)
device_exposure

# ## 4. Succes Rate Temporal Data Points - Data After Death Date

datas = [
    condition_occurrence, drug_exposure, measurement, procedure_occurrence,
    observation, device_exposure
]

master_df = visit_occurrence

for filename in datas:
    master_df = pd.merge(master_df, filename, on='src_hpo_id', how='outer')

master_df

succes_rate = pd.merge(master_df, site_df, how='outer', on='src_hpo_id')
succes_rate = succes_rate.fillna("No Data")

succes_rate

succes_rate.to_csv("data\data_after_death.csv")

# # Age of participant should NOT be below 18 and should NOT be too high (Achilles rule_id #20 and 21)

# ## Count number of unique participants with age <18

# +

######################################
print('Getting the data from the database...')
######################################

birth_df = pd.io.gbq.read_gbq('''
    SELECT
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(CURRENT_DATE, EXTRACT(DATE FROM birth_datetime), YEAR)<18) then 1 else 0 end) as wrong_death_date
         
    FROM
       `{}.person` AS t1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(birth_df.shape[0], 'records received.')
# -

birth_df

# +
######################################
print('Getting the data from the database...')
######################################

birth_df = pd.io.gbq.read_gbq('''
    SELECT
        person_id          
    FROM
       `{}.person` AS t1
    where 
        (DATE_DIFF(CURRENT_DATE, EXTRACT(DATE FROM birth_datetime), YEAR)<18)
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(birth_df.shape[0], 'records received.')
# -

# ## Count number of unique participants with age >120

# +

######################################
print('Getting the data from the database...')
######################################

birth_df = pd.io.gbq.read_gbq('''
    SELECT
        COUNT(*) AS total,
        sum(case when (DATE_DIFF(CURRENT_DATE, EXTRACT(DATE FROM birth_datetime), YEAR)>120) then 1 else 0 end) as wrong_death_date
         
    FROM
       `{}.person` AS t1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(birth_df.shape[0], 'records received.')

# +
######################################
print('Getting the data from the database...')
######################################

birth_df = pd.io.gbq.read_gbq('''
    SELECT
        person_id          
    FROM
       `{}.person` AS t1
    where 
        DATE_DIFF(CURRENT_DATE, EXTRACT(DATE FROM birth_datetime), YEAR)>120
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(birth_df.shape[0], 'records received.')
# -

birth_df

# ## Histogram

# +

######################################
print('Getting the data from the database...')
######################################

birth_df = pd.io.gbq.read_gbq('''
    SELECT
        DATE_DIFF(CURRENT_DATE, EXTRACT(DATE FROM birth_datetime), YEAR) as AGE    
    FROM
       `{}.person` AS t1
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                              dialect='standard')
print(birth_df.shape[0], 'records received.')
# -

birth_df.head()

birth_df['AGE'].hist(bins=88)

# # Participant should have supporting data in either lab results or drugs if he/she has a condition code for diabetes.

# ## T2D

# +
######################################
print('Getting the data from the database...')
######################################

t2d_condition = pd.io.gbq.read_gbq('''
        SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as t2d
        FROM
            `{}.concept` t1 
        INNER JOIN
            `{}.condition_occurrence` AS t2
        ON
            t1.concept_id=t2.condition_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM 
                `{}._mapping_condition_occurrence`)  AS t3
        ON
            t3.condition_occurrence_id=t2.condition_occurrence_id
        WHERE concept_id in (4140466,43531588,45769888,45763582,37018912,43531578,
        43531559,43531566,43531653,43531577,43531562,37016163,45769894,45757474,
        37016768,4221495,43531616,43531564,443767,443733,43530689,4226121,36712686,
        36712687,43531608,43531597,443732,45757280,45769906,4177050,4223463,43530690,45769890,
        37018728,45772019,45769889,37016349,45770880,45757392,45771064,45757447,45757446,45757445,
        45757444,45757363,45772060,36714116,45769875,4130162,45771072,45770830,45769905,45757435,43531651,
        45770881,4222415,45769828,376065,45757450,45770883,45757255,37016354,43530656,45769836,443729,45757278,
        37017432,4063043,43531010,4129519,43530685,45770831,45757499,443731,45770928,45757075,45769872,45769835,
        36712670,46274058,4142579,45770832,45773064,201826,4230254,4304377,4321756,4196141,4099217,201530,4151282,
        4099216,4198296,4193704,4200875,4099651,45766052,40482801,45757277,45757449)
        and (invalid_reason is null or invalid_reason='')
        GROUP BY
            1,2
        ORDER BY
            1,2 desc
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                   dialect='standard')
t2d_condition.shape

# -

t2d_condition.head()

# ## Drug

# +
######################################
print('Getting the data from the database...')
######################################

drug = pd.io.gbq.read_gbq('''
    SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as drug
        FROM
            `{}.concept`  AS t1
        INNER JOIN
            `{}.drug_exposure` AS t2
        ON
            t1.concept_id=t2.drug_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM
                 `{}._mapping_drug_exposure`)  AS t3
        ON
            t3.drug_exposure_id=t2.drug_exposure_id
        WHERE concept_id in (1529331,1530014,1594973,1583722,1597756,1560171,19067100,1559684,1503297,1510202,1502826,
        1525215,1516766,1547504,1580747,1502809,1515249)and (invalid_reason is null or invalid_reason='')
    UNION DISTINCT 
        select 
            DISTINCT
            src_hpo_id,
            person_id,
            1 as drug
                FROM
                    `{}.concept`  AS t4
                INNER JOIN 
                    `{}.concept_ancestor` AS t5
                ON 
                    t4.concept_id = t5.descendant_concept_id
                INNER JOIN
                    `{}.drug_exposure` AS t6
                ON
                    t4.concept_id=t6.drug_concept_id
                INNER JOIN
                    (SELECT
                        DISTINCT * 
                    FROM
                         `{}._mapping_drug_exposure`)  AS t7
                ON
                    t7.drug_exposure_id=t6.drug_exposure_id
          and t5.ancestor_concept_id in (1529331,1530014,1594973,1583722,1597756,1560171,19067100,1559684,1503297,1510202,
          1502826,1525215,1516766,1547504,1580747,1502809,1515249)
          and (t4.invalid_reason is null or t4.invalid_reason='')
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                          dialect='standard')
drug.shape
# -

drug.head(15)

# ## glucose_lab

# +
######################################
print('Getting the data from the database...')
######################################

glucose_lab = pd.io.gbq.read_gbq('''
    SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as drug
        FROM
            `{}.concept`  as t1
        INNER JOIN
            `{}.measurement` AS t2
        ON
            t1.concept_id=t2.measurement_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM
                 `{}._mapping_measurement`)  AS t3
        ON
            t2.measurement_id=t3.measurement_id
        WHERE 
            concept_id in (3004501,3000483) and (invalid_reason is null or invalid_reason='')

    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                 dialect='standard')
glucose_lab.shape
# -

glucose_lab.head()

#
# -glucose lab may not be a got clasifier

# ## fasting_glucose

# +
######################################
print('Getting the data from the database...')
######################################

fasting_glucose = pd.io.gbq.read_gbq('''
    SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as drug
        FROM
            `{}.concept`  as t1
        INNER JOIN
            `{}.measurement` AS t2
        ON
            t1.concept_id=t2.measurement_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM
                 `{}._mapping_measurement`)  AS t3
        ON
            t2.measurement_id=t3.measurement_id
        WHERE
            concept_id  in (3037110) and (invalid_reason is null or invalid_reason='')

    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                     dialect='standard')
fasting_glucose.shape
# -

fasting_glucose.head()

# ## a1c

# +
######################################
print('Getting the data from the database...')
######################################

a1c = pd.io.gbq.read_gbq('''
    SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as drug
        FROM
            `{}.concept`  as t1
        INNER JOIN
            `{}.measurement` AS t2
        ON
            t1.concept_id=t2.measurement_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM
                 `{}._mapping_measurement`)  AS t3
        ON
            t2.measurement_id=t3.measurement_id
        WHERE concept_id  in (3004410,3007263,3003309,3005673) and (invalid_reason is null or invalid_reason='')

    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                         dialect='standard')
a1c.shape
# -

a1c.head()

# ## t1d_condition

# +

######################################
print('Getting the data from the database...')
######################################

t1d_condition = pd.io.gbq.read_gbq('''
    SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as t1d
        FROM
            `{}.concept` t1 
        INNER JOIN
            `{}.condition_occurrence` AS t2
        ON
            t1.concept_id=t2.condition_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM 
                `{}._mapping_condition_occurrence`)  AS t3
        ON
            t3.condition_occurrence_id=t2.condition_occurrence_id
        WHERE concept_id  in (36715571,4143857,45769891,45763585,45773688,45773576,45769901,45771075,45769902,45769903,45769837,
        45757674,37016767,4225656,45769832,43531565,373999,4227210,45757074,435216,37016353,45769904,45757507,45769892,37017429,
        45771068,37016348,45757432,443592,45757393,45771067,45769876,4228112,45757362,4047906,4102018,36717215,439770,4224254,
        45757535,37016179,43530660,37016180,4225055,4224709,45769829,377821,45769830,45763583,45769834,36713094,318712,37018566,
        4222687,4222553,37017431,4063042,43531008,43531009,45763584,45757604,200687,45757266,45757073,45771533,45773567,
        45769833,46269764,4143689,45769873,201254,4099215,40484648,4152858,4096668,201531,4151281,443412,4295011,4099214,
        45766051,45770902) 
        and (invalid_reason is null or invalid_reason='')

    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET),
                                   dialect='standard')
t1d_condition.shape
# -

t1d_condition.head()

# ## insulin

# +
######################################
print('Getting the data from the database...')
######################################

insulin = pd.io.gbq.read_gbq('''
    SELECT
            DISTINCT
            src_hpo_id,
            person_id,
            1 as insulin
        FROM
            `{}.concept`  AS t1
        INNER JOIN
            `{}.drug_exposure` AS t2
        ON
            t1.concept_id=t2.drug_concept_id
        INNER JOIN
            (SELECT
                DISTINCT * 
            FROM
                 `{}._mapping_drug_exposure`)  AS t3
        ON
            t3.drug_exposure_id=t2.drug_exposure_id
        WHERE t1.concept_id in (19122121,1567198,1531601,1516976,1502905,1544838,1550023,1513876,1517998) 
        and (t1.invalid_reason is null or t1.invalid_reason='')
    UNION DISTINCT 
        SELECT 
            DISTINCT
            src_hpo_id,
            person_id,
            1 as drug
                FROM
                    `{}.concept`  AS t4
                INNER JOIN 
                    `{}.concept_ancestor` AS t5
                ON 
                    t4.concept_id = t5.descendant_concept_id
                INNER JOIN
                    `{}.drug_exposure` AS t6
                ON
                    t4.concept_id=t6.drug_concept_id
                INNER JOIN
                    (SELECT
                        DISTINCT * 
                    FROM
                         `{}._mapping_drug_exposure`)  AS t7
                ON
                    t7.drug_exposure_id=t6.drug_exposure_id
          and t5.ancestor_concept_id in (19122121,1567198,1531601,1516976,1502905,1544838,1550023,1513876,1517998)
          and (t4.invalid_reason is null or t4.invalid_reason='')
    '''.format(DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET, DATASET, DATASET, DATASET, DATASET, DATASET,
               DATASET, DATASET),
                             dialect='standard')
insulin.shape
# -

insulin.head(15)

diabet = pd.merge(t2d_condition,
                  t1d_condition,
                  on=["src_hpo_id", "person_id"],
                  how="outer")
diabet["diabetes"] = 1

diabet = diabet.loc[:, ["src_hpo_id", "person_id", "diabetes"]]
diabet.shape

diabet.head()

total_diab = diabet.drop_duplicates(keep=False, inplace=False)
total_diab.shape

total_diab = total_diab.groupby(["src_hpo_id"
                                ]).size().reset_index().rename(columns={
                                    0: 'total_diabetes'
                                }).sort_values(["total_diabetes"])
total_diab

test = pd.merge(drug, glucose_lab, on=["src_hpo_id", "person_id"], how="outer")
test = pd.merge(test,
                fasting_glucose,
                on=["src_hpo_id", "person_id"],
                how="outer")
test = pd.merge(test, a1c, on=["src_hpo_id", "person_id"], how="outer")
test = pd.merge(test, insulin, on=["src_hpo_id", "person_id"], how="outer")
test["tests"] = 1

test = test.loc[:, ["src_hpo_id", "person_id", "tests"]]
test.shape

test.head()

total_test = test.drop_duplicates(keep=False, inplace=False)
total_test.shape

total_test = total_test.groupby(["src_hpo_id"
                                ]).size().reset_index().rename(columns={
                                    0: 'total_diabetes'
                                }).sort_values(["total_diabetes"])
total_test

diabetes_and_test = pd.merge(test,
                             diabet,
                             on=["src_hpo_id", "person_id"],
                             how="outer")

diabetes_and_test.head()

mistakes = diabetes_and_test.loc[(diabetes_and_test["tests"].isnull()) &
                                 (diabetes_and_test["diabetes"] == 1), :]

mistakes.shape

mistakes.head(5)

diabets_no_proof = mistakes.groupby(['src_hpo_id'
                                    ]).size().reset_index().rename(columns={
                                        0: 'diabets_no_proof'
                                    }).sort_values(["diabets_no_proof"])
diabets_no_proof

combined = diabetes_and_test = pd.merge(diabets_no_proof,
                                        total_diab,
                                        on=["src_hpo_id"],
                                        how="outer")
combined = combined.fillna(0)
combined

combined = pd.merge(combined, site_df, how='outer', on='src_hpo_id')
combined = combined.fillna("No Data")
combined

combined.to_csv("data\diabetes.csv")

