#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>

    This script filters pairs of UniProt IDs and gene IDs from the file idmapping.dat. The first and the third coulmn, which are UniProt Id and gene Id (if the second column equals "GeneID"), are saved in the file filtered_idmapping.csv. A test case using only gene IDs from the GeneTUKit output file pmid_geneid_syn.csv can be run with "-t".
"""

#optparse - Parser for command line options
from optparse import OptionParser

if __name__=="__main__":
    parser= OptionParser()
    parser.add_option("-t", "--test_case", dest="t", action="store_true", default=False, help="Run this script with a given number of PubMed IDs in pmid_geneid_syn.csv (default: False).")    
    parser.add_option("-i", "--input", dest="i", help='name of the input file with gene IDs, UniProt IDs, and other information',default="idmapping.dat")
    parser.add_option("-r", "--result", dest="r", help='name of the other input file with the results from GeneTUKit',default="pmid_geneid_syn.csv")
    parser.add_option("-o", "--output", dest="o", help='name of the output file containing only UniProt IDs and gene IDs',default="filtered_idmapping.csv")

    (options,args)=parser.parse_args()

    #save parameters in an extra variable
    test_case = options.t
    input_file = options.i
    output_file = options.o
    results_file = options.r

    # open files
    infile = open (input_file,"r")
    outfile = open(output_file,"w")
    results=open(results_file,"r")

    # for each line in pmid_geneid_syn.csv, get the gene ID and save it in a list
    gene_id_list=[]
    for line in results:
        temp = line.strip().split("\t")
        gene_id_list.append(temp[1])

    # test case with a small number of gene IDs from pmid_geneid_syn.csv
    if test_case:
        print gene_id_list

    #read every line in file - line is a string
    for line in infile:
        # strip() deletes leading plus ending spaces, etc.
        # split(delimiter) generates a list out of a string and deletes the "delimiter" (here: tab)
        temp = line.strip().split("\t")
        # Check the second column - if its value equals "GeneID", the required UniProt ID and gene ID is stored in the output file
        # debug:
        # if test_case is True
        if test_case:
            idtype="GeneID"
            try:
                if temp[1] == idtype:
                    if temp[2] in gene_id_list:
                        outfile.write(temp[0]+"\t"+temp[2]+"\n")
            # debug:
            except:
                print line
        else:
            idtype="GeneID"
            try:
                if temp[1] == idtype:
                    outfile.write(temp[0]+"\t"+temp[2]+"\n")
            # debug:
            except:
                print line

    # close files
    outfile.close()
    infile.close()

