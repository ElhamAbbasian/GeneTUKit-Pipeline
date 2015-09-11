#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
    Copyright (c) 2015, Elham Abbasian <e_abbasian@yahoo.com>, Kersten Doering <kersten.doering@gmail.com>

    This script selects title and abstract texts from a PostgreSQL database which can be built with PubMed2Go before (here: pancreatic_cancer_db from the PubMed2Go documentation). The input is a list of PubMed IDs, e.g. taken from the PostgreSQL tables pubmed.tbl_medline_citation or pubmed.tbl_abstract. It is also possible to directly use the NCBI download file (default: pubmed_result.txt) as described in the PubMed2Go documentation. Every document for the given list of PubMed IDs is saved in NXML format (used in the BioCreAtIvE III challenge and by GeneTUKit: http://www.qanswers.net/GeneTUKit/help.html). If a publication does not contain an abstract in PubMed, the title is saved within the abstract XML tags to be classified by GeneTUKit.
"""

# to connect to the PostgreSQL database
import psycopg2
# join paths to files and folders
import os
# escape special characters in XML documents
from xml.sax.saxutils import escape
# parser for command-line options
from optparse import OptionParser

# connect to PostgreSQL database
def connect_postgresql():
    # connection parameters
    connection = psycopg2.connect("dbname='"+postgres_db+"' user='"+postgres_user+"' host='"+postgres_host+"' password='"+postgres_password+"'")
    cursor = connection.cursor()
    return connection , cursor

# disconnect from PostgreSQL database
def disconnect_postgresql(connection, cursor):
    cursor.close()
    connection.close()

#get title and abstract with LEFT OUTER JOIN, if there is no abstract text, the secon value in the tuple to be returned is None
#general command (without specific PubMed ID):
#select a.pmid, a.article_title,b.abstract_text from pubmed.tbl_medline_citation a LEFT OUTER JOIN pubmed.tbl_abstract b ON a.pmid = b.fk_pmid;
def get_abstract(cursor,pmid):
    stmt =  """
            SELECT
                a.article_title, b.abstract_text
            FROM
                pubmed.tbl_medline_citation a
            LEFT OUTER JOIN
                pubmed.tbl_abstract b
            ON
                a.pmid = b.fk_pmid
            WHERE
                a.pmid = %s;
            """
    #specify the PubMed ID (can be extended to an array by using IN and round brackets with a list of PubMed IDs)
    cursor.execute(stmt,(pmid,))
    #return a tuple with title and text or title and None (or None and None, if a PubMed ID is not contained in the PostgreSQL database)
    output = cursor.fetchone()
    return output

#Add xml tags at the beginning and end of the text , and around the title text
def add_xml_tag(title,abstract):
    if abstract:
        # add xml tags for title and text
        abstract = "<article><article-meta><title>"+ escape(title) + "</title><abstract><p>" + escape(abstract) + "</p></abstract></article-meta></article>"
    else:
        # add the title in abstract text XML tags without the title tag
        abstract = "<article><article-meta><abstract><p>" + escape(title) + "</p></abstract></article-meta></article>"
    #return the modified article in NXML format 
    return abstract

########################################### MAIN PART OF THE SCRIPT ################################################

if __name__=="__main__":
    parser= OptionParser()
    parser.add_option("-i", "--input", dest="i", help='name of the input file containing pmids',default="pubmed_result.txt")
    parser.add_option("-o", "--output", dest="o", help='name of the output folder containing all downloaded abstracts',default="downloaded_abstracts")
    parser.add_option("-d", "--database", dest="d", help='name of the PostgreSQL database to connect to',default="pancreatic_cancer_db")
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

    #connect to PostgreSQL
    postgres_connection , postgres_cursor = connect_postgresql()

    #getting all the pmids from "pubmed_result.txt" file and saving in a dictionary
    pmids_list = []
    pmids_file = open (input_pmid,"r")
    for line in pmids_file :
        pmids_list.append(line.strip())
    pmids_file.close()

    # iterate over PubMed IDs and save each article in an XML document with NXML tags
    for pmid in pmids_list:
        article = get_abstract(postgres_cursor,pmid)
        # if a PubMed ID is not contained in the PostgreSQL database, continue with the next one
        if not article:
            print "This PubMed ID is not containd in the PostgreSQL database: ", pmid
            continue
        else:
            # add NXML tags to article texts of title and abstract (escaped within the function add_xml_tag())
            abstract_tagged = add_xml_tag(article[0],article[1])
        # save each article with its PubMed ID in an extra file
        nxml_file = pmid+".nxml"
        # write to file in the declared output folder (add XML header)
        nxml_file_w = open(os.path.join(output_directory,nxml_file),"w")
        nxml_file_w.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        nxml_file_w.write(abstract_tagged)
        nxml_file_w.close()

    # disconnect from PostgreSQL
    disconnect_postgresql(postgres_connection, postgres_cursor)

