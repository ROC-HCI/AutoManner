# -*- coding: utf-8 -*-
"""
Created on Mon Dec 15 00:49:26 2014

@author: Md.Iftekhar
"""
import numpy as np
import os

#################################### FILE IO ##################################
# read point definition file
def readPointDic(dicFilename):
    with open(dicFilename) as f:
        pointName = [dat.strip().split('=') for dat in f.readlines()]
        points = dict((elem[0].strip(),int(elem[1])) for elem in pointName)
        return points 

# returns a tensor containing the kinect skeleton data and corresponding 
# timestamp (in Second) for each row. Also the screen coordinates.
def readDataFile(readDataFile,joints):
    # read datafile
    with open(readDataFile) as f:
        temp = [x.split(',') for x in f.readlines()]
    # Convert the data into a convenient numpy array
    dat = np.array([x[0:-1] for x in temp]).astype(np.float)
    timeStampSec = (dat[:,0] - dat[0,0])/300    # copy the timestamp
    dat = np.delete(dat,0,axis=1)               # Delete timestamp column
    # Copy x and y locations of the points
    screenXY = dat[:,(np.arange(101)%5==3) | (np.arange(101)%5==4)]
    # reshape the data in a higher dimensional tensor
    m,n = dat.shape
    dat.shape = (m,20,5)
    dat = np.delete(dat,(3,4),axis=2)
    if not joints:
        joints = range(20)
    return dat[:,joints,:],timeStampSec,screenXY

# We delete last nSec * 30 frames because that is usually garbage
def clean(dat,nSec = 10):
    return dat[:-(30*nSec),:,:]
    
# Normalization of the skeleton data. x,y,z components are individually
# meansubtracted and divided by
def normalizeDat(dat):    
    datMean = np.mean(dat,axis=0)
    dat = (dat - datMean)
    datStd = np.max(np.std(dat,axis=0),axis=1)
    for j in xrange(np.size(dat,axis=1)):
        dat[:,j,:]/=datStd[j]
    return dat

# Reads all the skeleton tracking file in a folder and concatenates to 
# to a single 3 dimensional array. First dimension is for frame number. 2nd and 
# 3rd dimension is for jointID and (x,y,z) values respectively 
# returns a tensor containing the data from all files
# Applies some rudimentary preprocessing if preprocess is turned on
def readAllFiles(fullFiles,suffix,preprocess,joints=(),nSec = 10):
    if not joints:
        m = 20
    else:
        m = len(joints)
    allData = np.zeros((1,m,3))
    boundDic = {}
    bound = (-1,-1)
    for root,folder,files in os.walk(fullFiles):
        for afile in files:
            if afile.lower().endswith(suffix.lower()):
                # create full filename and print
                fullPath = os.path.join(root,afile)
                print fullPath
                # Read file. 
                dat,_,_ = readDataFile(fullPath,joints)
                # Preprocess
                if preprocess:
                    dat = normalizeDat(clean(dat,nSec))
                # Keep a record of where each file starts and ends 
                bound = (bound[1]+1,bound[1]+np.size(dat,axis=0))
                boundDic[bound] = fullPath
                # Concatenate all the data
                allData = np.concatenate((allData,dat),axis=0)
    allData=np.delete(allData,0,axis=0)
    allData = np.transpose(allData,axes=[0,2,1])
    return allData,boundDic

# Given any row index and the doundary dictionary it returns from which
# file the row is coming. Important to trace back for finding the frame in
# the video
def findWhichFile(rowIndx,boundDic):
    rowNumber = np.where((np.array(boundDic.keys())[:,0]<rowIndx) & \
    (np.array(boundDic.keys())[:,1]>rowIndx))[0][0]
    return boundDic.values()[rowNumber]
    
# Generate and return a toy data
def toyExample_large():
    alpha = np.zeros((5000,1))
    alpha[500] = 1
    alpha[2500] = 0.5
    alpha[3000] = -1
    xVal = np.arange(-np.pi,np.pi,0.0075)
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = np.sin(np.sin(xVal))
    psi[:,1,0] = np.sin(np.sin(np.pi + xVal))
    psi[:,2,0] = np.sin(np.sin(np.pi/4 + xVal))
    return alpha,psi

# Generate and return a toy data
def toyExample_medium():
    alpha = np.zeros((250,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.arange(-np.pi,np.pi,0.4)
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = np.sin(4*xVal-np.pi/4)
    return alpha,psi

# Generate and return a toy data
def toyExample_medium_boostHighFreq():
    alpha = np.zeros((250,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.arange(-np.pi,np.pi,0.4)
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = 0.5*np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = 2*np.sin(4*xVal-np.pi/4)
    return alpha,psi

# Generate and return a toy data
def toyExample_medium_boostLowFreq():
    alpha = np.zeros((250,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.arange(-np.pi,np.pi,0.4)
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = 2*np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = 0.5*np.sin(4*xVal-np.pi/4)
    return alpha,psi

# Generate and return a toy data
def toyExample_medium_1d():
    alpha = np.zeros((250,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.arange(-np.pi,np.pi,0.23)
    psi = np.zeros((len(xVal),1,1))
    psi[:,0,0] = np.sin(xVal)
    return alpha,psi

# Generate and return a toy data
def toyExample_small():
    alpha = np.zeros((10,1))
    alpha[3] = 1
    alpha[7] = -0.5
    psi = np.zeros((3,3,1))
    psi[:,0,0] = [1,2,1]
    psi[:,1,0] = [1,2,1]
    psi[:,2,0] = [0.5,1,0.5]
    return alpha,psi
############################## End File IO ####################################
