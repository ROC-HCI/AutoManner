''' File Input-Output Module
    ========================
    This module reads, preprocess and saves the skeleton animation data (saved
    in csv format) as convenient .mat format which can be fed into analyze
    module. It contains number of convenience functions for file handling.
    
    Functions starting with the prefix "toyExample" are sample datasets
    created for testing while writing various sections of the code.
    Other functions are created to load and preprocess the original dataset.

Note 1: Data Formats
....................
1) csvData: it is the exact data from the CSV file
2) data: It contains all the join coordinates with frame number and timestamp.
      The first two columns of are frame number and timestamp respectively
3) X: In this matrix each column represents either x, y, or, z component of
      a joint. It is not defined which column represents which joint. 
      However, the columns are placed in a nondecreasing order of jointID

Note 2: mat file format
.......................
The output mat file (which is input to analyze.py module) is saved in
two different styles. 'concat' style concatenates all the data in a big time
series data. On the other hand, 'separate' style keeps the data separate.

Note 3: Order of Data flow
..........................
readskeletaltree
readallfiles_concat
readallfiles_separate
writeAll
readdatafile            --> (csvData output)
|    subsample          --> (csvData output) [call before clean]
|    clean              --> (csvData output)
|    calcinvarient      --> (csvData output) [call after clean]
|    splitcsvfile      --> (data output)
|    |    pad           --> (data output)
|    |    vcat          --> (data output)
|    |    getjointdata  --> (X output)
|    |    |                                                               
|    |    (data input)
|    (csvData input)
(file/folder level input)
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
import scipy.signal as sg
############################## Convenience ####################################
# TODO: change arguments to all lower case
# Read the Skeletal tree file
def readskeletaltree(treeFilename):
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

# Reads the joint position (animation) data file (csv) for the skeleton 
# returns the contents of the csv file and the headers for each column
def readdatafile(csvFileName):
    # read datafile
    with open(csvFileName) as f:
        header = f.readline().split(',')[0:-1]
        csvData = [x.split(',') for x in f.readlines()]
        csvData = np.array([x[0:-1] for x in csvData]).astype(np.float)
    return csvData,header

# subsample the animation data. The first two columns (Timeframe and Timestamp)
# are automatically adjusted.
# Note: subsampling involves applying low pass filter and then decimate. Low
# pass filter introduces ripple effect at the boundaries of the signal.
# Therefore, it is suggested to apply subsample before cleaning the data
def subsample(csvdata,header,decimateratio):
    noFilterCols = [0,1]
    noFilterCols.extend([idx for idx,x in enumerate(header) \
                                        if x=='Start_Joint' or x=='End_Joint'])
    filtCols = [idx for idx in range(len(header)) if not idx in noFilterCols]
    nofiltDat = csvdata[::decimateratio,noFilterCols]
    sampledCSVdata = np.zeros((len(nofiltDat),np.size(csvdata,axis=1)))
    sampledCSVdata[:,noFilterCols] = nofiltDat
    sampledCSVdata[:,filtCols] = sg.decimate(csvdata[:,filtCols],\
                                                    decimateratio,axis=0)
    return sampledCSVdata

# Delete the nSecBegin seconds from the begining and nSecEnds seconds from
# the end because that is usually garbage. The actual crop positions
# may vary but it will be returned as cropBoundStart,cropBoundEnd
def clean(csvData,nSecBegin = 5,nSecEnd = 5):
    cropBoundStart = np.argmax(csvData[:,1]>nSecBegin*1000)
    cropBoundEnd = np.argmax(csvData[:,1]>(csvData[-1,1] - nSecEnd*1000))
    csvData = csvData[cropBoundStart:cropBoundEnd,:]
    csvData[:,:2] = csvData[:,:2] - csvData[0,:2]
    return csvData,cropBoundStart,cropBoundEnd

# TODO: Rotational invariance
# Calculates invarient feature by translating the origin in the body
# It only works on joint coordinates
def calcinvarient(csvdata,header):
    # skeletal joints
    alljoint_x = [idx for idx,x in enumerate(header) if (x.endswith('x'))\
    and x.find('Orientation')==-1]
    alljoint_y = [idx for idx,x in enumerate(header) if (x.endswith('y'))\
    and x.find('Orientation')==-1]
    alljoint_z = [idx for idx,x in enumerate(header) if (x.endswith('z'))\
    and x.find('Orientation')==-1]
    # Reference    
    spine=header.index('SPINE_x')
    shldr=header.index('SHOULDER_CENTER_x')
    # The spine is the origin. subtract the coordinate of spine from the 
    # coordinates of all the joints in the skeleton
    csvdata[:,alljoint_x]=csvdata[:,alljoint_x]-csvdata[:,spine][None].T.\
                                        dot(np.ones((1,len(alljoint_x))))
    csvdata[:,alljoint_y]=csvdata[:,alljoint_y]-csvdata[:,spine+1][None].T.\
                                        dot(np.ones((1,len(alljoint_y))))
    csvdata[:,alljoint_z]=csvdata[:,alljoint_z]-csvdata[:,spine+2][None].T.\
                                        dot(np.ones((1,len(alljoint_z))))
    # Scale the skeleton so that the spine length becomes unity
    spineVector = csvdata[:,shldr:shldr+3]
    spineVecLen = np.linalg.norm(spineVector,axis=1)[None].T
    csvdata[:,alljoint_x] = csvdata[:,alljoint_x]/spineVecLen
    csvdata[:,alljoint_y] = csvdata[:,alljoint_y]/spineVecLen
    csvdata[:,alljoint_z] = csvdata[:,alljoint_z]/spineVecLen
    return csvdata
    
# Given the contents of the animation data file, it returns the following:
# data, data_header, Orientation, Orien_Head, ScreenXY, ScreenXY_header
# The contents of the animation data file should be read using the function
# readdatafile. Output of this function can be fed directly to this function
def splitcsvfile(csvData,header):
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
    
# returns the x,y,z columns for the specified joint locations only
def getjointdata(data,joints):
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

# Pad the end of the first axis with nPad number of null rows. Frame number and
# Time stamps for the rows are computed automatically for the null rows
def pad(data,nPad):
    timepad=np.array([np.arange(nPad)]*2).T
    timepad[:,1]=timepad[:,0]*data[-1,1]/(data[-1,0]) # Keep the framerate same
    timepad += data[-1,:2]
    data = np.pad(data,((0,nPad),(0,0)),'constant',constant_values=0)
    data[-len(timepad):,:2] = timepad
    return data

# Vertically concatenate two matrices. Frame number and
# Time stamps for the rows are automatically adjusted
def vcat(dat1,dat2):
    dat2[:,:2]+=dat1[-1,:2]
    return np.concatenate((dat1[:-1,:],dat2),axis=0)

## Reads all the skeleton tracking file in a folder and concatenates into one.
# This function subsamples and cleans the data before concatenating into a
# giant time series
def readallfiles_concat(startPath,suffix,decimateratio,invariant=True,\
                                            nPad=150,nSecBegin=5,nSecEnd=5):
    firstIter = True
    boundDic = {}
    for root,folder,files in os.walk(startPath):
        for afile in files:
            if afile.lower().endswith(suffix.lower()):
                # create full filename and print
                fullPath = os.path.join(root,afile)
                print fullPath
                # Read file. 
                csvdat,header = readdatafile(fullPath)                
                # Clean and pad with zeros
                dat = clean(subsample(csvdat,header,decimateratio)\
                                                        ,nSecBegin,nSecEnd)[0]
                if invariant:
                    dat = calcinvarient(dat,header)
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

## Reads all the skeleton tracking file in a folder and concatenates into one.
# This function subsamples and cleans the data before concatenating into a
# giant time series
def readallfiles_separate(startPath,suffix,decimateratio,invariant=True,\
                                            nPad=150,nSecBegin=5,nSecEnd=5):
    csvDataList = []
    filenamelist = []
    for root,folder,files in os.walk(startPath):
        for afile in files:
            if afile.lower().endswith(suffix.lower()):
                # create full filename and print
                fullPath = os.path.join(root,afile)
                print fullPath
                # Read file. 
                csvdat,header = readdatafile(fullPath)                
                # Clean and pad with zeros
                csvdat = clean(subsample(csvdat,header,decimateratio)\
                                                        ,nSecBegin,nSecEnd)[0]
                if invariant:
                    csvdat = calcinvarient(csvdat,header)
                csvDataList.append(csvdat)
                filenamelist.append(fullPath)
    return csvDataList,filenamelist,header

# Writes all the data as input mat file. style can take either 'concat' or
# 'separate'. Before writing, this function subtracts the mean
def writeAll(outfilename,style,inputpath='Data/',\
    meanfile = 'Data/meanSkel.mat',decimateRatio=5):
    assert style=='concat' or style=='separate'
    meandata = sio.loadmat(meanfile)

    if style == 'concat':
        # Read all the files and split
        csvDat,boundDic,header = readallfiles_concat(inputpath,'.csv',\
                        decimateRatio,True)
        data,dataHead = splitcsvfile(csvDat,header)[:2]
        #Subtract mean
        data = data - meandata['avgSkel']
        # Save the data in matlab format
        sio.matlab.savemat(outfilename,\
        {'csvDat':csvDat,'header':header,'data':data,'dataHead':dataHead,\
        'decimateratio':decimateRatio,'invariant':True,'nPad':150,\
        'nSecBegin':5,'nSecEnd':5,'style':style})
        sio.matlab.savemat(outfilename+'_bound.mat',boundDic)
        print 'Data Saved'
    else:
        csvlist,filenamelist,header = readallfiles_separate(inputpath,'.csv',\
                        decimateRatio,True)
        datDic={}
        data=[]
        for i,csvDat in enumerate(csvlist):
            datDic['csvDat_'+str(i)]=csvDat
            datDic['data_'+str(i)]=splitcsvfile(csvDat,header)[0]
            data.append(datDic['data_'+str(i)])
        dataHead = splitcsvfile(csvDat,header)[1]
        datDic['header']=header
        datDic['filenamelist']=filenamelist
        datDic['dataHead']=dataHead
        datDic['decimateratio']=decimateRatio
        datDic['invariant']=True
        datDic['nSecBegin']=5
        datDic['nSecEnd']=5
        datDic['style']=style
        # Save the data in matlab format
        sio.matlab.savemat(outfilename,datDic)
        print 'Data Saved'
    return data,dataHead
############################## Toy dataset ####################################
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
    alpha = np.zeros((256,3))
    alpha[30,0] = 0.5
    alpha[100,0] = 1
    alpha[120,0] = -0.5
    alpha[230,0] = -1
    alpha[50,1] = -0.5
    alpha[100,1] = 1
    alpha[150,1] = -1
    alpha[200,1] = 1
    alpha[75,2] = 0.5    
    alpha[100,2] = -1
    alpha[140,2] = 0.25
    alpha[170,2] = -0.75
    alpha[230,2] = 1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),1,3))
    psi[:,0,0] = np.cos(xVal/2.0)
    psi[:,0,1] = np.pi - np.abs(xVal)
    psi[:,0,2] = np.greater_equal(np.pi/2.,np.abs(xVal))
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
############################## Test Modules ####################################
# Read, subsample, clean and concatenate all the data and save as mat file
def unitTest1(outfilename='Data/skeletal_Data_inv_subsampled_separate.mat'):
    bones = readskeletaltree('Data/KinectSkeleton.tree')[1]
    data,dataHead = writeAll(outfilename,'concat','Data/',\
    'Data/meanSkel.mat',5)
    #Animate data
    gui = sp.plotskeleton(data,dataHead,bones,skipframes=0)
    gui.show()
# Read, subsample, clean all the data but keep them separate
def unitTest1_sep(outfilename='Data/skeletal_Data_inv_subsampled_separate.mat'):
    data,dataHead = writeAll(outfilename,'separate','Data/',\
    'Data/meanSkel.mat',5)
    pass
# load matfile -- test of getjointdata (returns the x,y,z columns for the
#    specified joint locations only). Not particularly useful
def unitTest2():
    allData = sio.loadmat('Data/all_skeletal_Data.mat')
    joints,_ = readskeletaltree('Data/KinectSkeleton.tree')
    X,datHead = getjointdata(allData['data'],(joints['SHOULDER_RIGHT'],\
    joints['ELBOW_RIGHT'],joints['WRIST_RIGHT'],joints['HAND_RIGHT']),\
    allData['dataHead'])
    print np.shape(X)
    pass
# Animate/Plot cleaned and invariant data
def unitTest3():
    bones = readskeletaltree('Data/KinectSkeleton.tree')[1]
    csvDat,header = readdatafile('Data/20.2.csv')
    dat,datHead = splitcsvfile(calcinvarient(clean(csvDat)[0],header),\
                                                            header)[:2]
    gui = sp.plotskeleton(dat,datHead,bones,jointid1=2,skipframes=0)
    gui.show()
# Animate/Plot subsampled, cleaned, and invariant data
def unitTest4():
    bones = readskeletaltree('Data/KinectSkeleton.tree')[1]
    csvDat,header = readdatafile('Data/20.2.csv')
    # Subsample by a ratio of 5, clean and split the data
    dat,datHead = splitcsvfile(calcinvarient(clean(subsample(csvDat,\
                                            header,5))[0],header),header)[:2]    
    gui = sp.plotskeleton(dat,datHead,bones,jointid1=2,skipframes=0)
    gui.show()
# Calculate the average pose from the whole dataset    
def unitTest5():
    csvlist,filenamelist,header = readallfiles_separate('Data/',\
    suffix='.csv',decimateratio=5,invariant=True)
    firsttime=True
    count=0.
    # to remove the weight of each video length, we calculate the average of
    # the average
    for acsv in csvlist:
        data = splitcsvfile(acsv,header)[0]
        if firsttime:
            firsttime=False            
            sumdat = np.sum(data,axis=0)
        else:
            sumdat = sumdat + np.sum(data,axis=0)
        count+=len(data)
    avgSkel = sumdat/count
    avgSkel[0:2]=0
    header = splitcsvfile(acsv,header)[1]
    sio.savemat('Data/meanSkel.mat',{'avgSkel':avgSkel,'header':header})
    print 'done'
# Calculate per person average
def unitTest6():
    csvlist,filenamelist,csvheader = readallfiles_separate('Data/',\
                    suffix='.csv',decimateratio=5,invariant=True)
    oldperid = int(filenamelist[0][-8:-6])
    sumdat=0
    count=0
    for id,acsv in enumerate(csvlist):
        data,header = splitcsvfile(acsv,csvheader)[:2]
        perid = int(filenamelist[id][-8:-6])
        if not (oldperid == perid):
            avgSkel = sumdat/count
            avgSkel[0:2]=0    
            sio.savemat('Data/meanSkel_'+str(oldperid)+'.mat',\
                        {'avgSkel':avgSkel,'header':header})
            oldperid=perid
            sumdat=0
            count=0
        else:
            sumdat = sumdat + np.sum(data,axis=0)
            count = count + len(data)
    print 'done'    

if __name__ == '__main__':
    unitTest1()
    #unitTest5()