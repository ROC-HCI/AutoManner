# -*- coding: utf-8 -*-
"""
Created on Sun May 24 00:32:12 2015

@author: itanveer
"""

import fileio as fio
from skelplot_mayavi import * 
import numpy as np
from sklearn.decomposition import PCA

# Foot_left = 15 and Foot_Right = 19 
def makeTranslationInvariant(data):
    # Origin is set to the average of left and right foot
    ref_x,ref_y,ref_z = (data[:,2+15*3] + data[:,2+19*3])/2.,\
                        (data[:,3+15*3] + data[:,3+19*3])/2.,\
                        (data[:,4+15*3] + data[:,4+19*3])/2.
    data[:,2::3] = data[:,2::3] - ref_x[None].T # x component
    data[:,3::3] = data[:,3::3] - ref_y[None].T # y component
    data[:,4::3] = data[:,4::3] - ref_z[None].T # z component    
    return data
    
data,dataheader=fio.splitcsvfile(*fio.readdatafile('Data/14.3.csv'))[0:2]
data = makeTranslationInvariant(data)
meandata = np.mean(data,axis=0)
# Apply Principal Component Analysis
pca = PCA(n_components=3)
pca = pca.fit(data)
movement = np.sin(np.arange(-np.pi,np.pi,0.1))[None].T*pca.components_[2][None]
animateSkeleton(meandata + movement)
#drawskel(meandata)
#animateSkeleton(data)