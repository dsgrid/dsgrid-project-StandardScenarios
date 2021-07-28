#!/usr/bin/env python
# coding: utf-8

## Import necessary libraries
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import sys
import os
import shutil
import toml

## User input and directory creation
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
            initialize_model.source = [['res', 'ResStock'], ['null', 'null']]
            initialize_model.sector = [['res', 'Residential'], ['null', 'null']]
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
 
 # For local path directions   
def cleardir():
    def direction():
        print("Are you using user paths (1), pathlib (2), or S3 (3)")
        pointer = input()
        if pointer == "1":
            cleardir.scripts_path = os.getcwd()
            cleardir.path = os.path.join(cleardir.scripts_path,'..')
            cleardir.dimension_path = os.path.join(cleardir.scripts_path, '..', 'dimensions','')
            cleardir.sources_path = os.path.join(cleardir.scripts_path, '..', 'sources','')
            cleardir.dimension_mappings_path = os.path.join(cleardir.scripts_path, '..', 'dimension_mappings','')
            print("Great. I love user paths!")
            return
        # Will add pathlib directions below the future
        elif pointer == "2":
            print("Dang, that functionality is still in development. Try again.")
            direction()
        # Will add s3 directions below in the future
        elif pointer == "3":
            print("Dang, that functionality is still in development. Try again.")
            direction()
        else: 
            print("Invalid input. Let's try that again.")
            direction()
    direction()
      
    isdir1 = os.path.isdir(cleardir.dimension_path)
    if isdir1 == True:
        shutil.rmtree(cleardir.dimension_path)
        os.mkdir(cleardir.dimension_path)
    else:
        os.mkdir(cleardir.dimension_path)
    
    isdir2 = os.path.isdir(cleardir.dimension_mappings_path)
    if isdir2 == True:
        return
    else:
        os.mkdir(cleardir.dimension_mappings_path)
        return

# Run functions
initialize_model()
initialize_timeseries()
initialize_county()
cleardir()


##Translate inputted file into appropriate dataframes
# Change to sources directory
os.chdir(cleardir.sources_path)

# Read parquet file
timeseries = pq.read_table(initialize_timeseries.file)

# Translate parquet file into a dataframe
timeseries_df = timeseries.to_pandas()

## Create enduse dataframe
column = list(timeseries_df.columns)

# Create index column for enduse dataframe
enduse = [s for s in column if s.startswith('electricity') or s.startswith('fuel_oil') or s.startswith('natural_gas') or s.startswith('propane')or s.startswith('wood_heating')]
    

# Create name column for enduse dataframe
enduse_short = []
for i in enduse:
    enduse_partition = i.rpartition('_')[0]
    enduse_short.append(enduse_partition)   

# Create fuel type column for enduse dataframe
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

# Create units column for enduse data frame
units = []
for i in enduse:  
    unit_partition = i.rpartition('_')[-1]
    units.append(unit_partition)

# Combine id, name, fuel type, and units into final enduse dataframe
enduse_final = {'id':enduse,'name':enduse_short,'fuel type': fuel_type_final, 'units': units}
enduse_final_df = pd.DataFrame(enduse_final)


## Create county dataframe
county_df = pd.read_csv(initialize_county.file)

# Pull relevant columns for county dataframe
id = county_df.loc[:,"long_name"]
fips = county_df.loc[:,"fips"]
county = county_df.loc[:,'county_name']
state = county_df.loc[:,'state_abbr']

# Combine columns into final county dataframe
county_csv = {'id':id,'name':county,'state': state, 'geoid_id':fips}
county_final_df = pd.DataFrame(county_csv)

## Create final sources dataframe
sources_df = pd.DataFrame(initialize_model.source, columns = ['id','name'])
sources_df.drop([1], axis=0, inplace = True)

## Create final sectors dataframe
sectors_df = pd.DataFrame(initialize_model.sector, columns = ['id','name'])
sectors_df.drop([1], axis=0, inplace = True)

## Create model year dataframe
model_year = list(range(2010,2052,2))
model_year_csv = {'id':model_year,'name':model_year}
model_year_df = pd.DataFrame(model_year_csv)

## Create subsectors dataframe
subsectors_df = pd.read_csv("Geometry_Building_Type_RECS.tsv", sep='\t')
subsectors_column = list(subsectors_df.columns)
del subsectors_column[0]
del subsectors_column[5:8]

subsectors_scrape = []
for i in subsectors_column:  
    subsectors_partition = i.partition('=')[-1]
    subsectors_scrape.append(subsectors_partition)

subsectors_num = len(subsectors_scrape)
subsectors_id = []
for i in range(0,subsectors_num):
    subsectors_id.append(i)

subsectors_csv = {'id':subsectors_scrape,'name':subsectors_scrape}
subsectors_df = pd.DataFrame(subsectors_csv)

## Create weather year dataframe
weather_id = ["2012"]
weather_name = ["2012"]
weather_years_csv = {'id':weather_id,'name':weather_name}
weather_years_df = pd.DataFrame(weather_years_csv)

## Create mapping dataframes
fips_short = []
for i in fips:
    fips_partition = i.partition('G')[-1]
    fips_short.append(fips_partition)
county_mapping = {'from_id':id, 'to_id':fips_short}
county_mapping_df = pd.DataFrame(county_mapping)


## Create .csv files in output directory
# Change to ouput directory
os.chdir(cleardir.dimension_path)

# Create enduses.csv
enduse_final_df.to_csv('enduses.csv', index = False)

# Create sources.csv file
sources_df.to_csv('sources.csv', index = False)

# Create sectors.csv file
sectors_df.to_csv('sectors.csv', index = False)

# Create county.csv file
county_final_df.to_csv('counties.csv', index = False)

# Create model_year.csv file
#model_year_df.to_csv('model_years.csv', index = False)

# Create subsectors.csv
subsectors_df.to_csv('subsectors.csv', index = False)

# Create subsectors.csv
weather_years_df.to_csv('weather_years.csv', index = False)

## Create .toml file
# Change to sources directory
os.chdir(cleardir.sources_path)

# Transform .toml file into a dictionary
dimensions_toml = toml.load("template.toml")

# Edit toml dictionary with initialize_model function inputs
dimensions_toml['dimensions'][1]['description'] = 'dsgrid Standard Scenarios 2021 Sectors;'+ initialize_model.sector_output+' Only'
dimensions_toml['dimensions'][1]['name'] = 'Standard Scenarios 2021 Sectors-'+initialize_model.sector_output +'-Only'
dimensions_toml['dimensions'][2]['description'] ='dsgrid Standard Scenarios 2021 Data Sources;'+ initialize_model.model_output +' Only'
dimensions_toml['dimensions'][2]['name'] = 'Standard Scenarios 2021 DataSourcs -'+initialize_model.model_output +'-Only'

# Change to ouput directory and delete existing file
os.chdir(cleardir.path)
dimension_toml = os.path.join(cleardir.path, 'dimensions.toml')
isfile = os.path.isdir(dimension_toml)
if isfile == True:
    os.remove("dimensions.toml")

# Create .toml file
with open ('dimensions.toml','w') as f:
   data = toml.dump(dimensions_toml,f)

## Create dimension mapping .csv files
# Change to dimension_mappings directory
os.chdir(cleardir.dimension_mappings_path)

# Create resstock_county_to_dsgrid_county.csv
county_mapping_df.to_csv('resstock_county_to_dsgrid_county.csv', index = False)

# Return to original path for if code is run on the same kernel multiple times
os.chdir(cleardir.scripts_path)