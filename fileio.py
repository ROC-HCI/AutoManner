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
1) csvData: it is the exact data from the CSV file (output of Kinect skeleton tracker)
2) data: It contains all the join coordinates with frame number and timestamp.
      The first two columns of are frame number and timestamp respectively
3) X: In this matrix each column represents either x, y, or, z component of
      a joint. It is not defined which column represents which joint. 
      However, the columns are placed in an ascending order of jointID

Note 2: mat file format
.......................
The output mat file (which is input to sisc_wrapper.py module) is saved in
two different styles. 'concat' style concatenates all the data in a big time
series data. On the other hand, 'separate' style keeps the data separate.

Note 3: Order of Data flow
..........................
readskeletaltree
readallfiles_concat
readallfiles_separate
writeAll
rdstartstop             --> start stop frame number
readdatafile            --> (data output)
|    subsample          --> (data output) [call before clean]
|    clean              --> (data output)
|    calcinvarient      --> (data output) [call after clean]
|    splitcsvfile       --> (data output)
|    pad                --> (data output)
|    vcat               --> (data output)
|    txfmdata           --> (data output)
|    getjointdata       --> (X output)
|    |                                                               
|    (data input)
(file/folder level input)

-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
import numpy as np
import os
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

# Reads the data file (10.1.csv etc.) for the skeleton 
# returns the contents of the csv file and the headers for each column
def readdatafile(csvFileName):
    # read datafile
    with open(csvFileName) as f:
        header = f.readline().split(',')[0:-1]
        csvData = [x.split(',') for x in f.readlines()]
        csvData = np.array([x[0:-1] for x in csvData]).astype(np.float)
    scnIdx=[i for i,x in enumerate(header) if x == 'ScreenX' or x == 'ScreenY']
    datIdx = [x for x in range(scnIdx[-1]+1) if x not in scnIdx]
    data = csvData[:,datIdx] 
    data_header = [header[L] for L in datIdx]
    return data,data_header

# subsample the data. The first two columns (Timeframe and Timestamp)
# are automatically adjusted.
# Note: subsampling involves applying low pass filter and then decimate. Low
# pass filter introduces ripple effect at the boundaries of the signal.
# Therefore, it is suggested to apply subsample before cleaning the data
def subsample(data,decimateratio):
    noFilterCols = [0,1]
    filtCols = range(2,np.size(data,axis=1))
    nofiltDat = data[::decimateratio,noFilterCols]
    sampledCSVdata = np.zeros((len(nofiltDat),np.size(data,axis=1)))
    sampledCSVdata[:,noFilterCols] = nofiltDat
    sampledCSVdata[:,filtCols] = sg.decimate(data[:,filtCols],\
                                                    decimateratio,axis=0)
    return sampledCSVdata

# crop the data that falls within the [stframe,enframe] range
def clean(data,stframe,enframe):
    idx = (data[:,0]>=stframe)*(data[:,0]<=enframe)
    data = data[idx,:]
    return data

# Calculates invarient feature by translating the origin in the body
# It only works on joint coordinates
# Foot_left = 15 and Foot_Right = 19 
# HIP_LEFT = 12 and HIP_RIGHT = 16
def calcinvarient(data):
    # Translation Invaariance
    # =======================
    # Origin is set to the average of left and right foot
    ref_x,ref_y,ref_z = ((data[:,2+15*3] + data[:,2+19*3])/2.)[None].T,\
                        ((data[:,3+15*3] + data[:,3+19*3])/2.)[None].T,\
                        ((data[:,4+15*3] + data[:,4+19*3])/2)[None].T
    data[:,2::3] = data[:,2::3] - ref_x # x component
    data[:,3::3] = data[:,3::3] - ref_y # y component
    data[:,4::3] = data[:,4::3] - ref_z # z component

    # Rotation Invariance
    # ===================
    # Represent the data in 3D format
    m,n = np.shape(data)
    dat3d = np.reshape(data[:,2:],(m,(n-2)/3,3))
    leftH = dat3d[:,12,:]
    rightH = dat3d[:,16,:]
    hipVec = leftH - rightH
    hipVec = hipVec/np.linalg.norm(hipVec,axis=1)[None].T
    # Unit vector towards hipVec 90 rotated counterclockwise about y axis
    rotcc90=np.array([[0,0,-1],[0,1,0],[1,0,0]])
    uorient = rotcc90.dot(hipVec.T).T
    # cosangle between -x axis and uorient projected on xz plane
    cos_posx = (-1*uorient[:,0])/np.linalg.norm(uorient[:,[0,2]],axis=1)
    #th = np.arccos(cos_negz)*np.sign(cos_posx)
    th = np.arccos(cos_posx) - np.pi/2
    for i in range(len(th)):
        invrot = np.array([[np.cos(th[i]),0,np.sin(th[i])],[0,1,0],\
        [-1*np.sin(th[i]),0,np.cos(th[i])]])
        dat3d[i,:,:]=invrot.dot(dat3d[i,:,:].T).T
    data[:,2:]=np.reshape(dat3d,(m,n-2))
    
    # Scale Invariance
    # ================
    height = np.linalg.norm(dat3d[:,3,:],axis=1)   # Head = 3
    data[:,2:]=data[:,2:]/height[None].T
    return data,np.concatenate((ref_x,ref_y,ref_z),axis=1),th,height

