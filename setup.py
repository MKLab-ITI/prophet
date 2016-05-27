"""
This file is part of the PROPheT tool.

Copyright (C) 2016: MKLab <pmitzias@iti.gr; mriga@iti.gr; skontopo@iti.gr>

http://mklab.iti.gr/project/prophet-ontology-populator
https://github.com/MKLab-ITI/prophet

Licensed under the Apache License, Version 2.0 (the "License").
You may use this file in compliance with the License. 
For more details, see LICENCE file. 

"""

__authors__ = 'Panagiotis Mitzias (pmitzias@iti.gr), Marina Riga (mriga@iti.gr)'


from distutils.core import setup
import py2exe
 
setup(
    windows = [{
            "script":"Main.py",
            # "script":"D:\\Ontology Population Tool\\Workspace\\Main.py",
            "icon_resources": [(1, "images\\prophet_icon.ico")]
            # "icon_resources": [(1, "D:\\Ontology Population Tool\\Workspace\\dist\\images\\prophet_icon.ico")]
            }],
    options = {
        "py2exe": {
            "includes": ["sip", "PyQt4.QtGui", "PyQt4.QtCore"],
            "packages":["SPARQLWrapper", "rdflib", "isodate"],
            'bundle_files': 3,
        }
    }
)

"""
NOTES
- sip package is always required
- isodate package is required by RDFLib
"""
