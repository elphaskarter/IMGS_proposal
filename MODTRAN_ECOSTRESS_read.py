# # -- code -- 
# """
# Author:ELPHAS KHATA
# CODE: Reads tape7.scn from MODTRAN and generates L_TOA
# """
# # -- end --
# import numpy as np
# import pandas as pd

# def read_modtran_tape7scn(filename):
#     with open(filename, 'r') as file:
#         lines = file.readlines()
#         (wavlen_micron, ground_reflected_total, total_radiance) = [[] for _ in range(11)]
        
#         for i, line in enumerate(lines):
#             if 'FREQ' in line and 'WAVLEN' in line: 
#                 start_idx = i + 1
#                 break

#         for line in lines[start_idx:]:
#             parts = line.split()
#             if len(parts) == 15:
#                 wavlen_micron.append(float(parts[1]))
#                 ground_reflected_total.append(float(parts[9]))
#                 total_radiance.append(float(parts[12]))

#         arrays = np.array([wavlen_micron, ground_reflected_total, total_radiance]) * 1e4
#         (wavlen_micron, ground_reflected_total, total_radiance) = arrays
#         total_trans = np.array(total_trans)

#         columns = ['WAVLEN', 'GRND_RFLCT', 'TOT_RAD']
#         values = [wavlen_micron, ground_reflected_total, total_radiance]
#         data = pd.DataFrame(dict(zip(columns, values)))
#     return data

# # Call function
# input_path = "processed_data"
# df = read_modtran_tape7scn(input_path)

import os
import glob
import numpy as np
import pandas as pd

def read_modtran_tape7scn(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        wavlen_micron, ground_reflected_total, total_radiance = [], [], []
        start_idx = None
        
        # Identify the starting index for the data
        for i, line in enumerate(lines):
            if 'WAVLEN NCRN' in line:
                start_idx = i + 1
                break

        if start_idx is None:
            raise ValueError(f"Header not found in {filename}")

        # Read spectral data
        for line in lines[start_idx:]:
            parts = line.split()
            if len(parts) == 15:
                wavlen_micron.append(float(parts[1]))
                ground_reflected_total.append(float(parts[9]))
                total_radiance.append(float(parts[12]))

        # Convert to NumPy array and scale wavelength
        arrays = np.array([wavlen_micron, ground_reflected_total, total_radiance]) * 1e4
        wavlen_micron, ground_reflected_total, total_radiance = arrays

        return pd.DataFrame({'WAVLEN': wavlen_micron, 'GRND_RFLCT': ground_reflected_total, 'TOT_RAD': total_radiance})

    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return None

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
                    data = read_modtran_tape7scn(scn_file)
                    
                    if data is not None:
                        data['ALBEDO'] = albedo
                        data['WATER_VAPOR'] = water_vapor
                        data['FILE_NAME'] = file_name
                        all_data.append(data)

            except Exception as e:
                print(f"Error processing {subdir}: {e}")

    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Execution
input_path = "processed_data"
df = process_directory(input_path)

print(df.head())