# Read the start and end frame numbers for each speach
def rdstartstop(labeldataFile='Data/labeldata.csv'):
    with open(labeldataFile,'r') as readfile:
        alldata = readfile.readlines()
        alldata = alldata[0].split('\r')
        startframes = {item.split(',')[0]:int(item.split(',')[1]) \
        for item in alldata}
        endframes = {item.split(',')[0]:int(item.split(',')[3]) \
        for item in alldata}
    return startframes, endframes
    
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

# Read a single file and preprocess accordingly
def preprocess(filename,stenfile='Data/labeldata.csv'):
    data,header = readdatafile(filename)
    stfr,enfr = rdstartstop(stenfile)
    data = clean(data,stfr[filename[-8:-4]],enfr[filename[-8:-4]])
    data,tx,th,ht = calcinvarient(data)
    return data,header,tx,th,ht

# Transforms data into PCA domain
def txfmdata(data):
    X = data[:,2:]
    x_mean = np.mean(X,axis=0)
    X = X - x_mean
    d,v = np.linalg.svd(X,full_matrices=True)[1:]
    d=d/np.sum(d) # Normalize
    idx = d>=0.01
    princomps = v.T[:,idx]
    X_proj = X.dot(princomps)
    return X_proj,princomps,x_mean

############################## Toy dataset ####################################
# Generate and return a toy data
def toyExample_medium():
    alpha = np.zeros((256,1))
    alpha[35] = 0.5
    alpha[140] = 0.5
    alpha[160] = 1
    alpha[220] = 1
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
    alpha[140] = 0.5
    alpha[160] = 1
    alpha[220] = 1
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
    alpha[140] = 0.5
    alpha[160] = 1
    alpha[220] = 1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),3,1))
    psi[:,0,0] = 2*np.sin(xVal)
    psi[:,1,0] = np.sin(2*xVal-np.pi)
    psi[:,2,0] = 0.5*np.sin(4*xVal-np.pi/4)
    return alpha,psi
# Generate and return a toy data similar to the real life dataset
def toyExample_reallike(N=4096,M=64):
    D = 8
    K = 60
    alpha = np.zeros((N,D))
    psi = np.zeros((M,K,D))
    xVal = np.linspace(-1,1,M)*np.pi
    for d in xrange(D):
        alpha[[int(x) for x in np.random.rand(5)*(N-1)],d]=1.
    for d in xrange(D):
        for k in xrange(K):
            psi[:,k,d] = 2.0*np.sin(xVal*(d+1)/D + 1.0*k/K*np.pi)
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_1d_multicomp():
    alpha = np.zeros((256,2))
    alpha[30,0] = 0.5
    alpha[100,0] = 1
    alpha[125,0] = 1
    alpha[175,0] = 1
    alpha[230,0] = 1
    alpha[50,1] = 0.5
    alpha[100,1] = 1
    alpha[150,1] = 1
    alpha[200,1] = 1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),1,2))
    psi[:,0,0] = -1*np.cos(xVal/2.0)
    psi[:,0,1] = np.pi - np.abs(xVal)
    #psi[:,0,2] = np.greater_equal(np.pi/2.,np.abs(xVal))
    return alpha,psi
# Generate and return a toy data
def toyExample_medium_3d_multicomp():
    alpha = np.zeros((256,2))
    alpha[35,0] = 0.5
    alpha[180,0] = 1
    alpha[140,0] = 0.5
    alpha[160,0] = 1
    alpha[220,0] = 1
    alpha[50,1] = 1
    alpha[75,1] = 0.5
    alpha[100,1] = 0.5
    alpha[160,1] = 1
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
# A deceitful dataset where the addition of two components result in
# a signal orthogonal to the components. 
def toyExample_orthogonal_3d_multicomp():
    alpha = np.zeros((256,2))
    alpha[35,0] = 0.5
    alpha[180,0] = 1
    alpha[140,0] = 0.5
    alpha[160,0] = 1
    alpha[220,0] = 1
    alpha[50,1] = 1
    alpha[75,1] = 0.5
    alpha[100,1] = 0.5
    alpha[160,1] = 1
    alpha[200,1] = 1
    xVal = np.linspace(-1,1,32)*np.pi
    psi = np.zeros((len(xVal),3,2))
    psi[:,0,0] = 0.5*np.sin(4*xVal) - np.sin(xVal)
    psi[:,1,0] = 0.5*np.sin(4*(xVal+np.pi/6)) - np.sin(xVal+np.pi/6)
    psi[:,2,0] = 0.5*np.sin(4*(xVal+np.pi/4)) - np.sin(xVal+np.pi/4)
    psi[:,0,1] = np.sin(xVal)
    psi[:,1,1] = np.sin(xVal+np.pi/6)
    psi[:,2,1] = np.sin(xVal+np.pi/4)
    return alpha,psi    
# Generate and return a toy data
def toyExample_large_3d_multicomp(N=8192,M=64):
    alpha = np.zeros((N,2))
    alpha[[int(x) for x in np.ceil(np.random.rand(10)*(N-1))],0]=\
    5*np.random.rand(10)
    alpha[[int(x) for x in np.ceil(np.random.rand(10)*(N-1))],1]=\
    5*np.random.rand(10) 
    xVal = np.linspace(-1,1,M)*np.pi
    psi = np.zeros((len(xVal),3,2))
    psi[:,0,0] = np.sin(xVal)
    psi[:,1,0] = np.sin(xVal/2.0)
    psi[:,2,0] = np.sin(xVal/4.0 + np.pi/2)
    psi[:,0,1] = np.pi - np.abs(xVal)
    psi[:,1,1] = np.pi - np.abs(xVal/2.0)
    psi[:,2,1] = np.abs(xVal/2.0)
    return alpha,psi