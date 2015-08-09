'''
This module to "pretty print" the results
-------------------------------------------------------------------------------
    Coded by Md. Iftekhar Tanveer (itanveer@cs.rochester.edu)
    Rochester Human-Computer Interaction (ROCHCI)
    University of Rochester
-------------------------------------------------------------------------------
'''
import matplotlib
from argparse import ArgumentParser
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import math

def plotLcurve(args):
    LplotDat = []
    for afile in args.Files:
        if afile.lower().endswith('.mat'):
                allDat = sio.loadmat(afile)
                LplotDat.append(np.concatenate((allDat['L0'],\
                    allDat['reconError'],\
                allDat['Beta'],allDat['cost']),axis=1))
    LplotDat = np.concatenate(LplotDat,axis=0)
    plt.scatter(LplotDat[:,0],LplotDat[:,1])
    ax=plt.gca()
    for idx in xrange(len(LplotDat)):
        ax.annotate('Beta='+str(LplotDat[idx,2])+'\n'+\
            '{:0.2e}'.format(LplotDat[idx,3])\
        ,(LplotDat[idx,0],LplotDat[idx,1]+\
            np.mean(LplotDat[:,1])/2*np.random.rand()))
    plt.xlabel('L0 norm of alpha')
    plt.ylabel('Reconstruction Error')
    plt.show()

def buildArg():
    pars = ArgumentParser(description="Program to 'pretty print' the results.\
        It can also plot L curve.")
    pars.add_argument('Files',nargs='+',help='List of the (.mat) files from\
     which the results are to read')
    pars.add_argument('-pprint',nargs='+',\
        choices=['D','M','K','Beta','reconError','cost','SNR','L0'],\
        help='Print the specified parameters from the files in a pretty format')
    pars.add_argument('-hi',nargs='?',\
        choices=['D','M','K','Beta','reconError','cost','SNR','L0'],\
        help='Specify a parameter name.\
        The program returns names of all the files that contain the highest\
        value of this parameter')
    pars.add_argument('-lo',nargs='?',\
        choices=['D','M','K','Beta','reconError','cost','SNR','L0'],\
        help='Specify a parameter name.\
        The program returns names of all the files that contain the lowest\
        value of this parameter')
    pars.add_argument('-nhi',nargs='?',\
        choices=['D','M','K','Beta','reconError','cost','SNR','L0'],\
        help='Specify a parameter name.\
        The program returns names of all the files that does not \
        contain the highest\
        value of this parameter')
    pars.add_argument('-nlo',nargs='?',\
        choices=['D','M','K','Beta','reconError','cost','SNR','L0'],\
        help='Specify a parameter name.\
        The program returns names of all the files that does not\
         contain the lowest\
        values of this parameter')
    pars.add_argument('--Lcurve',action='store_true',help='Command to\
        draw an L curve')
    pars.add_argument('--showresults',action='store_true',help='Command to\
        plot the patterns (psi) and corresponding activation sequences (alpha).\
        If multiple files are given, it chooses one with minimum L0*exp(cost).')
    return pars

def showresults(args):
    import skelplot_mayavi as splt
    for idx,afile in enumerate(args.Files):
        if afile.lower().endswith('.mat'):
            allData = sio.loadmat(afile)
            L0 = allData['L0']
            cost = allData['cost']
            mult = L0*math.exp(cost)
            if idx==0:
                lowmult = mult
                bestFile = afile
            elif mult<lowmult:
                lowmult = mult
                bestFile = afile
    allData = sio.loadmat(bestFile)
    # Print nonzero component indices
    sumAlpha = np.sum(allData['alpha_recon'],axis=0)
    validIdx = np.nonzero(sumAlpha)
    print 'Available nonzero components are:'
    for ind in validIdx:
        print ind,
    print
    component = input('which component do you want to see?')
    mult = input('please enter a multiplier:')
    psi = mult*allData['psi_comp'][:,:,component].dot(allData['princmp'].T)\
                        +allData['xmean']
    splt.animateSkeleton(psi)
    plt.clf()
    plt.plot(allData['alpha_recon'][:,component])
    plt.xlabel('frame')
    plt.ylabel('alpha')
    plt.show()

def printparams(args):
    filelen = max([len(afile) for afile in args.Files])
    # Build Template
    template = '{0:'+str(filelen)+'} | '
    for cnt,par in enumerate(args.pprint):
        template=template+'{'+str(cnt+1)+':'+str(max(len(par),5))+'} | '
    template = template[:-3]
    # Print Header
    header=template.format(*(['FILENAME']+[item for item in args.pprint]))
    print header
    print '='*len(header)
    # Print the data    
    for afile in args.Files:
        if afile.lower().endswith('.mat'):
            allData = sio.loadmat(afile)    
            paramdat = ['{:0.2f}'.format(float(allData[par][0][0]))\
            for par in args.pprint]
            print template.format(*([afile]+paramdat))

def filtfile(args):
    if args.hi or args.nhi:
        # Scan all the highest indices
        for idx,afile in enumerate(args.Files):
            if afile.lower().endswith('.mat'):
                curval = sio.loadmat(afile)[args.hi if \
                    args.hi else args.nhi][0][0]
                if idx == 0:
                    hiIdx = [idx]
                    curmax = curval
                else:
                    if curval > curmax:
                        hiIdx = [idx]
                        curmax = curval
                    elif curval == curmax:
                        hiIdx = hiIdx + [idx]
        for idx,afile in enumerate(args.Files):
            if afile.lower().endswith('.mat'):
                if args.hi and idx in hiIdx:
                    print afile
                elif args.nhi and not idx in hiIdx:
                    print afile
    elif args.lo or args.nlo:
        # Scan all the lowest indices
        for idx,afile in enumerate(args.Files):
            if afile.lower().endswith('.mat'):
                curval = sio.loadmat(afile)[args.lo \
                        if args.lo else args.nlo][0][0]
                if idx == 0:
                    loIdx = [idx]
                    curlo = curval
                else:
                    if curval < curlo:
                        loIdx = [idx]
                        curlo = curval
                    elif curval == curlo:
                        loIdx = loIdx + [idx]
        for idx,afile in enumerate(args.Files):
            if afile.lower().endswith('.mat'):
                if args.lo and idx in loIdx:
                    print afile
                elif args.nlo and not idx in loIdx:
                    print afile
        
def main():
    parser = buildArg()
    args = parser.parse_args()
    if not args.Files:
        return
    if args.pprint:
        printparams(args)
    if args.hi or args.lo or args.nhi or args.nlo:
        filtfile(args)
    if args.Lcurve:
        plotLcurve(args)
    if args.showresults:
        showresults(args)

if __name__ == '__main__':
    main()
