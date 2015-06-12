'''
Module for display skeleton animation. There is a provision for plotting
a selected number joint position over time.
TODO: Plot bone orientation, global angles etc.
TODO: Save a realtime movie out of the animation
TODO: Save publishable image sequences out of the animation
TODO: Deploy in internet
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
import numpy as np
import matplotlib.pyplot as plt
import fileio as fio
import scipy.io as sio
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import matplotlib.cm as cm

# # TODO: change arguments to all lower case. Camelcase is difficult to remember
# class plotskeleton(object):
#     #TODO: redesign
#     # Initialize the visualization class
#     def __init__(self,data,dataheader,boneconnection,jointid1=1,\
#     jointid2=9,startendtime=[],skipframes=0):
#         # startendtime denotes the time (in millisec) from where the animation
#         # starts and finishes. bx (boundary index) contains the same
#         #  information as vector indices.
#         if not startendtime:
#             self.bx = (0,len(data),1+skipframes)
#         else:
#             assert startendtime[0]<startendtime[1]
#             self.bx = (np.argmax(data[:,1]>startendtime[0]),\
#             np.argmax(data[:,1]>startendtime[1]),1+skipframes)
#         # Joints to display in the two plots. Make sure they are tuple or list
#         # not scalar
#         if isinstance(jointid1,tuple) == False and \
#             isinstance(jointid1,list) == False:
#             self.jointid1 = (jointid1,)
#         else:
#             self.jointid1 = jointid1
#         if isinstance(jointid2,tuple) == False and \
#             isinstance(jointid2,list) == False:
#             self.jointid2 = (jointid2,)
#         else:
#             self.jointid2 = jointid2
#         # x,y, z positions of all the 20 joints and corresponding names
#         # x axis mirroring for display
#         self.x = data[:,2::3]*-1
#         self.xhead = dataheader[2::3]
#         self.y = data[:,3::3]
#         self.yhead = dataheader[3::3]        
#         self.z = data[:,4::3]
#         self.zhead = dataheader[4::3]
#          # Timestamp in millisec
#         self.timeStamp = data[:,1]
#         # Connection of bones
#         self.boneStartIdx = boneconnection[:,0]   
#         self.boneEndIdx = boneconnection[:,1]
#         self.numBones = len(self.boneStartIdx)
#         self.elev = 0
#         self.azim = -90
#         # Minimum and maximum of all the data columns
#         self.minVals = np.min(data[self.bx[0]:self.bx[1],:],axis=0)
#         self.maxVals = np.max(data[self.bx[0]:self.bx[1],:],axis=0)
#         # Setup the figure and axes
#         self.fig = plt.figure('Skeleton Plotter', figsize=(15, 10), dpi=80)
#         self.ax = self.fig.add_axes([0,0,0.45,1], projection='3d')
#         self.axplott1 = self.fig.add_axes([0.48,0.58,0.5,0.34])
#         self.axplott2 = self.fig.add_axes([0.48,0.14,0.5,0.34])
#         # Draw the 2D plot
#         data1,legend1,data2,legend2 = self.prepDatToPlot()
#         # Draw the 2d plots of joint positions
#         self.axplott1.plot(self.timeStamp[self.bx[0]:self.bx[1]]/1000.0,data1)
#         self.axplott1.axis('tight')
#         self.axplott1.grid('on')
#         self.axplott1.legend(legend1,prop={'size':8},bbox_to_anchor=\
#         (0., 1.02, 1., .102), loc=3,ncol=6, mode="expand", borderaxespad=0.)
#         self.axplott2.plot(self.timeStamp[self.bx[0]:self.bx[1]]/1000,data2)                               
#         self.axplott2.axis('tight')
#         self.axplott2.grid('on')
#         self.axplott2.legend(legend2,prop={'size':8},bbox_to_anchor=\
#         (0., 1.02, 1., .102), loc=3,ncol=6, mode="expand", borderaxespad=0.)
#         # Start Animation
#         self.ani = animation.FuncAnimation(self.fig, self.update,\
#                     xrange(self.bx[0],self.bx[1],self.bx[2]),interval=5,\
#                     init_func=self.setup_plot, blit=False)
#     # This function will prepare the data and legend strings for plotting
#     def prepDatToPlot(self):
#         dat1 = np.zeros((self.bx[1]-self.bx[0],3*len(self.jointid1)))
#         leg1 = ['LegText']*(3*len(self.jointid1))
#         dat2 = np.zeros((self.bx[1]-self.bx[0],3*len(self.jointid2)))
#         leg2 = ['LegText']*(3*len(self.jointid2))
#         for idx in xrange(len(self.jointid1)):
#             dat1[:,3*idx]=self.x[self.bx[0]:self.bx[1],self.jointid1[idx]]
#             dat1[:,3*idx+1]=self.y[self.bx[0]:self.bx[1],self.jointid1[idx]]
#             dat1[:,3*idx+2]=self.z[self.bx[0]:self.bx[1],self.jointid1[idx]]
#             leg1[3*idx]=self.xhead[self.jointid1[idx]]
#             leg1[3*idx+1]=self.yhead[self.jointid1[idx]]
#             leg1[3*idx+2]=self.zhead[self.jointid1[idx]]
#         for idx in xrange(len(self.jointid2)):
#             dat2[:,3*idx]=self.x[self.bx[0]:self.bx[1],self.jointid2[idx]]
#             dat2[:,3*idx+1]=self.y[self.bx[0]:self.bx[1],self.jointid2[idx]]
#             dat2[:,3*idx+2]=self.z[self.bx[0]:self.bx[1],self.jointid2[idx]]
#             leg2[3*idx]=self.xhead[self.jointid2[idx]]
#             leg2[3*idx+1]=self.yhead[self.jointid2[idx]]
#             leg2[3*idx+2]=self.zhead[self.jointid2[idx]]
#         return dat1,leg1,dat2,leg2

#     # The data is being plotted with the following convension. This
#     # enables us to properly rotate the plot
#     # X_component od data ---> x axis of plot
#     # Y_component od data ---> z axis of plot
#     # Z_component od data ---> y axis of plot
#     def setup_plot(self):
#         self.ax.grid(True)
#         self.ax.tick_params(\
#             axis='both',
#             which='both',      # both major and minor ticks are affected
#             bottom='off',      # ticks along the bottom edge are off
#             top='off',         # ticks along the top edge are off
#             left='off',
#             right='off',
#             labelbottom='off',
#             labeltop='on',
#             labelleft='on',
#             labelright='off') # labels along the bottom edge are off
#         self.ax.set_animated=True
#         # Draw the skeleton plots
#         self.lines = [self.ax.plot([self.x[self.bx[0],start],\
#         self.x[self.bx[0],end]],[self.z[self.bx[0],start],\
#         self.z[self.bx[0],end]],zs=[self.y[self.bx[0],start],\
#         self.y[self.bx[0],end]],animated=True)[0]\
#                     for start,end in zip(self.boneStartIdx,self.boneEndIdx)]
#         # Set up vertical lines as time marker
#         yMinMax1=self.axplott1.get_ylim()
#         yMinMax2=self.axplott2.get_ylim()
#         self.marker1 = self.axplott1.plot([self.timeStamp[self.bx[0]]/1000.0,\
#         self.timeStamp[self.bx[0]]/1000.0],yMinMax1,c='r',linewidth=2)[0]
#         self.marker2 = self.axplott2.plot([self.timeStamp[self.bx[0]]/1000.0,\
#         self.timeStamp[self.bx[0]]/1000.0],yMinMax2,c='r',linewidth=2)[0]
#         # Set up viewing angle
#         self.ax.view_init(elev=self.elev, azim=self.azim)
#         # Set the x, y and z ranges of the skeleton plot
#         self.ax.set_xlim3d(np.min(self.minVals[2::3]),\
#             np.max(self.maxVals[2::3]))
#         self.ax.set_ylim3d(np.min(self.minVals[4::3]),\
#             np.max(self.maxVals[4::3]))
#         self.ax.set_zlim3d(np.min(self.minVals[3::3]),\
#             np.max(self.maxVals[3::3]))
#         # These elements will be cleared
#         todelete = self.lines[:]
#         todelete.append(self.marker1)
#         todelete.append(self.marker2)
#         return (item for item in todelete)
#     # The data is being plotted with the following convension. This
#     # enables us to properly rotate the plot
#     # X_component od data ---> x axis of plot
#     # Y_component od data ---> z axis of plot
#     # Z_component od data ---> y axis of plot
#     def update(self, i):
#         # Update the datapoints in the skeleton plot
#         for idx,_ in enumerate(self.lines):
#             self.lines[idx].set_data([self.x[i,self.boneStartIdx[idx]],\
#                            self.x[i,self.boneEndIdx[idx]]],\
#                           [self.z[i,self.boneStartIdx[idx]],\
#                            self.z[i,self.boneEndIdx[idx]]])
#             self.lines[idx].set_3d_properties([self.y[i,\
#             self.boneStartIdx[idx]],self.y[i,self.boneEndIdx[idx]]])   
#         plt.draw()
#         # Update the marker
#         self.marker1.set_data([self.timeStamp[i]/1000.0,\
#         self.timeStamp[i]/1000.0],self.axplott1.get_ylim())
#         self.marker2.set_data([self.timeStamp[i]/1000.0,\
#         self.timeStamp[i]/1000.0],self.axplott2.get_ylim())
#         # Okay, draw now
#         plt.draw()
#         # These elements will be cleared
#         todelete = self.lines[:]
#         todelete.append(self.marker1)
#         todelete.append(self.marker2)
#         return (item for item in todelete)
#     # Start the animated plot
#     def show(self):
#         plt.show()

# Helper Function: name each bone in terms of joints
def skelNames(dataheader,boneconnection):
    xhead = dataheader[2::3]
    jointname = [str(item.split('_')[0]) for item in xhead]
    # Names of the bones
    bonename = [jointname[item1]+'_'+jointname[item2] \
    for (item1,item2) in boneconnection]
    return jointname,bonename
    
# Plot only a single frame on axis ax
def plotsingleframe(ax,data,dataheader,boneconnection,azim,elev,boxon=True):
    # x,y,z coordinates of the joints. x axis mirroring for display
    x = data[:,2::3]*-1
    y = data[:,3::3]
    z = data[:,4::3]
    # Names of elements of skeleton
    jointname,bonename = skelNames(dataheader,boneconnection)
    uj = list(set(jointname))
    ub = list(set(bonename))
    # draw each bone in a unique color
    boneColorMap = cm.nipy_spectral(np.linspace(0,1,len(boneconnection)))
    for idx,(start,end) in enumerate(boneconnection):
        thisbonecolor = boneColorMap[ub.index(bonename[idx])]
        ax.plot([x[0,start],x[0,end]],[z[0,start],z[0,end]],\
        zs=[y[0,start],y[0,end]],linewidth=2,c=thisbonecolor)
    # Draw each joint in a unique color
    jointColorMap = cm.hsv(np.linspace(1,0,len(x.T)))
    for idx,(x_,y_,z_) in enumerate(zip(x.T,y.T,z.T)):
        thisjointcolor = jointColorMap[uj.index(jointname[idx])]
        if jointname[idx]=='HEAD':
            ax.scatter(x_,z_,y_,s=500,c=jointColorMap[6])
        else:
            ax.scatter(x_,z_,y_,s=30,c=thisjointcolor)
    __setaxis__(ax,azim,elev,boxon)
def __setaxis__(ax,azim,elev,boxon):
    # Setting up view related parameters
    ax.grid(False)
    ax.tick_params(\
        axis='both',
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        left='off',
        right='off',
        labelbottom='off',
        labeltop='off',
        labelleft='on',
        labelright='off') # labels along the bottom edge are off   
    ax.view_init(elev=elev, azim=azim)
    ax.set_aspect(5)
    plt.xlabel('azimuth = '+str(abs(azim)))
    if not boxon:
        ax.set_axis_off()
# Plot Multiple frames on axis ax
def plotmultiframe(ax,multidata,spacing,dataheader,boneconnection,azim,elev,boxon=True):
    # x,y,z coordinates of the joints. x axis mirroring for display
    for id,data in enumerate(multidata):
        data=data[None]
        x = data[:,2::3]*-1 + id*spacing
        y = data[:,3::3]
        z = data[:,4::3]
        # Names of elements of skeleton
        jointname,bonename = skelNames(dataheader,boneconnection)
        uj = list(set(jointname))
        ub = list(set(bonename))
        # draw each bone in a unique color
        boneColorMap = cm.nipy_spectral(np.linspace(0,1,len(boneconnection)))
        for idx,(start,end) in enumerate(boneconnection):
            thisbonecolor = boneColorMap[ub.index(bonename[idx])]
            ax.plot([x[0,start],x[0,end]],[z[0,start],z[0,end]],\
            zs=[y[0,start],y[0,end]],linewidth=2,c=thisbonecolor,alpha=(id+1.)/(len(multidata)+1))
        # Draw each joint in a unique color
        jointColorMap = cm.hsv(np.linspace(1,0,len(x.T)+1))
        for idx,(x_,y_,z_) in enumerate(zip(x.T,y.T,z.T)):
            thisjointcolor = jointColorMap[uj.index(jointname[idx])]
            if jointname[idx]=='HEAD':
                ax.scatter(x_,z_,y_,s=500,c=jointColorMap[6],alpha=(id+1.)/(len(multidata)+1))
            else:
                ax.scatter(x_,z_,y_,s=30,c=thisjointcolor,alpha=(id+1.)/(len(multidata)+1))
    # Setting up view related parameters
    __setaxis__(ax,azim,elev,boxon)
# Plot Multiple frames on axis ax with Selective Bone Highlight feature
def plotmultiframe_SBH(ax,multidata,spacing,dataheader,boneconnection,\
    azim,elev,highlightedBones,boxon=True,zspacing=False):
    # x,y,z coordinates of the joints. x axis mirroring for display
    for id,data in enumerate(multidata):
        data=data[None]
        x = data[:,2::3]*-1 + id*spacing
        y = data[:,3::3]
        if zspacing:
            z = data[:,4::3] + id*spacing*0.2
        else:
            z = data[:,4::3]
        # Names of elements of skeleton
        jointname,bonename = skelNames(dataheader,boneconnection)
        uj = list(set(jointname))
        ub = list(set(bonename))
        # draw each bone in a unique color
        boneColorMap = cm.bone(np.linspace(0,1,len(boneconnection)))
        for idx,(start,end) in enumerate(boneconnection):
            thisbonecolor = boneColorMap[ub.index(bonename[idx])]
            if bonename[idx] in highlightedBones:
                ax.plot([x[0,start],x[0,end]],[z[0,start],z[0,end]],\
                zs=[y[0,start],y[0,end]],linewidth=2,c=thisbonecolor,alpha=1.0)
            else:
                ax.plot([x[0,start],x[0,end]],[z[0,start],z[0,end]],\
                zs=[y[0,start],y[0,end]],linewidth=2,c=thisbonecolor,alpha=0.2)
        # Draw each joint in a unique color
        jointColorMap = cm.hsv(np.linspace(1,0,len(x.T)+1))
        for idx,(x_,y_,z_) in enumerate(zip(x.T,y.T,z.T)):
            thisjointcolor = jointColorMap[uj.index(jointname[idx])]
            if jointname[idx]=='HEAD':
                ax.scatter(x_,z_,y_,s=500,c=jointColorMap[6],alpha=0.2)
            else:
                ax.scatter(x_,z_,y_,s=30,c=thisjointcolor,alpha=0.2)
    # Setting up view related parameters
    __setaxis__(ax,azim,elev,boxon)        
# Plot only a single frame on axis ax
def plotsingleframe_multiangle(data,dataheader,boneconnection,azims,elev,\
                                figurename='multiangle plot',boxon=True):
    N = len(azims)+2
    fig = plt.figure(figurename)
    for i,angl in enumerate(azims):
        ax = fig.add_axes([(i+1)*1./N,0,1./N,1], projection='3d')
        plotsingleframe(ax,data,dataheader,boneconnection,angl,elev,boxon)
    plt.show()

# This function is used when there is no frame or timestamp associated with
# the joint movement data. It constructs the animation data with the assumption
# of a specific framerate and displays it. Alternatively it is possible to
# return the data instead of displaying it
# Framerate is in frames per second
def plotJointsOnly(X,framerate=30,noShow=False):
    N,D = np.shape(X)
    framestep = 1000/framerate # milliseconds per frame    
    # Prepare data
    dataheader=fio.splitcsvfile(*fio.readdatafile('Data/10.1.csv'))[1]
    boneconnection = fio.readskeletaltree('Data/KinectSkeleton.tree')[1]
    data = np.zeros((N,D+2))
    data[:,2:] = X
    data[:,0] = range(N)
    data[:,1] = data[:,0]*framestep
    if not noShow:
        # Plot skeleton
        gui = plotskeleton(data,dataheader,boneconnection)
        gui.show()
    else:
        return data
############################## Test Modules ####################################        
# Reads a file and plots it
def unittest1():
    data,dataheader=fio.splitcsvfile(*fio.readdatafile('Data/20.1.csv'))[0:2]
    boneconnection = fio.readskeletaltree('Data/KinectSkeleton.tree')[1]
    a = plotskeleton(data,dataheader,boneconnection,jointid2=(9,10),\
        skipframes=5,startendtime=[5000,25000])
    a.show()
# Visualizes the results
def unittest2(filename):
    framerate = 6
    # Read result file
    allData = sio.loadmat(filename)
    # Print nonzero component indices
    sumAlpha = np.sum(allData['alpha_recon'],axis=0)
    validIdx = np.nonzero(sumAlpha)
    while True:
        print 'Available nonzero components are:'
        for ind in validIdx:
            print ind,
        print
    #    print 'sum of alpha for these components are:'    
    #    for sumAlpha in sumAlpha[validIdx]:
    #        print '{:0.2}'.format(sumAlpha),
    #    print
        component = input('which component do you want to see?')
        # Visualize
        plt.clf()
        plt.plot(allData['alpha_recon'][:,component])
        plt.xlabel('frame')
        plt.ylabel('alpha')
        # Show the animation    
        X = allData['psi_recon'][:,:,component]
        plotJointsOnly(X,framerate)
        plt.clf()
# Load mean skeleton and draw publishable plot from three different angles
def unittest3(meanfile,boxon1=True):
    data = sio.loadmat(meanfile)
    boneconnection = fio.readskeletaltree('Data/KinectSkeleton.tree')[1]
    plotsingleframe_multiangle(data['avgSkel'],data['header'],boneconnection,\
            azims=[-45,-90,-135],elev=5,figurename='Average Pose',boxon=boxon1)
# Load a component from the result and draw publishable plot illustrating
# the action
def unittest4(filename, actionidx):
    allData = sio.loadmat(filename)
    boneconnection = fio.readskeletaltree('Data/KinectSkeleton.tree')[1]
    header = [str(head.strip()) for head in allData['Header']]
    data = fio.calcinvarient(plotJointsOnly(allData['psi_recon'][:,:,actionidx],\
    framerate=30/allData['decimateratio'],noShow=True),header)
    N = len(data)
    fig = plt.figure('Action')
    fig.set_facecolor('white')
    for i,adata in enumerate(data):
        ax = fig.add_axes([i*1./N,0,1./N,1], projection='3d')
        plotsingleframe(ax,adata[None],allData['Header'],boneconnection,-90,5,False)
    plt.show()
# Load a component from the result and draw publishable plot illustrating
# the action. In another format    
def unittest5(filename, actionidx):
    allData = sio.loadmat(filename)
    boneconnection = fio.readskeletaltree('Data/KinectSkeleton.tree')[1]
    header = [str(head.strip()) for head in allData['Header']]
    data = fio.calcinvarient(plotJointsOnly(allData['psi_recon'][:,:,actionidx],\
    framerate=30/allData['decimateratio'],noShow=True),header)
    fig = plt.figure('Action')
    ax = fig.add_subplot(111, projection='3d')
    plotmultiframe(ax,data,4,allData['Header'],boneconnection,-100,5,False)
    plt.show()
# Load a component from the result and draw publishable plot illustrating
# the action. Utilize bone highlight feature
def unittest6(filename, actionidx,azim,elev,highlightedBones=[\
    'SHOULDER_ELBOW','ELBOW_WRIST','WRIST_HAND'],space=4,boxon=False,zspacing=False):
    allData = sio.loadmat(filename)
    boneconnection = fio.readskeletaltree('Data/KinectSkeleton.tree')[1]
    header = [str(head.strip()) for head in allData['Header']]
    data = fio.calcinvarient(plotJointsOnly(allData['psi_recon'][:,:,actionidx],\
    framerate=30/allData['decimateratio'],noShow=True),header)
    fig = plt.figure('Action')
    ax = fig.add_subplot(111, projection='3d')
    plotmultiframe_SBH(ax,data,space,allData['Header'],boneconnection,azim,\
    elev,highlightedBones,boxon,zspacing)
    plt.show()    
if __name__ == '__main__':
    #unittest1()
    #unittest2('Results/result_3__M=64_D=16_beta=0.055_04_58_38.mat')
    unittest3('Data/meanSkel.mat',True)    
    #unittest4('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',1)
    #unittest5('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',1)
    #unittest6('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',1,-97,5)
    #unittest6('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',3,-90,25)    
    #unittest6('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',\
    #5,-85,-160,highlightedBones=['HIP_KNEE','KNEE_ANKLE','ANKLE_FOOT'],space=10,zspacing = False)    
    #unittest6('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',\
    #7,94,178,space=8,highlightedBones=['HIP_KNEE','KNEE_ANKLE','ANKLE_FOOT','SHOULDER_ELBOW','ELBOW_WRIST'],boxon=False)
    #unittest6('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',\
    #8,-85,-158,space=4)
    #unittest6('Results/top8_all/result_M=8_D=12_beta=4.5e-07_ALL_20_42_35.mat',\
    #11,87,2,space=3,highlightedBones=['HIP_KNEE','KNEE_ANKLE','ANKLE_FOOT'],boxon=False)

