import csv

# --- User Configuration ---
# 1. Replace 'your_input_file.csv' with the actual name of your data file.
input_filename = 'FDA_Approved_structures.csv'

# 2. Replace 'output.smi' with the desired name for your new SMILES file.
output_filename = 'output.smi'
# --- End of Configuration ---

print(f"Starting conversion of '{input_filename}'...")

try:
    # Open the input file for reading and the output file for writing
    with open(input_filename, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:

        # The csv.reader correctly handles fields that are enclosed in quotes,
        # which is important for chemical names containing commas.
        reader = csv.reader(infile)

        # Process each row in the input file
        for row in reader:
            # Ensure the row is not empty and contains exactly two columns
            if row and len(row) == 2:
                # The first column is the name, the second is the SMILES string
                name = row[0]
                smiles = row[1]

                # Write the SMILES string, a space, and then the name to the output file
                # followed by a new line.
                outfile.write(f"{smiles} {name}\n")
            else:
                # Notify about any malformed lines
                print(f"Skipping malformed or empty line: {row}")

    print(f"Conversion complete! Check for your new file: '{output_filename}'")

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
    print("Please make sure your input file is in the same folder as this script,")
    print("or provide the full path to the file.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

