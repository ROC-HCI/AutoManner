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
def dispPlots(alpha,psi,X,figureName):
    _,D = np.shape(alpha)
    for d in xrange(D):
        pp.figure(figureName + ' for component # '+'{:0}'.format(d))
        pp.clf()    
        pp.subplot(511)
        pp.plot(X)
        yrange = pp.ylim()        
        pp.title('Original Data')        
        pp.subplot(512)
        L = recon(alpha,psi)
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
        pp.title('psi')
        pp.subplot(D,2,2*d+2)
        pp.plot(alpha[:,d])
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
def modelfunc_alpha(alpha_k,alpha,psi,X,Gamma,gradAlpha):
    return calcP(X,alpha_k,psi) + \
    np.sum(gradAlpha*(alpha - alpha_k)) + \
    0.5*(1/Gamma)*np.linalg.norm(alpha - alpha_k)**2.0
def modelfunc_psi(alpha,psi_k,psi,X,Gamma,gradPsi):
    return calcP(X,alpha,psi_k) + \
    np.sum(gradPsi*(psi - psi_k)) + \
    0.5*(1/Gamma)*np.linalg.norm(psi - psi_k)**2.0
################### Functions for calculating objectives ######################
# Mean squared error part of the objective function
def calcP(X,alpha,psi):
    L = recon(alpha,psi)
    return 0.5*np.sum((X-L)**2.)
# Actual value of the objective function
def calcObjf(X,alpha,psi,beta):
    return calcP(X,alpha,psi)+beta*np.sum(np.abs(alpha))
# Logarithm of the objective function
def loglike(X,alpha,psi,beta):
    return M.log(calcObjf(X,alpha,psi,beta))
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
    psi = projectPsi(np.random.randn(M,K,D),1.0)
    alpha = np.zeros((N,D))
    return psi,alpha
######################## Functions for Data Reconstruction ####################
# This function performs convolution (*) of alpha and psi
# alpha is N x D (axis-0:time/frame, axis-1: various AEB)
# alpha represents sparse coefficient for various AEB's
# psi is M x K x D (axis-1: x, y and z components of AEB)
# psi represents all the AEBs (D number of them)
# OUTPUT: returns an N x k x d tensor which is alpha*psi over axis-0
def convAlphaPsi(alpha,psi):
    szAlpha = np.shape(alpha)
    szPsi = np.shape(psi)
    assert len(szAlpha) == 2 and len(szPsi) == 3 and szAlpha[1] == szPsi[2]
    convRes = np.zeros((szAlpha[0],szPsi[1],szAlpha[1]))
    for d in xrange(szAlpha[1]):
        for k in xrange(szPsi[1]):
            convRes[:,k,d] = sg.fftconvolve(alpha[:,d],psi[:,k,d],'same')
    return convRes
# Reconstruct the data from components
# s is d x 1 tensor containing scalar loading for each alpha*psi
# alpha is N x D, psi is M x K X D
# OUTPUT: inner product of alpha*psi and s
def recon(alpha,psi):
    szAlpha = np.shape(alpha)
    szPsi = np.shape(psi)
    assert len(szAlpha) == 2 and len(szPsi) == 3 and szAlpha[1] == szPsi[2]
    convRes = convAlphaPsi(alpha,psi)
    return np.sum(convRes,axis=2)
####################### Exact calculation of Gradient #########################
# Manually Checked with sample data -- Working as indended
# Grad of P wrt alpha is sum((X(t)-L(t))psi(t-t'))
# Returns an NxD tensor representing gradient of P with respect to psi
def calcGrad_alpha(alpha,psi,X):
    N,D = np.shape(alpha)
    M,K,_ = np.shape(psi)
    gradP_alpha = np.zeros((N,D,K))
    L = recon(alpha,psi)
    lxDiff = L - X
    for d in xrange(D):
        for k in xrange(K):
            # this is actually a correlation operation. Notice that 
            # psi is actually flipped
            gradP_alpha[:,d,k] = \
            sg.fftconvolve(lxDiff[:,k],\
            psi[::-1,k,d],'full')[(M+N)/2-N/2:(M+N)/2+N/2]
    gradP_alpha = np.sum(gradP_alpha,axis=2)
    return gradP_alpha
