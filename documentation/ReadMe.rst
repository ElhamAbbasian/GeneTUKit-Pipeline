=========================================================
Protein Annotation of PubMed XML Abstracts with GeneTUKit
=========================================================


************
Introduction
************

- The following pipeline annotates genes/proteins in a set of PubMed abstracts with GeneTUKit.

- It uses PubMed2Go to build a PostgreSQL database from PubMed XML files that can be downloaded from NCBI.

- Start by copying the whole project folder from GitHub to your local disk.

- The pipeline was tested on a Linux system with Ubuntu 14.04.

- The following flow chart shows the order of the pipeline scripts and their input and output files.

.. image:: flowchart.jpg


****************************
Download of PubMed Abstracts
****************************

- The title and abstract part of requested PubMed XML documents can be accessed with PubMed2Go:

    - https://github.com/KerstenDoering/PubMed2Go/wiki

- The PubMed2Go documentation shows how to download a data set and build a PostgreSQL relational database. Follow the installation instructions. The part describing how to build a Xapian full text index is not needed here:

    - https://github.com/KerstenDoering/PubMed2Go/blob/master/documentation/quick_install.rst

- This documentation refers to the PubMed2Go example data set processing texts which deal with the disease pancreatic cancer.

- The script download_articles.py reads the PubMed IDs in the file pubmed_result.txt. Four randomly selected abstracts with the PubMed IDs 10025831, 23215050, 24622518, and 24842107 were selected from the PostgreSQL database and saved in the folder downloaded_abstracts in pseudo XML format using this script. 

    - The script can be run with "python download_articles.py" and modified with the name of the database, output folder, and input file (use "python download_articles.py -h" for more information).

- Unfortunately, the plain text parameter in GeneTUKit does not work. That is the reason for using pseudo XML files. These XML tags are required to run GeneTUKit in XML mode and to recognise the title and text separately.

- The following steps cannot only be applied to PubMed XML abstracts, but to any texts that are given in NXML format.

- NXML is a data structure used in BioCreAtIvE III and the example on the GeneTUKit homepage refers to this document:

    - http://www.qanswers.net/download/genetukit/1934391.nxml

- The mandatory XML structure used by GeneTUKit is <article><article-meta><article-title> TITLE </article-title><abstract><p> ABSTRACT </p></abstract></article-meta></article>.

- If no abstract text is provided by PubMed, the structure is <article><article-meta><abstract><p> TITLE </p></abstract></article-meta></article>. In this special case, the title has to be encoded within the abstract tags to be recognised by GeneTUKit.

- In XML documents, certain characters are not allowed in normal text, e.g. "<" and "&". Therefore they are escaped by the script and replaced with their ASCII codes.


*************************************
Gene/Protein Extraction wit GeneTUKit
*************************************

- The extraction of gene/protein names is done by running GeneTUKit and the output is saved in a CSV file.

- The latest version of GeneTUKit can be freely downloaded from http://www.qanswers.net/GeneTUKit/download.html.

- There is also a link providing the latest EntrezGene data set (gene_info.gz). This file has to be downloaded and copied into the EntrezGene directory of the downloaded GeneTUKit folder.

