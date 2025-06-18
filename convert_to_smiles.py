# Python script to parse a plain-text drug list and generate a .smi file

# === File settings ===
input_file = "P3-07-Approved_smi_inchi.txt"    
output_file = "approved_drugs.smi"   # Output SMILES file

# === Read and validate input file ===
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    raise FileNotFoundError(
        f"File '{input_file}' not found. Please save your drug entries in a file named '{input_file}' in this directory."
    )

# === Split entries by blank lines ===
entries = [entry for entry in content.strip().split('\n\n') if entry.strip()]

# === Extract SMILES and DrugName, write to .smi file ===
with open(output_file, 'w', encoding='utf-8') as out:
    for entry in entries:
        smiles = None
        name = None
        for line in entry.splitlines():
            if line.startswith("DRUGSMIL"):
                _, val = line.split(None, 1)
                smiles = val.strip()
            elif line.startswith("DRUGNAME"):
                _, val = line.split(None, 1)
                name = val.strip().replace(" ", "_")
        if smiles and name:
            out.write(f"{smiles} {name}\n")

print(f"Done! SMILES file saved to '{output_file}'")
