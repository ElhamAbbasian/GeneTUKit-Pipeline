#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>

    This script reads the file filtered_idmapping.csv (UniProt ID \t gene ID) and stores its data in a dictionary with the gene ID as the key and the UniProt ID(s) as the value in a list.
"""

# read input file
input_file = open ("filtered_idmapping.csv","r")
#dictionary initialisation
idmapping={}
#read each line in file
for line in input_file:
    temp = line.strip().split("\t")
    # UniProt ID \t gene ID
    geneid = temp[1]
    uniprotid = temp[0]
    # if gene ID is not yet stored in the dictionary
    if not (geneid in idmapping):
        #key: gene ID, value: list of UniProt IDs (or list with one element)
        idmapping[geneid] = [uniprotid]
    # else: append UniProt ID to the list if it is not yet inside
    elif (geneid in idmapping) and (not (uniprotid in idmapping[geneid])):
        idmapping[geneid].append(uniprotid)
#close file
input_file.close()



