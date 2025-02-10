import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# repository path
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

# threshold for band limits (1% of peak)
THRESHOLD = 0.01

# Generate RSR data
sigma_values = {band: cwv * 0.05 for band, cwv in bands.items()}
wavelengths = np.linspace(0.3, 13.0, 10000)

rsr_data = {}
band_limits = {}  
for band, cwv in bands.items():
    sigma = sigma_values[band]
    rsr = np.exp(-((wavelengths - cwv) ** 2) / (2 * sigma ** 2))
    
    # Compute band limits using threshold
    delta = sigma * np.sqrt(-2 * np.log(THRESHOLD))
    left_limit = cwv - delta
    right_limit = cwv + delta
    band_limits[band] = (left_limit, right_limit)
    
    # Save data
    file_path = os.path.join(output_dir, f"{band}_RSR.txt")
    with open(file_path, "w") as f:
        f.write("Wavelength\tRSR\n")
        for wl, rsr_val in zip(wavelengths, rsr):
            f.write(f"{wl:.4f}\t{rsr_val:.6f}\n")
    
    df = pd.DataFrame({"Wavelength": wavelengths, "RSR": rsr})
    rsr_data[band] = df

# Create subplots for Band 12, 13, and 15
fig, ax = plt.subplots(1, 1, figsize=(15, 5))

def get_trimmed_data(band_name):
    left, right = band_limits[band_name]
    df = rsr_data[band_name]
    mask = (df["Wavelength"] >= left) & (df["Wavelength"] <= right)
    return df["Wavelength"][mask], df["RSR"][mask]

# Get trimmed data for plotting
nir1_wave, nir1_rsr = get_trimmed_data("NIR1")
water_vapor_wave, water_vapor_rsr = get_trimmed_data("Water_Vapor")
swir2a_wave, swir2_rsrs = get_trimmed_data("SWIR2a")

# Dictionary of DataFrames (Band limits)
SENSOR_RSR_FRAME = {
    "NIR1": pd.DataFrame({"Wavelength": nir1_wave, "RSR": nir1_rsr }),
    "Water_Vapor": pd.DataFrame({"Wavelength": water_vapor_wave, "RSR": water_vapor_rsr}),
    "SWIR2a": pd.DataFrame({"Wavelength": swir2a_wave, "RSR": swir2_rsrs})
}

# Plot
ax.plot(nir1_wave, nir1_rsr, label="NIR1 (Band12)", linewidth=2)
ax.plot(water_vapor_wave, water_vapor_rsr, label="Water Vapor (Band13)", linewidth=2)
ax.plot(swir2a_wave, swir2_rsrs, label="SWIR2a (Band15)", linewidth=2)

# Add vertical lines to mark band edges
for band_name, color in zip(["NIR1", "Water_Vapor", "SWIR2a"], ["blue", "green", "red"]):
    left, right = band_limits[band_name]
    ax.axvline(left, color=color, linestyle="--", alpha=0.5)
    ax.axvline(right, color=color, linestyle="--", alpha=0.5)

ax.set_xlabel("Wavelength (µm)")
ax.set_ylabel("RSR")
ax.set_title("Band 12, 13, and 15 RSR (Threshold-Based Limits)")
ax.legend()

plt.tight_layout()
plt.show()

# Print band limits
print(f"NIR1 Band Limits: [{band_limits['NIR1'][0]:.4f} µm, {band_limits['NIR1'][1]:.4f} µm]")
print(f"Water Vapor Band Limits: [{band_limits['Water_Vapor'][0]:.4f} µm, {band_limits['Water_Vapor'][1]:.4f} µm]")
print(f"SWIR2a Band Limits: [{band_limits['SWIR2a'][0]:.4f} µm, {band_limits['SWIR2a'][1]:.4f} µm]")

if __name__ == "__main__":
    pass