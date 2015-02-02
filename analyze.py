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
import numpy as np
import scipy.signal as sg
import scipy.io as sio
import fileio as fio
import matplotlib.pyplot as pp
import math as M

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
        pp.plot(alpha[:,d])
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
def modelfunc_alpha(alpha_k,alpha,psi,X,Gamma):
    return calcP(X,alpha_k,psi) + \
    np.sum(calcGrad_alpha(alpha_k,psi,X)*(alpha - alpha_k)) + \
    0.5*(1/Gamma)*np.linalg.norm(alpha - alpha_k)**2.0
def modelfunc_psi(alpha,psi_k,psi,X,Gamma):
    return calcP(X,alpha,psi_k) + \
    np.sum(calcGrad_psi(alpha,psi_k,X)*(psi - psi_k)) + \
    0.5*(1/Gamma)*np.linalg.norm(psi - psi_k)**2.0
################### Functions for calculating objectives ######################
# Mean squared error part of the objective function
def calcP(X,alpha,psi):
    L = recon(alpha,psi)
    return (0.5*np.sum((X-L)**2.))
# Actual value of the objective function
def calcObjf(X,alpha,psi,beta):
    L = recon(alpha,psi)
    return (0.5*np.sum((X-L)**2.) + beta*np.sum(np.abs(alpha)))
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
    gradP_alpha = np.sum(gradP_alpha,axis=2)  # Should we really avg?
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
####################### Main Gradient Descent Procedure #######################
# Applies Convolutional Sparse Coding with Proximal Gradient Descent Algorithm    
# X is N x K data tensor for only one joint 
# M is a scalar integer representing time/frame length for AEB     
# D represents how many AEB we want to capture
# beta is the weight for sparcity constraint
#def csc_pgd(alpha_orig,psi_orig,X,M,D,beta,iter_thresh=65500,thresh = 1e-5):
def csc_pgd(X,M,D,beta,iter_thresh=65536,thresh = 1e-5,disp=False):
    iter = 0
    N,K = np.shape(X)
    # M and N must be nonzero and power of two
    assert (M&(M-1)==0) and (N&(N-1)==0) and M!=0 and N!=0
    psi,alpha = csc_init(M,N,K,D)   # Random initialization
    #psi = psi_orig                 # Setting the initial value to actual
    #alpha = alpha_orig + 0.01      # solution. Debug purpose only    
    factor = 0.5
    prevlikeli = loglike(X,alpha,psi,beta)
    maxDeltaLikeli = 0
    countZero = 0
    # Main optimization loop
    while iter < iter_thresh:
        print 'iter = ', iter,
        # Update psi and alpha with line search        
        # Update psi
        gamma_psi = 16.0
        # Calculate gradient of P with respect to psi
        grpsi = calcGrad_psi(alpha,psi,X)
        while True:        
            newPsi = projectPsi(psi - gamma_psi*grpsi,1.0)
            if modelfunc_psi(alpha,psi,newPsi,X,gamma_psi)<calcP(X,alpha,newPsi):
                gamma_psi *= factor
            else:
                break
            if gamma_psi<1e-15:
                gamma_psi = 0
                newPsi = projectPsi(psi - gamma_psi*grpsi,1.0)
                break
        print ' Gamma_psi = ', '{:.4e}'.format(gamma_psi), ' ',
        psi = newPsi.copy()
