import numpy as np
import matplotlib.pyplot as plt
import fileio as fio
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# TODO: change arguments to all lower case
class plotskeleton(object):
    #TODO
    # Initialize the visualization class
    def __init__(self,data,dataHeader,boneConnection,JointID1=1,\
    JointID2=9,startEndTime=[],skipframes=0):
        # startEndTime denotes the time (in millisec) from where the animation
        # starts and finishes. bx (boundary index) contains the same
        #  information as vector indices.
        if not startEndTime:
            self.bx = (0,len(data),1+skipframes)
        else:
            assert startEndTime[0]<startEndTime[1]
            self.bx = (np.argmax(data[:,1]>startEndTime[0]),\
            np.argmax(data[:,1]>startEndTime[1]),1+skipframes)
        # Joints to display in the two plots. Make sure they are tuple or list
        # not scalar
        if isinstance(JointID1,tuple) == False and \
            isinstance(JointID1,list) == False:
            self.jointID1 = (JointID1,)
        else:
            self.jointID1 = JointID1
        if isinstance(JointID2,tuple) == False and \
            isinstance(JointID2,list) == False:
            self.jointID2 = (JointID2,)
        else:
            self.jointID2 = JointID2
        # x,y, z positions of all the 20 joints and corresponding names
        self.x = data[:,2::3]
        self.xhead = dataHeader[2::3]
        self.y = data[:,3::3]
        self.yhead = dataHeader[3::3]        
        self.z = data[:,4::3]
        self.zhead = dataHeader[4::3]
         # Timestamp in millisec
        self.timeStamp = data[:,1]
        # Connection of bones
        self.boneStartIdx = boneConnection[:,0]   
        self.boneEndIdx = boneConnection[:,1]
        self.numBones = len(self.boneStartIdx)
        self.elev = 0
        self.azim = -90
        # Minimum and maximum of all the data columns
        self.minVals = np.min(data[self.bx[0]:self.bx[1],:],axis=0)
        self.maxVals = np.max(data[self.bx[0]:self.bx[1],:],axis=0)
        # Setup the figure and axes
        self.fig = plt.figure('Skeleton Plotter', figsize=(15, 10), dpi=80)
        self.ax = self.fig.add_axes([0,0,0.45,1], projection='3d')
        self.axplott1 = self.fig.add_axes([0.48,0.58,0.5,0.34])
        self.axplott2 = self.fig.add_axes([0.48,0.14,0.5,0.34])
        # Draw the 2D plot
        data1,legend1,data2,legend2 = self.prepDatToPlot()
        # Draw the 2d plots of joint positions
        self.axplott1.plot(self.timeStamp[self.bx[0]:self.bx[1]]/1000.0,data1)
        self.axplott1.axis('tight')
        self.axplott1.grid('on')
        self.axplott1.legend(legend1,prop={'size':8},bbox_to_anchor=\
        (0., 1.02, 1., .102), loc=3,ncol=6, mode="expand", borderaxespad=0.)
        self.axplott2.plot(self.timeStamp[self.bx[0]:self.bx[1]]/1000,data2)                               
        self.axplott2.axis('tight')
        self.axplott2.grid('on')
        self.axplott2.legend(legend2,prop={'size':8},bbox_to_anchor=\
        (0., 1.02, 1., .102), loc=3,ncol=6, mode="expand", borderaxespad=0.)
        # Start Animation
        self.ani = animation.FuncAnimation(self.fig, self.update,\
                    xrange(self.bx[0],self.bx[1],self.bx[2]),interval=5,\
                    init_func=self.setup_plot, blit=True)
    # This function will prepare the data and legend strings for plotting
    def prepDatToPlot(self):
        dat1 = np.zeros((self.bx[1]-self.bx[0],3*len(self.jointID1)))
        leg1 = ['LegText']*(3*len(self.jointID1))
        dat2 = np.zeros((self.bx[1]-self.bx[0],3*len(self.jointID2)))
        leg2 = ['LegText']*(3*len(self.jointID2))
        for idx in xrange(len(self.jointID1)):
            dat1[:,3*idx]=self.x[self.bx[0]:self.bx[1],self.jointID1[idx]]
            dat1[:,3*idx+1]=self.y[self.bx[0]:self.bx[1],self.jointID1[idx]]
            dat1[:,3*idx+2]=self.z[self.bx[0]:self.bx[1],self.jointID1[idx]]
            leg1[3*idx]=self.xhead[self.jointID1[idx]]
            leg1[3*idx+1]=self.yhead[self.jointID1[idx]]
            leg1[3*idx+2]=self.zhead[self.jointID1[idx]]
        for idx in xrange(len(self.jointID2)):
            dat2[:,3*idx]=self.x[self.bx[0]:self.bx[1],self.jointID2[idx]]
            dat2[:,3*idx+1]=self.y[self.bx[0]:self.bx[1],self.jointID2[idx]]
            dat2[:,3*idx+2]=self.z[self.bx[0]:self.bx[1],self.jointID2[idx]]
            leg2[3*idx]=self.xhead[self.jointID2[idx]]
            leg2[3*idx+1]=self.yhead[self.jointID2[idx]]
            leg2[3*idx+2]=self.zhead[self.jointID2[idx]]
        return dat1,leg1,dat2,leg2

    # The data is being plotted with the following convension. This
    # enables us to properly rotate the plot
    # X_component od data ---> x axis of plot
    # Y_component od data ---> z axis of plot
    # Z_component od data ---> y axis of plot
    def setup_plot(self):
        self.ax.grid(True)
        self.ax.tick_params(\
            axis='both',
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            left='off',
            right='off',
            labelbottom='off',
            labeltop='on',
            labelleft='on',
            labelright='off') # labels along the bottom edge are off
        # Draw the skeleton plots
        self.lines = [self.ax.plot([self.x[self.bx[0],start],\
        self.x[self.bx[0],end]],[self.z[self.bx[0],start],\
        self.z[self.bx[0],end]],zs=[self.y[self.bx[0],start],\
        self.y[self.bx[0],end]],animated=True)[0]\
                    for start,end in zip(self.boneStartIdx,self.boneEndIdx)]
        # Set up vertical lines as time marker
        yMinMax1=self.axplott1.get_ylim()
        yMinMax2=self.axplott2.get_ylim()
        self.marker1 = self.axplott1.plot([self.timeStamp[self.bx[0]]/1000.0,\
        self.timeStamp[self.bx[0]]/1000.0],yMinMax1,c='r',linewidth=2)[0]
        self.marker2 = self.axplott2.plot([self.timeStamp[self.bx[0]]/1000.0,\
        self.timeStamp[self.bx[0]]/1000.0],yMinMax2,c='r',linewidth=2)[0]
        # Set up viewing angle
        self.ax.view_init(elev=self.elev, azim=self.azim)
        # Set the x, y and z ranges of the skeleton plot
        self.ax.set_xlim3d(np.min(self.minVals[2::3]),\
            np.max(self.maxVals[2::3]))
        self.ax.set_ylim3d(np.min(self.minVals[4::3]),\
            np.max(self.maxVals[4::3]))
        self.ax.set_zlim3d(np.min(self.minVals[3::3]),\
            np.max(self.maxVals[3::3]))
        # These elements will be cleared
        todelete = self.lines[:]
        todelete.append(self.marker1)
        todelete.append(self.marker2)
        return (item for item in todelete)
    # The data is being plotted with the following convension. This
    # enables us to properly rotate the plot
    # X_component od data ---> x axis of plot
    # Y_component od data ---> z axis of plot
    # Z_component od data ---> y axis of plot
    def update(self, i):
        # Update the datapoints in the skeleton plot
        for idx,_ in enumerate(self.lines):
            self.lines[idx].set_data([self.x[i,self.boneStartIdx[idx]],\
                           self.x[i,self.boneEndIdx[idx]]],\
                          [self.z[i,self.boneStartIdx[idx]],\
                           self.z[i,self.boneEndIdx[idx]]])
            self.lines[idx].set_3d_properties([self.y[i,self.boneStartIdx[idx]],\
                                    self.y[i,self.boneEndIdx[idx]]])
        # Update the marker
        self.marker1.set_data([self.timeStamp[i]/1000.0,\
        self.timeStamp[i]/1000.0],self.axplott1.get_ylim())
        self.marker2.set_data([self.timeStamp[i]/1000.0,\
        self.timeStamp[i]/1000.0],self.axplott2.get_ylim())
        # Okay, draw now
        plt.draw()
        # These elements will be cleared
        todelete = self.lines[:]
        todelete.append(self.marker1)
        todelete.append(self.marker2)
        return (item for item in todelete)
    # Start the animated plot
    def show(self):
        plt.show()

# TODO: Implement it
def plotSubSkeleton(data,dataHeader,boneConnection,visibleJoints,JointID1=1,\
    JointID2=9,startEndTime=[],skipframes=0):
    pass

if __name__ == '__main__':
    data,dataHeader=fio.splitDataFile(*fio.readDataFile('Data/20.1.csv'))[0:2]
    boneConnection = fio.readSkeletalTree('Data/KinectSkeleton.tree')[1]
    a = plotskeleton(data,dataHeader,boneConnection,JointID2=(9,10),\
        skipframes=5,startEndTime=[5000,25000])
    a.show()