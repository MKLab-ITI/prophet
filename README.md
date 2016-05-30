#PROPheT Ontology Populator

Description
-------------
PROPheT (PeRicles Ontology Population Tool) is a novel application that enables **instance extraction** and **ontology population** from Linked Data, using a user-friendly graphical user interface (GUI). In PROPheT, concepts, i.e. realisations of entities, and relations populated in online Linked Data sources (such as <a href="http://wiki.dbpedia.org/" target="_blank">DBPedia</a>) can be located, filtered and inserted into a user’s own domain ontology. 

PROPheT offers **three** types of instance extraction-related functionalities (*instance-based populating*, *class-based populating* and *instance enrichment*) along with **user-driven mapping** of data properties. It is flexible enough to work with any domain ontology (written in OWL) and any RDF Linked Data set that is available via a SPARQL endpoint. 

Features
-----------
PROPheT offers the following key features:
* Three modes of instance extraction-related functionalities.
* User-driven mapping of data properties.
* Importing a domain ontology (over HTTP or locally).
* Exporting the populated ontology in the most popular formats (.*owl*, .*rdf*, .*ttl*, .*nt* and .*n3*).
* Flexibility to seamlessly work with any domain ontology (written in OWL) and any Linked Data resource that is available via a SPARQL endpoint.
* Elimination of redundancy in the instance set by handling duplicates.
* User-friendly GUI with enriched display of content and information, as well as useful function utilities for the user. 

Requirements
---------------
PROPheT tool is written in Python 2.7.

Instructions
--------------
1. Install Python 2.7 in your computer.
2. Clone the project locally in your computer.
3. Open command prompt and change directory to the local path of the stored project:
    ``` cd "C:\your_path_to_project" ```
4. Run Main.py through the command:
    ``` "C:\your_path_to_python27_library\python.exe" Main.py ``` 

  ![cmd_image](https://raw.githubusercontent.com/MKLab-ITI/prophet/master/images/cmd.PNG)


Documentation
--------------
The official documentation of PROPheT is [here](http://mklab.iti.gr/prophet/).

Credits
-------------
PROPheT was created by <a href="http://mklab.iti.gr/" target="_blank">MKLab group</a> under the scope of <a href="http://pericles-project.eu/" target="_blank">PERICLES</a> FP7 Research Project.

![prophet logo](http://mklab.iti.gr/prophet/_static/logo.png)  ![mklab logo](http://mklab.iti.gr/prophet/_static/mklab_logo.png)  ![pericles logo](http://mklab.iti.gr/prophet/_static/pericles_logo.png)
