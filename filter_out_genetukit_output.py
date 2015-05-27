#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>
"""

#Elham 03.11.2014
#in this script should read the output of GeneTUKit , the big file , extract the pmids and list of geneid and synonyms for each pmids and save
#in a table in SQL as a three tuple row .

#psycopg is the most popular PostgreSQL DB adaptor for Python. psycopg2 has both client-side and server-side cursors.
import psycopg2
from psycopg2 import extras
import os
import subprocess
import re

#optparse - Parser for command line options
from optparse import OptionParser

def filterout_inputfile(GTK_input):

    #define a patern for the first line of each part in GTK output file ,
    patern1 = re.compile('^Results.*(\d{8})$')

    #define the second patern , which appears in some lines ,
    patern2 = re.compile ('^\.nxml$')
    
    #define an empty 2D list to save the tuples of pmid...geneid...synonyms
    GTK_list = []

    #find the lines which starts with "Results for" and contains PMID for each of the runs
    for line in GTK_input:
        p_obj = re.search('.[/](\d{4,})' ,line ,re.IGNORECASE)
        n_obj = re.search('.nxml' ,line ,re.IGNORECASE)

        if p_obj:
            pmid = p_obj.group(1)
            print "current pmid=",pmid

        elif n_obj:
            continue

        elif (len(line.strip()) == 0):
            continue

        else :
            temp = line.strip().split("\t")
            #define a 2D list , each row has three columns which are (pmid....geneid....synonyms)
            #for each new tuple should define a new list inside the GTK_list
            GTK_list.append([pmid,temp[0],temp[1]])

    return GTK_list

###########################################MAIN PART OF THE SCRIPT ################################################

if __name__=="__main__":

    parser= OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the input file which is GeneTUKit ouput file',default="gtk_output.csv")

    (options,args)=parser.parse_args()

    #save parameters in an extra variable
    input_file = options.i

    #open GeneTUKit input file , which contains output of genetukit itself for all 20,000 abstract file .
    GTK_input = open (input_file , "r")
    genetukit_list = filterout_inputfile(GTK_input)


    #write all the inner lists into a file , in a way that will poduce a big file .
    PGS =open("pmid_geneid_syn.csv","w") 
    
    rows=len(genetukit_list)
    columns = 3

    for i in range(rows) :
        for j in range(columns) :
            PGS.write(genetukit_list[i][j]+"\t")
        PGS.write("\n")

    PGS.close()




