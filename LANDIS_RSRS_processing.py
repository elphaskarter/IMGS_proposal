# LANDIS RSR Analysis
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import norm

# Function for RSR calculation
def load_rsr(sensor: str, wavelength_range: np.ndarray, center: float, FWHM: float) -> np.ndarray:
    if sensor.upper() == 'GAUSS':
        sigma = FWHM / 2.3548
        rsr = norm.pdf(wavelength_range, loc=center, scale=sigma)
        rsr /= np.max(rsr)  # Normalize to max of 1
    elif sensor.upper() == 'RECT':
        rsr = np.where((wavelength_range >= center - FWHM / 2) & 
                       (wavelength_range <= center + FWHM / 2), 1.0, 0.0)
    else:
        raise ValueError("Invalid sensor type. Choose 'GAUSS' or 'RECT'.")
    return rsr

# Repository path
output_dir = "RSR_functions"
os.makedirs(output_dir, exist_ok=True)

# Extracted values from the Landsat Next Spectral Bandpass Table
bands_data = {
    "Band Name": ["NIR1", "Water_Vapor", "SWIR2a"],
    "Center Wavelength (µm)": [0.865, 0.945, 1.035],
    "Minimum Lower Band Edge (µm)": [0.855, 0.935, 1.025],
    "Maximum Upper Band Edge (µm)": [0.875, 0.955, 1.045]
}

df_bands = pd.DataFrame(bands_data)
df_bands["FWHM (µm)"] = df_bands["Maximum Upper Band Edge (µm)"] - df_bands["Minimum Lower Band Edge (µm)"]
wavelengths = np.linspace(0.3, 13.0, 100000)

# Generate RSR data and save to files
rsr_data = {}
band_limits = {}
for index, row in df_bands.iterrows():
    band = row['Band Name']
    FWHM = row['FWHM (µm)']
    cwv = row['Center Wavelength (µm)']
    
    # Generate RSR
    rsr = load_rsr("GAUSS", wavelengths, cwv, FWHM)
    
    # Compute band limits
    left_limit = cwv - FWHM / 2
    right_limit = cwv + FWHM / 2
    band_limits[band] = (left_limit, right_limit)
    
    # Save to file
    file_path = os.path.join(output_dir, f"{band}_RSR.txt")
    pd.DataFrame({"Wavelength": wavelengths, "RSR": rsr}).to_csv(file_path, sep='\t', index=False)
    rsr_data[band] = {"Wavelength": wavelengths, "RSR": rsr}

# # Create subplots for Band 12, 13, and 15
# fig, ax = plt.subplots(1, 1, figsize=(15, 5))

# def get_trimmed_data(band_name):
#     left, right = band_limits[band_name]
#     df = rsr_data[band_name]
#     mask = (df["Wavelength"] >= left) & (df["Wavelength"] <= right)
#     return df["Wavelength"][mask], df["RSR"][mask]

# # Get trimmed data for plotting
# nir1_wave, nir1_rsr = get_trimmed_data("NIR1")
# water_vapor_wave, water_vapor_rsr = get_trimmed_data("Water_Vapor")
# swir2a_wave, swir2_rsrs = get_trimmed_data("SWIR2a")

# # Dictionary of DataFrames (Band limits)
# SENSOR_RSR_FRAME = {
#     "NIR1": pd.DataFrame({"Wavelength": nir1_wave, "RSR": nir1_rsr }),
#     "Water_Vapor": pd.DataFrame({"Wavelength": water_vapor_wave, "RSR": water_vapor_rsr}),
#     "SWIR2a": pd.DataFrame({"Wavelength": swir2a_wave, "RSR": swir2_rsrs})}

# # Plot
# ax.plot(nir1_wave, nir1_rsr, label="NIR1 (Band12)", linewidth=2)
# ax.plot(water_vapor_wave, water_vapor_rsr, label="Water Vapor (Band13)", linewidth=2)
# ax.plot(swir2a_wave, swir2_rsrs, label="SWIR2a (Band15)", linewidth=2)

# ax.set_xlabel("Wavelength (µm)")
# ax.set_ylabel("RSR")
# ax.set_title("Band 12, 13, and 15 RSR (Threshold-Based Limits)")
# ax.legend()
# plt.tight_layout()
# plt.show()

# # Print band limits
# print(f"NIR1 Band Limits: [{band_limits['NIR1'][0]:.4f} µm, {band_limits['NIR1'][1]:.4f} µm]")
# print(f"Water Vapor Band Limits: [{band_limits['Water_Vapor'][0]:.4f} µm, {band_limits['Water_Vapor'][1]:.4f} µm]")
# print(f"SWIR2a Band Limits: [{band_limits['SWIR2a'][0]:.4f} µm, {band_limits['SWIR2a'][1]:.4f} µm]")

if __name__ == "__main__":
    pass