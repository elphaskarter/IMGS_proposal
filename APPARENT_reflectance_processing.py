#--APPARENT REFLECTANCE CODE--#

from LANDIS_RSRS_processing import SENSOR_RSR_FRAME, band_limits
from L_TOA_processing import GROUPED_MODTRAN_DATA, profile_dict
from ECOSTRESS_spectrum_processing import modtran_wavelen
from scipy.interpolate import interp1d
import numpy as np
import csv
import matplotlib.pyplot as plt
import contextlib
import io
import pandas as pd

# Suppress print statements
with contextlib.redirect_stdout(io.StringIO()):
    GROUPED_MODTRAN_DATA  
    SENSOR_RSR_FRAME

# Suppress plots
plt.close('all')  # Close any open plots

def band_effective_data(wl, reflect, rsr_frame, bands):
    wl = np.array(wl)
    reflect = np.array(reflect)

    eff_val = {}
    for band, (min_wl, max_wl) in bands.items():
        rsr_wl = np.array(rsr_frame[band]['Wavelength'])
        rsr = np.array(rsr_frame[band]['RSR'])

        mask = (wl >= min_wl) & (wl <= max_wl)
        filt_wl = wl[mask]
        filt_trans = reflect[mask]

        interp_rsr = interp1d(rsr_wl, rsr, kind='linear', fill_value="extrapolate")
        filt_rsr = interp_rsr(filt_wl)

        num = np.trapz(filt_trans * filt_rsr, filt_wl)
        denom = np.trapz(filt_rsr, filt_wl)
        eff_trans = np.round(num / denom, 3) if denom != 0 else np.nan  # Avoid division by zero

        eff_val[band] = eff_trans

    return eff_val

def downsample(wav_micron, reflec, target_wav):
    interp_func = interp1d(wav_micron, reflec, kind='linear', fill_value="extrapolate")
    dwnsmpl_val = interp_func(target_wav)
    return dwnsmpl_val

def read_CSV_data(file):
    wavelength = []
    solar_irradiance = []
    with open(file, 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # Skip the header row
        
        for row in csv_reader:
            wavelength.append(float(row[1])) # Wavelength (Mm)
            solar_irradiance.append(float(row[3]))  # Solar Irradiance (W M-2 uM-1)
    
    return np.array(wavelength), np.array(solar_irradiance)

# Call functions here
wave_ = np.array(modtran_wavelen)
wavelength, irradiance = read_CSV_data('solar_irradiance.txt')
solar_irrad = downsample(wavelength, irradiance, wave_)
solar_irrad_df = pd.DataFrame({'WAVELENGTH': wave_, 'SOLAR_IRRADIANCE': solar_irrad})

fig, ax = plt.subplots(1, 1, figsize=(6, 4))
ax.plot(modtran_wavelen, solar_irrad, label='Solar Irradiance', linestyle='-', linewidth=2)
ax.set_xlabel('Wavelength (um)', fontsize=12)
ax.set_ylabel('Solar Irradiance (W m-2 um-1)', fontsize=12)
ax.set_title('SOLAR IRRADIANCE', fontsize=14)
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()

bands = {'NIR1': band_limits['NIR1'], 'Water_Vapor': band_limits['Water_Vapor'], 
         'SWIR2a': band_limits['SWIR2a']}

IRRAD_SOLAR = solar_irrad_df['SOLAR_IRRADIANCE']

# MODTRAN_MODEL_DATA = {
#     profile: {
#         group_name: group_df.assign(SOLAR_IRRADIANCE=IRRAD_SOLAR)
#         for group_name, group_df in groups.items()
#     }
#     for profile, groups in GROUPED_MODTRAN_DATA.items() 
#     if groups  # Filter out empty profiles
# }

# MODTRAN_MODEL_DATA = {
#     profile: {
#         group_name: group_df.assign(
#             SOLAR_IRRADIANCE=IRRAD_SOLAR,
#             R_manmade=lambda x: x['L_TOA_manmade'] / x['SOLAR_IRRADIANCE'],
#             R_vegetation=lambda x: x['L_TOA_vegetation'] / x['SOLAR_IRRADIANCE'],
#             R_water=lambda x: x['L_TOA_water'] / x['SOLAR_IRRADIANCE']
#         )
#         for group_name, group_df in groups.items()
#     }
#     for profile, groups in GROUPED_MODTRAN_DATA.items() 
#     if groups
# }

SURFACE_TYPES = ['manmade', 'vegetation', 'water']
MODTRAN_MODEL_DATA = {
    profile: {
        group_name: group_df.assign(
            SOLAR_IRRADIANCE=IRRAD_SOLAR,
            **{
                f'R_{stype}': lambda x, st=stype: x[f'L_TOA_{st}'] / x['SOLAR_IRRADIANCE']
                for stype in SURFACE_TYPES
            }
        )
        for group_name, group_df in groups.items()
    }
    for profile, groups in GROUPED_MODTRAN_DATA.items() 
    if groups
}

for profile, groups in MODTRAN_MODEL_DATA.items():
    print(f"Profile: {profile}")
    for group_name, group_df in groups.items():
        print(f"  Group: {group_name}")
        print(group_df)

profile = list(MODTRAN_MODEL_DATA.keys())[0]
group = list(MODTRAN_MODEL_DATA[profile].keys())[0]
df = MODTRAN_MODEL_DATA[profile][group]

# print(f"Profile: {profile}")
# print(f"Group: {group}")
# print(df)
print(df[['L_TOA_manmade', 'R_manmade', 'SOLAR_IRRADIANCE']])
# Check one of the output files

with pd.ExcelWriter("all_results.xlsx", engine='openpyxl') as writer:
    for profile, groups in MODTRAN_MODEL_DATA.items():
        for group_name, group_df in groups.items():
            # Create unique sheet name combining profile and group
            sheet_name = f"{profile}_{group_name}"[:31]
            group_df.to_excel(writer, sheet_name=sheet_name, index=False)

