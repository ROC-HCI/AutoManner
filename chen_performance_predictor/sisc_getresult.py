import sisc_wrapper as ssw
import scipy.io
import numpy as np
import csv
import subprocess 
import copy
import sys


#argv[0] is video name #argv[1] is frame speed.

#print str(sys.argv[1]);
#print str(sys.argv[2])+'\n\n\n\n';

cmd = 'python sisc_wrapper.py -diff_thresh 1e-6 -Beta 0.2 -D 5 --pca -i '+str(sys.argv[1]);
subprocess.check_output(cmd,shell=True);
mat = scipy.io.loadmat('Results/result_M=64_D=5_beta=0.2_i='+str(sys.argv[1])[:-4]+'.mat');
alpha = mat['alpha_recon'];
psi = mat['psi_recon'];


#print('Start write');

timeline = [];
skeleton = [];
for i in range(5):
	tempa = alpha[:,i];
	templist = copy.copy(tempa.tolist());
	rangelist = len(templist);
	for j in range(5):
		writelist = [];
		writelist.append(str(i)+'.'+str(j));
		tempmaxval = max(templist);
		if tempmaxval > 0:
			maxindex = templist.index(tempmaxval);
			tempstart = maxindex;
			tempend = maxindex;
			templist[maxindex] = 0;
			for k in range(32):
				tempstart = tempstart-1;
				tempend = tempend+1;
				if tempstart>=0:
					templist[tempstart]=0;
				if tempend < rangelist:
					templist[tempend]=0;
			if tempstart<0:
				tempstart=0;
			if tempend >= rangelist:
				tempend = rangelist-1;
			speed = float(sys.argv[2]);
			writelist.append(int(tempstart/speed));
			writelist.append(int(tempend/speed));
			timeline.append(writelist);

			checkmax = max(templist);
			checkmaxindex = templist.index(checkmax);
			while checkmax !=0 and abs(checkmaxindex-maxindex)<64:
				templist[checkmaxindex]=0;
				checkmax = max(templist);
				checkmaxindex = templist.index(checkmax);
		else:
			break;

#skeletitle = [];
#for i in range(60):
#	sktname = 'skt'+str(i+1);
#	skeletitle.append(sktname);

for i in range(5):
	psilist = psi[:,:,i].tolist();
	skelelist = [];
	for row in psilist:
		skelelist.append([0,0]+row);

	writename = 'Results/skele_'+str(i)+'_'+str(sys.argv[1])[:-4]+'.csv';
	#skelelist = [skeletitle]+skelelist;
	with open(writename,'w') as writefile:
		writer = csv.writer(writefile);
		writer.writerows(skelelist);


timetitleline = ['vpname', 'starttime', 'endtime'];
timeline = [timetitleline]+timeline;
timewritename = 'Results/timeline_'+str(sys.argv[1])[:-4]+'.csv';
with open(timewritename,'w') as writefile:
	writer = csv.writer(writefile);
	writer.writerows(timeline);


#a = scipy.io.loadmat('Results/result_M=64_D=5_beta=0.2.mat')
#b = a['alpha_recon']
#c = groupdata(b)
#print c;
#a = [0,2,3,4,0,1,2,3,0,1,2];
#c = groupdata(a);
#print c;


