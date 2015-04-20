'''
Module to plot L curve from the results saved as mat file
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
import os
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt

#resultPath = 'Results/top1_test/'
resultPath = 'Results/top8_all/'

LplotDat = []
for root,folder,files in os.walk(resultPath):
    for afile in files:
        if afile.lower().endswith('.mat'):
            # create full filename and print
            fullPath = os.path.join(root,afile)
            print fullPath
            
            allDat = sio.loadmat(fullPath)
            LplotDat.append(np.concatenate((allDat['L0'],allDat['reconError'],\
            allDat['Beta'],allDat['logObj']),axis=1))
LplotDat = np.concatenate(LplotDat,axis=0)

plt.scatter(LplotDat[:,0],LplotDat[:,1])
ax=plt.gca()
for idx in xrange(len(LplotDat)):
    ax.annotate('Beta='+str(LplotDat[idx,2])+'\n'+'{:0.2e}'.format(LplotDat[idx,3])\
    ,(LplotDat[idx,0],LplotDat[idx,1]+np.mean(LplotDat[:,1])/2*np.random.rand()))
plt.xlabel('L0 norm of alpha')
plt.ylabel('Reconstruction Error')
plt.show()

