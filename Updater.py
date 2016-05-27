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


import Functions
from shutil import copyfile
from os import system

# Get list of Files to update
print "Preparing for update..."
list_of_files = Functions.getListOfFilesToUpdate()

# Copy files
for filename in list_of_files:
    source = "update\\" + filename

    if '/' in filename:
        source = "update\\" + filename.split('/')[1]
        destination = filename.replace('/', '\\')

    else:
        source = "update\\" + filename
        destination = filename

    print "Copy file " + source + "to " + destination
    copyfile(source, destination)

# Delete update folder
Functions.deleteUpdateFolder()

# Run PROPheT.exe
system("PROPheT.exe")
