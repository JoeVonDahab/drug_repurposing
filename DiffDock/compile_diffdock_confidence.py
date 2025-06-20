#!/usr/bin/env python3
"""
Collect best confidence per drug, check if its best pose lies inside the
docking box, produce a CSV, and copy all in-pocket SDFs.

Outputs
-------
best_confidence_per_drug.csv      (drug,confidence,within_pocket)
in_pocket_sdfs/                   (all compounds whose pose is in the pocket)
"""
from pathlib import Path
import csv, re, shutil

# ----------------------------------------------------------------------
RESULT_DIRS = ["results_gpu0", "results_gpu1"]
OUTPUT_CSV  = "best_confidence_per_drug.csv"
OUTPUT_SDF_DIR = Path("in_pocket_sdfs")
# pocket boundaries (min, max) — edit if you change the box
BOX_MIN = (15.4116, -4.725237, -16.6718)
BOX_MAX = (30.8764, 6.455263, -4.6052)
# ----------------------------------------------------------------------

CONF_RE = re.compile(r"_confidence(-?\d+\.\d+)\.sdf$", re.I)

def sdf_centroid(path: Path):
    """
    Return (x,y,z) centre of all atoms in an SDF without RDKit.
    """
    with path.open() as fh:
        lines = fh.readlines()
    if len(lines) < 4:
        return None
    try:
        natoms = int(lines[3][:3])
    except ValueError:
        return None
    xyz = []
    for line in lines[4:4+natoms]:
        try:
            x, y, z = float(line[0:10]), float(line[10:20]), float(line[20:30])
            xyz.append((x, y, z))
        except ValueError:
            return None
    if not xyz:
        return None
    xs, ys, zs = zip(*xyz)
    return (sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs))

def in_box(coord, vmin=BOX_MIN, vmax=BOX_MAX):
    if coord is None:
        return False
    return all(a >= b and a <= c for a, b, c in zip(coord, vmin, vmax))

def scan_confidence_files():
    """Yield (drug, confidence, path) across all result folders."""
    for rdir in RESULT_DIRS:
        root = Path(rdir)
        if not root.is_dir():
            continue
        for drug_dir in root.iterdir():
            if not drug_dir.is_dir():
                continue
            drug_name = drug_dir.name
            for sdf in drug_dir.glob("*_confidence*.sdf"):
                m = CONF_RE.search(sdf.name)
                if m:
                    yield drug_name, float(m.group(1)), sdf

def main():
    # keep best confidence & path for each drug
    best = {}
    for drug, conf, path in scan_confidence_files():
        if drug not in best or conf > best[drug][0]:
            best[drug] = (conf, path)

    rows = []
    for drug, (conf, path) in best.items():
        centre = sdf_centroid(path)
        inside = in_box(centre)
        rows.append((drug, conf, inside, path))

    # sort by confidence high→low
    rows.sort(key=lambda x: x[1], reverse=True)

    # write CSV
    with open(OUTPUT_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["drug", "highest_confidence", "within_pocket"])
        for drug, conf, inside, _ in rows:
            w.writerow([drug, f"{conf:.4f}", inside])

    print(f"✅  CSV written: {OUTPUT_CSV}")

    # --- MODIFIED SECTION ---
    # Prepare directory for all in-pocket SDFs
    OUTPUT_SDF_DIR.mkdir(exist_ok=True)
    # clear old content
    for f in OUTPUT_SDF_DIR.glob("*"):
        f.unlink()
    
    # Filter for only the rows where the molecule is inside the pocket
    in_pocket_rows = [r for r in rows if r[2]]
    
    # Iterate through all in-pocket molecules and copy their SDFs
    for rank, (drug, conf, _, path) in enumerate(in_pocket_rows, 1):
        # The filename includes its rank by confidence score
        dst = OUTPUT_SDF_DIR / f"{rank:04d}_{drug}.sdf"
        shutil.copy2(path, dst)
        
    print(f"✅  Copied {len(in_pocket_rows)} in-pocket SDFs → {OUTPUT_SDF_DIR}/")

if __name__ == "__main__":
    main()