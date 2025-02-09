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

def process_tape7_scn(main_dir):
    profile_dfs = {}
    profile_groups = {}
    accessed_folders = []
    for root, dirs, _ in os.walk(main_dir):
        for dir_name in dirs:
            match = re.match(r"^([A-Za-z]+)_ALB(\d+)_WAT([\d.]+)$", dir_name)
            if match:
                profile, alb, wvp = match.groups()
                key = (profile, float(wvp))
                profile_groups.setdefault(key, {})[f'ALB{alb}'] = os.path.join(root, dir_name)
    for (profile, wvp), paths in profile_groups.items():
        try:
            alb0_data = getModtranData(paths['ALB0'])
            alb1_data = getModtranData(paths['ALB1'])

            merged = pd.DataFrame({'WAVLEN_MCRN': alb0_data['WAVLEN MCRN'],
                'TOTAL_RAD': alb0_data['TOTAL RAD'], 'GRND_RFLCT': alb1_data['GRND RFLT'],
                'PROFILE': profile, 'INITIAL_H2O': wvp})
            
            profile_dfs[profile] = pd.concat([profile_dfs.get(profile, pd.DataFrame()), merged])
            accessed_folders.extend([f"{profile}_ALB0_WAT{wvp:.2f}", f"{profile}_ALB1_WAT{wvp:.2f}"])
        except Exception as e:
            print(f"Error processing {profile} pair: {', '.join(os.path.basename(p) for p in paths.values())}")
            print(f"Error details: {str(e)}")
    return profile_dfs, accessed_folders

def readTape6(main_dir, folders_accessed):
    data = []
    for folder in folders_accessed:
        tape6_path = os.path.join(main_dir, folder, 'tape6')
        if not os.path.exists(tape6_path):
            continue  # Skip this folder if file doesn't exist

        with open(tape6_path, 'r') as fP:
            lines = fP.readlines()

        line_89 = lines[88].strip() if len(lines) > 88 else ""
        line_87 = lines[86].strip() if len(lines) > 86 else ""
        final_h2o = (line_89[10:19].strip() if line_89.startswith("FINAL:") 
            
            else line_87[48:56].strip())

        parts = folder.split("_")
        atm_profile = parts[0]  # First part (e.g., MLS)
        initial_h2o = parts[-1].replace("WAT", "")  # Last part, removing 'WAT' (e.g., 0.25)
        data.append([atm_profile, initial_h2o, final_h2o])
        data_frame = pd.DataFrame(data, columns=["ATM_PROFILE", "INITIAL_H2O", "FINAL_H2O"])
    return data_frame

# Main
main_dir = 'MODTRAN_models_2025_b'
profile_dataframes, folders_accessed = process_tape7_scn(main_dir)
tape6Data = readTape6(main_dir, folders_accessed)

# Ensure INITIAL_H2O is numeric
tape6Data["INITIAL_H2O"] = pd.to_numeric(tape6Data["INITIAL_H2O"], errors="coerce")

# Update FINAL_H2O column using merge
ATM_DATA_FRAME = {}
for profile, df in profile_dataframes.items():
    if not df.empty:
        # Merge with tape6Data
        merged_df = df.merge(
            tape6Data[["ATM_PROFILE", "INITIAL_H2O", "FINAL_H2O"]],
            on=["ATM_PROFILE", "INITIAL_H2O"],
            how="left"
        )
        # Update FINAL_H2O column
        df["FINAL_H2O"] = merged_df["FINAL_H2O"]
        ATM_DATA_FRAME[profile] = df



