"""An implementation of the EM-based approach to estimate the precision (i.e., accuracy)
   of individual workers, given the turkers' input.
   
   To execute the code, Run the following command:
     python turkers_EM.py
"""

import csv
import sys
import numpy as np
import math
# My local classes



# The number of questions included in the estimation.
nQuestions = 1;

videos = ['"10.1"','"10.2"','"10.3"','"13.2"','"13.3"','"14.1"','"14.2"','"14.3"','"15.1"','"15.2"','"15.3"','"16.1"','"16.2"','"16.3"','"17.1"','"17.2"','"17.3"','"18.1"','"18.2"','"18.3"','"19.1"','"19.2"','"19.3"','"20.1"','"20.2"','"20.3"','"21.1"','"21.2"','"21.3"','"23.1"','"23.2"','"23.3"','"24.1"','"24.2"','"24.3"','"25.1"','"25.2"','"25.3"','"26.1"','"26.2"','"26.3"','"27.1"','"27.2"','"27.3"','"29.2"','"29.3"','"30.1"','"30.2"','"30.3"','"31.1"','"31.2"','"31.3"','"32.1"','"32.2"','"32.3"'];

def generate_csv(outputfile):
  result = [];
  a1,b1 = EM('MTurk_First_17_Participants.csv',6);
  a2,b2 = EM('MTurk_2nd_half_participants.csv',4);
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

  for v in videos:
    tempresult = [];
    count = 0;
    vid = '';
    for row in part1list:
      if count==0:
        count = count+1;
      else:
        if row[28]==v:
          vid = row[27];
    count=0;
    for row in part2list:
      if count==0:
        count = count+1;
      else:
        if row[28]==v:
          vid = row[27];
    tempresult.append(v);
    if vid in a1:
      tempresult.append(a1[vid]);
    if vid in a2:
      tempresult.append(a2[vid]);
    result.append(tempresult);
  with open(outputfile,'w') as writefile:
    writer = csv.writer(writefile);
    writer.writerows(result);

  return result;





def readGT(turkscoreMap):
  file = open(turkscoreMap,'r');
  read = csv.reader(file);
  turkmap = {};
  count =0;
  title = [];
  for row in read:
    if count==0:
      title = row;
    else:
      vid = row[27];
      if vid in turkmap:
        print 'have vid';
        wid = row[15];
        rate = float(row[45]);
        turkmap[vid][wid] = rate;
      else:
        print 'no vid';
        turkmap[vid] = {};
        wid = row[15];
        rate = float(row[45]);
        turkmap[vid][wid] = rate;
    count = count+1;
  return turkmap;



##############################################################
def EM(filename, nIters):
  """The iterative EM algorithm implementation."""
  turkscoreMap = readGT(filename);
  # the true label indexed by video id
  y_i = {}
  # the quality of workers
  lambda_j = {}

  for iter in range(nIters):
    y_i = EStep(turkscoreMap, lambda_j)
    lambda_j = MStep(turkscoreMap, y_i)
    ll = LogLikelihood(turkscoreMap, y_i, lambda_j)
    print("Log likelihood" + str(ll))
  for wid in sorted(lambda_j):
    print(wid, lambda_j[wid])
  return y_i,lambda_j
##############################################################
def EStep(turkscoreMap, lambda_j):
  """Reestimate the true labels (y_i)."""
  y_i = {}

  for vid in sorted(turkscoreMap):
    if vid not in y_i:
      y_i[vid] = 0.0

    yval = 0.0
    weight = 0.0
    for wid in turkscoreMap[vid]:
      if wid == "AGGR":
        continue
      if wid not in lambda_j:
        lambda_j[wid] = 1.0

      try:
        val = float(turkscoreMap[vid][wid])
      except (ValueError, KeyError):
        continue
      yval = yval + val * lambda_j[wid]
      weight = weight + lambda_j[wid]
    y_i[vid] = yval / weight
  return y_i

##############################################################
def MStep(turkscoreMap, y_i):
  """Reestimate the precision parameters (lambda_j)."""
  # the quality of workers
  lambda_j = {}
  count_j = {}
  for vid in sorted(turkscoreMap):
    for wid in turkscoreMap[vid]:
      if wid == "AGGR":
        continue
      try:
        val = float(turkscoreMap[vid][wid])
      except (ValueError, KeyError):
        continue
      deviation = (y_i[vid] - val) * (y_i[vid] - val)
      if wid not in count_j:
        count_j[wid] = 0.0
      if wid not in lambda_j:
        lambda_j[wid] = 0.0
              
      lambda_j[wid] = lambda_j[wid] + deviation
      count_j[wid] = count_j[wid] + 1.0

  for wid in lambda_j:
    lambda_j[wid] = count_j[wid]/lambda_j[wid]

  return lambda_j

##############################################################
def LogLikelihood(turkscoreMap, y_i, lambda_j):
  """Estimate the Loglikelihood value for the given data and parameters."""
  ll = 0.0
  for vid in sorted(turkscoreMap):
    for wid in turkscoreMap[vid]:
        # ignore the AGGR worker
      if wid == "AGGR":
        continue
      try:
        val = float(turkscoreMap[vid][wid])
      except (ValueError, KeyError):
        continue
      deviation = (y_i[vid] - val) * (y_i[vid] - val)
      ll_ij = 0.5 * math.log(lambda_j[wid]) - 0.5 * lambda_j[wid] * deviation
      ll = ll + ll_ij
  return ll

##############################################################

def WriteWeightedAverageScores(turkscoreMap, y_i, participantMap):
  for vid in turkscoreMap:
    workers = turkscoreMap[vid].workers
    break

  participants = []
  for p in range(1,90):
    participants.append("".join(["p",str(p)]))
  for p in range(1,90):
    participants.append("".join(["pp",str(p)]))

  lines = []
  # write the pre scores
  for pid in participants:
    if pid not in participantMap:
      continue
    vid = participantMap[pid]
    if vid not in turkscoreMap:
      continue
    for wid in workers:
      if wid == "AGGR":
        continue
      if wid not in turkscoreMap[vid].worker_scores:
        continue

      outline = []
      outline.append(pid)
      outline.append(wid)
      total_score = 0.0
      for q in range(19):
        outline.append(str(turkscoreMap[vid].worker_scores[wid][q]))
      lines.append(",".join(outline))
    mean_line = [pid, "AGGR"]
    total_mean = 0.0
    for q in range(18):
      mean_line.append(str(y_i[vid][q]))
      total_mean = total_mean + y_i[vid][q]
    mean_line.append(str(total_mean))
    lines.append(",".join(mean_line))
  # open the file to write
  fout = open("turker_scores_weighted.csv", "w")
  fout.write("\n".join(lines))
  fout.close()

##############################################################
#def main():
  # Read the video file map
#  video_map_file = "vid_to_participant_map.txt";
#  videoMap = GetVideoMap(video_map_file);
#  participantMap = GetParticipantToVideoMap(videoMap);
  # Read the turker scores for overall videos
 # turkscoreMap = ReadTurkScores('turker_scores_full_list.csv', participantMap)
#  question_names = ["Overall", "RecommendHiring",	"Colleague",	"Engaged",	"Excited", "EyeContact", "Smiled", "SpeakingRate", "NoFillers", "Friendly", "Paused", "EngagingTone", "StructuredAnswers", "Calm", "NotStressed", "Focused", "Authentic", "NotAwkward"]
#  y_i,lambda_j = EM(turkscoreMap, 20)
  # write weighted average scores
#  WriteWeightedAverageScores(turkscoreMap, y_i, participantMap)


#######################################
#if __name__ == "__main__":
#  main()
