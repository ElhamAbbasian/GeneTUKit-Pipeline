#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>
"""

#Elham 22.07.2014
#This script is for filtering idmapping.dat file , in a way that we are searching in ID-Type column (second column) , for lines with the "Gene-ID" value , and save
# the first and third coulmn which are protein-id and Gene-id respectively in a .csv file (filteredidmapping.csv) .
#Input lines are in 3 columns like this : protein_ID    ID-Type    Gene-ID
#output format is like , searching in ID-Type coloumn and for the lines with "GeneID" value , write a line in output like : protein_ID    Gene-ID

#optparse - Parser for command line options
from optparse import OptionParser


parser= OptionParser()
parser.add_option("-i", "--input", dest="i", help='true or false. This option specifies wether the user uses this pipeline as a test case or not',default="true")

(options,args)=parser.parse_args()

#save parameters in an extra variable
test_case = options.i

infile = open ("idmapping.dat","r")
outfile = open("filtered_idmapping.csv","w")
pgs_file=open("pmid_geneid_syn.csv","r")

#for every line in "pmid_geneid_syn.csv" file, fetch the gene-id and save in a list.
gene_id_list=[]
for line in pgs_file:
	temp = line.strip().split("\t")
	gene_id_list.append(temp[1])

print gene_id_list


#read every line in file - line is a string
for line in infile:
    #strip deletes leading plus ending spaces, etc.
    #split generates a list out of a string and deletes "delimiter"
    temp = line.strip().split("\t")
    
    #debug:
    #Check for second column , if it's value is "GeneID" , then write the required columns in output file
    if test_case == "true" :
        idtype="GeneID"
        try:
            if temp[1] == idtype:
                if temp[2] in gene_id_list:
                    outfile.write(temp[0]+"\t"+temp[2]+"\n")
        except:
            print line
    else :
        idtype="GeneID"
        try:
            if temp[1] == idtype:
                outfile.write(temp[0]+"\t"+temp[2]+"\n")

        except:
            print line



#close file pointers
outfile.close()
infile.close()

