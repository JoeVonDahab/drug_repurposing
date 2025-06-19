# this goes results/docking_results_ranked_docked.csv and find which smiles are docked and separeate smiles that are not docked from smile file
import pandas as pd

csv_file_path = 'docking_results_ranked_docked.csv' # Path to the CSV file containing docking results
smiles_file_path = '1m.smi' # Path to the SMILES file containing all compounds
new_smiles_file_path = 'undocked_smiles.smi'    # Path to save the undocked SMILES
csv_data = pd.read_csv(csv_file_path)

def separate_undocked_smiles(csv_data, smiles_file_path):
    # Extract the docked SMILES from the CSV data
    docked_smiles = set(csv_data['SMILES'].dropna().unique())
    
    undocked_smiles = {}
    # Read the SMILES file
    with open(smiles_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            smile = parts[0]
            name = parts[1] 
            if smile not in docked_smiles:
                undocked_smiles[smile] = name
    
    # Write the undocked SMILES to the new SMILES file
    with open(new_smiles_file_path, 'w') as new_file:
        for smile, name in undocked_smiles.items():
            new_file.write(f"{smile}\t{name}\n")
    number_of_undocked_smiles = len(undocked_smiles)
    print(f"Number of undocked SMILES: {number_of_undocked_smiles}")
    print(f"Undocked SMILES have been written to {new_smiles_file_path}")
if __name__ == "__main__":
    separate_undocked_smiles(csv_data, smiles_file_path)
    print("Undocked SMILES separation completed.")
# This script separates undocked SMILES from a given SMILES file based on the docking results in a CSV file.
