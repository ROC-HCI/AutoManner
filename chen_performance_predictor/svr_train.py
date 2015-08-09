import csv
import numpy
from sklearn import svm
from sklearn import cross_validation


def getgroundtruth(filename):
	file = open(filename,'r');
	read = csv.reader(file);
	truthtable = [];
	for row in read:
		truthtable.append(float(row[1]));
	return truthtable;

def getdata(filename):
	file = open(filename,'r');
	read = csv.reader(file);
	datatable = [];
	num = 0;
	for row in read:
		if num==0:
			num = num+1;
		else:
			row = [0 if x=='--undefined--' else x for x in row];
			row = map(float,row);
			datatable.append(row);
			num = num+1;
	return datatable;


truth = getgroundtruth('cleanrating.csv');
data = getdata('face_prosody.csv');

corsum=0;
corlist=[];


for i in range(5000):
	a_train, a_test, b_train, b_test = cross_validation.train_test_split(data, truth, test_size=0.33);
	clf = svm.LinearSVR();
	clf.fit(a_train,b_train);
	predictmex = clf.predict(a_test);
	temp = numpy.corrcoef(predictmex,b_test);
	corlist.append(temp);
	corsum = corsum+temp[0][1];
averacc = corsum/5000;
print 'The SVR accuracy is',averacc;
