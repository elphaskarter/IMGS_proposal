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

# read tape7.scn
def getModtranData(run):
    file_path = os.path.join(run, 'tape7.scn')
    with open(file_path) as fp:
        step1 = fp.readlines()
        activate = False
        data = []
        labels = []
        
        for line in step1:
            if "WAVLEN" in line:
                activate = True
                labels = re.split(r'\s{2,}', line.strip())  # Split on 2+ spaces
                
                # Remove unwanted labels safely
                for unwanted in ['THRML SCT', 'DEPTH']:
                    if unwanted in labels:
                        labels.remove(unwanted)
                
            elif activate:
                if line.strip() == '-9999.':
                    activate = False
                    continue
                else:
                    data.append(line.strip().split())

        data2 = np.float32(data)
        runData = {label: data2[:, i] for i, label in enumerate(labels)}
        
    return runData

# apparent reflectance
def apprnt_reflectance(L_TOA, E_SUN, THETA_SUN, DOY):
    d = 1 - 0.01672 * np.cos(2*np.pi*(DOY-4)/365)
    THETA_SUN_rad = np.radians(THETA_SUN)
    rho_app = (np.pi * L_TOA * d**2) / (E_SUN * np.cos(THETA_SUN_rad))
    return rho_app

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
