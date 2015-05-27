#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>
"""

#Elham 05.11.2014
#in this script I will try to fetch "Uniprotids" from idmapping dictionary ,
#for all geneids that are mentioned in "pmid_geneid_syn.csv" file , and add the 
#related uniprotids to them .in a way that in new file we will have 
# "pmid geneid synonyms uniprotids"

#import idmapping Dictionary from maptodict.py which has such pair of geneid:uniportids
from map_to_dict import idmapping
import pickle

#Function to add related idmappings to each line of "pmid_geneid_syn.csv" file
def merge_GTKoutput_idmapping(PGS,idmapping):

    #go through all lines in PGS input file to search for existing Geneids in idmapping dictionary . 
    #try:
    for line in PGS:
        temp = line.strip().split("\t")

        pmid = temp[0]
        geneid = temp[1]
        synonyms = temp[2]

        if (geneid in idmapping):
            #check if there is more than one synonyms for this geneid , if yes they should be saved in different rows.
            l_synonyms = synonyms.strip().split("|")

            for item in l_synonyms:
                final_line = pmid+"\t"+geneid +"\t"+item+"\t"

                if (len(idmapping[geneid]) == 1):
                    final_line = final_line+idmapping[geneid][0]
                    Final_f.write(final_line+"\n")

                elif (len(idmapping[geneid]) > 1):
                    Final_f.write(final_line+",".join(idmapping[geneid])+"\n")

        else:
            print "missing Gene-ID in idmapping =",geneid
    #except:
        #print "Genetukit output File Name =",PGS
    Final_f.close()

    #read the created Final_f.csv file and make a dictionary out of it: of "synonym : Uniprotid"
    r_Final_f = open ("merged_file.csv","r")
    
    black_list=['Protein','id','Id']
#    for line in r_Final_f:
#        temp = line.strip().split("\t")
#        syn = temp[2]
#        if not syn in black_list :
#            if not syn in syndict :
#                syndict[syn]=[temp[3]]
#            else :
#                syndict[syn].append(temp[3])

#    #for loop over syndict dictionary to save all the lines in a .csv file .
#    for key in syndict :
#        #should delete all repeated uniprotids fo each synonym
#        syndict[key]=list(set(syndict[key]))
#        upid = ",".join(list(set(syndict[key])))
#        syndict_file.write(key+"\t"+upid+"\n")


    #Elham 13.01.2015
    #this new part is going to make a dictionary of dictionary , whose keys are pmids and it's values are another dictionary with synonym:unipotids pairs as key:value pair.
    #I use merged_file.csv file except second column which is geneid .

    #go over all lines of merged_file.csv , check the same pmids and fetch synonyms:uniprotids .
    for line in r_Final_f:
        temp = line.strip().split("\t")
        pmid = temp[0]
        syn = temp[2]
        uproid = temp[3]

        if not syn in black_list :
            if not pmid in pmiddict :
                pmiddict[pmid]={}
                pmiddict[pmid][syn]=uproid
            else:
                pmiddict[pmid][syn]=uproid

#    for key in pmiddict:
#        syndict_file.write(key+"\t"+str(pmiddict[key]))
#        syndict_file.write("\n")

        #print key

    return
###########################################MAIN PART OF THE SCRIPT ################################################

if __name__=="__main__":

    #open the "pmid_geneid_syn.csv" file , and send it to the function.
    PGS = open ("pmid_geneid_syn.csv","r")
    
    #make another file , for final-merged file
    Final_f = open("merged_file.csv","w")
    
    #make a .csv file for saving syndict in it , for using in bulkloader later .
#    syndict_file = open ("syndict_bulkloader.csv","w")

    #define a dictionary to save the synonym : Uniprotids pair
    syndict={}

    #define a dictionary of dictionary
    pmiddict={}

    merge_GTKoutput_idmapping(PGS,idmapping)
    Final_f.close()
#    syndict_file.close()

    print len(pmiddict)

    #save the syndict dictionary into a pickle file , in such that can be use later .
    pickle.dump(pmiddict,open("save.p","wb"))


