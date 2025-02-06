# -*- coding: utf-8 -*-
"""
This code prepares tape5 for reanalysis data in MODTRAN card2
Created on Fri Sep 23 28:35:02 2024
@author: KHATA ELPHAS
"""
from pathlib import Path
import pandas as pd

def modify_tape5_file(input_file, output_file, csv_file):
    with open(input_file, 'r') as file:
        lines = file.readlines() 
    first_part = lines[:4]
    last_part = lines[-5:]

    df = pd.read_csv(csv_file)
    df = df[['Level', 'Atmospheric Pressure', 'Air Temperature', 'Dew Point']].dropna()
    profile_data = df.values
    
    formatted_profile = "\n".join(
        [f"    {alt:6.3f} {pres:8.3e} {temp:8.3e} {dew:8.3e} 0.000e+00 0.000e+00AAF"
         for alt, pres, temp, dew in profile_data])
    
    modified_content = first_part + [formatted_profile + "\n"] + last_part
    with open(output_file, 'w') as file:
        file.writelines(modified_content)

def process_directory_files(input_tape5, output_dir, csv_directory):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for csv_file in Path(csv_directory).glob('*.csv'):
        output_file = Path(output_dir) / f"{csv_file.stem}.tp5"
        modify_tape5_file(input_tape5, output_file, csv_file)
        # print(f"Processed {csv_file.name} and saved to {output_file.name}")

csv_directory = Path(r"C:\Users\elpha\OneDrive\PhD Research\2024_Fall\IMGS890_Research\GEOS-5\Reanalysis_data")
input_tape5 = Path(r"C:\Users\elpha\OneDrive\PhD Research\2024_Fall\IMGS890_Research\GEOS-5\tape5_1100am_closest.tp5")
output_dir = Path(r"C:\Users\elpha\OneDrive\PhD Research\2024_Fall\IMGS890_Research\GEOS-5\Reanalysis_data_tape5")
process_directory_files(input_tape5, output_dir, csv_directory)
