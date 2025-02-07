# -- code -- 
"""
Author:ELPHAS KHATA
CODE: Reads tape7.scn from MODTRAN and generates L_TOA
"""
# -- end --

import os
import numpy as np
import pandas as pd
import glob

def tape7scn(file_path):
    data = {'WAVLEN MCRN': [], 'GRND RFLT': [], 'TOTAL RAD': []}
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
        for line in lines[11:]:  # Start from line 12 (index 11)
            wavlen_mcrn = line[4:13].strip()  # Columns 5-13
            grnd_rflt = line[75:86].strip()   # Columns 76-86
            total_rad = line[97:108].strip()  # Columns 98-108
            
            if wavlen_mcrn and grnd_rflt and total_rad:
                data['WAVLEN MCRN'].append(wavlen_mcrn)
                data['GRND RFLT'].append(grnd_rflt)
                data['TOTAL RAD'].append(total_rad)
    
    return data

def process_directory(base_dir):
    all_data = []
    
    for subdir in sorted(os.listdir(base_dir)):  # Sorting ensures order
        subdir_path = os.path.join(base_dir, subdir)
        
        if os.path.isdir(subdir_path) and subdir.startswith('alb'):
            try:
                # Extract albedo and water vapor values from the directory name
                parts = subdir.split('_')
                if len(parts) < 2:


                    print(f"Skipping {subdir}: Incorrect format")
                    continue

                albedo = float(parts[0].replace('alb', ''))
                water_vapor = float(parts[1])

                # Find .scn files
                scn_files = glob.glob(os.path.join(subdir_path, '*.scn'))
                if not scn_files:
                    print(f"No .scn files found in {subdir}")

                for scn_file in scn_files:
                    file_name = os.path.basename(scn_file)
                    data = tape7scn(scn_file)
                    
                    if data is not None:
                        data['ALBEDO'] = albedo
                        data['WATER_VAPOR'] = water_vapor
                        data['FILE_NAME'] = file_name
                        all_data.append(data)

            except Exception as e:
                print(f"Error processing {subdir}: {e}")

    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Execution
input_path = os.path.join('processed_data')
df = process_directory(input_path)
print(df.head())

# # Usage
# file_path = 'MLS_tape7.scn'
# extracted_data = tape7scn(file_path)

# # Print the entries of each parameter
# for key, values in extracted_data.items():
#     print(f"{key}: {values[:]}")
