#!/usr/bin/env python3
import glob
import pandas as pd
from rdkit import Chem

rows = []
for fn in glob.glob("scored/*_scored.sdf"):
    base = fn.split("/")[-1].replace("_scored.sdf","")
    suppl = Chem.SDMolSupplier(fn, removeHs=False)
    for mol in suppl:
        if mol is None: continue
        data = {"ligand": base}
        for tag in ("CNNscore","CNNaffinity","Affinity"):
            data[tag] = float(mol.GetProp(tag)) if mol.HasProp(tag) else None
        rows.append(data)

df = pd.DataFrame(rows)
df = df.sort_values("CNNaffinity", ascending=False).reset_index(drop=True)
df.to_csv("gnina_scores.csv", index=False)
print(f"Wrote {len(df)} rows to gnina_scores.csv")
