#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>

    This script selects all available UniProt IDs from the dictionary based on filtered_idmapping.csv, which is implicitly built by importing idmapping from map_to_dict.py. Furthermore, it writes the dictionary save.p which is dictionary of dictionaries to save the UniProt IDs for each synonym for each PubMed ID. This data structure will be used by annotate_abstracts.py. The output file merged_file.csv contains one gene or protein name per line with the tab-separated entries PubMed ID, gene ID, synonym, UniProt ID(s).
"""

# import dictionary idmapping (created while importing) from maptodict.py (gene ID : UniProt IDs)
from map_to_dict import idmapping
# to write a binary Python file (pickle)
import pickle

# main part of the script
if __name__=="__main__":
    # open input file with PubMed ID, gene ID, and synonym(s) (separated with "|")
    infile = open ("pmid_geneid_syn.csv","r")
    # part of the possible false positive synonyms from GeneTUKit
    black_list=['Protein','id','Id']
    # merged output file with PubMed ID, gene ID, synonym, UniProt ID(s)
    outfile = open("merged_file.csv","w")
    # not yet used:
    # define a dictionary to save the pairs synonym : UniProt ID(s)
#    syndict={}
    # define a dictionary of dictionaries pmiddict[pmid] = {synonym:[UniProt ID(s)]}
    pmiddict={}
    # read input file
    for line in infile:
        # tab-separated input format
        temp = line.strip().split("\t")
        # first column PubMed ID
        pmid = temp[0]
        # second column gene ID
        geneid = temp[1]
        # third column synonym(s) 
        synonyms = temp[2]
        # if a gene ID is contained in the dictionary idmapping, it will be processed
        if (geneid in idmapping):
            # check if there is more than one synonym for a gene ID (separated with "|"),
            # if yes they should be splitted and written to merged_file.csv with one synonym per line
            l_synonyms = synonyms.strip().split("|")
            # iterate over the list of synonyms
            for item in l_synonyms:
                # check whether molecule name is contained in the blacklist
                if not item in black_list:
                    # string that should be written to file as one line
                    final_line = pmid+"\t"+geneid +"\t"+item+"\t"
                    # if there is only one UniProt ID, add it to the string
                    if (len(idmapping[geneid]) == 1):
                        uproid = idmapping[geneid][0]
                        final_line = final_line + uproid
                        outfile.write(final_line+"\n")
                    # if there are several UniProt IDs, concatenate them comma-separated
                    elif (len(idmapping[geneid]) > 1):
                        uproid = ",".join(idmapping[geneid])
                        outfile.write(final_line + uproid + "\n")
                    # add a new dictionary to the dictionary pmiddict
                    # add the synonym (item) and the UniProt IDs
                    if not pmid in pmiddict:
                        pmiddict[pmid]={}
                        pmiddict[pmid][item]=uproid
                    # if the PubMed ID is already contained in pmiddict, just add the 
                    elif not item in pmiddict[pmid]:
                        pmiddict[pmid][item]=uproid
                    # if the synonym appears twice with different UniProt IDs (possible?)
                    else:
                        print pmiddict[pmid][item], pmid, item, uproid
                else:
                    print pmid, item, "blacklisted"
        # gene ID not found in idmapping
        else:
            print "missing Gene-ID in idmapping =",geneid
    outfile.close()
    # debug:
#    print len(pmiddict)

    #save the pmiddict dictionary into a pickle file (Python binary file) to be used within the next pipeline step
    pickle.dump(pmiddict,open("save.p","wb"))


