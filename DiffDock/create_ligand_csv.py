# create_ligand_csv.py
import os

protein_path = "2GQG_one_chain_docking.pdb"
ligand_dir = "ligand_sdf_files"
output_csv = "all_ligands.csv"

def create_master_list():
    print(f"Scanning '{ligand_dir}' for SDF files...")
    ligand_files = [os.path.join(ligand_dir, f) for f in os.listdir(ligand_dir) if f.endswith('.sdf')]
    if not ligand_files:
        print(f"Error: No SDF files found in '{ligand_dir}'.")
        return

    print(f"Found {len(ligand_files)} SDF files. Creating '{output_csv}'...")
    with open(output_csv, 'w') as f:
        f.write("complex_name,protein_path,ligand_description,protein_sequence\n")
        for ligand_file in ligand_files:
            complex_name = os.path.splitext(os.path.basename(ligand_file))[0]
            f.write(f"{complex_name},{protein_path},{ligand_file},\n")
    print(f"✅ Successfully created {output_csv} with all required columns.")

if __name__ == "__main__":
    create_master_list()