#        # Update Alpha        
        gamma_alpha = 16.0
        # Calculate gradient of P with respect to alpha
        gralpha = calcGrad_alpha(alpha,psi,X)
        while True:
            newAlpha = shrink(alpha - gamma_alpha*gralpha,gamma_alpha*beta)
            if modelfunc_alpha(alpha,newAlpha,psi,X,gamma_alpha)<\
            calcP(X,newAlpha,psi):
                gamma_alpha *= factor
            else:
                break
            if gamma_alpha<1e-15:
                gamma_alpha = 0
                newAlpha = shrink(alpha - gamma_alpha*gralpha,gamma_alpha*beta)
                break
        print 'Gamma_alpha = ', '{:.4e}'.format(gamma_alpha),' ',
        alpha = newAlpha.copy()
        # Count the iteration
        iter += 1
        # Debug and Display        
        likeli = loglike(X,alpha,psi,beta)
        valP = calcP(X,alpha,psi)
        if disp:
            # Display alpha, psi, X and L
            dispPlots(alpha,psi,X,'Iteration Data')
            # Display Gradiants
            dispGrads(gralpha,grpsi)
    #        # Display Log Likelihood
            pp.figure('Log likelihood plot')
            pp.scatter(iter,likeli,c = 'b')
            pp.title('Likelihood Plot for Beta = ' + '{:0.2f}'.format(beta))
            pp.draw()
            pp.pause(1)
        # Print status. Sparsity ratio is the percentage of error coming from
        # sparsity
        delta = prevlikeli - likeli
        maxDeltaLikeli = max(maxDeltaLikeli,abs(delta))
        print ' Sparsity Ratio = ', \
            '{:.2e}%'.format((np.exp(likeli) - valP)/np.exp(likeli)*100),\
            ' likeli = ', '{:.2f}'.format(likeli), \
            ' delta = ', '{:.2e}'.format(delta),
        if maxDeltaLikeli!=0.0:
            print '({:.2f}%)'.format((prevlikeli - likeli)/maxDeltaLikeli*100)
        else:
            print        
        # terminate loop
        allowZero_number = 8
        if (delta<thresh) or np.isnan(delta):
            if (delta<thresh or np.isnan(delta)) and countZero<allowZero_number:
                countZero += 1
            elif (delta < thresh or np.isnan(delta)) and \
            countZero>=allowZero_number:
                break
            print countZero
        else:
            countZero = 0
            prevlikeli = likeli        
    return alpha,psi
################################## Main Entrance ##############################        
def main():
#    # read joint names and data file
    #jointID = fio.readPointDic('Data/pointDef.dic')    
    #dat,timeIndx,_ = readDataFile('Data/','.csv',joints=(\
    # jointID['ELBOW_RIGHT'],jointID['WRIST_RIGHT']),preprocess=True)
    #dat,boundDic = fio.readAllFiles('Data/','.csv',preprocess=True)
    #sio.savemat('Data/jointInfo.mat',{'dat':dat})
#    dat = sio.loadmat('Data/jointInfo.mat')['dat']
#    
#    #TODO: Delete this line. For debug only
#    dat = dat[:500,:,:]
#    

#    # attempt to model only one joint for now    
#    X = dat[:,:,jointID['WRIST_RIGHT']]

#    # Toy Data
#    # ========
#    alpha,psi = fio.toyExample_small()
#    alpha,psi = fio.toyExample_medium()
#    alpha,psi = fio.toyExample_medium_boostHighFreq()
#    alpha,psi = fio.toyExample_medium_1d()
#    alpha,psi = fio.toyExample_medium_1d_multicomp()
    alpha,psi = fio.toyExample_medium_3d_multicomp() 
#    alpha,psi = fio.toyExample_large_3d_multicomp()
    X = recon(alpha,projectPsi(psi,1.0))
    dispOriginal(alpha,psi)    

    # Apply Convolutional Sparse Coding. 
    # Length of AEB is set to 2 seconds (60 frames)    
    # D represents how many Action Units we want to capture
    #(alpha_recon,psi_recon) = csc_pgd(alpha,psi,X,M=(len(psi)),D=2,beta=0.05)
    (alpha_recon,psi_recon) = csc_pgd(X,M=64,D=2,beta=0.05)
    # Display the reconstructed values
    dispPlots(alpha_recon,psi_recon,X,'Final Data')
    pp.show()
    
if __name__ == '__main__':
    main()