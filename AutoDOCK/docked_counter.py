# this script processes docking results to extract SMILES strings and their corresponding compound names
import os

def get_docked_compounds(directory):
    """
    This function scans the specified directory for files containing docking results,
    extracts the SMILES strings and their corresponding names, and returns a dictionary
    mapping names to SMILES.
    :param directory: Directory containing docking result files.
    :return: Dictionary with compound names as keys and SMILES strings as values.
    """
    compound_names = {}
    number_of_compounds = 0
    for filename in os.listdir(directory):
        if filename.endswith('_docked.dlg'):
            compound_name = filename.split('_docked.dlg')[0]
            compound_names[compound_name] = ''
            number_of_compounds += 1
    print(f"Number of compounds docked: {number_of_compounds}")
    return compound_names

def get_smiles_from_file(file_path, compound_names):
    smiles = {}
    docked_ones = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split(None, 1)
            if len(parts) != 2:
                print(f"Skipping line: {line} cause it does not contain exactly two parts.")
                continue
            smi = parts[0]
            name = parts[1]
            smiles[name] = smi
    for name in compound_names:
        if name in smiles:
            docked_ones[name] = smiles[name]
        else:
            print(f"Compound {name} not found in SMILES file.")
    return docked_ones

def create_smiles_file(input_directory, smiles_file, output_filename='docked_compounds.smi'):
    """
    This function creates a file containing the names and SMILES strings of docked compounds.
    :param input_directory: Directory containing docking result files.
    :param smiles_file: Path to the file with names and SMILES.
    :param output_filename: Path to the output file where names and SMILES will be saved.
    """
    compound_names = get_docked_compounds(input_directory)
    docked_smiles = get_smiles_from_file(smiles_file, compound_names)

    with open(output_filename, 'w') as output_file:
        for name, smi in docked_smiles.items():
            output_file.write(f"{smi}\t{name}\n")
    print(f"Docked compounds saved to '{output_filename}'.")

if __name__ == "__main__":
    input_directory = 'docking_results_compiled'
    smiles_file = '50k.smi'
    create_smiles_file(input_directory, smiles_file)
    print("Docked compounds processing completed.")
