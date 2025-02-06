# -- code -- 
"""
Author:ELPHAS KHATA
CODE: Reads tape7.scn from MODTRAN and generates L_TOA
"""
# -- end --

import os
import numpy as np
import pandas as pd


# def process_directory(base_dir):
#     all_data = []
    
#     for subdir in sorted(os.listdir(base_dir)):  # Sorting ensures order
#         subdir_path = os.path.join(base_dir, subdir)
        
#         if os.path.isdir(subdir_path) and subdir.startswith('alb'):
#             try:
#                 # Extract albedo and water vapor values from the directory name
#                 parts = subdir.split('_')
#                 if len(parts) < 2:
#                     print(f"Skipping {subdir}: Incorrect format")
#                     continue

#                 albedo = float(parts[0].replace('alb', ''))
#                 water_vapor = float(parts[1])

#                 # Find .scn files
#                 scn_files = glob.glob(os.path.join(subdir_path, '*.scn'))
#                 if not scn_files:
#                     print(f"No .scn files found in {subdir}")

#                 for scn_file in scn_files:
#                     file_name = os.path.basename(scn_file)
#                     data = read_modtran_tape7scn(scn_file)
                    
#                     if data is not None:
#                         data['ALBEDO'] = albedo
#                         data['WATER_VAPOR'] = water_vapor
#                         data['FILE_NAME'] = file_name
#                         all_data.append(data)

#             except Exception as e:
#                 print(f"Error processing {subdir}: {e}")

#     return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# # Execution
# input_path = os.path.join('processed_data')
# df = process_directory(input_path)
# print(df.head())
