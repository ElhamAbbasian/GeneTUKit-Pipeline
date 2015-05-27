#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>
"""

#Elham 27.10.2014
#This scripts suppose to fetch all the downloaded abstracts .nxml files from related abstract folder , which we will set it as the current directory in command line , 
#try to read the data , abstract title and abstract text , annotate them and will save with its "pmid"..."ann_abs_title"..."ann_abs_text" , into a big .csv file .

import os
import re
import pickle

#optparse - Parser for command line options
from optparse import OptionParser

#Function which does the more important part : Annotate the existing "proteins" in title and text of downloaded abstract .  
def annotate_abstract(abstext,abstitle,pmid):
    #This function should search for synonyms from "merged_file.csv" file in text and title of the abstract , and replace them with a tag like:
    #<potein-id = \unipotid1,unipotid2,....\> synonym </protein>

    #new taged title and new tagged abstract text
    title_new = abstitle.decode('utf-8')
    text_new = abstext.decode('utf-8')

    #define the term enclosed in brackets - <term>
    tag = "protein-id"

    #go through list of search itemes and highlight each one that was identified
    #re.escape(string) :Return string with all non-alphanumerics backslashed; this is useful if you want to match an arbitrary literal string that may have regular expression metacharacters in it.
    #IGNORECASE(re.I) :    Perform case-insensitive matching; expressions like [A-Z] will match lowercase letters, too. This is not affected by the current locale.
    #re.compile(pattern, flags=0) : Compile a regular expression pattern into a regular expression object, which can be used for matching using its match() and search() methods, described below.

    for key in pmiddict[pmid]:
        #upid = ",".join(pmiddict[pmid][key])
        upid = pmiddict[pmid][key]

        #return a regular expression that can find 'peter' only if it's written alone (next to space, start of string, end of string, comma, etc) but not if inside another word like peterbe 
        pattern = re.compile("\\b" + re.escape(key) + "\\b",re.I)

        (title_new,count1) = re.subn(pattern,u'<%(tag)s=\"%(uniprotid)s\">%(word)s</%(tag)s>' % dict(tag=tag, word=key, uniprotid=upid),title_new)
        (text_new,count2) = re.subn(pattern,u'<%(tag)s=\"%(uniprotid)s\">%(word)s</%(tag)s>' % dict(tag=tag, word=key, uniprotid=upid),text_new)

    #Here after compelate annotation, check for nested tagging for both abstract_title and abstract_text
    title_new=remove_nested_tagging(title_new)
    text_new=remove_nested_tagging(text_new)

    #write the annotated abstract title and text in ann_out file .
    t_new = text_new.encode('utf-8')
    ti_new = title_new.encode('utf-8')
    ann_out.write(pmid+"\t"+ti_new+"\t"+t_new+"\n")


##################################################################################################################

#Elham 19.01.15
#After tagging the abstracts , some abstracts has nested annotations, which is false and has to be fix . In the way that inner annotation should be deleted.
#For thsi issue, I will have a loop over all annotated abstracts , in the way of ,directly after tagging the abstracts title and text , before witing in .csv file , check for nested tagging
#and fix it .
#I will define a new function for this issue and call it inside the annotate_abstract function.
def remove_nested_tagging(ann_text) :

    #get the list of (start,end) positions which shows the boundries of annotations.
    #1.fisrt find the single and inner tags
    inner_positions =  [(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text))]
    #print "inner position",inner_positions,"\n"

    #2.find all big pattern which has some nested tagging inside , then add them to the positions list
    nessted_positions_typ1 =[(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">([\w+\-]+)(<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>)+<\/protein-id>',ann_text))]
    nessted_positions_typ2 =[(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">(<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>)+([\s\w+\-]+)<\/protein-id>',ann_text))]
    nessted_positions_typ3 =[(a.start(), a.end()) for a in list(re.finditer('<protein-id="([\w{6}\,]+)">(<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>)+<\/protein-id>',ann_text))]
    #print "outer positions typ1",nessted_positions_typ1,"\n"
    #print "outer positions typ2",nessted_positions_typ2,"\n"

    #combine the two lists
    positions=[]
    positions+=inner_positions
    positions+=nessted_positions_typ1
    positions+=nessted_positions_typ2
    positions+=nessted_positions_typ3

    #sort the positions list , reversely
    positions.sort(reverse=True)
    #print "list of positions:",positions,"\n"

    #delete the repeated entries from positions list
    #positions=list(set(positions))

    #define an empty list as the blacklist , which will be contain the inner nested tags that should be deleted from text.
    blacklist=[]

    #Do a for loop over the positions list but check if one of the nessted_positions list has at least one element inside , it means
    #in the inner_positions there is/are some nessted tags

    #if not len(positions) == 0 and len(positions)>1 :
    if len(nessted_positions_typ1) > 0 or len(nessted_positions_typ2) > 0 or len(nessted_positions_typ3) > 0 :
        if len(positions) == 2 :
            blacklist=inner_positions
        else:
            for elemi in range(0,len(positions)-1) :
                elemj=elemi+1
                if positions[elemi][0] < positions[elemj][1]:
                    blacklist.append(positions[elemi])

        #delete the probably repeated items in blacklist
        blcklist=list(set(blacklist)) 
        #print "blacklist=",blacklist
    #elif:
        #in this case , all the founded tags listed in inner_positions are single tagging .
        #then the text can return without any changes
        


    #check if blacklist is empty, it means that there is no nested tagging for this text and can continue with the next text :
    if len(blacklist) > 1 :
        for i in range(0,len(blacklist)) :
            #check if element i and element i+1 has overlapping
            j = i+1

            #have to check separetely if j is out of range of i
            if j == len(blacklist) :
                syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[i][0]:blacklist[i][1]]).group(2)
                ann_text = ann_text[0:blacklist[i][0]] + syn + ann_text[blacklist[i][1]:]
            else :
                if blacklist[i][0] < blacklist[j][1]:
                    #it means they are overlapped , first have to get the synonym inside the start-end position of text and update the text.
                    syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[i][0]:blacklist[i][1]]).group(2)
                    ann_text = ann_text[0:blacklist[i][0]] + syn + ann_text[blacklist[i][1]:]

                    #because this element has overlapping whith next pair(element i+1) , then the end of next pair should be updated .
                    #it has to be constructed from the length of last pattern maching (<ptotein-id=...>...</protein-id>) expet length of exported synonym.
                    blacklist[j][1] -= (blacklist[i][1]-blacklist[i][0]-len(syn))

                else :
                    #means they are not averlapping and text should just be updated
                    syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[i][0]:blacklist[i][1]]).group(2)
                    ann_text = ann_text[0:blacklist[i][0]] + syn + ann_text[blacklist[i][1]:]

    elif len(blacklist) == 1 :
        #in this case it doesn't need to have a loop , we can just update the text according to the exsiting pair.
        syn = re.match('<protein-id="([\w{6}\,]+)">([\w+\-]+)<\/protein-id>',ann_text[blacklist[0][0]:blacklist[0][1]]).group(2)
        #print syn,"\n"
        ann_text = ann_text[0:blacklist[0][0]] + syn + ann_text[blacklist[0][1]:]

    #print ann_text,"\n"
    return ann_text

########################################### MAIN PART OF THE SCRIPT ################################################

if __name__=="__main__":

    parser= OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the directory containing one group of abstracts',default="abstracts-group1")

    (options,args)=parser.parse_args()

    #save parameters in an extra variable
    input_dir= options.i

    #following command try to fetch save.p file , which contains pmiddict , build from make_merged_file.py scipt .
    pmiddict = pickle.load(open("save.p","rb"))

    #define the output big file which contains all annotated abstract title and abstarct text .
#    ann_out_file = "annottedfile_bigfile.csv"
    ann_out_file = "annotated_abstracts.csv"
    ann_out = open(ann_out_file,"w")

    #get the list of downloaded abstracts files from interested directory of downloded abstracts
    cmd =input_dir+"/"
    os.chdir(cmd)

    abstracts_list = filter(os.path.isfile, os.listdir( os.curdir ) )

    #do a loop over all the abstracts files to annotate them
    for i in range(0,len(abstracts_list)) :
        #open every file to read
        curr_abstract_file = open(abstracts_list[i],"r")

        #here "pmid" number has to extract from curr_abstract_file name 
        pmid_obj = re.search('(\d{8})' , abstracts_list[i] , re.IGNORECASE)
        if pmid_obj :
            pmid = pmid_obj.group(1)

        #go through the content of each file
        #Elham 13.1.15
        #but with the condition of existing the pmid in pmiddict .
        if pmid in pmiddict :
            file_text = curr_abstract_file.read()
            file_text = " ".join(file_text.split("\n"))

            #abstract title and abstract text has to be extracted from file_text
            #before sending the title and text to the function to annotate the existing proteins , have to replace all the newlines("\n") with " "(space) .

            text_obj = re.search('<p>(.*)</p>' ,file_text ,re.IGNORECASE)
            if text_obj :
                text = text_obj.group(1)

            title_obj = re.search('<title>(.*)</title>' ,file_text ,re.IGNORECASE)
            if title_obj :
                title = title_obj.group(1)


            #now the title and text are ready to sending to funtion for annotation . 
            annotate_abstract(text,title,pmid)

            print "abstract number",i,"with pmid=",pmid,"had been annotated","\n"
        else:
            print "abstract with pmid=",pmid,"was missing in pmiddict","\n"



    #back to the min directory
    cmd=".."
    os.chdir(cmd)

    ann_out.close()





