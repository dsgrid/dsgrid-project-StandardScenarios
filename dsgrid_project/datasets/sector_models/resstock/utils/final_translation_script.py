#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries

# In[1]:


import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import sys
import os
import shutil


# User input and directory creation

# In[3]:


def initialize_timeseries():
    print('Input the timeseries results file')
    initialize_timeseries.file = input()
    print('You have entered '+ initialize_timeseries.file+', is that correct? [y/n]')
    def file_input1():
        initialize_timeseries.file_answer = input()
        if initialize_timeseries.file_answer == 'y':
            print('Great!')
            return
        elif initialize_timeseries.file_answer == 'n':
            print("Okay. Let's try again.")
            initialize_timeseries()
        else: 
            print("Invalid input. Let's try again.")
            print('You have entered '+ initialize_timeseries.file+', is that correct? [y/n]')
            file_input1()
    file_input1()
              
def initialize_model():
    print('What model was used to create these results?')
    initialize_model.model = input()
    print('You have entered '+ initialize_model.model+', is that correct? [y/n]')
    file_answer = input()
    if file_answer == 'y':
        if initialize_model.model == 'ResStock' or initialize_model.model =='resstock' or initialize_model.model =='Resstock':
            initialize_model.source = [['rld', 'ResStock'], ['null', 'null']]
            initialize_model.sector = [['rld', 'Residential'], ['null', 'null']]
            initialize_model.model_output = 'ResStock'
            initialize_model.sector_output = 'Residential'
            print('Great!')
            return
        elif initialize_model.model == 'Tempo' or initialize_model.model =='tempo' or initialize_model.model =='TEMPO':
            initialize_model.source = [['tld', 'TEMPO'], ['null', 'null']]
            initialize_model.sector = [['tld', 'Transportation'], ['null', 'null']]
            initialize_model.model_output = 'TEMPO'
            initialize_model.sector_output = 'Transportation'
            print('Great!')
            return
        elif initialize_model.model == 'ComStock' or initialize_model.model =='comstock' or initialize_model.model =='Comstock':
            initialize_model.source = [['cld', 'ComStock'], ['null', 'null']]
            initialize_model.sector = [['cld', 'Commercial'], ['null', 'null']]                
            initialize_model.model_output = 'ComStock'
            initialize_model.sector_output = 'Commercial'
            print('Great')
            return
        else:
            print("Invalid input. Let's try again.")
            initialize_model()
    elif file_answer == 'n':
        print("Okay. Let's try again.")
        initialize_model()
    else: 
        print("Invalid input. Let's try again.")            
        initialize_model()
    
    

def initialize_county():
    print('Input the county lookup table file')
    initialize_county.file = input()
    print('You have entered '+ initialize_county.file+', is that correct? [y/n]')
    def file_input2():
        file_answer = input()
        if file_answer == 'y':
            print('Great!')
            return
        elif file_answer == 'n':
            print("Okay. Let's try again.")
            initialize_county()
        else: 
            print("Invalid input. Let's try again.")
            print('You have entered '+ initialize_county.file+', is that correct? [y/n]')
            file_input2()
    file_input2()
       
def cleardir():
    cleardir.path = '/Users/nsandova/NREL_Practice/Translation'
    cleardir.dimension_path = '/Users/nsandova/NREL_Practice/Translation/dimensions'
    cleardir.sources_path = '/Users/nsandova/NREL_Practice/Translation/sources'
    cleardir.utils_path = '/Users/nsandova/NREL_Practice/Translation/utils'
    isdir = os.path.isdir(cleardir.dimension_path)
    if isdir == True:
        shutil.rmtree(cleardir.dimension_path)
        os.mkdir(cleardir.dimension_path)
        os.chdir(cleardir.sources_path)
        return
    else:
        os.mkdir(cleardir.dimension_path)
        os.chdir(cleardir.sources_path)
        return
    
initialize_model()
initialize_timeseries()
initialize_county()
cleardir()

Translate inputted file into appropriate dataframes
# In[4]:


