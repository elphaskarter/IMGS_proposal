"""
Reads ECOSTRESS spectral data file
Returns:
        Tuple of (wavelengths, reflectances) as numpy arrays
        wavelengths: in micrometers (µm)
        reflectances: scaled 0-1
"""
import numpy as np
from scipy.interpolate import interp1d
from modtran_processing import PROFILES_DATA_FRAME


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

# Spectral downsampling
def downsample(wav_micron, reflec, target_wav):
    interp_func = interp1d(wav_micron, reflec, kind='linear', bounds_error=False, fill_value=np.nan)
    dwnsmpl_val = interp_func(target_wav)
    return dwnsmpl_val

wave = PROFILES_DATA_FRAME['MLS']['WAVLEN_MCRN']
# oak_wav_micron, oak_reflec = read_ECOSTRESS_data.read_ECOSTRESS_data('Quercus_agrifolia.txt')
# asphalt_wav_micron, asphalt_reflec = read_ECOSTRESS_data.read_ECOSTRESS_data('Construction_Asphalt.txt')
# oak_downsmpl = downsample(oak_wav_micron, oak_reflec, wave)
# asphalt_downsmpl = downsample(asphalt_wav_micron, asphalt_reflec, wave)
