from LANDIS_RSRS_processing import SENSOR_RSR_FRAME, band_limits
from scipy.interpolate import interp1d
import numpy as np
from L_TOA_processing import GROUPED_MODTRAN_DATA
import os

def band_effective_data(wl, reflect, rsr_wl, rsr_df, bands):
    eff_val = {}
    for band, (min_wl, max_wl) in bands.items():
        rsr = rsr_df
        mask = (wl >= min_wl) & (wl <= max_wl)
        filt_wl = wl[mask]
        filt_trans = reflect[mask]
        
        interp_rsr = interp1d(rsr_wl, rsr, kind='linear', fill_value="extrapolate")
        filt_rsr = interp_rsr(filt_wl)
        
        num = np.trapz(filt_trans * filt_rsr, filt_wl)
        denom = np.trapz(filt_rsr, filt_wl)
        eff_trans = np.round(num / denom, 3)
        eff_val[band] = eff_trans
    return eff_val

def downsample(wav_micron, reflec, target_wav):
    interp_func = interp1d(wav_micron, reflec, kind='linear', fill_value="extrapolate")
    dwnsmpl_val = interp_func(target_wav)
    return dwnsmpl_val

output_dir = "solar_irradiance.txt"
os.makedirs(output_dir, exist_ok=True)


bands = {'NIR1': band_limits['NIR1'], 'Water_Vapor': band_limits['Water_Vapor'], 
         'SWIR2a': band_limits['SWIR2a']}

