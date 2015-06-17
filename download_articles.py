#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>
"""

#Elham 27.10.2014
#extracting abstarct text and titel from PSQL DB by PubMed2Go and join them as a row in .nxml file
#in a way that having like : """" pmid title text """"

#according to the pmids in "tbl_pmids_in_file" form "Pancreatic_cancer_db" try to download the abstract titles from "tbl_medline_citation" and abstract texts
#from "tbl_abstract"

# to connect to the PostgreSQL database
import psycopg2
from psycopg2 import extras

import os
import subprocess
import re

#optparse - Parser for command line options
from optparse import OptionParser

#(dis)connection to mongo and psql database
def connect_postgresql():
    connection = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"'")
    
    #normal connection.cursor() gives back a list of tuples with fetchall(), DictCursor gives back a list of lists
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return connection , cursor


def disconnect_postgresql(connection, cursor):
    cursor.close()
    #connection.ommit()
    connection.close()

#Run the SQL command to download the abstract text from PostgreSQL DB
def get_abstract(cursor,pmid):
    #sql command should be like this : 
    #select abstract_text from pubmed.tbl_abstract where fk_pmid=pmid;
    stmt = """
            SELECT
                abstract_text
            FROM
                pubmed.tbl_abstract
            WHERE
                fk_pmid = %s;
            """
    #when we want to give a parameter for a WHERE clause , type in :
    cursor.execute(stmt,(pmid,))

    #return list of list with fetchall() and DictCursor
    #here we use fetchone() to return Row or none
    output = cursor.fetchone()
    return output

#Run the SQL command to download the abstract title from PostgreSQL DB
def get_title(cursor,pmid):
    #sql command should be like this :
    #select article_title from pubmed.tbl_medline_citation where pmid='......';
    stmt =  """
            SELECT
                article_title
            FROM
                pubmed.tbl_medline_citation
            WHERE
                pmid = %s;
            """
    cursor.execute(stmt,(pmid,))
    output = cursor.fetchone()
    return output

#Add xml tags at the beginning and end of the text , and around the title text .
def add_xml_tag(abstract,title):

    # add xml tags at the first and end of abstract file
    abstract = "<article><article-meta><title>"+ title+ "</title><abstract><p>" + abstract + "</p></abstract></article-meta></article>"
    
    #return the modified abstract text , which is changed to nxml format via adding tags at first and end of text .
    return abstract

###########################################MAIN PART OF THE SCRIPT ################################################

if __name__=="__main__":

    parser= OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the input file containing pmids',default="pubmed_result.txt")
    parser.add_option("-o", "--output", dest="o", help='name of the output folder containing all downloaded abstracts',default="downloaded_abstracts")
    parser.add_option("-d", "--database", dest="d", help='name of the database to connect to',default="pancreatic_cancer_db")
    (options,args)=parser.parse_args()

    #save parameters in an extra variable
    input_pmid = options.i
    output_directory = options.o

    #settings for psql connection
    postgres_user       ="parser"
    postgres_password   ="parser"
    postgres_host       ="localhost"
    postgres_port       ="5432"
    postgres_db         =options.d

    #connect
    postgres_connection , postgres_cursor = connect_postgresql()

    #getting all the pmids from "pubmed_result.txt" file and saving in a dictionary
    pmids_list = []
    pmids_file = open (input_pmid,"r")

    for line in pmids_file :
        line.strip()
        pmids_list.append(line)

    pmids_file.close()

    #runing throgh all pmids, get each title and each abstract text , try to tagged them and save in a .nxml file .
    for pmid in pmids_list :
        
        abstract_text = get_abstract(postgres_cursor,pmid)

        if (abstract_text) :
            if "<" in abstract_text[0] :
                abstract_text[0] = re.sub("<","&lt;",abstract_text[0])
            if "&" in abstract_text[0] :
                abstract_text[0] = re.sub("&","&amp;",abstract_text[0])

            abstract_title = get_title(postgres_cursor,pmid)

            if "<" in abstract_title[0] :
                abstract_title[0]=re.sub("<","&lt;",abstract_title[0])
            if "&" in abstract_title[0] :
                abstract_title[0] = re.sub("&","&amp;",abstract_title[0])

            #add XML tags to the beginnign and end of abstract file
            abstract_tagged = add_xml_tag(abstract_text[0],abstract_title[0])

            # save each abstracts with its title in an extra file
            nxml_file = pmid+".nxml"
            nxml_file="".join(nxml_file.split("\n"))
            # write to file in the declared output folder
            nxml_file_w = open(os.path.join(output_directory,nxml_file),"w")
   
            nxml_file_w.write(abstract_tagged)
            nxml_file_w.close()

        else :
            invalid_pmid_list =[]
            invalid_pmid_list.append(pmid)

    # disconnect
    disconnect_postgresql(postgres_connection, postgres_cursor)








    
