#!/usr/bin/env python3
# this script maps each unique atom in a SMILES file to the first compound ID it appears in.
import re

# Regex to grab:
#  - bracketed atoms:  [Fe], [NH+], etc.
#  - two-letter elements: Br, Cl, Si, etc.
#  - single-letter elements: C, N, O, S, P, F, I, B, etc.
ATOM_REGEX = re.compile(r'\[.*?\]|Br|Cl|[A-Z][a-z]?')

def extract_atoms(smiles):
    """
    Given a SMILES string, return a list of element symbols.
    - For bracketed tokens ([NH+]), we strip brackets and extract the leading element.
    - Otherwise we take the token as the element.
    """
    atoms = []
    for token in ATOM_REGEX.findall(smiles):
        if token.startswith('['):
            inner = token[1:-1]               # e.g. "NH+"
            m = re.match(r'^([A-Z][a-z]?)', inner)
            if m:
                atoms.append(m.group(1))
        else:
            atoms.append(token)
    return atoms

def build_atom_dict(smi_path):
    """
    Reads a SMILES file and returns a dict mapping each atom
    symbol → first compound ID in which it appears.
    """
    atom_dict = {}
    with open(smi_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            smiles, cid = parts
            for atom in extract_atoms(smiles):
                if atom not in atom_dict:
                    atom_dict[atom] = cid
    return atom_dict

if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
        description="Map each unique atom in a SMILES file to the first compound ID it appears in."
    )
    p.add_argument("smi", help="Input SMILES file (tab‐ or space‐delimited: SMILES ID)")
    args = p.parse_args()

    mapping = build_atom_dict(args.smi)
    print("Atom → First-Seen Compound ID")
    for atom, cid in sorted(mapping.items()):
        print(f"{atom}: {cid}")
