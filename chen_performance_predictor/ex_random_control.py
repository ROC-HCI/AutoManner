import csv
import sys
import math
from random import randint
import os

#python ex_random_control.py 13.3.csv

directory = 'Results/'+str(sys.argv[1])[:-4]+'_random/';
speed = 30.2;
if not os.path.exists(directory):
	os.makedirs(directory);

skelefile = 'skeleton_test/'+str(sys.argv[1]);
file = open(skelefile,'r');
read = csv.reader(file);
rawtitle = [];
resultlist = [];

count = 0;
for row in read:
	if count == 0:
		rawtitle = row[2:102];
		count = count+1;
	else:
		tempraw = row[2:102];
		seclist = [];
		for i in range(len(tempraw)):
			if rawtitle[i] != 'ScreenX' and rawtitle[i] != 'ScreenY':
				seclist.append(float(tempraw[i]));
		resultlist.append(seclist);

totalframe = len(resultlist)-1;

timelinefile = 'Results/'+str(sys.argv[1])[:-4]+'/timeline_'+str(sys.argv[1]);
file2 = open(timelinefile,'r');
read2 = csv.reader(file2);
pattnum = [];
count2 = 0;
tempnum = 0;

for row in read2:
	if count2 == 0 :
		count2 = count2+1;
	else:	
		if row!='': 
			if int(math.trunc(float(row[0])))==len(pattnum):
				tempnum = tempnum+1;
			else:
				pattnum.append(tempnum);
				tempnum=1;
		else:
			break;

pattnum.append(tempnum);
tempnum=0;

faketimeline = [];
pattcount = 0;
for patt in pattnum:
#for patt in range(3,4):
	#print patt;
	tempskele = [];
	temptimeline = [];
	for i in range(patt):
		check = 0;
		rand1 = randint(70,totalframe-61);
		#print rand1;
		while check ==0:
			if len(temptimeline)==0:
				check=1;
			for ele in temptimeline:
				if abs(ele-rand1)<64:
					rand1 = randint(70,totalframe-61);
					check = 0;
					break;
				else:
					check = 1;
		
		temptimeline.append(rand1);
		timestr = str(pattcount)+'.'+str(i);
		temptimelist = [];
		temptimelist.append(float(timestr));
		temptimelist.append(int((rand1-64)/speed));
		temptimelist.append(int(rand1/speed));
		faketimeline.append(temptimelist);
		if i==0:
			for j in range(rand1+1-64,rand1+1):
				tempskele.append(resultlist[j]);
	print len(tempskele);
	skelewritename = directory+'skele_'+str(pattcount)+str(sys.argv[1])[:-4]+'.csv';
	with open(skelewritename,'w') as writefile:
		writer = csv.writer(writefile);
		writer.writerows(tempskele);
	pattcount = pattcount+1;
	

timewritename = directory+'timeline_'+str(sys.argv[1])[:-4]+'.csv';
timetitle = ['vpname','starttime','endtime'];
faketimeline = [timetitle]+faketimeline;
with open(timewritename,'w') as writefile:
	writer = csv.writer(writefile);
	writer.writerows(faketimeline);
