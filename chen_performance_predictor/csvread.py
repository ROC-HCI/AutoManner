import csv
import numpy as np
import scipy.signal as ss

#resample scipy numpy
#q = cr.generateCSV('Skeleton-Data/10.1.csv','Prosody/10.1.loud','Prosody/10.1.pitch','FacialExpression/10.1.MTS.csv',b,'finaldata/10.1.final.csv');
#Convert a csv form into a dic. dic form : {framenum {variables} }. filename is csv name



def csvtolist(filename):
	file = open(filename,'r');
	read = csv.reader(file);
	resultlist = [];

	for row in read:
		resultlist.append(row[0:len(row)-1]);

	return resultlist;

#soundfile is the loud or pitch file. 
#nvN is the number of frames of the raw normal video.
#kvN is the number of frmaes of the labeld kinect video with start and end
#nvstart is the labeled start of normal video
#nvEnd is the labeled end of normal video
def resample_sound(soundfile, nvN, kvN, nvStart, nvEnd):
	file = open(soundfile,'r');
	rawsamples = file.readline()[:-2].split('	');
	rawnvsamples = ss.resample(rawsamples,nvN);
	cutsamples = rawnvsamples[nvStart:nvEnd+1];
	resultarr = ss.resample(cutsamples,kvN);
	return resultarr;

#csvfile is the CSV file with many data.
#loudfile is loud file
#pitch file is pitch file
#mts file is the face expression file
# labeldata is one list that contains filename, startNV, startKV, endNV, endKV, NVframes
#csvwrite is the csv file that we will write
def generateCSV(csvfile, loudfile, pitchfile,mtsfile, labeldata, csvwrite):

	titleline = [];
	nvN = int(labeldata[5]);
	kvN = int(labeldata[4])-int(labeldata[2]);
	nvStart = int(labeldata[1]);
	nvEnd = int(labeldata[3]);
	kvStart = int(labeldata[2]);
	kvEnd = int(labeldata[4]);
	csvlist = csvtolist(csvfile);
	titleline = titleline+csvlist[0];
	csvlist = csvlist[1:len(csvlist)-1];

	mtsarr = readMTS(mtsfile,labeldata);
	loudarr = resample_sound(loudfile, nvN, kvN, nvStart, nvEnd);
	pitcharr = resample_sound(pitchfile, nvN, kvN, nvStart, nvEnd);
	titleline.append('Loud');
	titleline.append('Pitch');
	titleline = titleline + mtsarr[0];
	mtsarr = mtsarr[1:len(mtsarr)-1];

	for k in csvlist:
		tempframe = int(k[0]);
		#print tempframe;
		if (tempframe > kvStart) and (tempframe < kvEnd):
			#print tempframe;
			soundin = tempframe-kvStart;
			k.append(loudarr[soundin]);
			k.append(pitcharr[soundin]);
		else:
			k.append('');
			k.append('');
			#print tempframe;
			#csvlist.remove(k);
	count = 0;
	for k in csvlist:
		temp = k[len(k)-1];
		if temp!='':
			break;
		count = count+1;

	csvlist = csvlist[count:len(csvlist)-1];
	count =0;
	for k in csvlist:
		temp = k[len(k)-1];
		if temp=='':
			break;
		count = count+1;
	csvlist = csvlist[0: count];
	#print len(mtsarr);
	index=0;
	for k in range(len(csvlist)):
		framenum = int(csvlist[k][0])-kvStart;
		csvlist[k]=csvlist[k]+mtsarr[framenum];
		#print framenum;

	csvlist = [titleline]+csvlist;
	with open(csvwrite,'w') as writefile:
		writer = csv.writer(writefile);
		writer.writerows(csvlist);
	return csvlist;

def convert_24_30(labeldata):
	labeldata[1] = int((labeldata[1]/24)*29.92);
	labeldata[3] = int((labeldata[3]/24)*29.92);
	labeldata[5] = int((labeldata[3]/24)*29.92);
	return labeldata;

def readMTS(mtsfile, labeldata):
	file = open(mtsfile,'r');
	read = csv.reader(file);
	resultlist = [];
	titleline = [];
	count=0;
	for row in read:
		if count == 0:
			titleline = row[1:len(row)-1];
		else:
			resultlist.append(row[1:len(row)-1]);
		count = count + 1;
	labeldata_30 = convert_24_30(labeldata);
	nvStart = int(labeldata_30[1]);
	kvN = int(labeldata_30[4])-int(labeldata_30[2]);
	mtsarr = resultlist[nvStart:nvStart+kvN+1];
	titleline = [titleline];
	mtsarr = titleline + mtsarr;
	return mtsarr;



