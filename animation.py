import csv
import numpy as np
import skelplot_mayavi as skm
import fileio as fio

file = open('Results/skele_0.csv');
read = csv.reader(file);
anilist = [];

for row in read:
	f = map(float,row)
	anilist.append(f);

aniarr = np.array(anilist);
#x_proj,eigvec,x_mean = fio.txfmdata(aniarr);
skm.unitTest1(aniarr);