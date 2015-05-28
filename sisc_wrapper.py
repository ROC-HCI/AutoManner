''' Human Behavior Analysis Module
    ==============================
    This program extracts Behavioral Action Units (BAU's) using 
    Shift Invariant Sparse Coding. This module is the main extrance point.
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
from argparse import ArgumentParser
from sisc_optimizer import *
import scipy.io as sio
import fileio as fio
import time
##################################
####### NEEDS REFACTORING ########
##################################
##################################
######### NEEDS Debuging #########
##################################

################################# Main Helper #################################
def buildArg():
    args = ArgumentParser(description="Automatic Extraction of Human Behavior")

    args.add_argument('-i',nargs='?',default='Data/all_skeletal_Data.mat',\
    metavar='INPUT_MAT_FILENAME',\
    help='A mat file containing all the data concatenated into matrix. \
    or a list of csv files from where the data has to be read\
    (default: %(default)s)')
    
    args.add_argument('-o',nargs='?',default='Results/result',\
    metavar='OUTPUT_FILE_PATH_AND_PREFIX',\
    help='Path and any prefix of the generated output mat files. \
    (default: %(default)s)')
    
    args.add_argument('-p',nargs='?',type=int,default=4,\
    metavar='Num_Parallel',\
    help='Total number of parallel processes to be used. \
    (default: %(default)s)')

    args.add_argument('-toy',nargs='?',type=int,\
    choices=range(1,8),metavar='TOY_DATA_ID',\
    help='This will override the INPUT_MAT_FILENAME with synthetic toy data.\
    The ID refers different preset synthetic data. \
    Must be chosen from the following: %(choices)s')    
    
    args.add_argument('-skelTree',nargs='?',default=\
    'Data/KinectSkeleton.tree',metavar='SKELETON_TREE_FILENAME',\
    help='A .tree file containing kinect skeleton tree (default: %(default)s)')

    args.add_argument('-iter_thresh',nargs='?',type=int,default=65536,\
    metavar='ITERATION_THRESHOLD',\
    help='Threshold of iteration (termination criteria) (default:%(default)s)')
    
    args.add_argument('-diff_thresh',nargs='?',type=float,default=1e-5,\
    metavar='DIFFERENCE_THRESHOLD',\
    help='Threshold of difference in log objective function\
    (termination criteria) (default:%(default)s)')
    
    args.add_argument('-M',nargs='?',type=int,default=-2,\
    metavar='ATOM_LENGTH',\
    help='The length of atomic units (psi). IOW, the size of each \
    element of the dictionary. Must be a power of 2. (default: %(default)s)\
    A negative number indicates the system will automatically choose a\
    length which is approximately equvalent to abs(M) sec. Does not have\
    any effect on toy data')
    
    args.add_argument('-D',nargs='?',type=int,default=16,\
    metavar='DICTIONARY_LENGTH',\
    help='The total number of atomic units (psi). In Other Words, the total\
    number of elements in the dictionary (default: %(default)s). Does not have\
    any effect on toy data')
    
    args.add_argument('-Beta',nargs='?',type=float,default=3e-5,\
    metavar='NON-SPARSITY_COST',\
    help='Represents the cost of nonsparsity. The higer the cost, the \
    sparser the occurances of the dictionary elements.')
    
    args.add_argument('--Disp',dest='Disp', action='store_true',\
    default=False,help='Turns on displays relevant for Toy data.\
    Shows Original Data + Final Results. It is not applicable for data input\
    from mat. Does not slow down much.')
        
    args.add_argument('--DispObj',dest='Disp_Obj', action='store_true',\
    default=False,help='Turns on log of objective function plot. Hugely slows\
    down the algorithm.')
    
    args.add_argument('--DispGrad',dest='Disp_Gradiants', action='store_true',\
    default=False,help='Turns on the gradient plots. Mainly used for\
    debuging. Hugely slows down the algorithm.')
    
    args.add_argument('--DispIter',dest='Disp_Iterations',action='store_true',\
    default=False,help='Turns on the plots in each iteration. Mainly used for\
    debuging. Hugely slows down the algorithm.')
    return args
################################## Unit Test ##################################
def toyTest(dataID,D=2,M=64,beta=0.05,disp=True,dispObj=False,dispGrad=False,\
                                            dispIteration=False,totWorker=4):
#   Synthetic Toy Data
    if dataID==1:
        D=1
        alpha,psi = fio.toyExample_medium()
    elif dataID==2:
        D=1
        alpha,psi = fio.toyExample_medium_boostHighFreq()
    elif dataID==3:
        D=1
        alpha,psi = fio.toyExample_medium_boostHighFreq()
    elif dataID==4:
        D=1
        alpha,psi = fio.toyExample_medium_1d()
    elif dataID==5:
        alpha,psi = fio.toyExample_medium_1d_multicomp()
    elif dataID==6:
        alpha,psi = fio.toyExample_medium_3d_multicomp() 
    elif dataID==7:
        alpha,psi = fio.toyExample_large_3d_multicomp()    
    p = Pool(totWorker)
    # Construct the data            
    X = recon(alpha,projectPsi(psi,1.0),p)
    # Display Original Data if allowed
    if disp:
        dispOriginal(alpha,psi)
    # Apply Convolutional Sparse Coding. 
    # Length of AEB is set to 2 seconds (60 frames)    
    # D represents how many Action Units we want to capture
    alpha_recon,psi_recon = optimize_proxim(X,M,D,beta,dispObj=dispObj,\
                dispGrad=dispGrad,dispIteration=dispIteration,\
                psi_orig=psi,alpha_orig=alpha)[:2]
    # alpha_recon,psi_recon = optimize_proxim(X,M,D,beta,dispObj=dispObj,\
    #                 dispGrad=dispGrad,dispIteration=dispIteration)[:2]
    # Display the reconstructed values
    if disp:
        print '### Parameters ###'
        print 'N = ', str(len(X))
        print 'K = ', str(np.size(X,axis=1))
        print 'M = ', str(M)
        print 'D = ', str(D)
        print 'beta = ', str(beta),'(beta*N*K = ',\
                    str(beta*len(X)*np.size(X,axis=1)),')'
        dispPlots(alpha_recon,psi_recon,X,'Final Result',p)
        pp.pause(1)
        pp.show()
    return alpha_recon,psi_recon    

# Work with real data
def realTest(args):
    allData = sio.loadmat(args.i)
    X = fio.getjointdata(allData['data'],range(20))
    
    # Choose the correct length of psi if M is negative
    if args.M<0:
        args.M = nextpow2(np.argmax(allData['data'][:,0]>30*M.fabs(args.M)))

    # Pad the data to make it power of two and then 
    # apply Convolutional Sparse Coding
    numZeros = (nextpow2(len(X))-len(X))
    X = np.pad(X,((0,numZeros),(0,0)),'constant',constant_values=0)
    alpha_recon,psi_recon,logObj,reconError,L0 = optimize_proxim(X,M=args.M,\
    D=args.D,beta=args.Beta,iter_thresh=args.iter_thresh,\
    thresh = args.diff_thresh,dispObj=args.Disp_Obj,\
    dispGrad=args.Disp_Gradiants,dispIteration=args.Disp_Iterations,\
    totWorker=args.p)
    
    # Save the results
    resultName = args.o+'_M='+str(args.M)+'_D='+str(args.D)+'_beta='+\
        str(args.Beta)+'_'+'_'.join(args.j)+'_'+time.strftime(\
        '%H_%M_%S',time.localtime())
    sio.savemat(resultName+'.mat',{'alpha_recon':alpha_recon,\
    'psi_recon':psi_recon,'logObj':logObj,'reconError':reconError,'L0':L0,\
    'M':args.M,'D':args.D,'Beta':args.Beta,'joints':args.j,'Header':\
    allData['dataHead'],'timeData':allData['data'][:,0:2],\
    'decimateratio':allData['decimateratio']})
        
################################ Main Entrance ################################

def main():
    # Handle arguments
    parser = buildArg()
    args = parser.parse_args()
    
    # Handle the toy data
    if not args.toy == None:
        alpha_recon,psi_recon = toyTest(args.toy,D=2,M=args.M,beta=args.Beta,\
            disp=args.Disp,dispObj=args.Disp_Obj,dispGrad=args.Disp_Gradiants,\
            dispIteration=args.Disp_Iterations,totWorker=args.p)
        return
    else:
        # Handle the real data
        realTest(args)
    print 'Done!'    
    
if __name__ == '__main__':
    main()