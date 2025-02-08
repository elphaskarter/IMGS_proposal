import sys

def createTape5(atmospheric_model, water, albedo, scat):
    # Validate scat value
    if scat not in [-1, 1, 0]:
        raise ValueError("scat must be either -1 or 1")

    atm_model = int(atmospheric_model)
    
    # Ensure strict decimal places
    water_vapor = f"{water:.3f}"  # Always 3 decimal places
    albedo_str = f"{albedo:.2f}"  # Always 2 decimal places
    scat_val = f"{scat:>5}" # Right-align scat in a 5 charater field

    with open('tape5', 'w') as the_file:
        the_file.write(f'TS  {atm_model}    2    2{scat_val}    0    0    0    0    0    0    1    0    0 283.150   {albedo_str}\n')
        the_file.write(f'T   8T   0 360.00000     {water_vapor}         0 T F F         0.000\n')
        the_file.write('\n')
        the_file.write('    1    1    0    0    0    0     0.000     0.000     0.000     0.000     1.000\n')
        the_file.write(' 705.00000     1.000   180.000     0.000     0.000     0.000    0          0.000\n')
        the_file.write('   1     2  241    0\n')
        the_file.write('    43.680    77.490     0.000     0.000    16.000     0.000     0.000     0.000\n')
        the_file.write('     0.350     2.600     0.001     0.001RM        MR A\n')
        the_file.write('    0\n')

if __name__ == "__main__":
    if len(sys.argv) != 5:  # Updated to accept 4 arguments
        print("Usage: python modify_tape5.py <atmospheric_model> <water> <albedo> <scat>")
        sys.exit(1)

    atm = int(sys.argv[1])
    water = float(sys.argv[2])
    albedo = float(sys.argv[3])
    scatter = int(sys.argv[4])  
    try:
        createTape5(atm, water, albedo, scatter)
        print("✅ Modified `tape5` file successfully created!")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)