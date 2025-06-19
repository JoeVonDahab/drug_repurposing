"""
validate_smiles.py

Reads a .smi file and checks each SMILES string for validity using RDKit.
Usage: python validate_smiles.py input.smi [output_report.txt]
"""

import sys
from rdkit import Chem

def is_valid_smiles(smiles: str) -> bool:
    """Return True if RDKit can parse the SMILES into a molecule."""
    return Chem.MolFromSmiles(smiles) is not None

def main(input_path: str, report_path: str = None):
    out = open(report_path, 'w') if report_path else sys.stdout
    valid_count = 0
    invalid_count = 0

    with open(input_path, 'r') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            smiles = parts[0]
            name   = parts[1] if len(parts) > 1 else ''
            valid  = is_valid_smiles(smiles)
            status = "VALID" if valid else "INVALID"
            out.write(f"{lineno:4d}  {smiles:20s}  {status:7s}  {name}\n")
            
            if valid:
                valid_count += 1
            else:
                invalid_count += 1

    out.write(f"\nSummary:\n")
    out.write(f"Valid SMILES: {valid_count}\n")
    out.write(f"Invalid SMILES: {invalid_count}\n")
    out.write(f"Total SMILES: {valid_count + invalid_count}\n")

    if report_path:
        out.close()
        print(f"Validation report written to {report_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_smiles.py input.smi [output_report.txt]")
        sys.exit(1)
    inp = sys.argv[1]
    rpt = sys.argv[2] if len(sys.argv) > 2 else None
    main(inp, rpt)
