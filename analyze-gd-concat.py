''' Human Behavior Analysis Module
    ==============================
    This module extracts Behavioral Action Units (BAU's) using convolutional
    sparse coding
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool
from itertools import izip
import numpy as np
import scipy.signal as sg
import scipy.io as sio
import fileio as fio
import matplotlib.pyplot as pp
import math as M
import time

############################## Helper Functions ###############################
# Display the gradients
def dispGrads(gralpha,grpsi):
    _,D = np.shape(gralpha)    
    for d in xrange(D):    
        pp.figure('Plot of Gradients for component # '+'{:0}'.format(d))
        pp.clf()
        # Plot Gradient wrt psi
        pp.subplot(211)    
        pp.plot(grpsi[:,:,d])
        pp.title('Gradf wrt psi')
        # Plot Gradient wrt alpha 
        pp.subplot(212)        
        pp.plot(gralpha[:,d])
        pp.title('Gradf wrt alpha')
        pp.draw()
        pp.pause(1)
# Plots alpha, psi, original and reconstructed data
def dispPlots(alpha,psi,X,figureName,p):
    _,D = np.shape(alpha)
    for d in xrange(D):
        pp.figure(figureName + ' for component # '+'{:0}'.format(d))
        pp.clf()    
        pp.subplot(511)
        pp.plot(X)
        yrange = pp.ylim()        
        pp.title('Original Data')        
        pp.subplot(512)
        L = recon(alpha,psi,p)
        pp.plot(L)
        pp.ylim(yrange)
        pp.title('Reconstructed Data')    
        pp.subplot(513)
        pp.plot(L - X)
        pp.ylim(yrange)
        pp.title('Reconstructed - Original')        
        pp.subplot(514)
        pp.plot(psi[:,:,d])
        pp.title('psi')
        pp.subplot(515)
        pp.stem(alpha[:,d])
        pp.title('alpha')     
        pp.draw()
        pp.pause(0.3)
# Plot the original alpha, psi and X
def dispOriginal(alpha,psi):
    pp.figure('Original Alpha and Psi')
    pp.clf()
    _,D = np.shape(alpha)
    for d in xrange(D):
        pp.subplot(D,2,2*d+1)
        pp.plot(psi[:,:,d])
        pp.axis('tight')
        pp.title('psi')
        pp.subplot(D,2,2*d+2)
        pp.plot(alpha[:,d])
        pp.axis('tight')
        pp.title('alpha')
        pp.draw()
        pp.pause(1)    
# Find the next power of 2
def nextpow2(i):
    # do not use numpy here, math is much faster for single values
    buf = M.ceil(M.log(i) / M.log(2))
    return int(M.pow(2, buf))        
######################### Algorithm Control Functions #########################     
# Model functions
def modelfunc_alpha(alpha_k,alpha,psi,X,Gamma,gradAlpha,p):
    return calcP(X,alpha_k,psi,p) + \
    np.sum(gradAlpha*(alpha - alpha_k)) + \
    0.5*(1/Gamma)*np.linalg.norm(alpha - alpha_k)**2.0
def modelfunc_psi(alpha,psi_k,psi,X,Gamma,gradPsi,p):
    return calcP(X,alpha,psi_k,p) + \
    np.sum(gradPsi*(psi - psi_k)) + \
    0.5*(1/Gamma)*np.linalg.norm(psi - psi_k)**2.0
################### Functions for calculating objectives ######################
# Mean squared error part of the objective function
def calcP(X,alpha,psi,p):
    L = recon(alpha,psi,p)
    return 0.5*np.sum((X-L)**2.)
# Actual value of the objective function
def calcObjf(X,alpha,psi,beta,p):
    return calcP(X,alpha,psi,p)+beta*np.sum(np.abs(alpha))
# Logarithm of the objective function
def loglike(X,alpha,psi,beta,p):
    return M.log(calcObjf(X,alpha,psi,beta,p))
    #return (0.5*np.sum((X-L)**2.))
########################### Projection Functions ##############################
#Normalize psi (Project onto unit circle)    
def normalizePsi(psi):
    M,K,D = np.shape(psi)
    for d in xrange(D):
        psiNorm = np.linalg.norm(psi[:,:,d])
        if (psiNorm>0):
            psi[:,:,d] = psi[:,:,d]/psiNorm
    return psi
# Project psi in a set {Norm(psi) < c}
def projectPsi(psi,c):
    M,K,D = np.shape(psi)
    for d in xrange(D):
        psiNorm = np.linalg.norm(psi[:,:,d])
        psi[:,:,d] = min(c,psiNorm)*(psi[:,:,d]/psiNorm)
    return psi
# Apply Proximal/Shrinkage operation on alpha
def shrink(alpha, threshold):
    N,D = np.shape(alpha)
    assert(N>D)
    for d in xrange(np.shape(alpha)[1]):
        alpha[:,d] = np.sign(alpha[:,d])*np.maximum(\
        np.zeros(np.shape(alpha[:,d])),np.abs(alpha[:,d])-threshold)
    return alpha
######################### Initialization Function #############################
# Randomly initialize alpha and psi
# alpha is N x D (axis-0:time/frame, axis-1: various AEB)
# alpha represents sparse coefficient for various AEB's
# psi is M x K x D (axis-1: x, y and z components of AEB)
# psi represents all the AEBs (D number of them)
# M is a scalar integer representing time/frame length for AEB 
def csc_init(M,N,K,D):
    psi = projectPsi(np.random.rand(M,K,D),1.0) # Random initialization
    #psi = projectPsi(np.ones((M,K,D)),1.0)  # Fixed initialization
    alpha = np.zeros((N,D))
    return psi,alpha
######################## Functions for Data Reconstruction ####################
# This function performs convolution (*) of alpha and psi
# alpha is N x D (axis-0:time/frame, axis-1: various AEB)
# alpha represents sparse coefficient for various AEB's
# psi is M x K x D (axis-1: x, y and z components of AEB)
# psi represents all the AEBs (D number of them)
# OUTPUT: returns an N x k x d tensor which is alpha*psi over axis-0
# Note: The method uses multiple processes for faster operation
def __myconvolve(in2,in1,mode):
    return sg.fftconvolve(in1,in2,mode)
def convAlphaPsi(alpha,psi,p):
    szAlpha = np.shape(alpha)
    szPsi = np.shape(psi)
    assert len(szAlpha) == 2 and len(szPsi) == 3 and szAlpha[1] == szPsi[2]
    convRes = np.zeros((szAlpha[0],szPsi[1],szAlpha[1]))
    for d in xrange(szAlpha[1]):
        partconvolve = partial(__myconvolve,in1=alpha[:,d],mode='same')
        convRes[:,:,d] = np.array(p.map(partconvolve,psi[:,:,d].T,1)).T
    return convRes
# Reconstruct the data from components
# s is d x 1 tensor containing scalar loading for each alpha*psi
# alpha is N x D, psi is M x K X D
# OUTPUT: inner product of alpha*psi and s
def recon(alpha,psi,p):
    szAlpha = np.shape(alpha)
    szPsi = np.shape(psi)
    assert len(szAlpha) == 2 and len(szPsi) == 3 and szAlpha[1] == szPsi[2]
    convRes = convAlphaPsi(alpha,psi,p)
    return np.sum(convRes,axis=2)
####################### Exact calculation of Gradient #########################
# Manually Checked with sample data -- Working as indended
# Grad of P wrt alpha is sum((X(t)-L(t))psi(t-t'))
# Returns an NxD tensor representing gradient of P with respect to psi
# Note: The method uses multiple processes for faster operation
def __myconvolve1(parArgs):
    return sg.fftconvolve(parArgs[0],parArgs[1],'full')
def calcGrad_alpha(alpha,psi,X,p):
    N,D = np.shape(alpha)
    M,K,_ = np.shape(psi)
    gradP_alpha = np.zeros((N,D,K))
    L = recon(alpha,psi,p)
    lxDiff = (L-X).T
    for d in xrange(D):
        parArgs = izip(lxDiff,psi[::-1,:,d].T)
        gradP_alpha[:,d,:] = np.array(p.map(__myconvolve1,parArgs,1))\
        [:,(M+N)/2-N/2:(M+N)/2+N/2].T
    gradP_alpha = np.sum(gradP_alpha,axis=2)
    return gradP_alpha
# Manually Checked with sample data -- Working as indended
# Grad of P wrt psi is sum((X(t)-L(t))alpha(t-t'))
# Returns an MxKxD tensor representing gradient of P with respect to psi
# Note: The method uses multiple processes for faster operation    
def calcGrad_psi(alpha,psi,X,p):
    N,D = np.shape(alpha)
    M,K,_ = np.shape(psi)
    gradP_psi = np.zeros((M,K,D))
    L = recon(alpha,psi,p)
    lxDiff = (L - X).T
    for d in xrange(D):
        partconvolve = partial(sg.fftconvolve,in2=alpha[::-1,d],mode='full')
        gradP_psi[:,:,d] = np.array(p.map(partconvolve,lxDiff))\
                                                        [:,(N-M/2):(N+M/2)].T
    return gradP_psi
####################### Main Gradient Descent Procedure #######################
# Applies Convolutional Sparse Coding with Proximal Gradient Descent Algorithm    
# X is N x K data tensor for only one joint 
# M is a scalar integer representing time/frame length for AEB     
# D represents how many AEB we want to capture
# beta is the weight for sparcity constraint
def csc_pgd(X,X_mean,M,D,beta,iter_thresh=65536,thresh = 1e-5,dispObj=False,\
		dispGrad=False,dispIteration=False,totWorker=4):
    iter = 0
    X = X - X_mean
    N,K = np.shape(X)
    # Scaling of Beta: The nonsparsity cost beta should be linear to the 
    # total number of scalars involved in the objective function (N*K)
    # Therefore, a scaling of beta is necessary to resist tuning beta for
    # every different sample size
    beta = beta*N*K
    # M and N must be nonzero and power of two
    assert (M&(M-1)==0) and (N&(N-1)==0) and M!=0 and N!=0
    workers = Pool(processes=totWorker)   # Assign workers
    psi,alpha = csc_init(M,N,K,D)   # Random initialization
    #psi = psi_orig                 # Setting the initial value to actual
    #alpha = alpha_orig + 0.01      # solution. Debug purpose only    
    factor = 0.5
    prevlikeli = loglike(X,alpha,psi,beta,workers)
    maxDeltaLikeli = 0
    countZero = 0
    # Main optimization loop
    while iter < iter_thresh:
        itStartTime = time.time()
        print str(iter),
        # Update psi and alpha with line search        
        # Update psi
        gamma_psi = 1.0
        # Calculate gradient of P with respect to psi
        grpsi = calcGrad_psi(alpha,psi,X,workers)
        #Line search
        while True:
            newPsi = projectPsi(psi - gamma_psi*grpsi,1.0)
            if modelfunc_psi(alpha,psi,newPsi,X,gamma_psi,grpsi,workers)<\
                                            calcP(X,alpha,newPsi,workers):
                gamma_psi *= factor
            else:
                break
            if gamma_psi<1e-15:
                gamma_psi = 0
                newPsi = projectPsi(psi - gamma_psi*grpsi,1.0)
                break
        print 'LR_p/a','{:.1e}'.format(gamma_psi),'/',
        psi = newPsi.copy()
#        # Update Alpha        
        gamma_alpha = 1.0
        # Calculate gradient of P with respect to alpha
        gralpha = calcGrad_alpha(alpha,psi,X,workers)
        # Line search
        while True:
            newAlpha = shrink(alpha - gamma_alpha*gralpha,gamma_alpha*beta)
            if modelfunc_alpha(alpha,newAlpha,psi,X,gamma_alpha,gralpha,\
            workers)<calcP(X,newAlpha,psi,workers):
                gamma_alpha *= factor
            else:
                break
            if gamma_alpha<1e-15:
                gamma_alpha = 0
                newAlpha = shrink(alpha - gamma_alpha*gralpha,\
                                                            gamma_alpha*beta)
                break
        print '{:.2e}'.format(gamma_alpha),
        alpha = newAlpha.copy()
        # Count the iteration
        iter += 1
        # Debug and Display        
        likeli = loglike(X,alpha,psi,beta,workers)
        #valP = calcP(X,alpha,psi)
        
        if dispGrad: 
            # Display Gradiants
            dispGrads(gralpha,grpsi)
        if dispIteration:
            # Display alpha, psi, X and L
            dispPlots(alpha,psi,X,'Iteration Data',workers)
        # Display Log Objective
        if dispObj:
            pp.figure('Log likelihood plot')
            pp.scatter(iter,likeli,c = 'b')
            pp.title('Likelihood Plot for Beta = ' + '{:f}'.format(beta))
            pp.draw()
            pp.pause(1)
        # Print iteration status.
        delta = prevlikeli - likeli
        maxDeltaLikeli = max(maxDeltaLikeli,abs(delta))
        print 'N',str(N),'K',str(K),'M',str(M),'D',str(D),'Beta',\
        str(beta/N/K)+'('+str(beta)+')',\
            'logObj','{:.2f}'.format(likeli), \
            'delta','{:.2e}'.format(delta),\
            'iterTime','{:.2e}'.format(time.time() - itStartTime)
                
        # terminate loop
        allowZero_number = 8
        if (delta<thresh) or np.isnan(delta):
            if (delta<thresh or np.isnan(delta))and countZero<allowZero_number:
                countZero += 1
            elif (delta < thresh or np.isnan(delta)) and \
            countZero>=allowZero_number:
                break
            print countZero
        else:
            countZero = 0
            prevlikeli = likeli
    reconError = calcP(X,alpha,psi,workers)
    L0 = np.count_nonzero(alpha)
    if not np.sum(X_mean)==0:
        psi = psi + np.transpose(X_mean[None],axes=(0,2,1))
    return alpha,psi,likeli,reconError,L0
################################# Main Helper #################################
def buildArg():
    args = ArgumentParser(description="Automatic Extraction of Human Behavior")

    args.add_argument('-i',nargs='?',\
    metavar='INPUT_MAT_FILENAME',\
    help='A mat file containing all the data concatenated together \
    (i.e. style=concat). Required.')
    
    args.add_argument('-o',nargs='?',default='Results/result',\
    metavar='OUTPUT_FILE_PATH_AND_PREFIX',\
    help='Path and any prefix of the generated output mat files. \
    (default: %(default)s)')
    
    args.add_argument('-p',nargs='?',type=int,default=4,\
    metavar='Num_Parallel',\
    help='Total number of parallel processes to be used. \
    (default: %(default)s)')

    args.add_argument('-toy',nargs='?',type=int,\
    choices=range(1,8),metavar='TOY_DATA_ID',\
    help='This will override the INPUT_MAT_FILENAME with synthetic toy data.\
    The ID refers different preset synthetic data. \
    Must be chosen from the following: %(choices)s')    
    
    args.add_argument('-skelTree',nargs='?',default=\
    'Data/KinectSkeleton.tree',metavar='SKELETON_TREE_FILENAME',\
    help='A .tree file containing kinect skeleton tree (default: %(default)s)')

    args.add_argument('-meanFile',nargs='?',default=\
    'Data/meanSkel.mat',metavar='MEAN_SKELETON_FILENAME',\
    help='A .mat file containing the mean (average) of all the feature values \
    (default: %(default)s)')

    args.add_argument('-j',nargs='*',\
    default=['ALL'],\
    choices=['NONE','ALL','HIP_CENTER','SPINE','SHOULDER_CENTER','HEAD',\
    'SHOULDER_LEFT','ELBOW_LEFT','WRIST_LEFT','HAND_LEFT',\
    'SHOULDER_RIGHT','ELBOW_RIGHT','WRIST_RIGHT','HAND_RIGHT',\
    'HIP_LEFT','KNEE_LEFT','ANKLE_LEFT','FOOT_LEFT','HIP_RIGHT',\
    'KNEE_RIGHT','ANKLE_RIGHT','FOOT_RIGHT'],\
    metavar='JOINTS_TO_CONSIDER',\
    help='A list of joint names for which the analysis will\
    be performed. If NONE is selected, the joint selection will not be\
    performed; all the columns in the data variable from the mat file will\
    directly put to the optimizer. If you chose NONE, please alse choose an\
    appropriate value for -M. Otherwise, it will be automatically set to 2.\
    Note: joint selection is not applicable\
    for toy data. (default: %(default)s). Must be chosen from the following:\
    %(choices)s',required=False)

    args.add_argument('-iter_thresh',nargs='?',type=int,default=65536,\
    metavar='ITERATION_THRESHOLD',\
    help='Threshold of iteration (termination criteria) (default:%(default)s)')
    
    args.add_argument('-diff_thresh',nargs='?',type=float,default=1e-5,\
    metavar='DIFFERENCE_THRESHOLD',\
    help='Threshold of difference in log objective function\
    (termination criteria) (default:%(default)s)')
    
    args.add_argument('-M',nargs='?',type=int,default=-2,\
    metavar='ATOM_LENGTH',\
    help='The length of atomic units (psi). IOW, the size of each \
    element of the dictionary. Must be a power of 2. (default: %(default)s)\
    A negative number indicates the system will automatically choose a\
    length which is approximately equvalent to abs(M) sec. Does not have\
    any effect on toy data')
    
    args.add_argument('-D',nargs='?',type=int,default=16,\
    metavar='DICTIONARY_LENGTH',\
    help='The total number of atomic units (psi). In Other Words, the total\
    number of elements in the dictionary (default: %(default)s). Does not have\
    any effect on toy data')
    
    args.add_argument('-Beta',nargs='?',type=float,default=3e-5,\
    metavar='NON-SPARSITY_COST',\
    help='Represents the cost of nonsparsity. The higer the cost, the \
    sparser the occurances of the dictionary elements.')
    
    args.add_argument('--Disp',dest='Disp', action='store_true',\
    default=False,help='Turns on displays relevant for Toy data.\
    Shows Original Data + Final Results. It is not applicable for data input\
    from mat. Does not slow down much.')
        
    args.add_argument('--DispObj',dest='Disp_Obj', action='store_true',\
    default=False,help='Turns on log of objective function plot. Hugely slows\
    down the algorithm.')
    
    args.add_argument('--DispGrad',dest='Disp_Gradiants', action='store_true',\
    default=False,help='Turns on the gradient plots. Mainly used for\
    debuging. Hugely slows down the algorithm.')
    
    args.add_argument('--DispIter',dest='Disp_Iterations',action='store_true',\
    default=False,help='Turns on the plots in each iteration. Mainly used for\
    debuging. Hugely slows down the algorithm.')
    return args
################################## Unit Test ##################################
def toyTest(dataID,D=2,M=64,beta=0.05,disp=True,dispObj=False,dispGrad=False,\
                                            dispIteration=False,totWorker=4):
    #======================================================
#   Synthetic Toy Data
    if dataID==1:
        D=1
        alpha,psi = fio.toyExample_medium()
    elif dataID==2:
        D=1
        alpha,psi = fio.toyExample_medium_boostHighFreq()
    elif dataID==3:
        D=1
        alpha,psi = fio.toyExample_medium_boostHighFreq()
    elif dataID==4:
        D=1
        alpha,psi = fio.toyExample_medium_1d()
    elif dataID==5:
        D = 2
        M = 32
        beta =  5e-5
        alpha,psi = fio.toyExample_medium_1d_multicomp()
    elif dataID==6:
        alpha,psi = fio.toyExample_medium_3d_multicomp() 
    elif dataID==7:
        alpha,psi = fio.toyExample_large_3d_multicomp()    
    p = Pool(totWorker)
    # Construct the data            
    X = recon(alpha,projectPsi(psi,1.0),p)
    # Display Original Data if allowed
    if disp:
        dispOriginal(alpha,psi)    
    # Apply Convolutional Sparse Coding. 
    # Length of AEB is set to 2 seconds (60 frames)    
    # D represents how many Action Units we want to capture
    X_mean = np.zeros(np.shape(X))
    alpha_recon,psi_recon = csc_pgd(X,X_mean,M,D,beta,dispObj=dispObj,\
                    dispGrad=dispGrad,dispIteration=dispIteration)[:2]
    # Display the reconstructed values
    if disp:
        print '### Parameters ###'
        print 'N = ', str(len(X))
        print 'K = ', str(np.size(X,axis=1))
        print 'M = ', str(M)
        print 'D = ', str(D)
        print 'beta = ', str(beta),'(beta*N*K = ',\
                    str(beta*len(X)*np.size(X,axis=1)),')'
        dispPlots(alpha_recon,psi_recon,X,'Final Result',p)
        pp.pause(1)
        pp.show()
    return alpha_recon,psi_recon    
################################ Main Entrance ################################
def main():
    # Handle arguments
    parser = buildArg()
    args = parser.parse_args()
    
    # In case of toy data
    if not args.toy == None:
        alpha_recon,psi_recon = toyTest(args.toy,D=2,M=64,beta=args.Beta,\
            disp=args.Disp,dispObj=args.Disp_Obj,dispGrad=args.Disp_Gradiants,\
            dispIteration=args.Disp_Iterations,totWorker=args.p)
        return
        
    # In case of real data, load the input file
    allData = sio.loadmat(args.i)
    if not 'style' in allData.keys():
        allData['style']='concat'
    # Load the mean feature file
    meanDat = sio.loadmat(args.meanFile)
    
    # The input data file is saved in two different format: concat and separate
    if allData['style']=='concat':
        # Choose the joints according to arguments
        if 'NONE' in args.j:
            X = allData['data']
            X_mean = np.zeros(np.shape(X))
            args.M = M.fabs(args.M)
        elif 'ALL' in args.j:
            X = fio.getjointdata(allData['data'],range(20))
            X_mean = fio.getjointdata(meanDat['avgSkel'],range(20))
        else:
            joints,bones = fio.readskeletaltree(args.skelTree)
            jointList = [joints[jName] for jName in args.j]
            X = fio.getjointdata(allData['data'],jointList)
            X_mean = fio.getjointdata(meanDat['avgSkel'],jointList)
        # Choose the correct length of psi if M is negative
        if args.M<0:
            args.M=nextpow2(np.argmax(allData['data'][:,0]>30*M.fabs(args.M)))
        # Pad the data to make it appropriate size
        numZeros = (nextpow2(len(X))-len(X))
        X = np.pad(X,((0,numZeros),(0,0)),'constant',constant_values=0)    
        # Apply Convolutional Sparse Coding
        alpha_recon,psi_recon,logObj,reconError,L0 = csc_pgd(X,X_mean,\
        M=args.M,D=args.D,beta=args.Beta,iter_thresh=args.iter_thresh,\
        thresh = args.diff_thresh,dispObj=args.Disp_Obj,\
        dispGrad=args.Disp_Gradiants,dispIteration=args.Disp_Iterations,\
        totWorker=args.p)
    # if the input data file is saved as separate style, use stochastic
    # gradient descent module
    elif allData['style']=='separate':
        raise Exception('The input file format is not supported')
    # Save the results
    resultName = args.o+'_M='+str(args.M)+'_D='+str(args.D)+'_beta='+\
        str(args.Beta)+'_'+'_'.join(args.j)+'_'+time.strftime(\
        '%H_%M_%S',time.localtime())
    sio.savemat(resultName+'.mat',{'alpha_recon':alpha_recon,\
    'psi_recon':psi_recon,'logObj':logObj,'reconError':reconError,'L0':L0,\
    'M':args.M,'D':args.D,'Beta':args.Beta,'joints':args.j,'Header':\
    allData['dataHead'],'timeData':allData['data'][:,0:2],\
    'decimateratio':allData['decimateratio']})
    print    
    print 'Done!'
    
if __name__ == '__main__':
    main()