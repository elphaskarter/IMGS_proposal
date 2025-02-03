import numpy as np
import os

# GitHub repository path
output_dir = "RSR_functions"
os.makedirs(output_dir, exist_ok=True)

# Landsat Next Bands (CWV in microns)
bands = {
    "Violet": 0.412, "Coastal_Aerosol": 0.442, "Blue": 0.490, "Green": 0.560, "Yellow": 0.600,
    "Orange": 0.620, "Red_1": 0.650, "Red_2": 0.665, "Red_Edge_1": 0.705, "Red_Edge_2": 0.740,
    "NIR_Broad": 0.865, "NIR1": 0.945, "Water_Vapor": 1.035, "SWIR1": 1.375,
    "SWIR2a": 1.610, "SWIR2b": 2.105, "TIR_1": 3.100, "TIR_2": 8.600, 
    "TIR_3": 9.100, "TIR_4": 11.300, "TIR_5": 12.000
}

# Generate RSR data
sigma_values = {band: cwv * 0.05 for band, cwv in bands.items()}
wavelengths = np.linspace(0.3, 13.0, 1000)

for band, cwv in bands.items():
    sigma = sigma_values[band]
    rsr = np.exp(-((wavelengths - cwv) ** 2) / (2 * sigma ** 2))
    
    file_path = os.path.join(output_dir, f"{band}_RSR.txt")
    with open(file_path, "w") as f:
        f.write("# Wavelength (µm)\tRSR\n")
        for wl, rsr_val in zip(wavelengths, rsr):
            f.write(f"{wl:.4f}\t{rsr_val:.6f}\n")

print(f"Files saved to GitHub repository directory: {output_dir}")
