#!/bin/bash
#SBATCH --array=0-17
#SBATCH -t 10:59:59
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -J BActionP
#SBATCH -e Results/top5_allJoints/BActionP%A_%a.err
#SBATCH -o Results/top5_allJoints/BActionP%A_%a.out
module load anaconda
array=(3e-11 8e-11 3e-10 8e-10 3e-9 8e-9 1e-8 5e-8 6e-8 8e-8 1e-7 5e-7 6e-7 8e-7 3e-6 8e-6)
echo ${array[${SLURM_ARRAY_TASK_ID}]}
python ./analyze.py -i Data/top5_skeletal_Data.mat -j ALL -o Results/top5_allJoints/result -Beta ${array[${SLURM_ARRAY_TASK_ID}]} -D 8 -M 128 -iter_thresh 500
