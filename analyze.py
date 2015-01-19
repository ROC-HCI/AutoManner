import numpy as np
import scipy.signal as sg
import scipy.io as sio
import fileio as fio
import matplotlib.pyplot as pp

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
    for j in xrange(szAlpha[1]):
        for i in xrange(szPsi[1]):
            convRes[:,i,j] = np.convolve(alpha[:,j],psi[:,i,j],'same')
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

def calcP(X,alpha,psi):
    L = recon(alpha,psi)
    return (0.5*np.sum((X-L)**2.))

# TODO: Check it carefully    
def calcObjf(X,alpha,psi,beta):
    L = recon(alpha,psi)
    return (0.5*np.sum((X-L)**2.) + beta*np.sum(np.abs(alpha)))

# X_,L_,alpha_ are of X(:,:,i), L(:,:,i) and alpha(:,i)
def loglike(X,alpha,psi,beta):
    return np.log(calcObjf(X,alpha,psi,beta))
    #return (0.5*np.sum((X-L)**2.))

# Manually Checked with sample data -- Working as indended
# Grad of P wrt alpha is sum((X(t)-L(t))psi(t-t'))
# Returns an NxD tensor representing gradient of P with respect to psi
def calcGrad_alpha(alpha,psi,lxDiff):
    N,D = np.shape(alpha)
    M,K,_ = np.shape(psi)
    #gradL_alpha = buildToeplitz_alpha(psi,N) # NxNxDxK tensor
    gradP_alpha = np.zeros((N,D,K))
    for d in xrange(D):
        for k in xrange(K):
            # this is actually a correlation operation. Notice that 
            # psi is actually flipped
            gradP_alpha[:,d,k] = \
            sg.fftconvolve(lxDiff[:,k],psi[::-1,k,d],'full')[(M-1):]
    gradP_alpha = np.sum(gradP_alpha,axis=2)/K  # Should we really avg?
    return gradP_alpha

# Manually Checked with sample data -- Working as indended
# Grad of P wrt psi is sum((X(t)-L(t))alpha(t-t'))
# Returns an MxKxD tensor representing gradient of P with respect to psi
def calcGrad_psi(alpha,psi,lxDiff):
    N,D = np.shape(alpha)
    M,K,_ = np.shape(psi)
    gradP_psi = np.zeros((M,K,D))
    for d in xrange(D):    
        for k in xrange(K):
            # this is actually a correlation operation. Notice that 
            # alpha is actually flipped
            gradP_psi[:,k,d] = \
            sg.fftconvolve(lxDiff[:,k],alpha[::-1,d],'full')[(N-1):(N+M-1)] 
    return gradP_psi
    
# Randomly initialize alpha and psi
# alpha is N x D (axis-0:time/frame, axis-1: various AEB)
# alpha represents sparse coefficient for various AEB's
# psi is M x K x D (axis-1: x, y and z components of AEB)
# psi represents all the AEBs (D number of them)
# M is a scalar integer representing time/frame length for AEB 
def csc_init(M,N,K,D):
    psi = normalizePsi(np.random.randn(M,K,D))
    alpha = np.zeros((N,D))
    #alpha = np.random.randn(N,D)
    return psi,alpha

#Normalize psi    
def normalizePsi(psi):
    M,K,D = np.shape(psi)
#    for d in xrange(D):
#        for k in xrange(K):
#            psiNorm = np.linalg.norm(psi[:,k,d])
#            if psiNorm !=0:
#                psi[:,k,d] = psi[:,k,d]/psiNorm
    psiNorm = np.linalg.norm(psi)
    if (psiNorm!=0):
        psi = psi/psiNorm
    return psi

# Apply Proximal/Shrinkage operation
def shrink(operateOn, threshold):
        idx_z = np.where(np.abs(operateOn)<=threshold)
        idx_nz = np.where(np.abs(operateOn)>threshold)
        operateOn[idx_z] = 0.
        operateOn[idx_nz] -= threshold*np.sign(operateOn[idx_nz])
        return operateOn

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
        pp.stem(gralpha[:,d])
        pp.title('Gradf wrt alpha')
        pp.draw()
        pp.pause(0.1)
    
# Plots alpha, psi, original and reconstructed data
def dispPlots(alpha,psi,X,figureName):
    _,D = np.shape(alpha)
    for d in xrange(D):
        pp.figure(figureName + ' for component # '+'{:0}'.format(d))
        pp.clf()    
        pp.subplot(411)
        pp.plot(X)
        pp.title('Original Data')        
        pp.subplot(412)
        L = recon(alpha,psi)
        pp.plot(L)
        pp.title('Reconstructed Data')    
        pp.subplot(413)
        pp.plot(psi[:,:,d])
        pp.title('psi')
        pp.subplot(414)
        pp.stem(alpha[:,d])
        pp.title('alpha')
        pp.draw()
        pp.pause(0.1)

# Applies Convolutional Sparse Coding with Proximal Gradient Descent Algorithm    
# X is N x K data tensor for only one joint 
# M is a scalar integer representing time/frame length for AEB     
# D represents how many AEB we want to capture
# beta is the weight for sparcity constraint
def csc_pgd(X,M,D,beta,iter_thresh=250,thresh = 1e-4):
    iter = 0
    N,K = np.shape(X)
    psi,alpha = csc_init(M,N,K,D)    # Random initialization
        
    factor = 0.5
    prevlikeli = loglike(X,alpha,psi,beta)
    maxDeltaLikeli = 0
    countZero = 0
    while iter < iter_thresh:

        # No Line search: Linear decrease of learning rate
