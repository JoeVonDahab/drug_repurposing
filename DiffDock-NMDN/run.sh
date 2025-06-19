#!/usr/bin/env bash
python predict.py --prot 2GQG_one_chain_docking.pdb --ligs all_sdf/*.sdf --save_csv results_nmdn.csv
