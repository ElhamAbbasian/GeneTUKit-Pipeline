#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>
"""

# open the filteredidmapping.csv file , which each line should be like this : Uniprot-ID    Gene-ID
#and save it's data into a Dictionary datastructure . in a way of 'geneid:unipotids'

input_file = open ("filtered_idmapping.csv","r")

#define an empty dictionary to save our pairs of key:values
idmapping={}

#read each line in file
for line in input_file:
    temp = line.strip().split("\t")

    geneid = temp[1]
    uniprotid = temp[0]

    if not (geneid in idmapping):
        #initialize the Dictionary with new Gene-ID and its value
        idmapping[geneid] = [uniprotid]

    elif (geneid in idmapping) and (not (uniprotid in idmapping[geneid]) ) :
        #append the new uniprotid to existing geneid key
        idmapping[geneid].append(uniprotid)

#close the pointer 
input_file.close()



