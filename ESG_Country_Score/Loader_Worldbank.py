# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 16:08:27 2021

@author: Nguye
"""

import wbdata
import pandas as pd
import sqlite3

# Get ISO mapping
ISO_mapping=pd.read_csv("Worldbank_CountryCode_to_ISO.csv",sep='\t')
# Get list indicators and clean the name 
WBFields=pd.read_csv("WBFields_Loader.csv",sep='\t')
# Get list of countries to ignore
ignore_list=pd.read_csv("Ignorelist_Worldbank.ini",sep="\t")
ignore_list=ignore_list[ignore_list.columns[0]]

WBFields["id_renamed"]=WBFields["id"].replace('\.','_', regex=True)
WBFields.set_index("id",inplace=True)
indicators_tofetch=WBFields["id_renamed"].to_dict()

for key_i in indicators_tofetch:
    print(key_i)
    id_i=indicators_tofetch[key_i]
    
    try:
        # Fetch Data with wbdata and convert country names to ISO codescountries = [i['id'] for i in wbdata.get_country()]
        WBDataframe = wbdata.get_dataframe({key_i : id_i}, convert_date=False).rename(index=ISO_mapping.set_index("Country Name").to_dict()['Country Code'])
        
        # Check that all country names are correctly mapped to an ISO code, loader will fail if it is not empty
        list_of_masters=pd.Series(WBDataframe.index.get_level_values(0),).drop_duplicates(keep='first')
        list_non_ISO=list_of_masters[(list_of_masters.apply(lambda x: len(x)>3)) | (list_of_masters.str.contains(r'[a-z]'))]
        errors_to_treat=list_non_ISO[~list_non_ISO.isin(ignore_list)]
        
        if len(errors_to_treat)>0:
            print(errors_to_treat)
            # raise Exception("Some masters are not in ISO format, control andadd them to mapping or ignore file")
        
        # remove all non ISO country
        WBDataframe.drop(list_non_ISO.tolist(),level=0,axis=0,inplace=True)
    except:
        print(f"Issue with loading {id_i} using API")

    
    try:
        # Load into SQL Database
        con=sqlite3.connect("../SQL_Database/ESG_Database.sqlite3")
        cur = con.cursor()
        
        to_save=WBDataframe[id_i].rename("value")
        to_save.to_sql(f"{id_i}",con,if_exists='replace')
        
        # Create view with the latest data available
        
        cur.execute(f"""DROP VIEW IF EXISTS {id_i}_LATEST""")
        cur.execute(f"""
            CREATE VIEW IF NOT EXISTS {id_i}_LATEST AS
            SELECT * FROM {id_i} WHERE (country,date) in
            (SELECT country, max(date) FROM {id_i} where value IS NOT NULL GROUP BY country)
            """
            )
             # Create view with the latest data available and normalized
        cur.execute(f"""DROP VIEW IF EXISTS {id_i}_RENORMALIZED""")
        cur.execute(f"""
            CREATE VIEW IF NOT EXISTS {id_i}_RENORMALIZED AS
        SELECT 
            country,
            date,
            100*(value - min_value) / (max_value -min_value) normalized_value
        FROM {id_i}_LATEST  
        CROSS JOIN (
            SELECT min(value) min_value, max(value) max_value
            FROM {id_i}_LATEST
        ) 
            """
        )
        cur.close()
    except:
        print(f"Issue with {id_i}, could not create view")
    