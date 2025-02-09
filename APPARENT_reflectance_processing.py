from MODTRAN_processing import MODTRAN_DATA_FRAME
from ECOSTRESS_spectrum_processing import AVG_SPEC_DATA_FRAME
from LANDIS_RSRS_processing import SENSOR_RSR_FRAME
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


# Apparent reflectance
def apprnt_reflectance(L_TOA, E_SUN, THETA_SUN, DOY):
    d = 1 - 0.01672 * np.cos(2*np.pi*(DOY-4)/365)
    THETA_SUN_rad = np.radians(THETA_SUN)
    rho_app = (np.pi * L_TOA * d**2) / (E_SUN * np.cos(THETA_SUN_rad))
    return rho_app

def effect_reflect(mod_data, rsr_df, bands):
    wl = mod_data['WAVLEN']
    reflect = mod_data['TOT_TRANS']
    rsr_wl = rsr_df['Wavelength']

    eff_reflect = {}
    for band, (min_wl, max_wl) in bands.items():
        rsr = rsr_df[band]
        mask = (wl >= min_wl) & (wl <= max_wl)
        filt_wl = wl[mask]
        filt_trans = reflect[mask]
        
        interp_rsr = interp1d(rsr_wl, rsr, kind='linear', fill_value="extrapolate")
        filt_rsr = interp_rsr(filt_wl)
        
        num = np.trapz(filt_trans * filt_rsr, filt_wl)
        denom = np.trapz(filt_rsr, filt_wl)
        eff_trans = np.round(num / denom, 3)
        eff_reflect[band] = eff_trans
    return eff_reflect

