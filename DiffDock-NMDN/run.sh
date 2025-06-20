#!/usr/bin/env bash

python predict.py --prot receptor_ready_5tbm.pdb --ligs $(find all_sdf -name "*.sdf") --save_csv results_nmdn.csv

echo "Done!"
