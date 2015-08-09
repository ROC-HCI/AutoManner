''' Human Behavior Analysis Module
    ==============================
    This program is the main entry point for extracting Behavioral Action
    Units (BAU's) using Shift Invariant Sparse Coding.
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
import numpy as np
import csv
import copy
import os

##################################
####### NEEDS REFACTORING ########
##################################
##################################
######### NEEDS Debuging #########
##################################
#python sisc_wrapper_cleandata.py -diff_thresh 1e-6 -Beta 0.2 -D 5 --pca --SaveCSV -i skeleton_test/13.3.csv -o Results/13.3;
################################# Main Helper #################################
def buildArg():
    args = ArgumentParser(description="Automatic Extraction of Human Behavior")

    args.add_argument('-i',nargs='*',default='Data/13.3.csv',\
    metavar='INPUT_FILES',\
    help='CSV file(s) containing the seleton movements\
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
    choices=range(1,9),metavar='TOY_DATA_ID',\
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
    
    args.add_argument('-M',nargs='?',type=int,default=64,\
    metavar='ATOM_LENGTH',\
    help='The length of atomic units (psi)')
    
    args.add_argument('-D',nargs='?',type=int,default=16,\
    metavar='DICTIONARY_LENGTH',\
    help='The total number of atomic units (psi). In Other Words, the total\
    number of elements in the dictionary (default: %(default)s). Does not have\
    any effect on toy data')
    
    args.add_argument('-Beta',nargs='?',type=float,default=0.1,\
    metavar='NON-SPARSITY_COST',\
    help='Represents the cost of nonsparsity. The higer the cost, the \
    sparser the occurances of the dictionary elements.')
    
    args.add_argument('--pca',dest='applyPCA',action='store_true',\
    default=False,help='Applies frame level PCA before running SISC. When\
    displaying the results, it is necessary to backproject from PCA domain\
    to the skeleton domain.')
    
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

    args.add_argument('--SaveCSV',dest='SaveCSV',action='store_true',\
    default=False,help='Turns on the plots in each iteration. Mainly used for\
    debuging. Hugely slows down the algorithm.')
    return args
################################## Unit Test ##################################
def saveAscsv(args,alpha,psi,speed, tdp, Xmean):
    #print alpha.shape;
    #print psi.shape;
    #a = alpha[:,0].tolist();
    #print a.index(max(a));
    
    speed = float(speed);
    directory = 'Results/'+str(args.i)[16:-6];
    if not os.path.exists(directory):
        os.makedirs(directory);

    timeline = [];
    skeleton = [];
    
    for i in range(5):
        maxalpha = [];
        tempa = alpha[:,i];
        stablist = tempa.tolist();
        totalmax = max(stablist)*0.36;
        for ele in range(len(stablist)):
            if stablist[ele] <= totalmax:
                stablist[ele] = 0;
        templist = copy.copy(stablist);
        rangelist = len(templist);
        #print max(templist);
        maxalpha.append(max(templist));

        checkmaxval = [];
        j=0;
        checkloop = 0;
        while checkloop != 1:
            writelist = [];
            writelist.append(str(i)+'.'+str(j));
            j=j+1;
            tempmaxval = max(templist);
            #print tempmaxval;
            if tempmaxval > totalmax:
                maxindex = templist.index(tempmaxval);
                #print maxindex;
                ckv = 0;
                while ckv != 1:
                    #print maxindex;
                    if templist[maxindex] <= totalmax:
                        break;
                    if len(checkmaxval)>0:
                        for c in checkmaxval:
                            if abs(maxindex-c) < 64:
                                templist[maxindex] = 0;
                                stablist[maxindex] = 0;
                                maxindex = templist.index(max(templist));
                                ckv = 0;
                                break;
                            else:
                                ckv = 1;
                    else:
                        ckv = 1;

                checkmaxval.append(maxindex);
                print maxindex;
                templist[maxindex] = 0;
                tempstart = maxindex;
                tempend = maxindex;
                for k in range(32):
                    tempstart = tempstart-1;
                    tempend = tempend+1;
                    if tempstart>=0:
                        templist[tempstart]=0;
                        stablist[tempstart]=0;
                    if tempend < rangelist:
                        templist[tempend]=0;
                        stablist[tempstart]=0;
                if tempstart<0:
                    tempstart=0;
                if tempend >= rangelist:
                    tempend = rangelist-1;
                writelist.append(int(tempstart/speed));
                writelist.append(int(tempend/speed));
                timeline.append(writelist);
                if max(templist)<=totalmax:
                    checkloop=1;

            else:
                break;

    '''
    for i in range(5):
        psilist = psi[:,:,i].tolist();
        #psilist = psi[:,:,i].tolist();
        skelelist = [];
        for row in psilist:
            skelelist.append(row);

        writename = 'Results/'+str(args.i)[16:-6]+'/skele_'+str(i)+'_'+str(args.i)[16:-6]+'.csv';
        #skelelist = [skeletitle]+skelelist;
        with open(writename,'w') as writefile:
            writer = csv.writer(writefile);
            writer.writerows(skelelist);
    '''
    xeach = Xmean.tolist();
    for i in range(5):
        tdplist = tdp[:,:,i].tolist();
        tempskele = [];
        for row in tdplist:
            if row != '':
                tempskele.append(row);
        tempskele.append(xeach);
        writename = 'Results/'+str(args.i)[16:-6]+'/tdp_'+str(i)+'_'+str(args.i)[16:-6]+'.csv';
        with open(writename,'w') as writefile:
            writer = csv.writer(writefile);
            writer.writerows(tempskele);
    
    timetitleline = ['vpname', 'starttime', 'endtime'];
    timeline = [timetitleline]+timeline;
    timewritename = 'Results/'+str(args.i)[16:-6]+'/timeline_'+str(args.i)[16:-6]+'.csv';
    with open(timewritename,'w') as writefile1:
        writer1 = csv.writer(writefile1);
        writer1.writerows(timeline);
    






def toyTest(args):
    dataID = args.toy
#   Synthetic Toy Data
    if dataID==1:
        alpha,psi = fio.toyExample_medium()
    elif dataID==2:
        alpha,psi = fio.toyExample_medium_boostHighFreq()
    elif dataID==3:
        alpha,psi = fio.toyExample_medium_boostHighFreq()
    elif dataID==4:
        alpha,psi = fio.toyExample_reallike()
    elif dataID==5:
        alpha,psi = fio.toyExample_medium_1d_multicomp()
    elif dataID==6:
        alpha,psi = fio.toyExample_medium_3d_multicomp() 
    elif dataID==7:
        alpha,psi = fio.toyExample_large_3d_multicomp()
    elif dataID==8:
        alpha,psi = fio.toyExample_orthogonal_3d_multicomp()
    p = Pool(args.p)
    # Construct the data            
    X = recon(alpha,projectPsi(psi,1.0),p)
    # Display Original Data if allowed
    if args.Disp:
        dispOriginal(alpha,psi)
    # Apply Convolutional Sparse Coding. 
    # Length of AEB is set to 2 seconds (60 frames)    
    # D represents how many Action Units we want to capture
    alpha_recon,psi_recon,cost,reconError,L0,SNR = optimize_proxim(X,M=args.M,\
    D=args.D,beta=args.Beta,iter_thresh=args.iter_thresh,\
    thresh = args.diff_thresh,dispObj=args.Disp_Obj,\
    dispGrad=args.Disp_Gradiants,dispIteration=args.Disp_Iterations,\
    totWorker=args.p)
    # alpha_recon,psi_recon = optimize_proxim(X,M,D,beta,dispObj=dispObj,\
    #                 dispGrad=dispGrad,dispIteration=dispIteration)[:2]
    # Display the reconstructed values
    if args.Disp:
        print '### Parameters & Results ###'
        print 'N = ', str(len(X))
        print 'K = ', str(np.size(X,axis=1))
        print 'M = ', str(args.M)
        print 'D = ', str(args.D)
        print 'beta = ', str(args.Beta)
        print 'cost = ', str(cost)
        print 'SNR = ', str(SNR)
        print 'reconError = ', str(reconError)
        print 'L0 = ', str(L0)
        dispPlots(alpha_recon,psi_recon,X,'Final Result',p)
        pp.pause(1)
        pp.show()
    else:
        # Save the results
        resultName = args.o+'/result_M='+str(args.M)+'_D='+str(args.D)+'_beta='+\
            str(args.Beta)+'_i='+str(args.i)[16:-6];
        sio.savemat(resultName+'.mat',{'alpha_recon':alpha_recon,'SNR':SNR,\
        'psi_recon':psi_recon,'cost':cost,'reconError':reconError,'L0':L0,\
        'M':args.M,'D':args.D,'Beta':args.Beta,'X':X,'alpha_origin':alpha,\
        'psi_origin':psi,'Data_Origin':'Toy'},do_compression=True)

# Work with real data
def realTest(args):
    if len(args.i)>1:
        print 'Currently SISC takes only one data file'
        return
    if not args.applyPCA:
        data,header,tx,th,ht = fio.preprocess(args.i[0])
        X = data[:,2:]
    else:
        data,header = fio.readdatafile(args.i[0])
        X,princomps,Xmean = fio.txfmdata(data)    
    # Pad the data to make it power of two and then 
    # apply Convolutional Sparse Coding
    orgX,orgY =  np.shape(X);
    numZeros = (nextpow2(len(X))-len(X))
    X = np.pad(X,((0,numZeros),(0,0)),'constant',constant_values=0)
    alpha_recon,psi_recon,cost,reconError,L0,SNR = optimize_proxim(X,M=args.M,\
    D=args.D,beta=args.Beta,iter_thresh=args.iter_thresh,\
    thresh = args.diff_thresh,dispObj=args.Disp_Obj,\
    dispGrad=args.Disp_Gradiants,dispIteration=args.Disp_Iterations,\
    totWorker=args.p)
    alpha_recon = 8*alpha_recon[0:orgX,:]

    # Save the results
    if not args.applyPCA:
        resultName = args.o+'/result_M='+str(args.M)+'_D='+str(args.D)+'_beta='+\
            str(args.Beta)+'_i='+str(args.i)[16:-6];
        sio.savemat(resultName+'.mat',{'alpha_recon':alpha_recon,\
        'psi_recon':psi_recon,'cost':cost,'reconError':reconError,'L0':L0,\
        'M':args.M,'D':args.D,'K':np.size(X,axis=1),'Beta':args.Beta,'SNR':SNR,\
        'Data':data,'header':header,'N':np.size(X,axis=0),'Data_Origin':'Real'})
    else:
        M,K,D=np.shape(psi_recon)
        psi_decoded = np.zeros((M,np.size(princomps,axis=0),D))
        tdp = np.zeros((M,np.size(princomps,axis=0),D));
        for i in xrange(D):
            temp = psi_recon[:,:,i]/np.max(psi_recon[:,:,i])
            tdp[:,:,i] = temp.dot(princomps.T)
            psi_decoded[:,:,i] = temp.dot(princomps.T) + Xmean
        #print np.shape(psi_decoded)
        resultName = args.o+'/result_M='+str(args.M)+'_D='+str(args.D)+'_beta='+\
            str(args.Beta)+'_i='+str(args.i)[16:-6];
        if args.SaveCSV:
            saveAscsv(args,alpha_recon,psi_decoded,30.2, tdp, Xmean);
        else:
            sio.savemat(resultName+'.mat',{'alpha_recon':alpha_recon,\
        'psi_recon':psi_decoded,'cost':cost,'reconError':reconError,'L0':L0,\
        'M':args.M,'D':args.D,'Beta':args.Beta,'SNR':SNR,\
        'Data':data,'header':header,'K':np.size(X,axis=1),\
        'psi_comp':psi_recon,'princmp':princomps,'xmean':Xmean,\
        'N':np.size(X,axis=0),'Data_Origin':'Real'})
################################ Main Entrance ################################

def main():
    # Handle arguments
    parser = buildArg()
    args = parser.parse_args()
    # Handle the toy data
    if not args.toy == None:
        print 'not toy';
        toyTest(args)
    else:
        # Handle the real data
        print 'realtest';
        realTest(args)
    print 'Done!'    
    
if __name__ == '__main__':
    main()