#        gamma = 0.001/(iter+1)        
#        # Update alpha
#        L = recon(alpha,psi)        
#        lxDiff = L - X        
#        gralpha = calcGrad_alpha(alpha,psi,lxDiff)        
#        alpha = alpha - gamma*gralpha        
#        alpha = shrink(alpha,beta*gamma)      # Shrinkage
#        
#        # Update psi
#        L = recon(alpha,psi)        
#        lxDiff = L - X
#        grpsi = calcGrad_psi(alpha,psi,lxDiff)
#        psi = normalizePsi(psi - gamma*grpsi)
               

        # Update psi and alpha with line search        
        # Update psi
        gamma_psi = 100.0
        L = recon(alpha,psi)
        lxDiff = L - X
        grpsi = calcGrad_psi(alpha,psi,lxDiff)
        oldObj = calcObjf(X,alpha,psi,beta)
        while gamma_psi > (1e-3/(iter+1)):        
            newPsi = psi - gamma_psi*grpsi
            if calcObjf(X,alpha,newPsi,beta) >= oldObj:
                gamma_psi *= factor
            else:
                break        
        psi = normalizePsi(psi - gamma_psi*grpsi)   # Normalize
        # Update alpha
        gamma_alpha = 100.0
        L = recon(alpha,psi)
        lxDiff = L - X
        gralpha = calcGrad_alpha(alpha,psi,lxDiff)
        oldObj = calcObjf(X,alpha,psi,beta)
        while gamma_alpha > (1e-3/(iter+1)):        
            newAlpha = alpha - gamma_alpha*gralpha
            if calcObjf(X,newAlpha,psi,beta) >= oldObj:
                gamma_alpha *= factor
            else:
                break
        alpha = shrink(newAlpha,gamma_alpha*beta)   # Shrinkage
        # Count
        iter += 1
        
        # Display        
        likeli = loglike(X,alpha,psi,beta)
        valP = calcP(X,alpha,psi)
        # Display alpha, psi, X and L
        dispPlots(alpha,psi,X,'Iteration Data')
        # Display Gradiants
        dispGrads(gralpha,grpsi)
        # Display Log Likelihood
        pp.figure('Log likelihood plot')
        pp.scatter(iter,likeli,c = 'b')
        pp.title('Likelihood Plot for Beta = ' + '{:0.2f}'.format(beta))
        pp.draw()
        pp.pause(0.05)
        
        # Print status. Sparsity ratio is the percentage of error coming from
        # sparsity
        print 'Gamma_alpha = ', '{:.4e}'.format(gamma_alpha),\
        ' Gamma_psi = ', '{:.4e}'.format(gamma_psi),\
        ' Sparsity Ratio = ', '{:.2e}%'.format((np.exp(likeli) - valP)/np.exp(likeli)*100),\
        ' likeli = ', '{:.2f}'.format(likeli), \
        ' delta = ', '{:.2e}'.format(prevlikeli - likeli), \
        '({:.2f}%)'.format((prevlikeli - likeli)/maxDeltaLikeli*100)
        # terminate loop
        allowZero_number = 30
        maxDeltaLikeli = max(maxDeltaLikeli,abs(prevlikeli - likeli))
        if (prevlikeli - likeli)<1e-5:#*maxDeltaLikeli:
            if (prevlikeli - likeli) <1e-5 and countZero < allowZero_number:
                countZero += 1
            elif (prevlikeli - likeli) <1e-5 and countZero >= allowZero_number:
                break
            print countZero
        else:
            prevlikeli = likeli
        
        if abs(likeli - 1.0) < 0.1:
            break
    return alpha,psi
        
def main():
#    # read joint names and data file
#    jointID = fio.readPointDic('Data/pointDef.dic')    
#    #dat,timeIndx,_ = readDataFile('Data/','.csv',joints=(\
#    # jointID['ELBOW_RIGHT'],jointID['WRIST_RIGHT']),preprocess=True)
#    #dat,boundDic = fio.readAllFiles('Data/','.csv',preprocess=True)
#    #sio.savemat('Data/jointInfo.mat',{'dat':dat})
#    dat = sio.loadmat('Data/jointInfo.mat')['dat']
#    
#    #TODO: Delete this line. For debug only
#    dat = dat[:500,:,:]
#    
#    # apply Shift Invariant Sparse Coding. 
#    # Length of AEB is set to 2 seconds (60 frames)
#     # attempt to model only one joint for now    
#    X = dat[:,:,jointID['WRIST_RIGHT']]
    #alpha,psi = fio.toyExample_large()
    alpha,psi = fio.toyExample_medium()
    #alpha,psi = fio.toyExample_small()
    
    # Display original data
    X = recon(alpha,psi)
    pp.figure('Original alpha, psi and Data')
    pp.clf()
    pp.subplot(311)
    for i in xrange(3):
        pp.plot(X[:,i])
    pp.title('X')    
    pp.subplot(312)
    for i in xrange(3):
        pp.plot(psi[:,i])
    pp.title('psi')
    pp.subplot(313)
    pp.stem(alpha)
    pp.title('alpha')
    
    pp.draw()
    pp.pause(0.1)
    # D represents how many AEB we want to capture
    D = 1
    (alpha_recon,psi_recon) = csc_pgd(X,M=(len(psi)),D=D,beta=0.03)
    
    # Display the reconstructed values
    dispPlots(alpha_recon,psi_recon,X,'Final Data')
    pp.show()
    
    
if __name__ == '__main__':
    main()