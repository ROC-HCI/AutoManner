array=(3e-6 8e-6 3e-5 8e-5 3e-4 8e-4 3e-3 8e-3 3e-2 8e-2 3e-1 8e-1 3 8)

printf "%f\n" "${array[@]}"

for i in "${array[@]}"
do
python ./analyze.py -i Data/toy_Data.mat -j NONE -Beta ${i} -D 2
done


