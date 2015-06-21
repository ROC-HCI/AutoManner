########################################################################
################## OPTIMIZER DEMO WITH VARIOUS TOY DATA ################
########################################################################
# 3D signal (length=256) with only one component
# ------------------------------------------
# python sisc_wrapper.py -toy 1 --Disp -M 32 -Beta 0.05 -D 1

# 1D signal (length=256) with two components
# ------------------------------------------
# python sisc_wrapper.py -toy 5 --Disp -M 32 -Beta 0.05 -D 2

# 3D signal (length=256) with two components
# ------------------------------------------
# python sisc_wrapper.py -toy 6 --Disp -M 32 -Beta 0.1 -D 2

# Large 3D signal. 10 samples in each alpha component are randomly activated
# --------------------------------------------------------------------------
# python sisc_wrapper.py -toy 7 --Disp -M 64 -Beta 0.15 -D 2

# A deceitful dataset. The addition of two components result in
# a signal orthogonal to the components.
# -------------------------------------------------------------
# python sisc_wrapper.py -toy 8 --Disp -M 32 -Beta 0.1 -D 2

# A simulated dataset with real-like dimensions
#  python sisc_wrapper.py -toy 4 --Disp -M 64 -Beta 0.01 -D 8
########################################################################


########################################################################
##################### OPTIMIZER DEMO WITH A REAL DATA ##################
########################################################################
# One datafile at a time
# python sisc_wrapper.py -Beta 0.035 -i 'Data/13.3.csv'
#
# run sisc with compressed data (PCA over frames)
python sisc_wrapper.py -diff_thresh 1e-6 -Beta 0.2 -D 5 --pca -i 'Data/13.3.csv'


########################################################################
########################### VISUALIZATION DEMO #########################
########################################################################
# Print the parameters of the results with highlighting the desired parts
# -----------------------------------------------------------------------
# python filter.py Results/result_?__*.mat -p SNR cost L0|egrep --color "_1__|beta=0.05|$"

# Print parameters for Beta = 0.07
# --------------------------------
# python filter.py Results/*beta=0.07*.mat -pprint SNR cost L0

# Filter files with hi/low or not-hi/not-low parameter values this filtering
# procedure could be used to delete files based on their parameters
# --------------------------------------------------------------------------
# python filter.py Results/*.mat -nlo cost
# python filter.py Results/*.mat -hi SNR
#
# The following command will delete all the files with Beta = 0.06 and cost is
# not minimum
# ----------------------------------------------------------------------------
# python filter.py Results/*beta=0.06*.mat -nlo cost | xargs rm

# Plot an L curve
# python filter.py Results/*.mat --Lcurve

# Show a skeleton animation
# python skelplot_mayavi.py Data/13.1.csv

# Show a skeleton animation that is inflated from compressed data
# python -c "import skelplot_mayavi as my; my.unitTest1('Data/13.1.csv')"

# Show the results (psi and alpha)
# python filter.py --showresults Results/*.mat
########################################################################