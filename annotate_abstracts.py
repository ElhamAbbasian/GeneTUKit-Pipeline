#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>

    This script reads all NXML files from a folder to annotate them and store them in a CSV file (PubMed ID\tabstract title\tabstract text). It first annotates all names identified by GeneTUKit in an earlier step and then removes all nested or inner tags (false positives).
"""

# file path operations
import os
# regular expressions
import re
# binary Python format to read and write
import pickle

#optparse - Parser for command line options
from optparse import OptionParser

# function to annotate the gene and protein names in the title and the text (if available) of downloaded abstracts
def annotate_abstract(abstext,abstitle,pmid):
    # this function searches for synonyms from merged_file.csv file to replace them with a tag as shown here:
    #<potein-id="unipotid1,unipotid2,...">synonym</protein>
    #new taged title and new tagged abstract text
    title_new = abstitle.decode('utf-8')
    if abstext:
        text_new = abstext.decode('utf-8')

    #define the term enclosed in brackets, e.g. <protein-id=...>
    tag = "protein-id"

    #go through list of synonyms and highlight each one available
    #re.escape(string): Return string with all non-alphanumerics backslashed; this is useful if you want to match an arbitrary literal string that may have regular expression metacharacters in it. (https://docs.python.org/2/library/re.html)
    #IGNORECASE(re.I): Perform case-insensitive matching; expressions like [A-Z] will match lowercase letters, too. This is not affected by the current locale. (https://docs.python.org/2/library/re.html)
    #re.compile(pattern, flags=0) : Compile a regular expression pattern into a regular expression object, which can be used for matching using its match() and search() methods, described below. (https://docs.python.org/2/library/re.html)

    # each key is a synonym
    for key in pmiddict[pmid]:
        # get the UniProt ID(s)
        upid = pmiddict[pmid][key]

        #return a regular expression that can find a word only if it's written alone (next to space, start of string, end of string, comma, etc) but not if inside another word (https://mail.python.org/pipermail/python-list/2005-June/352087.html)
        pattern = re.compile("\\b" + re.escape(key) + "\\b",re.I)

        # https://github.com/daevaorn/djapian/issues/73
        # value = value.replace(word, u'<%(tag)s>%(word)s</%(tag)s>' % dict(tag=tag, word=word))
        (title_new,count1) = re.subn(pattern,u'<%(tag)s=\"%(uniprotid)s\">%(word)s</%(tag)s>' % dict(tag=tag, word=key, uniprotid=upid),title_new)
        if abstext:
            (text_new,count2) = re.subn(pattern,u'<%(tag)s=\"%(uniprotid)s\">%(word)s</%(tag)s>' % dict(tag=tag, word=key, uniprotid=upid),text_new)

    # after annotation, search for nested tags in abstract_title, abstract_text and remove them
    title_new=remove_nested_tagging(title_new)
    if abstext:
        text_new=remove_nested_tagging(text_new)

    # write the annotated abstract title and text to the file ann_out
    if abstext:
        t_new = text_new.encode('utf-8')
        ti_new = title_new.encode('utf-8')
        ann_out.write(pmid+"\t"+ti_new+"\t"+t_new+"\n")
    else:
        ti_new = title_new.encode('utf-8')
        ann_out.write(pmid+"\t"+ti_new+"\t\n")

# after tagging, some abstracts contain nested annotations, which has to be fixed
# at first, all annotations are inserted
# subsequently, all inner annotations will be removed before the abstract texts are stored in the CSV file
# this function is called inside annotate_abstract()
def remove_nested_tagging(ann_text) :
    #get the list of (start,end) positions which shows the boundaries of annotation
    #1. find single and inner tags
    inner_positions =  [(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text))]
    # debug:
#    print "inner position",inner_positions,"\n"

    #2. find all patterns which have nested tags inside and add them to the positions list
    nested_positions_typ1 =[(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">([\w+\-]+)(<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>)+<\/protein-id>',ann_text))]
    nested_positions_typ2 =[(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">(<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>)+([\s\w+\-]+)<\/protein-id>',ann_text))]
    nested_positions_typ3 =[(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">(<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>)+<\/protein-id>',ann_text))]
    # debug:
#    print "outer positions typ1",nested_positions_typ1,"\n"
#    print "outer positions typ2",nested_positions_typ2,"\n"

    # combine the two lists
    positions=[]
    positions+=inner_positions
    positions+=nested_positions_typ1
    positions+=nested_positions_typ2
    positions+=nested_positions_typ3

    # sort positions reversely
    positions.sort(reverse=True)
    # debug:
#    print "list of positions:",positions,"\n"

    # define an empty list as the blacklist, which will contain the inner tags that have to be deleted
    blacklist=[]

    # iterate over the list of positions list, but check whether there is at least one element in the lists of nested_positions
    # in the inner_positions there are some nested tags
    if len(nested_positions_typ1) > 0 or len(nested_positions_typ2) > 0 or len(nested_positions_typ3) > 0 :
        if len(positions) == 2 :
            blacklist=inner_positions
        else:
            for elemi in range(0,len(positions)-1) :
                elemj=elemi+1
                if positions[elemi][0] < positions[elemj][1]:
                    blacklist.append(positions[elemi])

        # delete the probably repeated items in blacklist
        blacklist=list(set(blacklist)) 
        # debug:
#        print "blacklist=",blacklist

    #check if blacklist is empty, which would mean that there are no nested tags for this text (continue with the next abstract) :
    if len(blacklist) > 1 :
        for i in range(0,len(blacklist)) :
            # check if element i and element i+1 are overlapping
            j = i+1

            # check separetely whether j is out of the range of i
            if j == len(blacklist) :
                syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[i][0]:blacklist[i][1]]).group(2)
                ann_text = ann_text[0:blacklist[i][0]] + syn + ann_text[blacklist[i][1]:]
            else :
                if blacklist[i][0] < blacklist[j][1]:
                    # overlapping tags - first get the synonym inside  and then update the text.
                    syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[i][0]:blacklist[i][1]]).group(2)
                    ann_text = ann_text[0:blacklist[i][0]] + syn + ann_text[blacklist[i][1]:]

                    # if the element is overlapping with the next pair (element i+1), update the end of the next pair
                    # it has to be constructed from the length of the last maching pattern (<protein-id=...>...</protein-id>)
                    blacklist[j][1] -= (blacklist[i][1]-blacklist[i][0]-len(syn))

                else :
                    # no overlap, just update the text
                    syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[i][0]:blacklist[i][1]]).group(2)
                    ann_text = ann_text[0:blacklist[i][0]] + syn + ann_text[blacklist[i][1]:]

    elif len(blacklist) == 1 :
        # in this case, there is no iteration needed, just update the text according to the exsiting pair of tags
        syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[0][0]:blacklist[0][1]]).group(2)
        # debug:
#        print syn,"\n"
        ann_text = ann_text[0:blacklist[0][0]] + syn + ann_text[blacklist[0][1]:]

    # debug:
#    print ann_text,"\n"
    return ann_text

### MAIN PART OF THE SCRIPT ###
if __name__=="__main__":

    parser= OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the directory containing abstracts',default="downloaded_abstracts")
    parser.add_option("-o", "--output", dest="o", help='name of the output file in CSV format containing all annotated abstracts',default="annotated_abstracts.csv")

    # get parameters
    (options,args)=parser.parse_args()

    #save parameters in an extra variable
    input_dir= options.i
    ann_out_file = options.o

    # read binary Python pickle file save.p file
    # it contains pmiddict, created by map_geneid_to_uniprotid.py
    pmiddict = pickle.load(open("save.p","rb"))

    # open the output csv file which contains all annotated abstract titles and texts
    ann_out = open(ann_out_file,"w")

    # get the list of downloaded abstracts files from interested directory of downloded abstracts
    os.chdir(input_dir)

    # get file names
    abstracts_list = filter(os.path.isfile, os.listdir( os.curdir ) )

    # iterate over all abstract files to annotate them
    for i in range(0,len(abstracts_list)) :
        #open every file to read
        curr_abstract_file = open(abstracts_list[i],"r")

        # get the PubMed ID from the name of curr_abstract_file
        pmid_obj = re.search('(\d{8})' , abstracts_list[i] , re.IGNORECASE)
        if pmid_obj :
            pmid = pmid_obj.group(1)

        # read the abstracts
        # check whether the current PubMed ID is contained in pmiddict
        if pmid in pmiddict :
            file_text = curr_abstract_file.read()
            # before processing title and text with annotate_abstract(), all "\n" have to be replaced with " "
            file_text = " ".join(file_text.split("\n"))

            # abstract title and abstract text have to be extracted from file_text
            # if an abstract has no abstact text, the title is encoded within the <p></p> elements
            text_obj = re.search('<p>(.*)</p>' ,file_text ,re.IGNORECASE)
            title_obj = re.search('<article-title>(.*)</article-title>' ,file_text ,re.IGNORECASE)
            if title_obj :
                title = title_obj.group(1)
                text = text_obj.group(1)
            else:
                # debug:
#                print pmid
                title = text_obj.group(1)
                text = None

            # annotate texts and write them to the CSV file ann_out
            annotate_abstract(text,title,pmid)
            # debug:
#            print "abstract number",i,"with pmid=",pmid,"had been annotated","\n"
        else:
            # debug:
            print "abstract with pmid=",pmid,"was missing in pmiddict","\n"

    # change back to the main directory
    os.chdir("..")

    # close output file
    ann_out.close()





