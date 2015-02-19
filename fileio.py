''' File Input-Output Module
    ========================
    Functions starting with the prefix "toyExample" are sample datasets
    created for testing while writing various sections of the code.
    Other functions are created to load and preprocess the original dataset.
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
import numpy as np
import os
import skeletonPlotter as sp
import scipy.io as sio

# TODO: change arguments to all lower case
#################################### FILE IO ##################################
# Note: 
# csvData: it is the exact data from the CSV file
# data: it is the first return value from the function "splitDataFile"
# First two columns of data are frame number and timestamp respectively
# X: From this matrix, each column represents either x,y, or, z component of
# a joint locations. It is not defined which column represents which joint. 
# However, the columns are placed in a nondecreasing order of jointID

# Read the Skeletal tree file
def readSkeletalTree(treeFilename):
    assert os.path.isfile(treeFilename)
    with open(treeFilename) as f:
        assert f.readline().startswith('Nodes:')
        allDat = [data.strip() for data in f.readlines()]
        nodeInfo = [dat.strip().split('=') for dat in allDat if '=' in dat]
        nodes = dict((elem[0].strip(),int(elem[1])) for elem in nodeInfo)
        assert 'Edges:' in allDat
        idx = allDat.index('Edges:')
        edges = np.array([elem.split(',') for elem in allDat[idx+1:]][:-1]\
                                                            ).astype(np.int)
        return nodes,edges

# Read the speech boundary file. This file contains information on where the
# actual speech started and where finished
# Returns videoList, start_End_time_List
# Please note that this is an approximate measure of speech boundary because
# it was measured in the independent video file. The kinect data is
# not synchronized with that video. So, there is no gurantee that the speech
# is properly cropped. Even the timestamp might be out of bound in the kinect data.
def readSpeechBoundary(csvFileName):
    with open(csvFileName) as f:
        f.readline()
        temp = [x.split(',') for x in f.readlines()]
        videoList = [x[0] for x in temp]
        starEndList = np.array([x[1:] for x in temp]).astype(np.int)
    return videoList,starEndList

# Reads the joint position (animation) data file (csv) for the skeleton 
# returns the contents of the csv file and the headers for each column
def readDataFile(csvFileName):
    # read datafile
    with open(csvFileName) as f:
        header = f.readline().split(',')[0:-1]
        csvData = [x.split(',') for x in f.readlines()]
        csvData = np.array([x[0:-1] for x in csvData]).astype(np.float)
    return csvData,header
    
# Given the contents of the animation data file, it returns the following:
# data, data_header, Orientation, Orien_Head, ScreenXY, ScreenXY_header
# The contents of the animation data file should be read using the function
# readDataFile. Output of this function can be fed directly to this function
def splitDataFile(csvData,header):
    # Read indices
    scnIdx=[i for i,x in enumerate(header) if x == 'ScreenX' or x == 'ScreenY']
    orientIdx = range(scnIdx[-1]+1,len(header))
    datIdx = [x for x in range(scnIdx[-1]+1) if x not in scnIdx]
    data = csvData[:,datIdx] 
    data_header = [header[L] for L in datIdx]
    orient = csvData[:,orientIdx]
    orient_header = [header[L] for L in orientIdx]
    screenxy = csvData[:,scnIdx]
    screenxy_header = [header[L] for L in scnIdx]
    return data,data_header,orient,orient_header,screenxy,screenxy_header

# TODO: Rotational and scale invariance
# Calculates invarient feature by translating the origin in the body
# It assumes the data to be in the same format 
# as given by the function readDataFile()
def calcInvarient(csvData):
    csvData[:,2::3]=csvData[:,2::3]-csvData[:,2][None].T.dot(np.ones((1,20)))
    csvData[:,3::3]=csvData[:,3::3]-csvData[:,3][None].T.dot(np.ones((1,20)))
    csvData[:,4::3]=csvData[:,4::3]-csvData[:,4][None].T.dot(np.ones((1,20)))
    return csvData

# Delete the nSecBegin seconds from the begining and nSecEnds seconds from
# the end because that is usually garbage. The actual crop positions
# may vary will be returned in cropBoundStart,cropBoundEnd
def clean(csvData,nSecBegin = 5,nSecEnd = 5):
    cropBoundStart = np.argmax(csvData[:,1]>nSecBegin*1000)
    cropBoundEnd = np.argmax(csvData[:,1]>(csvData[-1,1] - nSecEnd*1000))
    csvData = csvData[cropBoundStart:cropBoundEnd,:]
    csvData[:,:2] = csvData[:,:2] - csvData[0,:2]
    return csvData,cropBoundStart,cropBoundEnd
    
# returns the x,y,z columns for the specified joint locations only
def getJointData(data,joints):
    # If scalar, convert to tuple
    if isinstance(joints,tuple) == False and \
        isinstance(joints,list) == False:
        joints = (joints,)
    else:
        joints = sorted(joints)
    firstTime = True
    for ajoint in joints:
        temp = data[:,(2+3*ajoint):(2+3*ajoint+3)]
        if firstTime:
            X = temp.copy()
            firstTime = False
        else:
            X = np.concatenate((X,temp),axis=1)
    return X

### z-score normalization of skeleton data. The 
#def normalizeDat(X):    
#    xMean = np.mean(X,axis=0)
#    X = (X - xMean)
#    maxStd = np.max(np.std(X,axis=0))
#    return X/maxStd

# Pad the end of the first axis with nPad number of null rows. Frame number and
# Time stamps for the rows are computed automatically for the null rows
def pad(dat,nPad):
    timepad=np.array([np.arange(nPad)]*2).T
    timepad[:,1]=timepad[:,0]*dat[-1,1]/(dat[-1,0]) # Keep the framerate same
    timepad += dat[-1,:2]
    dat = np.pad(dat,((0,nPad),(0,0)),'constant',constant_values=0)
    dat[-len(timepad):,:2] = timepad
    return dat

# Vertically concatenate two matrices. Frame number and
# Time stamps for the rows are automatically adjusted
def vcat(dat1,dat2):
    dat2[:,:2]+=dat1[-1,:2]
    return np.concatenate((dat1[:-1,:],dat2),axis=0)

## Reads all the skeleton tracking file in a folder.
def readAllFiles_Concat(startPath,suffix,nPad=150,nSecBegin=5,nSecEnd=5):
    firstIter = True
    boundDic = {}
    for root,folder,files in os.walk(startPath):
        for afile in files:
            if afile.lower().endswith(suffix.lower()):
                # create full filename and print
                fullPath = os.path.join(root,afile)
                print fullPath
                # Read file. 
                dat,header = readDataFile(fullPath)                
                # Clean and pad with zeros
                dat = clean(dat,nSecBegin,nSecEnd)[0]
                datLen=len(dat)
                dat = pad(dat,nPad)
                # Concatenate the data
                if firstIter:
                    firstIter = False
                    allData = dat.copy()
                    boundDic[fullPath]=(0,datLen)
                else:
                    boundDic[fullPath]=(len(allData),len(allData)+datLen)                    
                    allData = vcat(allData,dat)
        return allData,boundDic,header

# Generate and return a toy data
#def toyExample_small():
#    alpha = np.zeros((16,1))
#    alpha[4] = 1
#    alpha[12] = -0.5
#    psi = np.zeros((4,1,1))
#    psi[:,0,0] = [1,2,1,-1]
#    return alpha,psi    
# Generate and return a toy data
def toyExample_medium():
    alpha = np.zeros((256,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = np.sin(4*xVal-np.pi/4)
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_boostHighFreq():
    alpha = np.zeros((256,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = 0.5*np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = 2*np.sin(4*xVal-np.pi/4)
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_boostLowFreq():
    alpha = np.zeros((256,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = 2*np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = 0.5*np.sin(4*xVal-np.pi/4)
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_1d():
    alpha = np.zeros((256,1))
    alpha[35] = 0.5
    alpha[140] = -0.5
    alpha[160] = 1
    alpha[220] = -1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),1,1))
    psi[:,0,0] = np.sin(xVal)
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_1d_multicomp():
    alpha = np.zeros((256,2))
    alpha[35,0] = 0.5
    alpha[140,0] = -0.5
    alpha[160,0] = 1
    alpha[220,0] = -1
    alpha[50,1] = 0.5
    alpha[100,1] = -0.5
    alpha[200,1] = 1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),1,2))
    psi[:,0,0] = np.sin(xVal)
    psi[:,0,1] = np.pi - np.abs(xVal)
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_3d_multicomp():
    alpha = np.zeros((256,2))
    alpha[35,0] = 0.5
    alpha[140,0] = -0.5
    alpha[160,0] = 1
    alpha[220,0] = -1
    alpha[50,1] = 0.5
    alpha[100,1] = -0.5
    alpha[200,1] = 1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),3,2))
    psi[:,0,0] = np.sin(xVal)
    psi[:,1,0] = np.sin(xVal/2.0)
    psi[:,2,0] = np.sin(xVal/2.0 + np.pi/2)
    psi[:,0,1] = np.pi - np.abs(xVal)
    psi[:,1,1] = np.pi - np.abs(xVal/2.0)
    psi[:,2,1] = np.abs(xVal/2.0)
    return alpha,psi
# Generate and return a toy data
def toyExample_large_3d_multicomp(N=8192,M=64):
    alpha = np.zeros((N,2))
    alpha[np.random.rand(N)>0.95,0]=1.0
    alpha[np.random.rand(N)>0.95,1]=1.0
    xVal = np.linspace(-1,1,M)*np.pi
    psi = np.zeros((len(xVal),3,2))
    psi[:,0,0] = np.sin(xVal)
    psi[:,1,0] = np.sin(xVal/2.0)
    psi[:,2,0] = np.sin(xVal/4.0 + np.pi/2)
    psi[:,0,1] = np.pi - np.abs(xVal)
    psi[:,1,1] = np.pi - np.abs(xVal/2.0)
    psi[:,2,1] = np.abs(xVal/2.0)
    return alpha,psi
############################## End File IO ####################################
def unitTest1():
    joints,bones = readSkeletalTree('Data/KinectSkeleton.tree')
    # Read all the files and split
    csvDat,boundDic,header = readAllFiles_Concat('Data/','.csv')
    data,dataHead = splitDataFile(csvDat,header)[:2]
    # Save the data in matlab format
    sio.matlab.savemat('Data/top5_skeletal_Data.mat',{'csvDat':csvDat,\
    'header':header,'data':data,'dataHead':dataHead})
    sio.matlab.savemat('Data/top5_skeletal_Data_bound.mat',boundDic)
    print 'Data Saved'
    #Animate data
    gui = sp.plotskeleton(data,dataHead,bones,skipframes=5)
    gui.show()
def unitTest2():
    allData = sio.loadmat('Data/all_skeletal_Data.mat')
    joints,_ = readSkeletalTree('Data/KinectSkeleton.tree')
    X = getJointData(allData['data'],(joints['SHOULDER_RIGHT'],\
    joints['ELBOW_RIGHT'],joints['WRIST_RIGHT'],joints['HAND_RIGHT']))
    print np.shape(X)
    pass
    

if __name__ == '__main__':
    unitTest1()