'''
This is the main optimizer module for Shift Invariant Sparse Coding.
Besides the optimizer module, it also contains several helper functions.
These functions are mainly required for debuging and plotting the results
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
from functools import partial
from multiprocessing import Pool
from itertools import izip
import numpy as np
import scipy.signal as sg
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
def sisc_init(M,N,K,D):
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
# alpha is N x D, psi is M x K X D
# OUTPUT: sum of alpha*psi
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
# Applies Shift Invariant Sparse Coding with Proximal Gradient Descent Algorithm
# It assumes the data (X) is given in batch mode -- i.e. X is exhaustive
# X is N x K data tensor for only one joint 
# M is a scalar integer representing time/frame length for AEB     
# D represents how many AEB we want to capture
# beta is the weight for sparcity constraint
# The last two parameters (psi_orig and alpha_orig) are for debug purposes only
def optimize_proxim(X,M,D,beta,iter_thresh=65536,\
    thresh = 1e-5,dispObj=False,dispGrad=False,dispIteration=False,totWorker=4,\
    psi_orig=[], alpha_orig=[]):
# def optimize_proxim(X,M,D,beta,iter_thresh=65536,thresh = 1e-3,dispObj=False,\
# 		dispGrad=False,dispIteration=False,totWorker=4):
    iter = 0
    N,K = np.shape(X)
    # Scaling of Beta: The nonsparsity cost beta should be linear to the 
    # total number of scalars involved in the objective function (N*K)
    # Therefore, a scaling of beta is necessary to resist tuning beta for
    # every different sample size
    # beta = beta*N*K
    # M and N must be nonzero and power of two
    assert (M&(M-1)==0) and (N&(N-1)==0) and M!=0 and N!=0
    workers = Pool(processes=totWorker)   # Assign workers
    psi,alpha = sisc_init(M,N,K,D)   # Random initialization
    #psi = psi_orig                 # Setting the initial value to actual
    #alpha = alpha_orig             # solution. Debug purpose only    
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
        # Update Alpha        
        gamma_alpha = 1.0
        # Calculate gradient of P with respect to alpha
        gralpha = calcGrad_alpha(alpha,psi,X,workers)
        # Apply accelerated
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
    return alpha,psi,likeli,reconError,L0
