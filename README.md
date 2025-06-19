# 🧪 Drug Repurposing Docking Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/JoeVonDahab/drug_repurposing/issues)

A fully reproducible pipeline for rapid *in silico* screening of FDA-approved drugs against novel protein targets, developed at the **Zhao Lab, UCSF**.

## 🎯 Table of Contents
- [🎯 Objective](#-objective)
- [📋 Overview](#-overview)
- [🏗️ Repository Layout](#️-repository-layout)
- [🔧 Installation & Setup](#-installation--setup)
- [🚀 Quick Start](#-quick-start)
- [📊 Sample Results](#-sample-results)


## 🎯 Objective
To provide a rapid, inexpensive, and reproducible first-pass screening pipeline to identify repositionable drugs for further medicinal-chemistry optimization or wet-lab validation. Our proof-of-concept targets **c-Abl tyrosine kinase (PDB: 2GQG)** for Parkinson's disease.

## 📋 Overview
This repository contains a complete pipeline for screening FDA-approved small-molecule drugs against understudied protein targets. The workflow is designed for speed and efficiency, leveraging GPU acceleration for molecular docking.

###  Workflow Steps
1.  **Data Curation**: Fetches and curates 2,579 FDA-approved drug records.
2.  **Ligand Preparation**: Converts drug structures to SMILES format and filters them by size, resulting in a final set of 2,480 ligands.
3.  **Protein Preparation**: Cleans the target protein crystal structure (`2GQG`), retaining a single chain and removing non-pocket artifacts.
4.  **Molecular Docking**: Runs `DiffDock` in batch mode to generate binding poses and affinity scores.
5.  **Pose Filtering**: Selects for poses where the ligand's center of mass is within the defined ATP-binding pocket.
6.  **Result Export**: Generates ranked CSV and SDF lists for visual inspection or downstream machine learning rescoring.

## 🏗️ Repository Layout

| Folder / File                 | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| `DiffDock/`                   | Docking engine and prepared `2GQG` receptor file            |
| `kaggle/`                     | some data from kaggle database                              |
| `results/`                    | Filtered docking outputs (poses, scores, summary CSV)       |
| `FDA_Approved_structures.csv` | Raw FDA drug records from the initial download              |
| `approved_drugs.smi`          | Final, dockable SMILES list (2,480 molecules)               |
| `convert_to_smiles.py`        | Helper script to generate `.smi` from CSV/SDF               |
| `README.md`                   | You are here                                                |

## 🔧 Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/JoeVonDahab/drug_repurposing.git](https://github.com/JoeVonDahab/drug_repurposing.git)
cd drug_repurposing

# Create and activate conda environment (recommended)
conda create -n diffdock python=3.9
conda activate diffdock

# Install key packages (install other dependencies as needed)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
conda install -c conda-forge rdkit
pip install biopython pandas tqdm scikit-learn
```
## Sample Results:

| Drug Name                 | Highest Confidence | Within Pocket |
| :------------------------ | :----------------- | :------------ |
| Propiolactone             | 0.8700             | False         |
| Thallous_Chloride_Tl_201  | 0.7600             | False         |
| Hydrogen_peroxide         | 0.7100             | False         |
| Fomepizole                | 0.6600             | False         |
| Glucarpidase              | 0.6400             | False         |
| Sulodexide                | 0.6200             | True          |
| Pyrithione_Zinc           | 0.6100             | False         |
| Olprinone                 | 0.5900             | True          |
| Naproxen                  | 0.5800             | True          |
| Sulfadiazine              | 0.5500             | True          |
| Allantoin                 | 0.5200             | False         |
| Zolmitriptan              | 0.4900             | True          |
| Ritlecitinib              | 0.4900             | True          |
| Abacavir                  | 0.4800             | True          |
| Nitric_Oxide              | 0.4800             | False         |
| Olanzapine                | 0.4500             | True          |
| Quercetin                 | 0.4300             | True          |
| Strontium_Chloride_Sr_89  | 0.4200             | False         |
| Temocillin_disodium       | 0.4000             | True          |
| Amlexanox                 | 0.4000             | True          |
| Allopurinol               | 0.3700             | True          |
| Mebendazole               | 0.3600             | True          |
| L_Proline                 | 0.3500             | True          |
| Isoniazid                 | 0.3500             | False         |
| Dalfampridine             | 0.3500             | False         |
| Phenazopyridine           | 0.3400             | True          |
| Nicotinamide              | 0.3400             | False         |

![image](https://github.com/user-attachments/assets/8d2bd380-4093-480b-8ce5-3a2ce0ee3d7d)

--------------------

# AutoDOCK Pipeline 

## 🧬 c-Abl Kinase ATP Pocket Residues

Below is a curated list of key residues forming the canonical ATP binding pocket of **human c-Abl kinase** (Abl1, UniProt P00519; typical PDB numbering ~2HYY / 2G2F).

| **Structural Element** | **Residues (Abl1 numbering)** | **Role** |
|------------------------|-------------------------------|----------|
| **P-loop / Gly-rich loop (β1–β2)** | Gly246, Gly247, Leu248, Gly250, Val256 | Cradles ATP phosphates; flexible loop shielding phosphates from solvent. |
| **Catalytic Lys salt bridge** | Lys271 (β3), Glu286 (αC-helix) | Lys271 contacts ATP phosphates; Glu286 stabilizes Lys via salt bridge. |
| **Gatekeeper residue** | Thr315 | Regulates access to back pocket; interacts with adenine edge. |
| **Hinge region** | Phe317, Met318, Gly321 | Main chain H-bonds anchor ATP adenine; Phe provides π-stacking. |
| **Catalytic HRD motif** | His361, Arg362, Asp363 | Aligns and activates γ-phosphate; Asp363 acts as base. |
| **DFG motif + Mg²⁺ site** | Asp381, Phe382, Gly383, Asn368 | Asp381 coordinates Mg²⁺; Phe toggles DFG-in/out; Asn368 orients Mg²⁺. |
| **Activation loop floor** | Leu370, Gly371, Ala372 | Shape pocket floor in active state. |
| **Hydrophobic back pocket (selectivity pocket)** | Leu248, Val299, Ile313, Leu370 | Lipophilic pocket used by type II inhibitors. |
| **Supporting residues** | Thr277 (β4), Ser345 (β6), Pro249 | Stabilize loop conformations; orient water/Mg²⁺ network. |

**Key direct ATP contacts:**  
- Lys271  
- Thr315  
- Met318 (backbone NH)  
- Asp381  
- Asn368  
- Gly-rich loop (Gly246–Gly250)

> ⚡ *Mutations in gatekeeper Thr315 (e.g., T315I) alter inhibitor binding but not ATP affinity dramatically.*

## ✍️ For Contact: 

-   **Youssef Abo-Dahab** — [@JoeVonDahab](https://github.com/JoeVonDahab)

