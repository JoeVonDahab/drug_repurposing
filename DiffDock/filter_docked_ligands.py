# this script filters docked ligands based on their geometric center coordinates
import numpy as np
import os
import shutil

def get_geometric_center_from_pdbqt_lines(pdbqt_lines):
    """Calculates the geometric center from ATOM/HETATM lines in a PDBQT."""
    coords = []
    for line in pdbqt_lines:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            try:
                # PDB format: X (30-38), Y (38-46), Z (46-54)
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                coords.append([x, y, z])
            except ValueError:
                print(f"Warning: Could not parse coordinates from line: {line.strip()}")
                return None # Or handle more gracefully
            except IndexError:
                print(f"Warning: Line too short to parse coordinates: {line.strip()}")
                return None
    if not coords:
        return None
    return np.mean(np.array(coords), axis=0)

def is_center_in_box(center_coords, box_min, box_max):
    """Checks if the geometric center is within the defined box."""
    if center_coords is None:
        return False
    return (box_min[0] <= center_coords[0] <= box_max[0] and
            box_min[1] <= center_coords[1] <= box_max[1] and
            box_min[2] <= center_coords[2] <= box_max[2])

# --- Define your box boundaries (calculated previously) ---
box_min_coords = np.array([36.8440, 71.9041,  33.2743])
box_max_coords = np.array([52.2194, 87.1073, 47.0206])

# --- Customize these paths ---
input_pdbqt_directory = "docked_converted"
output_filtered_directory = "docking_converted_filtered" 

# --- Create output directory if it doesn't exist ---
if not os.path.exists(output_filtered_directory):
    os.makedirs(output_filtered_directory)
    print(f"Created output directory: {output_filtered_directory}")

# --- Process each PDBQT file ---
files_in_box = 0
total_files = 0
files_processed_successfully = 0

print(f"Reading PDBQT files from: {os.path.abspath(input_pdbqt_directory)}")
print(f"Saving filtered files to: {os.path.abspath(output_filtered_directory)}")
print(f"Box Min Coords: {box_min_coords}")
print(f"Box Max Coords: {box_max_coords}\n")

for filename in os.listdir(input_pdbqt_directory):
    if filename.endswith(".pdbqt"):
        total_files += 1
        filepath = os.path.join(input_pdbqt_directory, filename)
        
        pdbqt_atom_lines = []
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.startswith("ATOM") or line.startswith("HETATM"):
                        pdbqt_atom_lines.append(line)
            
            if not pdbqt_atom_lines:
                print(f"Warning: No ATOM/HETATM records found in {filename}. Skipping.")
                continue
                
            ligand_center = get_geometric_center_from_pdbqt_lines(pdbqt_atom_lines)

            if ligand_center is None:
                print(f"Warning: Could not calculate geometric center for {filename}. Skipping.")
                continue
            
            files_processed_successfully +=1

            if is_center_in_box(ligand_center, box_min_coords, box_max_coords):
                files_in_box += 1
                destination_path = os.path.join(output_filtered_directory, filename)
                shutil.copy2(filepath, destination_path)
            else:
                pass 
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print(f"\n--- Processing Summary ---")
print(f"Total PDBQT files found: {total_files}")
print(f"Files processed for coordinates: {files_processed_successfully}")
print(f"Files copied (ligand center in box): {files_in_box}")
print(f"Filtered files are in: {output_filtered_directory}")