# Manually Checked with sample data -- Working as indended
# Grad of P wrt psi is sum((X(t)-L(t))alpha(t-t'))
# Returns an MxKxD tensor representing gradient of P with respect to psi
def calcGrad_psi(alpha,psi,X):
    N,D = np.shape(alpha)
    M,K,_ = np.shape(psi)
    gradP_psi = np.zeros((M,K,D))
    L = recon(alpha,psi)
    lxDiff = L - X
    for d in xrange(D):    
        for k in xrange(K):
            # this is actually a correlation operation. Notice that 
            # alpha is flipped
            gradP_psi[:,k,d] = sg.fftconvolve(lxDiff[:,k],alpha[::-1,d],\
            'full')[(N-M/2):(N+M/2)] 
    return gradP_psi
def onepointgd(X,psi,beta_,K,D,M,iter_,dispGrad,dispIteration,dispObj,\
                                                iter_thresh,breakfree):
    # N is adjusted based on the data
    N = np.shape(X)[0]
    # M and N must be nonzero and power of two
    assert (M&(M-1)==0) and (N&(N-1)==0) and M!=0 and N!=0
    # Scaling Beta
    beta = beta_*N*K
    alpha = csc_init(M,N,K,D)[1]   # drop previous alpha
    factor = 0.5
    prevlikeli = loglike(X,alpha,psi,beta)
    maxDeltaLikeli = 0

    # Looping 5 times is sufficient for a particular data point            
    for loop in xrange(5):
        itStartTime = time.time()
        print str(iter_),
        # Update psi and alpha with line search        
        # Update Alpha        
        gamma_alpha = 0.1
        # Calculate gradient of P with respect to alpha
        gralpha = calcGrad_alpha(alpha,psi,X)
        # Apply accelerated
        while True:
            newAlpha = shrink(alpha - gamma_alpha*gralpha,gamma_alpha*beta)
            if modelfunc_alpha(alpha,newAlpha,psi,X,gamma_alpha,\
            gralpha)<calcP(X,newAlpha,psi):
                gamma_alpha *= factor
            else:
                break
            if gamma_alpha<1e-15:
                gamma_alpha = 0
                newAlpha = shrink(alpha - gamma_alpha*gralpha,\
                                                gamma_alpha*beta)
                break
        print 'LR_a/p','{:.2e}'.format(gamma_alpha),
        alpha = newAlpha.copy()
        # Update psi
        gamma_psi = 0.01
        # Calculate gradient of P with respect to psi
        grpsi = calcGrad_psi(alpha,psi,X)
        while True:
            newPsi = projectPsi(psi - gamma_psi*grpsi,1.0)
            if modelfunc_psi(alpha,psi,newPsi,X,gamma_psi,grpsi)<\
                                            calcP(X,alpha,newPsi):
                gamma_psi *= factor
            else:
                break
            if gamma_psi<1e-15:
                gamma_psi = 0
                newPsi = projectPsi(psi - gamma_psi*grpsi,1.0)
                break
        print '{:.1e}'.format(gamma_psi),'/',
        psi = newPsi.copy()

        # Count the iteration
        iter_ += 1
        # Debug and Display        
        likeli = loglike(X,alpha,psi,beta)
        
        if dispGrad: 
            # Display Gradiants
            dispGrads(gralpha,grpsi)
        if dispIteration:
            # Display alpha, psi, X and L
            dispPlots(alpha,psi,X,'Iteration Data')
        # Display Log Objective
        if dispObj:
            pp.figure('Log likelihood plot')
            pp.scatter(iter_,likeli,c = 'b')
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
        if iter_ >= iter_thresh:
            breakfree = True
            break #for loop in xrange(5)
    return psi,alpha,likeli,breakfree,iter_,X
