import csvread
import sumface
import turkers_EM as te

#csvread.py. 
#Basically, the functions in this file are used to resample prosody
#files and combine skeleton, prosody and facialexpression data together.

#convert skeleton csv file to list
a = csvread.csvtolist('10.1.csv');

#We can get b by import the start/end labeled data. Then 'b' is one labeled data. In the sample, we use 10.1
#videoname, normal_video_start_frame,kinect_video_start_frame, normal_video_end_frame,kinect_video_end_frame, raw_normal_video_total_frame
b = [10.1,371,315,4943,5803,4967];

nvN = int(labeldata[5]);
kvN = int(labeldata[4])-int(labeldata[2]);
nvStart = int(labeldata[1]);
nvEnd = int(labeldata[3]);

#resample sound samples.
a = csvread.resample_sound('10.1.loud',nvN,kvN,nvStart,nvEnd);
#convert 24 frames/sec to 30 frames/sec
a = csvread.convert_24_30(b);
#read MTS facial experssion files
a = csvread.readMTS('10.1.MTS.csv',b);
#combine all files and generate a combined csv file with skeleton, prosody and facial experssion features.
a = csvread.generateCSV('10.1.csv','10.1.loud','10.1.pitch','10.1.MTS.csv',b,'10.1.final.csv');




#sumface.py
#compute the average, max, min for facial data
#combine the facial data and prosody data in order to put in the svr and lasso.
a = sumface.generatefacelist('10.1.MTS.csv','sum10.1.MTS.csv');


#turkers_EM.py
#clean the turkers rating data
videos = ['"10.1"','"10.2"','"10.3"','"13.2"','"13.3"','"14.1"','"14.2"','"14.3"','"15.1"','"15.2"','"15.3"','"16.1"','"16.2"','"16.3"','"17.1"','"17.2"','"17.3"','"18.1"','"18.2"','"18.3"','"19.1"','"19.2"','"19.3"','"20.1"','"20.2"','"20.3"','"21.1"','"21.2"','"21.3"','"23.1"','"23.2"','"23.3"','"24.1"','"24.2"','"24.3"','"25.1"','"25.2"','"25.3"','"26.1"','"26.2"','"26.3"','"27.1"','"27.2"','"27.3"','"29.2"','"29.3"','"30.1"','"30.2"','"30.3"','"31.1"','"31.2"','"31.3"','"32.1"','"32.2"','"32.3"'];
a = te.generate_csv('turker_rating.csv');


