import argparse
import os

def extract_n_compounds(input_filename, n, parts=1, output_prefix="output"):
    """
    Reads the first n lines from an input file and saves them to one or more .smi files.
    If parts > 1, splits the n lines into 'parts' files.
    """
    with open(input_filename, 'r') as infile:
        lines = [next(infile) for _ in range(n) if not infile.closed]

    if parts < 1:
        parts = 1

    part_size = n // parts
    remainder = n % parts

    start = 0
    for i in range(parts):
        end = start + part_size + (1 if i < remainder else 0)
        out_filename = f"{output_prefix}_part{i+1}.smi" if parts > 1 else f"{output_prefix}.smi"
        with open(out_filename, 'w') as outfile:
            outfile.writelines(lines[start:end])
        start = end

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract the first N compounds from a SMILES file, optionally splitting into parts.")
    parser.add_argument("input_file", help="Path to the input file (e.g., compounds.txt)")
    parser.add_argument("n_compounds", type=int, help="Number of compounds to extract")
    parser.add_argument("--parts", type=int, default=1, help="Number of parts to split the output into")
    parser.add_argument("--output_prefix", default="output", help="Prefix for output files (default: output)")

    args = parser.parse_args()

    extract_n_compounds(args.input_file, args.n_compounds, args.parts, args.output_prefix)
    print(f"Extracted {args.n_compounds} compounds from {args.input_file} into {args.parts} parts with prefix '{args.output_prefix}'.")