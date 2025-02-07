#!/bin/bash

# Ensure Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed! Install it first."
    exit 1
fi

# List Atmospheric Profile Options
echo "Select an Atmospheric Model:"
echo "1. TROPICAL"
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

# User enters Water Vapor
read -p "Enter Water Vapor Scaling (e.g., 0.000 - 100.000): " WATER
if ! [[ "$WATER" =~ ^[0-9]+(\.[0-9]{1,3})?$ ]]; then
    echo "❌ Invalid input! Enter a number with up to 3 decimal places."
    exit 1
fi

# User enters Albedo
read -p "Enter Albedo Value (0.00 - 1.00): " ALBEDO
if ! [[ "$ALBEDO" =~ ^[0-9]+(\.[0-9]{1,2})?$ ]] || (( $(echo "$ALBEDO < 0 || $ALBEDO > 1" | bc -l) )); then
    echo "❌ Invalid input! Enter a value between 0.00 and 1.00."
    exit 1
fi

# Run Python script with user inputs
python modify_tape5.py "$ATM" "$WATER" "$ALBEDO"

# Check if modification was successful
if [[ $? -eq 0 ]]; then
    echo "✅ 'tape5' file has been successfully modified!"
else
    echo "❌ Error modifying 'tape5' file."
fi
