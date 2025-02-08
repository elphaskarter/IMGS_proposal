#!/bin/bash

# Ensure Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed! Install it first."
    exit 1
fi

# List Atmospheric Profile Options
echo "Select an Atmospheric Model:"
echo "1. TROPICAL (TRP)"
echo "2. MID-LATITUDE SUMMER (MLS)"
echo "3. MID-LATITUDE WINTER (MLW)"
echo "4. SUBARCTIC SUMMER (SAS)"
echo "5. SUBARCTIC WINTER (SAW)"

# User selects the atmospheric model
read -p "Enter the number (1-5): " ATM
if [[ ! "$ATM" =~ ^[1-5]$ ]]; then
    echo "❌ Invalid choice! Please enter a number between 1 and 5."
    exit 1
fi

# Map ATM number to abbreviation
declare -A ATM_MAP=( [1]="TRP" [2]="MLS" [3]="MLW" [4]="SAS" [5]="SAW" )
ATM_ABBR=${ATM_MAP[$ATM]}

# User enters Albedo
read -p "Enter Albedo Value (0.00 - 1.00): " ALBEDO
if ! [[ "$ALBEDO" =~ ^[0-9]+(\.[0-9]{1,2})?$ ]] || (( $(echo "$ALBEDO < 0 || $ALBEDO > 1" | bc -l) )); then
    echo "❌ Invalid input! Enter a value between 0.00 and 1.00."
    exit 1
fi

# User manually enters Water Vapor values
echo "Enter Water Vapor Scaling values separated by spaces (e.g., 0.25 0.5 1.0 1.5 2.0):"
read -a WATER_VALUES

# Validate Water Vapor inputs
for WATER in "${WATER_VALUES[@]}"; do
    if ! [[ "$WATER" =~ ^[0-9]+(\.[0-9]{1,3})?$ ]]; then
        echo "❌ Invalid water vapor value: $WATER. Must be a number with up to 3 decimal places."
        exit 1
    fi
done

# Loop over manually entered water vapor values
for WATER in "${WATER_VALUES[@]}"; do
    # Format directory name
    ALBEDO_FORMAT=$(printf "%.0f" "$ALBEDO")  # Convert albedo to integer (0, 1)
    WATER_FORMAT=$(printf "%.1f" "$WATER")    # Keep one decimal place for water
    TASK_DIR="${ATM_ABBR}_ALB${ALBEDO_FORMAT}_WAT${WATER_FORMAT}"

    # Create the task directory if it doesn't exist
    mkdir -p "$TASK_DIR"

    # Run Python script to generate tape5 in the main directory
    python modify_tape5.py "$ATM" "$WATER" "$ALBEDO"

    # Move tape5 into the task directory
    mv tape5 "$TASK_DIR"/

    # Navigate to task directory
    cd "$TASK_DIR"

    # Create symbolic link to MODTRAN DATA directory
    ln -s /dirs/pkg/Mod4v3r1/DATA/

    # Execute MODTRAN
    echo "Running MODTRAN for WATER=$WATER..."
    /dirs/pkg/Mod4v3r1/Mod4v3r1.exe

    # Check if MODTRAN executed successfully
    if [[ $? -eq 0 ]]; then
        echo "✅ MODTRAN execution completed for WATER=$WATER! Check $TASK_DIR for details."
    else
        echo "❌ MODTRAN execution failed for WATER=$WATER! Check $TASK_DIR for errors."
    fi

    # Return to original directory
    cd ..
done

echo "✅ All MODTRAN simulations completed!"

