import numpy as np
import matplotlib.pyplot as plt
import fileio as fio
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

class AnimatedScatter(object):
    def __init__(self,data,orientDat):
        self.x = data[:,2::3]
        self.y = data[:,3::3]
        self.z = data[:,4::3]
        self.boneStartIdx = orientDat[0,0::8][1:]
        self.boneEndIdx = orientDat[0,1::8][1:]
        self.numBones = len(self.boneStartIdx)
        self.elev = 0
        self.azim = -90
        self.minVals = np.min(data,axis=0)
        self.maxVals = np.max(data,axis=0)
        # Setup the figure and axes
        self.fig = plt.figure(figsize=(15, 10), dpi=80)
        self.ax = self.fig.add_axes([0,0.15,0.45,0.85], projection='3d')
        self.axplott1 = self.fig.add_axes([0.48,0.6,0.5,0.34])
        self.axplott2 = self.fig.add_axes([0.48,0.2,0.5,0.34])
        self.ani = animation.FuncAnimation(self.fig, self.update, len(data),\
            interval=5,init_func=self.setup_plot, blit=True)

    def change_angle(self):
        self.azim = (self.azim + 0.1)%360

    # The data is being plotted with the following convension. This
    # enables us to properly rotate the plot
    # X_component od data ---> x axis of plot
    # Y_component od data ---> z axis of plot
    # Z_component od data ---> y axis of plot
    def setup_plot(self):
        self.ax.grid(False)
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
        # Draw the plots and set the viewing angle
        #self.scat = self.ax.scatter(self.x[0,:],self.z[0,:],self.y[0,:],\
        #    animated=True)
        self.lines = [self.ax.plot([self.x[0,start],self.x[0,end]],\
                               [self.z[0,start],self.z[0,end]],\
                               zs=[self.y[0,start],self.y[0,end]],\
                               animated=True)[0]\
                    for start,end in zip(self.boneStartIdx,self.boneEndIdx)]
        self.ax.view_init(elev=self.elev, azim=self.azim)
        # Set the x,y and z limits of the plot
        self.ax.set_xlim3d(np.min(self.minVals[2::3]),\
            np.max(self.maxVals[2::3]))
        self.ax.set_ylim3d(np.min(self.minVals[4::3]),\
            np.max(self.maxVals[4::3]))
        self.ax.set_zlim3d(np.min(self.minVals[3::3]),\
            np.max(self.maxVals[3::3]))
        temp = self.lines[:]
        #temp.append(self.scat)
        return (item for item in temp)

    # The data is being plotted with the following convension. This
    # enables us to properly rotate the plot
    # X_component od data ---> x axis of plot
    # Y_component od data ---> z axis of plot
    # Z_component od data ---> y axis of plot
    def update(self, i):
        # Update the datapoints
        #self.scat._offsets3d = (self.x[i,:],self.z[i,:],self.y[i,:])
        for idx,_ in enumerate(self.lines):
            self.lines[idx].set_data([self.x[i,self.boneStartIdx[idx]],\
                           self.x[i,self.boneEndIdx[idx]]],\
                          [self.z[i,self.boneStartIdx[idx]],\
                           self.z[i,self.boneEndIdx[idx]]])
            #self.lines[idx].set_c(colors_[idx%5])
            self.lines[idx].set_3d_properties([self.y[i,self.boneStartIdx[idx]],\
                                    self.y[i,self.boneEndIdx[idx]]])
        self.ax.view_init(self.elev,self.azim)
        
        plt.draw()
        temp = self.lines[:]
        #temp.append(self.scat)
        return (item for item in temp)

    def show(self):
        plt.show()
    
if __name__ == '__main__':
    data,_,orient,orientHead,_,_ = fio.readDataFile('Data/test_Data.csv')    
    a = AnimatedScatter(data,orient)
    a.show()