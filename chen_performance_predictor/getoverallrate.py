import csv

part1file = open('MTurk_First_17_Participants.csv','r');
part2file = open('MTurk_2nd_half_participants.csv','r');
part1read = csv.reader(part1file);
part2read = csv.reader(part2file);

part1list = [];
for row in part1read:
	part1list.append(row);
part2list = [];
for row in part2read:
	part2list.append(row);

videos = ['"10.1"','"10.2"','"10.3"','"13.2"','"13.3"','"14.1"','"14.2"','"14.3"','"15.1"','"15.2"','"15.3"','"16.1"','"16.2"','"16.3"','"17.1"','"17.2"','"17.3"','"18.1"','"18.2"','"18.3"','"19.1"','"19.2"','"19.3"','"20.1"','"20.2"','"20.3"','"21.1"','"21.2"','"21.3"','"23.1"','"23.2"','"23.3"','"24.1"','"24.2"','"24.3"','"25.1"','"25.2"','"25.3"','"26.1"','"26.2"','"26.3"','"27.1"','"27.2"','"27.3"','"29.2"','"29.3"','"30.1"','"30.2"','"30.3"','"31.1"','"31.2"','"31.3"','"32.1"','"32.2"','"32.3"'];
result = [];

for v in videos:
	print v;
	tempsum = 0;
	count = 0;
	num = 0;

	for row in part1list:
		if num==0:
			num = num+1;
		else:
			#print v + row[28];
			if row[28]==v:
				tempsum = tempsum+int(row[45]);
				count = count+1;
			num = num+1;
	num = 0;
	for row in part2list:
		if num==0:
			num = num+1;
		else:
			if row[28]==v:
				tempsum = tempsum+int(row[45]);
				count = count+1;
			num = num+1;
	print tempsum;
	templist = [];
	templist.append(v);
	tempnum = float(tempsum)/count;
	templist.append(tempnum);
	result.append(templist);

with open('overallrate.csv','w') as writefile:
	writer = csv.writer(writefile);
	writer.writerows(result);