####################### Main Gradient Descent Procedure #######################
# Applies Convolutional Sparse Coding with Stochastic GD
# M is a scalar integer representing time/frame length for AEB     
# D represents how many AEB we want to capture
# beta is the weight for sparcity constraint
def csc_sgd(Xlist,M,D,beta_,iter_thresh=65536,dispObj=False,\
		dispGrad=False,dispIteration=False,totWorker=4):
    iter_ = 0
    breakfree = False
    N,K = np.shape(Xlist[0])
    psi_dic = csc_init(M,N,K,D)[0]   # Random initialization of dictionary

    while True:
        np.random.shuffle(Xlist)
        # Stochastic loop -- 
        #TODO: this loop should be parallelized
        for _i_ in xrange(len(Xlist)):
            psi=psi_dic.copy()
            psi,alpha,likeli,breakfree,iter_,X = onepointgd(Xlist[_i_],\
            psi,beta_,K,D,M,iter_,dispGrad,dispIteration,dispObj,\
            iter_thresh,breakfree)
            # the updated psi will be added to the dictionary
            psi_dic = psi_dic + psi
            if breakfree:
                break #for _i_ in xrange(len(Xlist))
        if breakfree:
            break #while
    reconError = calcP(X,alpha,psi)
    L0 = np.count_nonzero(alpha)
    return alpha,psi,likeli,reconError,L0
################################# Main Helper #################################
def buildArg():
    args = ArgumentParser(description="Automatic Extraction of Human Behavior")

    args.add_argument('-i',nargs='?',default='Data/all_skeletal_Data.mat',\
    metavar='INPUT_MAT_FILENAME',\
    help='A mat file containing all the data concatenated into matrix. \
    or a list of csv files from where the data has to be read\
    (default: %(default)s)')
    
    args.add_argument('-o',nargs='?',default='Results/result',\
    metavar='OUTPUT_FILE_PATH_AND_PREFIX',\
    help='Path and any prefix of the generated output mat files. \
    (default: %(default)s)')
    
    args.add_argument('-p',nargs='?',type=int,default=4,\
    metavar='Num_Parallel',\
    help='Total number of parallel processes to be used. \
    (default: %(default)s)')
    
    args.add_argument('-skelTree',nargs='?',default=\
    'Data/KinectSkeleton.tree',metavar='SKELETON_TREE_FILENAME',\
    help='A .tree file containing kinect skeleton tree (default: %(default)s)')

    args.add_argument('-iter_thresh',nargs='?',type=int,default=65536,\
    metavar='ITERATION_THRESHOLD',\
    help='Threshold of iteration (termination criteria) (default:%(default)s)')
        
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
################################ Main Entrance ################################
def main():
    # Handle arguments
    parser = buildArg()
    args = parser.parse_args()
            
    # In case of real data, load the input file
    allData = sio.loadmat(args.i)
    if not 'style' in allData.keys():
        allData['style']='concat'
    
    # The input data file is saved in two different format: concat and separate
    if allData['style']=='concat':
        raise Exception('The input file format is not supported')
    elif allData['style']=='separate':
        datalist = [allData['data_'+str(i)] for i in \
                                    xrange(len(allData['filenamelist']))]
        X = [fio.getjointdata(data,range(20)) for data in datalist]
        
        # Choose the correct length of psi if M is negative
        if args.M<0:
            args.M=nextpow2(np.argmax(datalist[0][:,0]>30*M.fabs(args.M)))
        # Pad the data to make it appropriate size
        for indx in xrange(len(X)):
            numZeros = (nextpow2(len(X[indx]))-len(X[indx]))
            X[indx] = np.pad(X[indx],((0,numZeros),(0,0)),\
            'constant',constant_values=0)
        # Apply Convolutional Sparse Coding with stochastic gradient descent
        alpha_recon,psi_recon,logObj,reconError,L0 = csc_sgd(X,M=args.M,\
        D=args.D,beta_=args.Beta,iter_thresh=args.iter_thresh,\
        dispObj=args.Disp_Obj,dispGrad=args.Disp_Gradiants,
        dispIteration=args.Disp_Iterations,totWorker=args.p)
    # Save the results
    resultName = args.o+'_M='+str(args.M)+'_D='+str(args.D)+'_beta='+\
        str(args.Beta)+'_'+'_'+time.strftime(\
        '%H_%M_%S',time.localtime())
    sio.savemat(resultName+'.mat',{'alpha_recon':alpha_recon,\
    'psi_recon':psi_recon,'logObj':logObj,'reconError':reconError,'L0':L0,\
    'M':args.M,'D':args.D,'Beta':args.Beta,'Header':\
    allData['dataHead'],'timeData':allData['data'][:,0:2],\
    'decimateratio':allData['decimateratio']})
    print
    print 'Done!'
    
if __name__ == '__main__':
    main()