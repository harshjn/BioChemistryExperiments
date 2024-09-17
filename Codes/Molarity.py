#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codes for calculating osmolarity

Created on Wed Jul 24 15:44:16 2024

@author: harshjain
"""

import numpy as np

#%% How to make 10% DOPS Solution

Chemicals = ['DOPS','DOPC','LissRhod-PE', 'DOTAP', 'NBD-DOTAP']
Molecular_Weights = [809.518,785.593,1300.712,697.578,710.34]
#Exact masses extracted from Avanti-Lipids Website
Concentrations = [2.5,2.5,0.01,2.5,0.1]; # In chloroform

# https://avantilipids.com/product/840035
# https://avantilipids.com/product/850375
# https://avantilipids.com/product/810150
# https://avantilipids.com/product/890890
# https://www.medchemexpress.com/fluorescent-dotap.html

# DOPC is 2.5 mg/ml, DOPS is 2.5 mg/ml, LissRhod is 0.01 mg/ml,
# DOTAP is 2.5 mg/ml NBD-DoTAP is 0.1 mg/ml


#%% Let's make 10% charged DOPS-DOPC (Negative, Fluoroscent)
MixtureVolumes = [80,800,50 ,0,0]; #in microliters

# Number of Weights in mixture
Weights = np.array(np.multiply(MixtureVolumes, Concentrations))/1000 # in milligrams

Moles = np.array(Weights)/np.array(Molecular_Weights)

print('Moles')
print(Moles)

print('Weights (in milligrams)')
print(Weights)
# Percentage of moles in mixture

Percentages = np.round(100000 * np.array(Weights) / np.sum(Weights)) / 1000
print('Percentages')
print(Percentages)

#%% Let's make 90% charged DOTAP-DOPC (Positive, non-fluoroscent)
Chemicals = ['DOPS','DOPC','LissRhod-PE', 'DOTAP', 'NBD-DOTAP']
Concentrations = [2.5,10,0.01,2.5,0.1]; # In chloroform
MixtureVolumes = [0,800,0,320,15]; # in microliters

# Number of Weights in mixture
Weights = np.multiply(MixtureVolumes, Concentrations)

# Percentage of moles in mixture

Percentages = np.round(100000 * np.array(Weights) / np.sum(Weights)) / 1000

Moles = np.array(Weights)/np.array(Molecular_Weights)

print('Moles')
print(Moles)

print('Weights')
print(Weights)
# Percentage of moles in mixture
print('Percentages')
print(Percentages)

#%%

Moles = np.array(Weights)/np.array(Molecular_Weights)
print(Moles)
