# -- code -- 
# Author:ELPHAS KHATA
# CODE: TPW
# -- end --
import numpy as np
import pandas as pd

def read_modtran_tape6(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        (freq, wavlen_micron, path_thermal_micron, surface_emission, 
        path_scattered_total_micron, solar_single, ground_reflected_total,
        radiance_direct_cm, total_radiance, integral, total_trans) = [[] for _ in range(11)]
        
        for i, line in enumerate(lines):
            if 'FREQ' in line and 'WAVLEN' in line: 
                start_idx = i + 1
                break

        for line in lines[start_idx:]:
            parts = line.split()
            if len(parts) == 15:
                freq.append(float(parts[0]))
                wavlen_micron.append(float(parts[1]))
                path_thermal_micron.append(float(parts[3]))
                surface_emission.append(float(parts[4]))
                path_scattered_total_micron.append(float(parts[6]))
                solar_single.append(float(parts[7]))
                ground_reflected_total.append(float(parts[9]))
                radiance_direct_cm.append(float(parts[10]))             
                total_radiance.append(float(parts[12]))
                integral.append(float(parts[13]))  
                total_trans.append(float(parts[14]))

        arrays = np.array([path_thermal_micron, path_scattered_total_micron, ground_reflected_total, 
                           radiance_direct_cm, total_radiance]) * 1e4
        (path_thermal_micron, path_scattered_total_micron, ground_reflected_total, radiance_direct_cm, total_radiance) = arrays
        total_trans = np.array(total_trans)

        columns = ['FREQ', 'WAVLEN', 'PATH_THRML', 'SURF_EMISS', 'PATH_SCAT_RAD', 'SOLAR_SINGLE', 'GRND_RFLCT', 
                   'DIRECT_PATH', 'TOT_RAD', 'INTEGRAL', 'TOT_TRANS']
        values = [freq, wavlen_micron, path_thermal_micron, surface_emission, path_scattered_total_micron, 
                  solar_single, ground_reflected_total, radiance_direct_cm, total_radiance, integral, total_trans]
        data = pd.DataFrame(dict(zip(columns, values)))
    return data

# Call function
input_path = "MODTRAN_reanalysis\tape6"
df = read_modtran_tape6(input_path)