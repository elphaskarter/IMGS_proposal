"""
Reads ECOSTRESS spectral data file
Returns:
        Tuple of (wavelengths, reflectances) as numpy arrays
        wavelengths: in micrometers (µm)
        reflectances: scaled 0-1
"""
import numpy as np
from scipy.interpolate import interp1d
from MODTRAN_processing import MODTRAN_DATA_FRAME
import matplotlib.pyplot as plt
import os
import pandas as pd
from collections import defaultdict
import contextlib
import io

# Suppress print statements
with contextlib.redirect_stdout(io.StringIO()):
    MODTRAN_DATA_FRAME  

# Suppress plots
plt.close('all')  # Close any open plots

def ECOSTRESS_path():
    ecoDir = 'ecostress_download'
    for filename in os.listdir(ecoDir):
        if filename.endswith('.txt'):
            yield filename

def read_ECOSTRESS_data(file):
    wav = []
    reflect = []
    with open(file, 'r') as f:
        # Skip metadata headers
        for line in f:
            if line.strip() and line.strip()[0].isdigit():
                break  # Found first data line
        parts = line.strip().split()
        wav.append(float(parts[0]))
        reflect.append(float(parts[1])/100)  # Scale to 0-1
        for line in f:
            if line.strip():  # Skip empty lines
                parts = line.strip().split()
                wav.append(float(parts[0]))
                reflect.append(float(parts[1])/100)
    return np.array(wav), np.array(reflect)

def downsample(wav_micron, reflec, target_wav):
    interp_func = interp1d(wav_micron, reflec, kind='linear', fill_value="extrapolate")
    dwnsmpl_val = interp_func(target_wav)
    return dwnsmpl_val

def plot_spectra(data_frames):
    num_samples = len(data_frames)  # Determine number of subplots needed
    fig, ax = plt.subplots(1, num_samples, figsize=(5 * num_samples, 6))  
    
    if num_samples == 1:
        ax = [ax]

    for i, (sample_type, df) in enumerate(data_frames.items()):
            ax[i].plot(df['wavelength'], df['reflectance'], label=f'{sample_type} Average', linestyle='dashed', linewidth=2)
            ax[i].set_xlabel('Wavelength (microns)', fontsize=12)
            ax[i].set_ylabel('Reflectance', fontsize=12)
            ax[i].set_title(f'{sample_type} Average Reflectance', fontsize=14)
            ax[i].legend(loc='best', fontsize=10)
            ax[i].grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()

# Read ECOSTRESS data
mlw_df = MODTRAN_DATA_FRAME['MLW']
modtran_wavelen = mlw_df.groupby('INITIAL_H2O')['WAVLEN_MCRN'].apply(list).to_dict()
modtran_wavelen= np.array(list(modtran_wavelen.values())[0]) # MODTRAN SPECTRUM

spectra_dict = defaultdict(list)  # Initialize with defaultdict
for filename in ECOSTRESS_path():
    file_path = os.path.join('ecostress_download', filename)
    oak_wav_micron, oak_reflec = read_ECOSTRESS_data(file_path)
    reflect_downsmpl = downsample(oak_wav_micron, oak_reflec, modtran_wavelen)
    
    # store results in a dict
    sample_name = filename.split('.')[0]
    sorted_pairs = sorted(zip(modtran_wavelen, reflect_downsmpl))
    sample_wave, sample_reflect = zip(*sorted_pairs)
    spectra_dict[sample_name].append((sample_wave, sample_reflect))

# DataFrames for each sample type
dataframes = {}
AVG_SPEC_DATA_FRAME = {} # average reflectance per sample 
for sample_type, samples in spectra_dict.items():
    df = pd.DataFrame()
    reflectance_values = []  # Store reflectance values for averaging
    for i, (wave, reflect) in enumerate(samples, start=1):
        df[f'sample_{i}_wave'] = wave
        df[f'sample_{i}_reflect'] = reflect
        reflectance_values.append(reflect)

    avg_reflectance = pd.DataFrame(reflectance_values).mean(axis=0)
    avg_df = pd.DataFrame({'wavelength': wave,  'reflectance': avg_reflectance})
    dataframes[sample_type] = df
    AVG_SPEC_DATA_FRAME[sample_type] = avg_df 

plot_spectra(AVG_SPEC_DATA_FRAME)

if __name__ == "__main__":
    pass
# END