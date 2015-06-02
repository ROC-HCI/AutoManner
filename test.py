# -*- coding: utf-8 -*-
"""
Created on Sun May 24 00:32:12 2015

@author: itanveer
"""

import fileio as fio
from skelplot_mayavi import * 
import numpy as np
import sisc_optimizer as sisc

# Foot_left = 15 and Foot_Right = 19 
def makeTranslationInvariant(data):
    # Origin is set to the average of left and right foot
    ref_x,ref_y,ref_z = ((data[:,2+15*3] + data[:,2+19*3])/2.)[None].T,\
                        ((data[:,3+15*3] + data[:,3+19*3])/2.)[None].T,\
                        ((data[:,4+15*3] + data[:,4+19*3])/2)[None].T
    data[:,2::3] = data[:,2::3] - ref_x # x component
    data[:,3::3] = data[:,3::3] - ref_y # y component
    data[:,4::3] = data[:,4::3] - ref_z # z component    
    return data, np.concatenate((ref_x,ref_y,ref_z),axis=1)
    
data,dataheader=fio.splitcsvfile(*fio.readdatafile('Data/13.3.csv'))[0:2]
data,ref = makeTranslationInvariant(data)
meandata = np.mean(data,axis=0)
animateSkeleton(data)
# # Apply Principal Component Analysis
# #pca = PCA(n_components=3)
# #pca = pca.fit(data)
# #movement = np.sin(np.arange(-np.pi,np.pi,0.1))[None].T*pca.components_[2][None]
# #animateSkeleton(meandata + movement)
# #drawskel(meandata)
# #animateSkeleton(data)

# # Reformat the data (pad)
# X = fio.getjointdata(data,range(20))
# numZeros = (nextpow2(len(X))-len(X))
# X = np.pad(X,((0,numZeros),(0,0)),'constant',constant_values=0)

# # Apply SISC
# alpha_recon,psi_recon,logObj,reconError,L0 = sisc.optimize_proxim(X,M=60,D=12,)


