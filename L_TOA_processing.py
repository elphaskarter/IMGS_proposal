from MODTRAN_processing import MODTRAN_DATA_FRAME
from ECOSTRESS_spectrum_processing import AVG_SPEC_DATA_FRAME
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def compute_L_toa(grouped_data):
    L_toa = {}
    for profile, groups in grouped_data.items():
        L_toa[profile] = {}
        
        for water_vapor_level, df in groups.items():
            L_toa[profile][water_vapor_level] = {
                'manmade': df['GRND_RFLCT'] * df['manmade_reflect'] + df['TOTAL_RAD'],
                'vegetation': df['GRND_RFLCT'] * df['veg_reflect'] + df['TOTAL_RAD'],
                'water': df['GRND_RFLCT'] * df['water_reflect'] + df['TOTAL_RAD']}
    return L_toa

def add_L_TOA_cols(grouped_data, ltoa_data):
    for profile, groups in grouped_data.items():
        for water_vapor_level, df in groups.items():
            current_df = df.copy()
            
            current_df['L_TOA_manmade'] = ltoa_data[profile][water_vapor_level]['manmade']
            current_df['L_TOA_vegetation'] = ltoa_data[profile][water_vapor_level]['vegetation']
            current_df['L_TOA_water'] = ltoa_data[profile][water_vapor_level]['water']
            
            # Update the DataFrame in the original structure
            grouped_data[profile][water_vapor_level] = current_df
    
    return grouped_data

# gouping data to calculate L_TOA
water_vapor = [0.25, 0.50, 1.00, 1.50, 2.0] # Water vapor list here
profile_dict = {}
group_counts = {}

for profile, df in MODTRAN_DATA_FRAME.items():
    water_vapor_groups = {}
    
    for value in water_vapor:
        matched_rows = df[np.isclose(df['INITIAL_H2O'], value, atol=0.01)] 
        if not matched_rows.empty:
            water_vapor_groups[f'{value:.2f}'] = matched_rows

    profile_dict[profile] = water_vapor_groups
    group_counts[profile] = len(water_vapor_groups) 

for profile, groups in profile_dict.items():
    print(f"Profile: {profile}")
    for group_name, group_df in groups.items():
        print(f"  Group: {group_name}")
        print(group_df)

for profile, count in group_counts.items():
    print(f"Profile: {profile}, Total Groups: {count}")

# Add the reflectance data on each grouped data frame
manmade_reflectData = AVG_SPEC_DATA_FRAME['manmade']['reflectance']
veg_reflectData = AVG_SPEC_DATA_FRAME['vegetation']['reflectance']
water_reflectData = AVG_SPEC_DATA_FRAME['water']['reflectance']

GROUPED_MODTRAN_DATA = {}
for profile, groups in profile_dict.items():
    GROUPED_MODTRAN_DATA[profile] = {}
    for group_name, group_df in groups.items():
  
        new_df = group_df.copy()
        new_df.loc[:, 'manmade_reflect'] = manmade_reflectData
        new_df.loc[:, 'veg_reflect'] = veg_reflectData
        new_df.loc[:, 'water_reflect'] = water_reflectData
        GROUPED_MODTRAN_DATA[profile][group_name] = new_df

for profile, groups in GROUPED_MODTRAN_DATA.items():
    print(f"Profile: {profile}")
    for group_name, group_df in groups.items():
        print(f"  Group: {group_name}")
        print(group_df)

L_TOA_DATA = compute_L_toa(GROUPED_MODTRAN_DATA)
GROUPED_MODTRAN_DATA = add_L_TOA_cols(GROUPED_MODTRAN_DATA, L_TOA_DATA)

if __name__ == "__main__":
    pass
