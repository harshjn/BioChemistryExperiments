#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 12:46:25 2024

@author: harshjain
"""

def calculate_osmolarity(weight_mg, molecular_weight, volume_ml):
    # Convert weight from mg to g
    weight_g = weight_mg / 1000
    
    # Convert volume from ml to L
    volume_L = volume_ml / 1000
    
    # Calculate the number of moles
    moles = weight_g / molecular_weight
    
    # Calculate the molarity (moles/L)
    molarity = moles / volume_L
    
    # For sucrose (which does not dissociate), osmolarity is the same as molarity
    osmolarity_mOsm_L = molarity * 1000  # Convert from OsM to mOsm/L
    
    return osmolarity_mOsm_L

# Example usage
weight_mg = 1800  # Weight of sucrose in mg
molecular_weight = 342.3  # Molecular weight of sucrose in g/mol (sucrose's molecular weight)
volume_ml = 10  # Volume of water in ml

osmolarity = calculate_osmolarity(weight_mg, molecular_weight, volume_ml)
print(f"Osmolarity: {osmolarity} mOsm/L")
