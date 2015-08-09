# coding=utf-8
import sys
import re
import numpy as np
# import unirest                                      # unused
# import urllib                                       # unused
import os
import random
import math
import nltk
from nltk import word_tokenize, wordpunct_tokenize
# SVM classes for the libsvm library
#sys.path.append('./libsvm-3.17/python')
#from svmutil import *
import csv


def extract_words(filename):
	file = open(filename,'r');
	read = csv.reader(file);
	resultlist = [];
	title = [];
	count = 0;

	for row in read:
		if count==0:
			title.append(row);
		else:
			temp = row[28].replace('â€™',"'");
			resultlist.append(temp);
		count = count+1;
	return resultlist;

def match(LIWCDic, word):
    if word in LIWCDic:
        return LIWCDic[word]
    
    for i in range(1,len(word)):
        key = word[:i] + "*"
        if key in LIWCDic:
            return LIWCDic[key]
    return list()



def ReadLIWCDictionary(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    
    dic = {}

    for line in lines:
        parts = line.lstrip().rstrip().split("\t")

        values = list()
        for i in range(1, len(parts)):
#            print(parts[0], parts[i])
            values.append(int(parts[i]))

        dic[parts[0]] = values

    return dic

###########################################################################
def ReadLIWCCategories(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    categories = lines[0].split("\r")
    catdic = {}
    
    for cat in categories:
        catparts = cat.split("\t")
        catdic[int(catparts[0])] = catparts[1]
    return catdic

def extract_liwc(filename):
	LIWCDic = ReadLIWCDictionary('liwcdic2007.dic');
	categories = ReadLIWCCategories('liwccat2007.txt');
	liwc_categories = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,142,146,147,148,149,150,250,251,252,253,354,355,462,463,464];
	rawwords = extract_words(filename);
	liwclist = [];
	feature_names = [];

	index = 0;
	for trans in rawwords:
		print trans+'\t'+str(index)+'\n\n';
		templist = [];
		words = word_tokenize(trans);
		cat_counts = [0.0] * len(liwc_categories);

		for word in words:
			word = word.lower();
			matched_cats = match(LIWCDic,word);
			#print(word,matched_cats);
			for i_cat in range(len(liwc_categories)):
				if liwc_categories[i_cat] in matched_cats:
					cat_counts[i_cat] = cat_counts[i_cat] + 1.0;

		for i_cat in range(len(liwc_categories)):
			templist.append(str(float(cat_counts[i_cat])/float(len(words))));
			feature_names.append(categories[liwc_categories[i_cat]]);

		liwclist.append(templist);
		index = index+1;
	
	return liwclist;

def CountWord(textlist):
	wordcount = [];
	for text in textlist:
		words = re.split(' |\n|.\n|, ', text);
		tempcount = 0;
		for word in words:
			if (word == ' ') | (word == '') | (word==',')|(word=='\t'):
				continue;
			word = word.lstrip().rstrip().lower();
			tempcount = tempcount+1;
		wordcount.append(tempcount);
	return wordcount;

def WordFrequence(textlist):
	wordfreq = [];
	for text in textlist:
		words = re.split(' |\n|.\n|, ', text);
		tempfreq = {};
		for word in words:
			if (word == ' ') | (word == '') | (word==',')|(word=='\t'):
				continue;
			word = word.lstrip().rstrip().lower();
			if word in tempfreq:
				tempfreq[word] = tempfreq[word]+1;
			else:
				tempfreq[word] = 1;
		wordfreq.append(tempfreq);
	return wordfreq;


def CountUniqueWord(textlist):
	wordfreq = [];
	for text in textlist:
		words = re.split(' |\n|.\n|, ', text);
		tempfreq = {};
		for word in words:
			if (word == ' ') | (word == '') | (word==',')|(word=='\t'):
				continue;
			word = word.lstrip().rstrip().lower();
			if word in tempfreq:
				tempfreq[word] = tempfreq[word]+1;
			else:
				tempfreq[word] = 1;
		wordfreq.append(len(tempfreq));
	return wordfreq;


def GetFillerWordsCount(textlist):
	wordfreqs = WordFrequence(textlist);
	filler_list = [];
	filler_words = {'uhh':'uhh', 'um':'um', 'uh':'uh', 'umm':'umm', 'like':'like', 'know':'know', 'so':'so', 'think':'think', 'you':'you', 'know':'know', 'ah':'ah', 'umhum':'umhum', 'uhum':'uhum', 'uhm':'uhm'}
    
	for wordfreq in wordfreqs:
		filler_count = 0;
		for fw in filler_words:
			if wordfreq.get(fw) != None:
				filler_count = filler_count + wordfreq.get(fw);
		filler_list.append(filler_count);

	return filler_list;
    
def GetDuration(filename):
	file = open(filename,'r');
	read = csv.reader(file);
	duration = [];
	for row in read:
		temp = row[36];
		temp = float(temp);
		duration.append(temp);
	return duration;

def Getfpsec(textlist, filename):
	filler_count = GetFillerWordsCount(textlist);
	durationlist = GetDuration(filename);
	filler_rate = [];
	for i in range(len(filler_count)):
		temp = float(filler_count[i])/ float(duration[i]);
		filler_rate.append(temp);
	return filler_rate;


def Getwpsec(textlist, filename):
	word_count = CountWord(textlist);
	durationlist = GetDuration(filename);
	wpseclist = [];
	for i in range(len(word_count)):
		temp = float(word_count[i])/float(duration[i]);
		wpseclist.append(temp);
	return wpseclist;

def Getupsec(textlist, filename):
	unique_word = CountUniqueWord(textlist);
	durationlist = GetDuration(filename);
	upseclist = [];
	for i in range(len(unique_word)):
		temp = float(unique_word[i])/float(duration[i]);
		upseclist.append(temp);
	return upseclist;













