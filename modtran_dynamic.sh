#!/bin/bash

# ===== CONFIGURATION =====
MODTRAN_DATA_DIR="/dirs/pkg/Mod4v3r1/DATA"
MODTRAN_EXE="/dirs/pkg/Mod4v3r1/Mod4v3r1.exe"
PARENT_INPUT_DIR="$1"
# =========================

# Check if parent input directory is provided
if [ -z "$PARENT_INPUT_DIR" ]; then
  echo "Usage: $0 <parent_input_directory>"
  exit 1
fi

# Validate MODTRAN executable
if [ ! -x "$MODTRAN_EXE" ]; then
  echo "Error: MODTRAN executable not found or not executable: $MODTRAN_EXE"
  exit 1
fi

# Define output directory for processed data
FINAL_PARENT_DIR="processed_data"
mkdir -p "$FINAL_PARENT_DIR"

# Process each subdirectory in the parent input directory
for INPUT_DIR in "$PARENT_INPUT_DIR"/*; do
  [ -d "$INPUT_DIR" ] || continue  # Ensure it's a directory
  echo "Checking folder: $INPUT_DIR"

  INPUT_DIR_BASENAME=$(basename "$INPUT_DIR")

  # Extract suffix from input directory (e.g., "0.25" from "h20_0.25")
  SUFFIX=$(echo "$INPUT_DIR_BASENAME" | awk -F'_' '{print $2}')
  
  if [[ -z "$SUFFIX" || ! "$SUFFIX" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Skipping $INPUT_DIR: Invalid naming format (expected h20_XX.XX)"
    continue
  fi

  echo "Processing directory: $INPUT_DIR_BASENAME (SUFFIX: $SUFFIX)"
  echo "Found $(ls "$INPUT_DIR"/*.tp5 2>/dev/null | wc -l) .tp5 files"

  # Process all .tp5 files in the input directory
  shopt -s nullglob
  TP5_FILES=("$INPUT_DIR"/*.tp5)

  if [ ${#TP5_FILES[@]} -eq 0 ]; then
    echo "No .tp5 files found in $INPUT_DIR. Skipping."
    continue
  fi

  for TP5_FILE in "${TP5_FILES[@]}"; do
    # Extract profile and collection from filename (e.g., "MLS" and "alb0" from "tape5_MLS_alb0.tp5")
    FILENAME=$(basename "$TP5_FILE" .tp5)
    PROFILE=$(echo "$FILENAME" | cut -d'_' -f2)
    COLLECTION=$(echo "$FILENAME" | cut -d'_' -f3)

    # Validate parsed values
    if [ -z "$PROFILE" ] || [ -z "$COLLECTION" ]; then
      echo "Skipping $TP5_FILE: Invalid filename format (expected tape5_PROFILE_COLLECTION.tp5)"
      continue
    fi

    # Create directories for full results and selected files
    FULL_OUTPUTS_DIR="$FINAL_PARENT_DIR/${INPUT_DIR_BASENAME}/${PROFILE}_${COLLECTION}"
    SELECTED_RESULTS_DIR="$FINAL_PARENT_DIR/${COLLECTION}_${SUFFIX}"
    mkdir -p "$FULL_OUTPUTS_DIR"
    mkdir -p "$SELECTED_RESULTS_DIR"

    # Create temporary task directory
    TASK_DIR="$FINAL_PARENT_DIR/tmp_${PROFILE}_${COLLECTION}"
    mkdir -p "$TASK_DIR"

    # Cleanup function in case of failure
    trap 'rm -rf "$TASK_DIR"' EXIT

    # Copy .tp5 file to task directory and rename to "tape5"
    cp "$TP5_FILE" "$TASK_DIR/tape5"

    # Create symbolic link to MODTRAN DATA
    ln -sf "$MODTRAN_DATA_DIR" "$TASK_DIR/DATA"

    # Run MODTRAN in the task directory
    echo "Processing: $FILENAME"
    (cd "$TASK_DIR" && "$MODTRAN_EXE") || { 
      echo "MODTRAN failed for $FILENAME"; 
      continue; 
    }

    # Move ALL output files to the full_outputs directory (organized by original directory name)
    mv "$TASK_DIR"/* "$FULL_OUTPUTS_DIR/" 2>/dev/null

    # Move only tape7 and tape7.scn to the selected results directory
    mv "$FULL_OUTPUTS_DIR/tape7" "$SELECTED_RESULTS_DIR/${PROFILE}_tape7" 2>/dev/null
    mv "$FULL_OUTPUTS_DIR/tape7.scn" "$SELECTED_RESULTS_DIR/${PROFILE}_tape7.scn" 2>/dev/null

    # Cleanup temporary directory
    rm -rf "$TASK_DIR"
  done
done

echo "All tasks completed. Full outputs are in: $FINAL_PARENT_DIR"

