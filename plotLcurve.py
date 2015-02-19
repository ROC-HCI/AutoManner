# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 16:22:22 2015

@author: itanveer
"""

import os

def main():
    startPath = 'Result/'
    for root,folder,files in os.walk(startPath):
        for afile in files:
            if afile.lower().endswith('.mat'):
                # create full filename and print
                fullPath = os.path.join(root,afile)
                print fullPath
    
    
if __name__ == '__main__':
    main()