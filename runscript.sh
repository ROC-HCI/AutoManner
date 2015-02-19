#!/bin/bash
#SBATCH --array=0-11
#SBATCH -t 24:59:59 
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -J BActionP
#SBATCH -e Results/righthand_noninvariant/BActionP%A_%a.err
#SBATCH -o Results/righthand_noninvariant/BActionP%A_%a.out
#module load anaconda
#array=(3e-11 8e-11 3e-10 8e-10 3e-9 8e-9 7e-8 6e-8 1e-7 5e-7 1e-8 5e-8)
#echo ${array[${SLURM_ARRAY_TASK_ID}]}
python ./analyze.py -i Data/top5_skeletal_Data.mat -j ALL -o Results/righthand_noninvariant/result -Beta 1e-7 -D 8 -M 128 
