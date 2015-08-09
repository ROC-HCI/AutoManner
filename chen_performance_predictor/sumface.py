import csv
import os

def generatefacelist(filename,csvwritefile):
	file = open(filename,'r');
	read = csv.reader(file);
	oldtitleline = [];
	newtitleline = [];
	oldvaluelist = [];
	resultlist = [];
	count = 0;
	for row in read:
		if count==0:
			count = count+1;
			oldtitleline = row[2:14];
		else:
			row = row[2:14];
			print row;
			row = [0 if x=='' else x for x in row];
			tempresult = map(float,row);
			oldvaluelist.append(tempresult);
			count = count+1;
	for i in range(len(oldtitleline)):
		tempmin = 'min'+oldtitleline[i];
		tempmax = 'max'+oldtitleline[i];
		tempsd = 'sd'+oldtitleline[i];
		newtitleline.append(tempmin);
		newtitleline.append(tempmax);
		newtitleline.append(tempsd);
	checkmin = 0;
	checkmax = 0;
	checksum = 0;
	framesize = len(oldvaluelist);

	for j in range(len(oldvaluelist[0])):
		for i in range(framesize):
			if i > 0:
				if oldvaluelist[i][j]<checkmin:
					checkmin = oldvaluelist[i][j];
				if oldvaluelist[i][j]>checkmax:
					checkmax = oldvaluelist[i][j];
				checksum = checksum+oldvaluelist[i][j];
			else:
				checkmin = oldvaluelist[i][j];
				checkmax = oldvaluelist[i][j];
				checksum = checksum+oldvaluelist[i][j];
		resultlist.append(checkmin);
		resultlist.append(checkmax);
		tempsd = checksum/framesize;
		resultlist.append(tempsd);
	resultlist = [newtitleline]+[resultlist];
	with open(csvwritefile,'w') as writefile:
		writer = csv.writer(writefile);
		writer.writerows(resultlist);
	return resultlist;

########################################################################################
#for fn in os.listdir('/Users/kezhenchen/Documents/research/summer/FacialExpression/'):
#	print fn;
#	filename = '/Users/kezhenchen/Documents/research/summer/FacialExpression/'+fn;
#	writename = 'sum'+fn;
#	a = generatefacelist(filename,writename);
#########################################################################################

###########################################################################################################
#finalwritefile = [];
#titleline = [];
#for fn in os.listdir('/Users/kezhenchen/Documents/research/summer/faceexpression/labeled_face_file/'):
#	filename = '/Users/kezhenchen/Documents/research/summer/faceexpression/labeled_face_file/'+fn;
#	framenum = fn[3:7];

#	print filename;
#	file = open(filename,'r');
#	read = csv.reader(file);
#	num = 0;

#	for row in read:
#		if num==0:
#			num = num+1;
#			titleline = row;
#		else:
#			row = [framenum]+row;
#			finalwritefile.append(row);
#			num = num+1;
#titleline = ['framenum']+titleline;
#finalwritefile = [titleline]+ finalwritefile;

#with open('Facialexpression_finaldata.csv','w') as writefile:
#		writer = csv.writer(writefile);
#		writer.writerows(finalwritefile);
########################################################################################################

facefile = open('Facialexpression_finaldata.csv','r');
prosodyfile = open('Prosodydata.csv','r');
faceread = csv.reader(facefile);
proread = csv.reader(prosodyfile);

titleline = [];
sumlist = [];
num = 0;
for row in faceread:
	if num==0:
		num = num+1;
		titleline = row[1:];
	else:
		temp = row[1:];
		sumlist.append(temp);
		num = num+1;

num = 0;
for row in proread:
	if num==0:
		num = num+1;
		titleline = titleline+row[1:];
	else:
		temp = row[1:];
		sumlist[num-1] = sumlist[num-1]+temp;
		num = num+1;

sumlist = [titleline]+sumlist;

with open('face_prosody.csv','w') as writefile:
	writer = csv.writer(writefile);
	writer.writerows(sumlist);