- To install GeneTUKit, step one and three from the official help page (http://www.qanswers.net/GeneTUKit/help.html) are mandatory for using the pipeline presented herein.

- In this pipeline, the GeneTUKit installation with the default MySQL version was tested. Therefore, the GeneTUKit config file does not have to be changed.

    - It is possible to connect to a MySQL database via command-line with "mysql -u root -p".

- Install the latest MySQL database client and server version. Although the GeneTUKit documentation recommends the extra download of the jdbc driver JAR package for this database engine, this was not needed in the test system with Ubuntu 14.04 LTS.

- Copy the folder downloaded_abstracts with the NXML files generated in the last section into the new GeneTUKit directory.

- GeneTUKit is using CRF++ for NER (Name Entity Recognition), but the link provided by the just mentioned GeneTUKit page leads to a repository requiring a password. It's also possible to use BANNER for this purpose. Running GeneTUKit with a single NXML file (with BANNER) works as follows:

    - java -Djava.library.path=. -jar genetukit.jar -x downloaded_abstracts/23215050.nxml -banner

- If you want to process multiple files at ones, use the batch mode by providing the folder name instead of a file name:

        - java -Djava.library.path=. -jar genetukit.jar -x downloaded_abstracts -banner

- With ">", the output is piped to the output file gtk_output.csv and the Java library path can probably be omitted:

        - java -jar genetukit.jar -x downloaded_abstracts -banner > gtk_output.csv

- The running time for this step on a test data set of 5000 abstracts was around 5 h with a 2 GHz single core CPU. 


******************************
Modifying the GeneTUKit output
******************************

- From the output given by GeneTUKit (e.g. GeneTUKit/gtk_output.csv), the required values PubMed ID, gene ID, and the synonyms are saved in a new CSV file named pmid_geneid_syn.csv ("python filter_out_genetukit_output.py", executed from the original GitHub project folder GeneTUKit-Pipeline)

    - The default parameters can be shown with parameter "-h".

- GeneTUKit also provides an organism ID and a score for each prediction's certainty. These values are not further processed in this script, but it is reasonable to consider especially the prediction score.


**********************************
Mapping of UniProt IDs to Gene IDs
**********************************

- Each gene ID provided by GeneTUKit has to be mapped to its respective UniProt ID. Using UniProt IDs brings up the advantage of being able to access their sequenes (http://www.uniprot.org). The UniProt IDs are contained in idmapping.dat.gz. This file can be downloaded here and has to be extracted in the main project folder (GeneTUKit-Pipeline):

    - ftp://ftp.ebi.ac.uk/pub/databases/uniprot/current_release/knowledgebase/idmapping/

    - The file idmapping.dat.gz also contains some unrelated information. By running filter_idmapping.py with the option "-t", only the related gene IDs and UniProt IDs from pmid_geneid_syn.csv are saved in "filtered_idmapping.csv". The converted file is also saved in the main directory.

    - The option of using the test case with a small number of gene IDs was used to complete the example presented in this documentation. In general, all gene IDs are needed to extract the appropriate UniProt ID from idmapping.dat.

- The mapping process of storing PubMed ID, (mapped) gene ID, synonym(s), and UniProt ID(s) for each different synonym is executed with map_geneid_to_uniprotid.py.

- The script reads the file filtered_idmapping.csv by importing the script map_to_dict.py, which creates a dictionary data structure, containing the gene IDs as keys and the UniProt IDs as values.

    - This dictionary is used to create the output file merged_file.csv with one line per synonym (tab-separated): PubMed ID, gene ID, synonym, UniProt ID(s).

    - The script also creates a second file is which is a dictionary of dictionaries from PubMed IDs, containing all synonyms of an abstract as keys with all UniProt IDs as values. This output is stored as the Python pickle file "save.p" to be used within the next pipeline step.

- The script can be run without additional parameters:

    - python map_geneid_to_uniprotid.py


******************************
Annotation of PubMed Abstracts
******************************

- The gene/protein tags are added to the provided XML files with the following command: 

    - python annotate_abstracts.py -i downloaded_abstracts

- The script takes the path to the downloaded pseudo XML texts specified by the parameter "-i" and the list of synonym-UniProt ID pairs saved in the dictionary save.p from the last step. The tagged abstract titles and texts are saved tab-separated in a CSV file named annotated_abstracts.csv, each row a new PubMed ID (without pseudo XML tags).

- All abstract texts and titlse are separately searched for each synonym. The implementation takes care for nested tags in a way that it only highlights the longest matching synonym (function remove_nested_tagging()).


*******
Contact
*******

- Please, write an e-mail, if you have questions, feedback, improvements, or new ideas:

    - e_abbasian@yahoo.com

    - kersten.doering@pharmazie.uni-freiburg.de

- If you are interested in related projects, visit our working group's homepage:

    - http://www.pharmaceutical-bioinformatics.de

- This project is published with an ISC license given in "license.txt".
