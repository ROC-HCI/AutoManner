from mayavi import mlab
import numpy as np
from math import sqrt

# Bone-Joint coordinate calculator
def __joints(datarow,jointList):
    return ([datarow[2+j*3] for j in jointList],\
    [datarow[3+j*3] for j in jointList],[datarow[4+j*3] for j in jointList])

# Animates a skeleton based on data (output of splitcsvfile in fileio.py).
# Expects multiple rows
def animateSkeleton(data,delay=50,azim=0,elev=180,ro=0):
    m,n = np.shape(data)
    if n == 60:
        timcols = np.zeros((m,2))
        timcols[:,0]=np.arange(float(m))
        timcols[:,1]=timcols[:,0]*30
        data = np.concatenate((timcols,data),axis=1)
    # Draw a single skeleton first
    skeljoints,skelbone = drawskel(data[0,:],azim=0,elev=180,ro=0,showIt=False)
    # Make the skeleton move
    @mlab.show
    @mlab.animate(delay=delay)
    def anim():
        while True:
            for frno,aframe in enumerate(data):
                f=mlab.gcf()
                f.scene.disable_render=True
                # Change the Joint coordinates
                skeljoints.mlab_source.set(x=aframe[2::3],y=aframe[3::3],\
                    z=aframe[4::3])
                # Change the joint coordinates of the bones
                currentjoints = [__joints(aframe,range(0,4)),\
                                 __joints(aframe,[2]+range(4,8)),\
                                 __joints(aframe,[2]+range(8,12)),\
                                 __joints(aframe,[0]+range(12,16)),\
                                 __joints(aframe,[0]+range(16,19))]
                for i in range(5):
                    skelbone[i].mlab_source.set(x=currentjoints[i][0],\
                                                y=currentjoints[i][1],\
                                                z=currentjoints[i][2])
                f.scene.disable_render=False
                yield
    # Start Animation
    anim()

# Draws a single skeleton. Expects a single row of data (fileio.py)
def drawskel(rowdata,azim=0,elev=180,ro=0,showIt=True):
    # calculate distance from spine to sholder. The joints and bones radii 
    # will be scaled based on this
    x,y,z = __joints(rowdata,[1,2])
    dist = sqrt((x[0]-x[1])**2. + (y[0]-y[1])**2. + (z[0]-z[1])**2.)/0.36
    # Relative sizes of the joints
    jointSizes = np.array([0.09,0.1,0.1,0.2,0.1,0.1,0.08,0.08,0.1,0.1,0.08,\
                            0.08,0.1,0.1,0.1,0.09,0.1,0.1,0.1,0.09])*dist
    # Draw Joints
    skeljoints = mlab.points3d(rowdata[2::3],rowdata[3::3],rowdata[4::3],\
        jointSizes,scale_factor=1,resolution=16)
    # Draw Bones
    skelbone = [mlab.plot3d(*__joints(rowdata,range(0,4)),tube_radius=dist*0.01),\
    mlab.plot3d(*__joints(rowdata,[2]+range(4,8)),tube_radius=dist*0.01),\
    mlab.plot3d(*__joints(rowdata,[2]+range(8,12)),tube_radius=dist*0.01),\
    mlab.plot3d(*__joints(rowdata,[0]+range(12,16)),tube_radius=dist*0.01),\
    mlab.plot3d(*__joints(rowdata,[0]+range(16,19)),tube_radius=dist*0.01)]
    # Set the view
    mlab.view(azimuth=azim,elevation=elev,roll=ro)
    mlab.orientation_axes()
    if showIt:
        mlab.show()
    return skeljoints,skelbone

############################## Test Modules ####################################
# project on principal component space, then backproject and animate
def unitTest1(datafile='Data/13.3.csv'):
    import fileio as fio
    data,header=fio.readdatafile(datafile)
    x_proj,eigvec,x_mean = fio.txfmdata(data)
    animateSkeleton(x_proj.dot(eigvec.T)+x_mean)

def main():
    import fileio as fio
    import sys
    print sys.argv[1]
    data = fio.preprocess(sys.argv[1])[0]
    animateSkeleton(data)


if __name__ == '__main__':
    main()
