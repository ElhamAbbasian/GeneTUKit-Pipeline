#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>

    This script reads the output of GeneTUKit and extracts the PubMed IDs with identified gene IDs and synonyms.
"""

#optparse - Parser for command line options
from optparse import OptionParser

# the code to return a list is commented out - the file can be written directly
# if the user wants to upload the triples to a PostgreSQL database directly within this script, the usage of lists can be extended with SQL commands
# another approach is to use the bulkloader with the resulting CSV file
def filterout_inputfile(gtk_input, outfile):
    # list for saving lists of triples: PubMed ID, gene ID, and synonym
#    gtk_list = []
    #find the lines which start with "Results for" and store a list with three entries for each identified gene or protein: PubMed ID, gene ID (temp[0]), synonym (temp[1])
    for line in gtk_input:
        # get file name which contains the PubMed ID - split function: slashes and dots
        # e.g.: Results for /home/kersten/GeneTUKit-Pipeline/GeneTUKit/downloaded_abstracts/23215050.nxml :
        # multiple synonyms for the same gene ID are separated with a pipe ("|"), but not splitted within this script
        if "Results for" in line:
            pmid = line.split("/")[-1].split(".")[0]
            print "current pmid=",pmid
        # empty line
        elif (len(line.strip()) == 0):
            continue
        # store triple (in output file)
        else :
            temp = line.strip().split("\t")
            # pmid: PubMed ID, temp[0]: gene ID, temp[1]: synonym
#            gtk_list.append([pmid,temp[0],temp[1]])
            outfile.write(pmid + "\t" + temp[0] + "\t" + temp[1] + "\n")
#    return GTK_list

### MAIN PART OF THE SCRIPT ###

if __name__=="__main__":

    parser= OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the input file which is GeneTUKit ouput file',default="GeneTUKit/gtk_output.csv")
    parser.add_option("-o", "--output", dest="o", help='name of the output file which is GeneTUKit ouput file',default="pmid_geneid_syn.csv")

    (options,args)=parser.parse_args()

    #save parameters in an extra variable
    input_file = options.i
    output_file = options.o

    # open input (which contains the output of GeneTUKit for the given number of abstract files) and output file
    gtk_input = open (input_file, "r")
    outfile = open(output_file,"w")
    filterout_inputfile(gtk_input,outfile)
    gtk_input.close()
    outfile.close()

"""
# use lists and iterate over each entry to generate the output file
    genetukit_list = filterout_inputfile(GTK_input)
    #write all the inner lists into a file, in a way that one big file is produced
    outfile =open("pmid_geneid_syn.csv","w") 
    
    rows=len(genetukit_list)
    columns = 3

    for i in range(rows) :
        for j in range(columns) :
            outfile.write(genetukit_list[i][j]+"\t")
        outfile.write("\n")

    outfile.close()
"""



