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
# this function is called inside annotate_abstract()
def remove_nested_tagging(ann_text):
    # flag is used to repeat the procedure of removing misplaced inner tags
    flag = True
    # each time, a nested tag is found, flag is set to True to check the fragment again
    while flag:
        # assume that there are no inner tags
        flag = False
        # check all pairs of opening and closing tags
        test = [(a.start(), a.end()) for a in list(re.finditer('<protein-id=\"[A-Z].*?">(.*?)</protein-id>', ann_text))]
        # sort them reversely such that a later iteration step is still consistent with the positions after text concatenation
        test.sort(reverse=True)
        # check whether there is a nested tag inside these pairs
        # each pair is considered with the first opening and the first closing tag
        for elem in test:
            # if the last tag ends with a quotation mark, there are two opening tags
            test2 = [(a.start(), a.end()) for a in list(re.finditer('\">(.*?)<protein-id=\"[A-Z].*?">(.*?)</protein-id>', ann_text[elem[0]:elem[1]]))]
            # if there are nested tags, the length of the list is greater than zero
            if len(test2)>0:
                # group(0) is the whole text fragment
                # group(2) is the whole inner text fragment with the nested tags
                # group(4 ) is the tagged term inside the nested tags
                # replace the whole inner text fragment in nested tags with the term
                m = re.search('\">(.*?)((<protein-id=\"[A-Z].*?">)(.*?)(</protein-id>))',ann_text[elem[0]:elem[1]])
                ann_text = ann_text[0:elem[0]] + ann_text[elem[0]:elem[1]].replace(m.group(2),m.group(4)) + ann_text[elem[1]:]
                # set flag to True, because there might be more than one inner tag
                flag = True
    # return annotated text without misplaced inner tags
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