# Read parquet file
timeseries = pq.read_table(initialize_timeseries.file)

# Translate parquet file into a dataframe
timeseries_df = timeseries.to_pandas()

## Create enduse dataframe
column = list(timeseries_df.columns)
enduse = [s for s in column if s.startswith('electricity') or s.startswith('fuel_oil') or s.startswith('natural_gas') or s.startswith('propane')or s.startswith('wood_heating')]

# Create name column
enduse_short = []
for i in enduse:
    enduse_partition = i.rpartition('_')[0]
    enduse_short.append(enduse_partition)
    
# Create index column
num = len(enduse)
id = []
for i in range(0,num):
    id.append(i)

#Create fuel type column
fuel_type_scrape = []
for i in enduse:  
    fuel_type_partition = i.partition('_')[0]
    fuel_type_scrape.append(fuel_type_partition)
    
fuel_type_1 = []
for entry in fuel_type_scrape:
    fuel = entry.replace('fuel','fuel oil')
    fuel_type_1.append(fuel)
   
fuel_type_2 = []
for entry in fuel_type_1:
    fuel = entry.replace('natural','natural gas')
    fuel_type_2.append(fuel)

fuel_type_final = []
for entry in fuel_type_2:
    fuel = entry.replace('wood','wood heating')
    fuel_type_final.append(fuel)

# Create units column
units = []
for i in enduse:  
    unit_partition = i.rpartition('_')[-1]
    units.append(unit_partition)

# Combine id, name, fuel type, and units into final enduse dataframe
enduse_final = {'id':id,'name':enduse_short,'fuel type': fuel_type_final, 'units': units}
enduse_final_df = pd.DataFrame(enduse_final)


# Create county dataframe
county_df = pd.read_csv(initialize_county.file)

# Pull relevant columns
fips = county_df.loc[:,"fips"]
county = county_df.loc[:,'county_name']
state = county_df.loc[:,'state_abbr']

# Combine columns into final county dataframe
county_csv = {'id':fips,'name':county,'state': state}
county_final_df = pd.DataFrame(county_csv)

# Create final sources dataframe
sources_df = pd.DataFrame(initialize_model.source, columns = ['id','name'])
sources_df.drop([1], axis=0, inplace = True)

# Create final sectors dataframe
sectors_df = pd.DataFrame(initialize_model.sector, columns = ['id','name'])
sectors_df.drop([1], axis=0, inplace = True)


# Create .csv files in output directory

# In[5]:


# Change to ouput directory
os.chdir(cleardir.dimension_path)

# Create enduses.csv
enduse_final_df.to_csv('enduses.csv', index = False)

# Create sources.csv file
sources_df.to_csv('sources.csv', index = False)

# Create sectors.csv file
sectors_df.to_csv('sectors.csv', index = False)

# Create county.csv file
county_final_df.to_csv('county.csv', index = False)


# Create .toml file

# In[7]:


# Change to Translation directory
os.chdir(cleardir.sources_path)

# Import .toml file
import toml

# Transform .toml file into a dictionary
dimensions_toml = toml.load("template.toml")

# Edit toml dictionary with initialize_model function inputs
dimensions_toml['dimensions'][1]['description'] = 'dsgrid Standard Scenarios 2021 Sectors;'+ initialize_model.sector_output+' only'
dimensions_toml['dimensions'][1]['name'] = 'Standard Scenarios 2021 Sectors-'+initialize_model.sector_output +'-Only'
dimensions_toml['dimensions'][5]['description'] ='dsgrid Standard Scenarios 2021 Data Sources;'+ initialize_model.model_output +' Only\n'
dimensions_toml['dimensions'][5]['name'] = 'Standard Scenarios 2021 DataSourcs -'+initialize_model.model_output +'-Only'

# Change to ouput directory
os.chdir(cleardir.path)

# Create .toml file
with open ('dimensions.toml','w') as f:
   data = toml.dump(dimensions_toml,f)
 


# In[ ]:




