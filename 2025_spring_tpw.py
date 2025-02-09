# -- code -- 
"""
Author:ELPHAS KHATA
CODE: Reads tape7.scn from MODTRAN and generates L_TOA
"""
# -- end --

import numpy as np
import os
import re
import pandas as pd
from pathlib import Path

# Apparent reflectance
def apprnt_reflectance(L_TOA, E_SUN, THETA_SUN, DOY):
    d = 1 - 0.01672 * np.cos(2*np.pi*(DOY-4)/365)
    THETA_SUN_rad = np.radians(THETA_SUN)
    rho_app = (np.pi * L_TOA * d**2) / (E_SUN * np.cos(THETA_SUN_rad))
    return rho_app

# Process tape7.scn
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
                labels = re.split(r'\s{2,}', line.strip()) # Handle multi-word entries
                
                for unwanted in ['THRML SCT', 'DEPTH']: # Remove unwanted labels safely
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

# Process all profiles for tape7.scn
def process_tape7_scn(main_dir):
    profile_dfs = {}
    profile_groups = {}
    accessed_folders = []
    
    for root, dirs, files in os.walk(main_dir):
        for dir_name in dirs:
            # Match pattern: PROFILE_ALBx_WATy.y (e.g., "MLS_ALB0_WAT0.2")
            match = re.match(r"^([A-Za-z]+)_ALB(\d+)_WAT([\d.]+)$", dir_name)
            if match:
                profile, alb, wvp = match.groups()
                wvp = float(wvp)  # Convert to numeric
                key = (profile, wvp) # Create grouping key
                if key not in profile_groups:
                    profile_groups[key] = {'ALB0': None, 'ALB1': None}
                run_path = os.path.join(root, dir_name)
                profile_groups[key][f'ALB{alb}'] = run_path

    # Process each profile group
    for (profile, wvp), paths in profile_groups.items():
        
        missing = []
        if not paths['ALB0']:
            missing.append(f"{profile}_ALB0_WAT{wvp:.2f}")
        if not paths['ALB1']:
            missing.append(f"{profile}_ALB1_WAT{wvp:.2f}")
        
        if missing:
            error_msg = f"Skipping incomplete pair: Missing {', '.join(missing)}"
            if paths['ALB0'] or paths['ALB1']:
                existing = [p for p in [paths['ALB0'], paths['ALB1']] if p]
                error_msg += f" (Only found: {', '.join(os.path.basename(p) for p in existing)})"
            print(error_msg)
            continue            
        try:
            # Load ALB0 data (TOTAL_RAD)
            alb0_data = getModtranData(paths['ALB0'])
            alb0_df = pd.DataFrame({'WAVLEN_MCRN': alb0_data['WAVLEN MCRN'],
                'TOTAL_RAD': alb0_data['TOTAL RAD']})
            
            # Load ALB1 data (GRND_RFLCT)
            alb1_data = getModtranData(paths['ALB1'])
            alb1_df = pd.DataFrame({'WAVLEN_MCRN': alb1_data['WAVLEN MCRN'],
                'GRND_RFLCT': alb1_data['GRND RFLT']})
            
            # Merge on wavelength
            merged = pd.merge(alb0_df, alb1_df, on='WAVLEN_MCRN', how='inner')
            
            # Add metadata
            merged['PROFILE'] = profile
            merged['WATER'] = wvp
            
            # Include to data frames
            if profile not in profile_dfs:
                profile_dfs[profile] = merged
            else:
                profile_dfs[profile] = pd.concat([profile_dfs[profile], merged])
            
            # successfully accessed folders
            accessed_folders.append(f"{profile}_ALB0_WAT{wvp:.2f}")
            accessed_folders.append(f"{profile}_ALB1_WAT{wvp:.2f}")
                
        except Exception as e:
            dir_names = [os.path.basename(p) for p in paths.values()]
            print(f"Error processing {profile} pair: {', '.join(dir_names)}")
            print(f"Error details: {str(e)}")

    return profile_dfs, accessed_folders

# def reaTape6(main_dir, folders_accessed):
#     data = []

#     for folder in folders_accessed:
#         tape6_path = os.path.join(main_dir, folder, 'tape6')
#         if not os.path.exists(tape6_path):
#             print(f"Error: File not found - {tape6_path}")
#             continue  # Skip this folder if file doesn't exist

#         try:
#             with open(tape6_path, 'r') as fP:
#                 lines = fP.readlines()
#                 if len(lines) > 88:  # Ensure the file has at least 89 lines
#                     line_89 = lines[88].strip()

#                     if line_89.startswith("FINAL:"):
#                         final_h2o = line_89[10:19].strip()  # Extract characters from column 17-23
#                     elif len(lines) > 86:
#                         line_87 = lines[86].strip()
#                         if "THE WATER COLUMN IS BEING SET TO THE MAXIMUM," in line_87[0:57]:  
#                             final_h2o = line_87[48:56].strip()  # Extract data from column 55-66
#                         else:
#                             print(f"Error: Neither line 89 nor line 87 in {tape6_path} matched expected formats.")
#                             continue
#                     else:
#                         print(f"Error: Insufficient lines in {tape6_path}.")
#                         continue
                    
#                     data.append([folder, final_h2o])

#         except Exception as e:
#             print(f"Error processing {tape6_path}: {e}")

#     # Convert list to DataFrame
#     df = pd.DataFrame(data, columns=["ATM_PROFILE", "Final_H2O"])
#     return df

def reaTape6(main_dir, folders_accessed):
    data = []

    for folder in folders_accessed:
        tape6_path = os.path.join(main_dir, folder, 'tape6')

        # Read the file
        with open(tape6_path, 'r') as fP:
            lines = fP.readlines()
            if len(lines) > 88 and lines[88].startswith("FINAL:"):
                final_h2o = lines[88][10:19].strip()  # Extract from columns 11-19
            elif len(lines) > 86 and "THE WATER COLUMN IS BEING SET TO THE MAXIMUM," in lines[86]:
                final_h2o = lines[86][48:56].strip()  # Extract from columns 49-56

            data.append([folder, final_h2o])

    tape6_df = pd.DataFrame(data, columns=["ATM_PROFILE", "Final_H2O"])
    return tape6_df
# Main
main_dir = 'MODTRAN_models_2025_b'
profile_dataframes, folders_accessed = process_tape7_scn(main_dir)
tape6Data = reaTape6(main_dir, folders_accessed)
tape6Data
