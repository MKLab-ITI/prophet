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

from SPARQLWrapper import SPARQLWrapper, JSON
import sqlite3, urlparse, webbrowser, urllib, urllib2, os
from PyQt4 import QtCore, QtGui
from datetime import datetime
from Tkinter import Tk
from shutil import rmtree
from PyQt4.QtGui import QTreeWidgetItem

from rdflib.namespace import Namespace
from rdflib import RDF, URIRef, Literal

# myDB filepath
myDB_Filepath = "database\\myDB.sqlite"
logDB_Filepath = "database\\log.sqlite"
settingsDB_Filepath = "database\\settings.sqlite"

# Versioning urls
latest_version_folder = "https://dl.dropboxusercontent.com/u/27469926/PROPheT_Latest_Version/"

# Define prefixes
rdf = "prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> "
rdfs = "prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
obj = "prefix obj: <https://dl.dropboxusercontent.com/u/3157623/ontologies/pericles/sba-a#> "
cl = "prefix cl: <https://dl.dropboxusercontent.com/u/3157623/ontologies/pericles/sba-t#> "
dc = "prefix dc: <http://purl.org/dc/elements/1.1/> "
prov = "prefix prov: <http://www.w3.org/ns/prov#> "
foaf = "prefix foaf: <http://xmlns.com/foaf/0.1/> "
xml = "prefix xml: <http://www.w3.org/2001/XMLSchema#> "
owl = "prefix owl: <http://www.w3.org/2002/07/owl#> "
core = "prefix core: <http://purl.org/NET/cidoc-crm/core#> "
# dbo = "prefix dbo: <http://dbpedia.org/ontology/> "
# dbr = "prefix dbr: <http://dbpedia.org/resource/> "
# dbp = "prefix dbp: <http://dbpedia.org/property> "

prefixes = rdf + rdfs + obj + cl + dc + prov + foaf + xml + owl + core


# Get setting from the DB
def getSettingFromDB(setting):
    conn = sqlite3.connect(settingsDB_Filepath)

    with conn:

        cur = conn.cursor()

        cur.execute('SELECT ' + setting + ' FROM settings')

        value = cur.fetchone()

    conn.close()

    return value[0]

# Set setting to DB
def setSettingToDB(setting, new_value):
    conn = sqlite3.connect(settingsDB_Filepath)

    with conn:

        cur = conn.cursor()

        cur.execute('UPDATE settings SET ' + setting + ' = "' + str(new_value) + '"')

    conn.close()

# Get the current endpoint URL setting from the DB
def getEndpointURL():

    return getSettingFromDB('endpoint_url')

# Get the current endpoint name setting from the DB
def getEndpointName():
    conn = sqlite3.connect(myDB_Filepath)

    with conn:

        cur = conn.cursor()

        cur.execute("SELECT name FROM endpoints WHERE endpoint = '" + getEndpointURL() + "'")

        value = cur.fetchone()

    conn.close()

    return value[0]

# Set the endpoint URL setting to the DB
def setEndpointURL(oldUrl, newUrl):

    # Set the new URL to the database
    setSettingToDB('endpoint_url', str(newUrl))

    # conn = sqlite3.connect(settingsDB_Filepath)
    #
    # with conn:
    #
    #     cur = conn.cursor()
    #
    #     cur.execute('UPDATE settings SET endpoint_url = "' + str(newUrl) + '"')
    #
    # conn.close()

    # Check if the endpoint is reachable with the new URL
    if checkIfEndpointIsReachable():
        return True

    # If the new URL is not reachable, set the old URL again and return false
    else:
        # Set the old URL to the database
        setSettingToDB('endpoint_url', str(oldUrl))

        # conn = sqlite3.connect(settingsDB_Filepath)
        #
        # with conn:
        #
        #     cur = conn.cursor()
        #
        #     cur.execute('UPDATE settings SET endpoint_url = "' + str(oldUrl) + '"')
        #
        # conn.close()

        return False

# Define a SPARQL SELECT function
def executeSparqlSelect(query, withLimit):

    # Compose query endpoint
    dataset_select = getEndpointURL() # + '/query'

    # Connect to ontology
    sparql = SPARQLWrapper(dataset_select)    

    # Add prefixes to query
    query = prefixes + query # + " LIMIT 20"

    # Add limit to query
    if withLimit:
        query = query + ' LIMIT ' + str(getSettingFromDB('em_instances_limit'))

    # Set query
    # sparql.setQuery(str(query))
    try:
        sparql.setQuery(query)
    # In case it is not unicode
    except TypeError:
        sparql.setQuery(unicode(query))

    # Set output to JSON
    sparql.setReturnFormat(JSON)

    try:
        # Execute query and return results
        return sparql.query().convert()
    except:
        return False

def executeSQLSelect(query, database_path = myDB_Filepath):
    conn = sqlite3.connect(database_path)

    with conn:
        cur = conn.cursor()
        cur.execute(str(query))
        values = cur.fetchall()
    conn.close()

    return values

def executeSQLSubmit(query, database_path = myDB_Filepath):
    query = unicode(query)
    conn = sqlite3.connect(database_path)

    with conn:
        cur = conn.cursor()
        cur.execute(query)
    conn.close()

    return

def checkIfProphetDatabase(fileWithPath):
    conn = sqlite3.connect(fileWithPath)

    query = "SELECT name FROM endpoints"

    try:
        with conn:
            cur = conn.cursor()
            cur.execute(query)
            values = cur.fetchall()
        conn.close()
    except:
        return False

    return True

def checkIfEndpointIsReachable():

    # Try to make a selection
    if executeSparqlSelect('SELECT ?x WHERE {?x ?y ?z} LIMIT 1', withLimit=False) == False:
        return False
    else:
        return True

def checkIfInternetConnectionIsOn():
    try:
        response=urllib2.urlopen('http://google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        pass
    return False

def prepareUrl(url_string):
        # Prepare Url to load to webview
        if 'http' not in url_string:
            url_string = 'http://' + url_string

        return QtCore.QUrl(url_string)

def checkIfStringIsValidUrl(url_string):

    parts = urlparse.urlsplit(url_string)

    if not parts.scheme or not parts.netloc:
        return False
    else:
        return True


#########################################################

def getListOfLanguagesFromDB():
    query = "SELECT name, code FROM languages"

    return executeSQLSelect(query)

def getListOfEndpointsFromDB():

    query = "SELECT * FROM endpoints"

    return executeSQLSelect(query)

def getListOfEndpointNamesFromDB():

    query = "SELECT name FROM endpoints"

    result_list = executeSQLSelect(query)
    name_list = []

    for result in result_list:
        # name_list.append(str(result[0]))
        name_list.append(result[0])

    return name_list

def getListOfEndpointUrlsFromDB():

    query = "SELECT endpoint FROM endpoints"

    result_list = executeSQLSelect(query)
    url_list = []

    for result in result_list:
        url_list.append(str(result[0]))

    return url_list

def getCurrentEndpointName():

    query = "SELECT name FROM endpoints WHERE endpoint = '" + getEndpointURL() + "'"

    return executeSQLSelect(query)[0][0]

def addEndpointToDatabase(name, url):

    query = "INSERT INTO endpoints VALUES ('" + name + "', '" + url + "')"

    executeSQLSubmit(query)

def deleteEndpointFromDatabase(name):

    query = "DELETE FROM endpoints WHERE name = '" + name + "'"

    executeSQLSubmit(query)

def updateNameOfEndpointInDatabase(new_name, url):
    query = "UPDATE endpoints SET name = '" + new_name + "' WHERE endpoint = '" + url + "'"

    executeSQLSubmit(query)


def updateUrlOfEndpointInDatabase(name, new_url):
    query = "UPDATE endpoints SET endpoint = '" + new_url + "' WHERE name = '" + name + "'"

    executeSQLSubmit(query)

#########################################################

def addEntryToLog(description):

    query = "INSERT INTO log (timestamp, description) VALUES ('" + datetime.now().strftime("%d-%m-%Y %H:%M:%S") + "', '" + description + "')"

    executeSQLSubmit(query, logDB_Filepath)

def clearLog():

    query = "DELETE FROM log"

    executeSQLSubmit(query, logDB_Filepath)

def getListOfLogEntries():

    query = "SELECT timestamp, description FROM log"

    return executeSQLSelect(query, logDB_Filepath)


#########################################################

def getListOfNamespaces():

    query = "SELECT * FROM namespaces ORDER BY prefix"

    return executeSQLSelect(query)

def prefixToURL(prefix):

    query = "SELECT url FROM namespaces WHERE prefix = '" + prefix + "'"

    result = executeSQLSelect(query)

    if len(result) != 0:
        return result[0][0]
    else:
        return prefix

def URLToPrefix(url):

    query = "SELECT prefix FROM namespaces WHERE url = '" + url + "' OR url = '" + url + "/'"

    result = executeSQLSelect(query)

    if len(result) != 0:
        return result[0][0]
    else:
        return url

def URLAndNameToPrefixAndName(text):
    # Try to split by hash tag
    if '#' in text:
        # Split by hash tag and pop the last element of the list
        url = text.split('#')
        del url[-1]

        # Join the list to have the url into a string
        try:
            url = '#'.join(url) + '#'
        # In case it is a QStringList and not a string
        except TypeError:
            url = url.join('#') + '#'

        # Name is the last element of the list
        name = text.split('#')[-1]

    # Try to split by slash
    else:
        # Split by hash tag and pop the last element of the list
        url = text.split('/')
        del url[-1]

        # Join the list to have the url into a string
        try:
            url = '/'.join(url)
        # In case it is a QStringList and not a string
        except TypeError:
            url = url.join('/')


        # Name is the last element of the list
        name = text.split('/')[-1]


    # Check if url exists in namespaces in DB and if yes, get the appropriate prefix
    prefixOrUrl = URLToPrefix(url)

    # Check if namespace was found in DB
    if prefixOrUrl == url:
        prexifFound = False
    else:
        prexifFound = True

    return {'namespace': prefixOrUrl, 'name': name, 'prefix_found': prexifFound}

# def getRDFPhrasePrepared(phrase):
#     # This function gets a url + a name
#     # (e.g. http://www.semanticweb.org/pmitzias/ontologies/2015/10/untitled-ontology-69#Artist)
#     # and returns the final result (prefix + name or url + name)
#
#     # Get phrase into Prefix and Name
#     splitPhrase = URLAndNameToPrefixAndName(phrase)
#
#     # If a prefix was found
#     if splitPhrase['prefix_found'] == True:
#         return splitPhrase['namespace'] + ':' + splitPhrase['name']
#     else:
#         return phrase

def getPhraseWithURL(phrase):
    # This function gets a phrase (url + name or prefix + name)
    # and returns a url + name
    # (e.g. http://www.semanticweb.org/pmitzias/ontologies/2015/10/untitled-ontology-69#Artist)

    # If it comes with a prefix
    if ('http' or 'HTTP' or 'Http') not in phrase:
        # Get prefix
        prefix = phrase.split(':')[0]
        temp_name = phrase.split(':')[1:]

        try:
            name = ':'.join(temp_name)
        # In case it is a QStringList and not a string
        except TypeError:
            name = temp_name.join(':')

        # Convert it to url
        url = prefixToURL(prefix)
        # Connect it with the name
        if (url[-1] != '#') and (url[-1] != '/'):
            phrase = url + '/' + name
        else:
            phrase = url + name

    return phrase

def getPhraseWithPrefix(phrase):
    # This function gets a phrase (url + name or prefix + name)
    # and returns a prefix + name
    # (e.g. my_ont:Artist)

    # If it comes with a url
    if ('http' or 'HTTP' or 'Http') in phrase:
        splitPhrase = URLAndNameToPrefixAndName(phrase)

        # If a prefix was found for this phrase
        if splitPhrase['prefix_found'] == True:
            phrase = splitPhrase['namespace'] + ':' + splitPhrase['name']

    return phrase

def getURLOfPhrase(phrase):
    # Gets a phrase
    # e.g. http://www.semanticweb.org/pmitzias/ontologies/2015/10/untitled-ontology-69#Artist or my_ont:Artist
    # and returns the url http://www.semanticweb.org/pmitzias/ontologies/2015/10/untitled-ontology-69#

    my_URLAndName = URLAndNameToPrefixAndName(phrase)
    return prefixToURL(my_URLAndName['namespace'])

def createInstaceURIFromNamespaceAndInstanceName(namespaceOrPrefix, instanceName):
    # example
    #   namespaceOrPrefix = http://www.semanticweb.org/ontologies/untitled-ontology#
    #   instanceName = 'FooBarInstance'
    # result http://www.semanticweb.org/ontologies/untitled-ontology#FooBarInstance


    # if it comes with a URL
    if ('http' or 'HTTP' or 'Http') not in namespaceOrPrefix:
        # convert prefix to url
        namespace = prefixToURL(namespaceOrPrefix)
    else:
        namespace = namespaceOrPrefix

    #if namespace ends with #
    if namespace[-1] == '#' or namespace[-1] == '/':
        return namespace + instanceName
    else:
        return namespace + '/' + instanceName

def getListOfNamespacePrefixesFromDB():

    query = "SELECT prefix FROM namespaces ORDER BY prefix"

    result_list = executeSQLSelect(query)
    prefix_list = []

    for result in result_list:
        prefix_list.append(str(result[0]))

    return prefix_list

def getListOfNamespaceUrlsFromDB():

    query = "SELECT url FROM namespaces ORDER BY url"

    result_list = executeSQLSelect(query)
    url_list = []

    for result in result_list:
        url_list.append(str(result[0]))

    return url_list

def addNamespaceToDatabase(prefix, url):

    query = "INSERT INTO namespaces VALUES ('" + prefix + "', '" + url + "')"

    executeSQLSubmit(query)

def deleteNamespaceFromDatabase(prefix):

    query = "DELETE FROM namespaces WHERE prefix = '" + prefix + "'"

    executeSQLSubmit(query)

def updatePrefixOfNamespaceInDatabase(new_prefix, url):
    query = "UPDATE namespaces SET prefix = '" + new_prefix + "' WHERE url = '" + url + "'"

    executeSQLSubmit(query)


def updateUrlOfNamespaceInDatabase(prefix, new_url):
    query = "UPDATE namespaces SET url = '" + new_url + "' WHERE prefix = '" + prefix + "'"

    executeSQLSubmit(query)

#########################################################

def getListOfMyModelsFromDB():

    query = "SELECT * FROM my_models ORDER BY name"

    return executeSQLSelect(query)

def getListOfMyModelNamesFromDB():

    query = "SELECT name FROM my_models ORDER BY name"

    result_list = executeSQLSelect(query)
    name_list = []

    for result in result_list:
        name_list.append(str(result[0]))

    return name_list

def getListOfMyModelUrlsFromDB():

    query = "SELECT url FROM my_models ORDER BY url"

    result_list = executeSQLSelect(query)
    url_list = []

    for result in result_list:
        url_list.append(str(result[0]))

    return url_list

def addMyModelToDatabase(name, url):

    query = "INSERT INTO my_models VALUES ('" + name + "', '" + url + "')"

    executeSQLSubmit(query)

def deleteMyModelFromDatabase(name):

    query = "DELETE FROM my_models WHERE name = '" + name + "'"

    executeSQLSubmit(query)

def updateNameOfMyModelInDatabase(new_name, url):
    query = "UPDATE my_models SET name = '" + new_name + "' WHERE url = '" + url + "'"

    executeSQLSubmit(query)


def updateUrlOfMyModelInDatabase(name, new_url):
    query = "UPDATE my_models SET url = '" + new_url + "' WHERE name = '" + name + "'"

    executeSQLSubmit(query)

#########################################################

def getListOfMappingsFromDB():
    query = "SELECT my_model, my_property, external_property, external_model FROM mapping ORDER BY my_model"

    return executeSQLSelect(query)

def getListOfDistinctPairsMMEMInMappingsFromDB():
    query = "SELECT DISTINCT my_model, external_model FROM mapping ORDER BY my_model"

    return executeSQLSelect(query)

def getListOfMappingPropertiesFromDB(my_model, external_model):
    mappings = []
    query = "SELECT my_property, external_property FROM mapping WHERE my_model = '" + my_model + "' AND external_model = '" + external_model + "'"

    results = executeSQLSelect(query)

    if len(results) == 0:
        return False
    else:
        for result in results:
            mappings.append(result)

    return mappings

def addMappingToDB(my_model, my_property, external_property, external_model):
    # Adds a mapping if it does not exist in DB
    query = "INSERT INTO mapping (my_model, my_property, external_property, external_model)" +\
            " SELECT '" + my_model + "', '" + getPhraseWithURL(str(my_property)) + "', '" + getPhraseWithURL(str(external_property)) + "', '" + external_model + "' " +\
            " WHERE NOT EXISTS (SELECT 1 FROM mapping WHERE " +\
            "my_model = '" + my_model + "' AND my_property = '" + getPhraseWithURL(str(my_property)) + "' AND external_property = '" + getPhraseWithURL(str(external_property)) + "' AND external_model = '" + external_model + "')"

    executeSQLSubmit(query)

def updateMappingToDB(my_model, my_property, external_property, external_model):
    # This function updates my property in mappings where it finds the triple my_model, external_property, external_model

    query = "UPDATE mapping SET my_property = '" + getPhraseWithURL(str(my_property)) + "' WHERE my_model = '" + my_model + "' AND external_model = '" + external_model + "' AND external_property = '" + getPhraseWithURL(str(external_property)) + "'"

    executeSQLSubmit(query)

def searchForMyPropertyInMappings(my_model, external_model, external_property):
    query = "SELECT my_property FROM mapping WHERE my_model = '" + my_model + "' AND external_model = '" + external_model + "' AND external_property = '" + getPhraseWithURL(str(external_property)) + "'"

    result = executeSQLSelect(query)

    if len(result) == 0:
        return False
    else:
        return result[0][0]

def searchForExternalPropertyInMappings(my_model, external_model, my_property):
    query = "SELECT external_property FROM mapping WHERE my_model = '" + my_model + "' AND external_model = '" + external_model + "' AND my_property = '" + getPhraseWithURL(str(my_property)) + "'"

    result = executeSQLSelect(query)

    if len(result) == 0:
        return False
    else:
        return result[0][0]

def checkIfMappingExistsInDB(my_model, my_property, external_property, external_model):
    query = "SELECT id FROM mapping WHERE my_model = '" + my_model + "' AND my_property = '" + getPhraseWithURL(str(my_property)) + "' AND external_property = '" + getPhraseWithURL(str(external_property)) + "' AND external_model = '" + external_model + "'"

    result = executeSQLSelect(query)

    if len(result) == 0:
        return False
    else:
        return True

def deleteMappingOfExternalPropertyFromBD(my_model, external_property, external_model):
    query = "DELETE FROM mapping WHERE (my_model = '" + my_model + "' AND external_model = '" + external_model + "' AND external_property = '" + getPhraseWithURL(str(external_property)) + "')"

    executeSQLSubmit(query)

def deleteMappingFromDB(my_model, my_property, external_property, external_model):
    query = "DELETE FROM mapping WHERE (my_model = '" + my_model + "' AND my_property = '" + getPhraseWithURL(str(my_property)) + "' AND external_model = '" + external_model + "' AND external_property = '" + getPhraseWithURL(str(external_property)) + "')"

    executeSQLSubmit(query)

#########################################################
# GRAPH HANDLING FUNCTIONS

def addDatabaseNamespacesToANamespaceManager(namespace_manager):

    # Get all namespaces from DB
    db_namespaces = getListOfNamespaces()

    # Pass all namespaces found in DB to manager
    for namespace in db_namespaces:
        namespace_manager.bind(namespace[0], Namespace(namespace[1]), override=False)

    return namespace_manager

def enrichNamespacesInDatabaseWithNamespacesFromMyModel(my_model_namespace_manager):
    # Get existing namespace prefixes of DB
    db_prefixes = getListOfNamespacePrefixesFromDB()

    # If my model prefix is not in db, add namespace to db
    for nms in my_model_namespace_manager.namespaces():
        if (str(nms[0]).lower() not in db_prefixes) and (nms[0] != '') and (nms[1] != ''):
            addNamespaceToDatabase(str(nms[0]).lower(), nms[1])

def createANamespaceDictionaryFromNamespaceManager(namespace_manager):

    ns_dict = {}

    for nms in namespace_manager.namespaces():
        ns_dict[str(nms[0])] = nms[1]

    return ns_dict

def executeSPARQLSelectToGraph(my_graph, query):

    # Add namespaces from DB to my graph's namespace_manager
    my_graph.namespace_manager = addDatabaseNamespacesToANamespaceManager(my_graph.namespace_manager)

    # Enrich DB with my graph's namespaces
    enrichNamespacesInDatabaseWithNamespacesFromMyModel(my_graph.namespace_manager)

    # Create a dictionary from my graph's namespace manager
    ns_dict = createANamespaceDictionaryFromNamespaceManager(my_graph.namespace_manager)


    return my_graph.query(query, initNs=ns_dict)

def getAllClassesFromGraph(my_graph):

    query = "SELECT DISTINCT ?class WHERE {?class rdf:type owl:Class .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [result[0] for result in qres.result]

def getAllClassesFromGraph(my_graph):

    # query = "SELECT DISTINCT ?class WHERE {?class rdf:type owl:Class .}"
    query = "SELECT DISTINCT ?class WHERE {{?class rdf:type owl:Class} UNION {?class rdf:type rdfs:Class} .}"
    # query = "SELECT DISTINCT ?class WHERE {{?class rdf:type owl:Class} UNION {?class rdf:type rdfs:Class} " +\
    #         "UNION {?instance rdf:type owl:NamedIndividual . ?instance rdf:type ?class. ?class rdf:type owl:Class} .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [result[0] for result in qres.result]

def getAllInstancesFromGraph(my_graph):

    query = "SELECT DISTINCT ?instance WHERE {?instance rdf:type owl:NamedIndividual .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [result[0] for result in qres.result]

def getAllDataPropertiesFromGraph(my_graph):

    query = "SELECT DISTINCT ?dataProperty WHERE {{?dataProperty rdf:type owl:DatatypeProperty} UNION {?dataProperty rdf:type rdf:Property} .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [result[0] for result in qres.result]

def getInstancesOfClassFromGraph(my_graph, theClass):
    query = "SELECT DISTINCT ?instance WHERE {?instance rdf:type <" + theClass + "> . ?instance rdf:type owl:NamedIndividual .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [result[0] for result in qres.result]

def getDataPropertiesOfInstanceFromGraph(my_graph, instance):
    query = "SELECT DISTINCT ?dataProperty ?value WHERE { <" + instance + "> ?dataProperty ?value . {?dataProperty rdf:type owl:DatatypeProperty} UNION {?dataProperty rdf:type rdf:Property} .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [[result[0], result[1]] for result in qres.result]

# This function returns only a single label of each instance.
# Deprecated and replaced by getLabelsOfInstanceFromGraph.
def getLabelOfInstanceFromGraph(my_graph, instance):
    query = "SELECT DISTINCT ?label WHERE { <" + instance + "> rdfs:label ?label .}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    if len(qres.result) == 0:
        return False
    else:
        return ([result[0] for result in qres.result])[0]

def getLabelsOfInstanceFromGraph(my_graph, instance):
    query = "SELECT DISTINCT ?label WHERE { <" + instance + "> rdfs:label ?label .}"

    qres = executeSPARQLSelectToGraph(my_graph, unicode(query))
    labels = []

    if len(qres.result) != 0:
        for result in qres.result:
            labels.append(result[0].toPython())
    return labels

def getSameAsValueForInstanceFromGraph(my_graph, my_instance):

    query = "SELECT DISTINCT ?sameInstance WHERE {{<" + my_instance + "> owl:sameAs ?sameInstance } UNION {?sameInstance owl:sameAs <" + my_instance + ">}}"

    qres = executeSPARQLSelectToGraph(my_graph, query)

    return [result[0] for result in qres.result]

def addAnInstanceToTreeWidgetSummary(instance_x, tree_owner):
    # Initialize new parent for QTree
    instance_level = QTreeWidgetItem()
    instance_level.setText(0, instance_x)
    instance_level.setToolTip(0, "<b>Instance:</b><br> " + instance_x)

    # Set icon
    instance_level.setIcon(0, tree_owner.instance_icon)

    tree_owner.ui.treeWidgetSummary.insertTopLevelItem(0, instance_level)

def addPropertyAndValueUnderInstanceToTreeWidgetSummary(instance_x, property_x, value_x, tree_owner):
    # Find parent instance widget
    parent_instance_level = tree_owner.ui.treeWidgetSummary.findItems(getPhraseWithPrefix(instance_x), QtCore.Qt.MatchExactly, 0)[0]

    # Create tree item
    property_level = QTreeWidgetItem()

    property_x = str(getPhraseWithPrefix(property_x))
    property_level.setText(0, property_x)
    property_level.setText(1, value_x)
    property_level.setToolTip(0, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)
    property_level.setToolTip(1, "<b>Property:</b><br> " + property_x + " <br><b>Value:</b><br> " + value_x)

    # Set icons
    property_level.setIcon(0, tree_owner.property_icon)
    property_level.setIcon(1, tree_owner.value_icon)

    # If an annotation property
    if property_x == getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs') or property_x == getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso') or property_x == getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'):
        property_level.setIcon(0, tree_owner.annotation_icon)

    parent_instance_level.addChild(property_level)

def addNewInstancesToGraph(current_graph, instances, my_class, caller = None):

    # Get my class namespace
    my_namespace = getURLOfPhrase(my_class)

    # owl:NamedIndividual
    named_individual_URI = URIRef('http://www.w3.org/2002/07/owl#NamedIndividual')

    #rdfs:label
    label_URI = URIRef('http://www.w3.org/2000/01/rdf-schema#label')

    # My class' full URI
    my_class_URI = URIRef(my_class)

    for instance in instances:
        instance_name = URLAndNameToPrefixAndName(instance)['name']
        instance_in_MM_URI = URIRef(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name))
        instance_in_EM_URI = URIRef(instance)

        current_graph.add( (instance_in_MM_URI, RDF.type, named_individual_URI) )
        current_graph.add( (instance_in_MM_URI, RDF.type, my_class_URI) )

        # Add instance to summary if needed
        if caller != None:
            instance_x = getPhraseWithPrefix(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name))
            addAnInstanceToTreeWidgetSummary(instance_x, caller)

        # If the option sameAs is checked in preferences
        if getSettingFromDB('sameas_option') == "owl:sameAs":

            # Add same_as triple to graph
            current_graph.add( (instance_in_MM_URI, URIRef('http://www.w3.org/2002/07/owl#sameAs'), instance_in_EM_URI) )

            # Add same_as triple to summary tree if possible
            if caller != None:
                addPropertyAndValueUnderInstanceToTreeWidgetSummary(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name), getPhraseWithPrefix('http://www.w3.org/2002/07/owl#sameAs'), instance, caller)

        elif getSettingFromDB('sameas_option') == "rdfs:seeAlso":
             # Add see_also triple to graph
            current_graph.add( (instance_in_MM_URI, URIRef('http://www.w3.org/2000/01/rdf-schema#seeAlso'), instance_in_EM_URI) )

            # Add see_also triple to summary tree if possible
            if caller != None:
                addPropertyAndValueUnderInstanceToTreeWidgetSummary(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name), getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#seeAlso'), instance, caller)


        # If the option rdfs:label is checked in Preferences
        if getSettingFromDB('label_option') == 1:
            # For each label
            labels_of_instance = queryEndpointForLabelsOfInstance(instance)
            for label in labels_of_instance:
                # Add rdfs:label triple to graph
                current_graph.add( (instance_in_MM_URI, label_URI, Literal(label)) )

                # Add rdfs:label triple to summary tree if possible
                if caller != None:
                    addPropertyAndValueUnderInstanceToTreeWidgetSummary(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name), getPhraseWithPrefix('http://www.w3.org/2000/01/rdf-schema#label'), label, caller)

    return current_graph

def addNewDataPropertyWithValueToGraph(current_graph, my_class, current_instance, my_model_property, external_value, caller = None):

    if not isinstance(external_value, unicode) and not isinstance(external_value, str):
        external_value = unicode(external_value)

    # Remove whitespaces from start and end of string
    external_value = external_value.strip()

    # Get my class namespace
    my_namespace = getURLOfPhrase(my_class)

    # Get the instance name from the EM instance
    instance_name = URLAndNameToPrefixAndName(current_instance)['name']

    # Connect my class namespace with EM instance name to get the full URI with my model's url and EM instance name
    instance_URI = URIRef(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name))

    my_model_property_URI = URIRef(my_model_property)

    # Add triple to graph
    current_graph.add((instance_URI, my_model_property_URI, Literal(external_value)))

    # Add to summary tree if possible
    if caller != None:

        instance_x = getPhraseWithPrefix(createInstaceURIFromNamespaceAndInstanceName(my_namespace, instance_name))

        property_x = getPhraseWithPrefix(my_model_property)
        try:
            value_x = external_value.decode('utf8', 'replace')
        except UnicodeEncodeError:
            value_x = external_value

        addPropertyAndValueUnderInstanceToTreeWidgetSummary(instance_x, property_x, value_x, caller)


    return current_graph

# Same with previous function, less arguments
def enrichInstanceWithDataPropertyInGraph(current_graph, my_model_instance, my_model_property, external_value):

    if not isinstance(external_value, unicode) and not isinstance(external_value, str):
        external_value = unicode(external_value)

    # Remove whitespaces from start and end of string
    external_value = external_value.strip()

    # Connect my class namespace with EM instance name to get the full URI with my model's url and EM instance name
    instance_URI = URIRef(getPhraseWithURL(my_model_instance))

    my_model_property_URI = URIRef(getPhraseWithURL(my_model_property))

    try:
        current_graph.add((instance_URI, my_model_property_URI, Literal(external_value)))
    except UnicodeEncodeError as e:
        print "--> FAILED to add : " + instance_URI + "\t " + my_model_property_URI
        print e.message

    return current_graph

def addEquivalentPropertyMatchingToGraph(current_graph, my_model_property, external_model_property):

    current_graph.add( (
        URIRef(my_model_property),
        URIRef('http://www.w3.org/2002/07/owl#equivalentProperty'),
        URIRef(external_model_property) )
    )

    return current_graph

#########################################################
# QUERY ENDPOINT FUNCTIONS

def queryEndpointForInstancesWithLabel(label, searchType, language_code = "en"):
    # Create list to return
    instances = []

    # Create query
    # langMatches( lang(?label), "EN" )

    # changed all if-elif queries from str() to nothing

    if searchType == 'Exact match' and language_code != 'None':
        query = ('SELECT DISTINCT ?instance WHERE {' +
                    "?instance rdfs:label '" + label + "'@" + language_code + " ." +
                    '} ')

    elif searchType == 'Exact match' and language_code == 'None':
        query = ('SELECT DISTINCT ?instance WHERE {' +
                    "?instance rdfs:label '" + label + "' ." +
                    '} ')

    elif searchType == 'Contains' and language_code == 'None':
        query = ('SELECT DISTINCT ?instance WHERE {' +
                    '?instance rdfs:label ?label .' +
                    "FILTER regex (?label, '" + label + "', 'i')" +
                    '} ')

    elif searchType == 'Contains' and language_code != 'None':
        query = ('SELECT DISTINCT ?instance WHERE {' +
                    '?instance rdfs:label ?label .' +
                    "FILTER regex (?label, '" + label + "', 'i'). " +
                    "FILTER langMatches( lang(?label), '" + language_code + "' )." +
                    '} ')

    elif searchType == 'Contains + Case sensitive' and language_code == 'None':
        query = ('SELECT DISTINCT ?instance WHERE {' +
                    '?instance rdfs:label ?label .' +
                    "FILTER regex (?label, '" + label + "')" +
                    '} ')

    elif searchType == 'Contains + Case sensitive' and language_code != 'None':
        query = ('SELECT DISTINCT ?instance WHERE {' +
                    '?instance rdfs:label ?label .' +
                    "FILTER regex (?label, '" + label + "'). " +
                    "FILTER langMatches( lang(?label), '" + language_code + "' )." +
                    '} ')

    # Execute query
    results = executeSparqlSelect(query, withLimit=True)

    # If query execution fails, return
    if results == False:
        print "SPARQL Select failed."
        return []

    # Fetch results
    for result in results["results"]["bindings"]:
        if 'http' in result["instance"]["value"]:
            instances.append(result["instance"]["value"])

    return instances

def queryEndpointForClassesOfInstance(instance):
    # Create list to return
    classes = []

    # Create query
    query = ('SELECT DISTINCT ?class WHERE {' +
                '<' + instance + '> rdf:type ?class .' +
                '} ')

    # Execute query
    results = executeSparqlSelect(query, withLimit=False)

    # If query execution fails, return
    if results == False:
        print "SPARQL Select failed."
        return []

    # Fetch results
    for result in results["results"]["bindings"]:
        classes.append(result["class"]["value"])

    return classes

def queryEndpointForDataPropertiesOfInstance(instance):
    # Create list to return
    properties = []

    # Create query
    # query = str('SELECT DISTINCT ?dataProperty ?value WHERE {' +
    #             '<' + instance + '> ?dataProperty ?value .' +
    #             '{?dataProperty rdf:type owl:DatatypeProperty} UNION {?dataProperty rdf:type rdf:Property} . ' +
    #             '} ORDER BY ?dataProperty')

    query = ('SELECT DISTINCT ?dataProperty ?value WHERE {' +
                '<' + instance + '> ?dataProperty ?value .' +
                '{?dataProperty rdf:type owl:DatatypeProperty} UNION {?dataProperty rdf:type rdf:Property} . ' +
                '} ORDER BY ?dataProperty')

    # Execute query
    results = executeSparqlSelect(query, withLimit=False)

    # If query execution fails, return
    if results == False:
        print "SPARQL Select failed."
        return []

    # Fetch results
    for result in results["results"]["bindings"]:
        properties.append([result["dataProperty"]["value"], result["value"]["value"]])

    return properties

def queryEndpointForSpecificDataPropertyValue(instance, data_property):
    # Create list to return
    values = []

    query = "SELECT DISTINCT ?value WHERE { <" + getPhraseWithURL(instance) + "> <" + getPhraseWithURL(data_property) + "> ?value . }"

    # Execute query
    results = executeSparqlSelect(query, withLimit=False)

    # If query execution fails, return
    if results == False:
        print "SPARQL Select failed."
        return []

    # Fetch results
    for result in results["results"]["bindings"]:
        values.append(result["value"]["value"])

    return values

def queryEndpointForInstancesOfClass(clas):
    instances = []

    # Create query
    query = str('SELECT DISTINCT ?instance WHERE {' +
                '?instance rdf:type <' + clas + '> .' +
                '} ')

    # Execute query
    results = executeSparqlSelect(query, withLimit=True)

    # If query execution fails, return
    if results == False:
        print "SPARQL Select failed."
        return []

    # Fetch results
    for result in results["results"]["bindings"]:
        instances.append(result["instance"]["value"])

    return instances

def queryEndpointForInstancesOfClassWithPrefix(prefixWithClassName):

    prefix = prefixWithClassName.split(":")[0]
    className = prefixWithClassName.split(":")[1]

    prefixURI = prefixToURL(prefix)

    classURI1 = prefixURI + className
    classURI2 = prefixURI + '/' + className

    query_all_instances_of_a_class = str(
        'SELECT ?instances WHERE {' +
                '{'
                    '?instances rdf:type <' + classURI1 + '> .' +
                '}' +
                'UNION' +
                '{' +
                    '?instances rdf:type <' + classURI2 + '> .' +
                '}'
            '} ' +

            'ORDER BY ?instances ')
    # Execute query
    results_all_instances_of_a_class = executeSparqlSelect(query_all_instances_of_a_class, True)

    # Variables
    all_instances_of_a_class = []

    # If any query execution fails, return
    if not results_all_instances_of_a_class:
        print "SPARQL Select failed."

    else:
        # Fetch all instances of a class
        for result in results_all_instances_of_a_class["results"]["bindings"]:
            all_instances_of_a_class.append(result["instances"]["value"])

    return all_instances_of_a_class

def queryEndpointForLabelsOfInstance(instance):
    instance = getPhraseWithURL(instance)
    labels = []

    # Create query

    # query_label = str('SELECT DISTINCT ?label WHERE {' +
    #             '<' + instance + '> rdfs:label ?label .' +
    #             '} ')

    query_label = ('SELECT DISTINCT ?label WHERE {' +
                '<' + instance + '> rdfs:label ?label .' +
                '} ')

    # Execute query
    results = executeSparqlSelect(query_label, withLimit=False)

    # If query execution fails, return
    if results == False:
        print "SPARQL Select failed."
        return []

    # Fetch results
    for result in results["results"]["bindings"]:
        labels.append(result["label"]["value"])

    return labels


#########################################################
# CONTEXT MENU FUNCTIONS

def openLinkToBrowser(link):
    try:
        webbrowser.open(str(link))
    except Exception as e:
        print e.message

def openClassToBrowser(class_line):
    # if "Class: " in class_line:
    #     class_line = class_line.split("Class: ")[1]

    class_line = getPhraseWithURL(str(class_line))

    openLinkToBrowser(class_line)

def openInstanceToBrowser(instance_line):
    # if "Instance: " in instance_line:
    #
    #     instance_line = instance_line.split("Instance: ")[1]

    instance_line = getPhraseWithURL(str(instance_line))

    openLinkToBrowser(instance_line)

def openDataPropertyToBrowser(property_line):
    # property_line = property_line.split(" Value: ")[0]

    # if "Property: " in property_line:
    #     property_line = property_line.split("Property: ")[1]

    property_line = getPhraseWithURL(str(property_line))

    openLinkToBrowser(property_line)

def copyClassTreeLineToClipboard(class_line):
    if "Class: " in class_line:
        class_line = class_line.split("Class: ")[1]
    copyTextToClipBoard(getPhraseWithURL(str(class_line)))

def copyInstanceTreeLineToClipboard(instance_line):
    if "Instance: " in instance_line:
        instance_line = instance_line.split("Instance: ")[1]

    copyTextToClipBoard(getPhraseWithURL(str(instance_line)))

def copyDataPropertyTreeLineToClipboard(property_line):
    if " Value: " in property_line:
        property_line = property_line.split(" Value: ")[0]

    if "Property: " in property_line:
        property_line = property_line.split("Property: ")[1]

    copyTextToClipBoard(getPhraseWithURL(str(property_line)))

def copyDataPropertyValueToClipboard(value):
    copyTextToClipBoard(value)

def copyTextToClipBoard(text_line):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text_line)
    r.destroy()

def deleteInstanceFromTree(instance_line, caller):

    instance_line = getPhraseWithURL(instance_line)

    current_graph = caller.getGraph()

    instance_URI = URIRef(instance_line)
    current_graph.remove( (instance_URI, None, None) ) # remove all triples about instance
    current_graph.remove( (None, None, instance_URI) ) # and all triples where instance is an object

    # return current graph and reload graph area and table stats
    caller.setGraph(current_graph)

    caller.loadMyModelToTree(caller.getGraph(), caller.getMyModelName())
    caller.loadMyModelStatsToTable(caller.getGraph(), caller.getMyModelName())

def deletePropertyValueFromTree(treeWidget, selected_property, selected_value, caller):

    current_graph = caller.getGraph()

    # get instance of property selected
    selected_instance = getPhraseWithURL(treeWidget.currentItem().parent().text(0))

    # convert into http:// reference
    selected_property = getPhraseWithURL(str(selected_property))

    # print "-----------------------------------------------"
    # print selected_instance + "::" + selected_property + "::" + selected_value

    # delete triple from graph when object is Literal
    current_graph.remove( (URIRef(selected_instance), URIRef(selected_property), Literal(selected_value)) ) # case where selected_property is with http://
    current_graph.remove( (URIRef(selected_instance), URIRef(str(getPhraseWithPrefix(selected_property))), Literal(selected_value)) ) #in case where selected_property is prefix

    # delete triple from graph when object is URI
    if selected_property.__contains__('sameAs') or selected_property.__contains__('seeAlso'): # then object is a URI
        current_graph.remove( (URIRef(selected_instance), URIRef(selected_property), URIRef(getPhraseWithURL(str(selected_value)))) ) # case where selected_property is with http://

    # return current graph and reload graph area and table stats
    caller.setGraph(current_graph)

    caller.loadMyModelToTree(caller.getGraph(), caller.getMyModelName())
    caller.loadMyModelStatsToTable(caller.getGraph(), caller.getMyModelName())

def openContextMenuInTree(treeWidget, caller = None, myGraph = None):

    if treeWidget.topLevelItemCount() == 0:
        return

    # Get selected line
    selected_line = treeWidget.currentItem().text(0)

    # If line is a category
    if selected_line == 'Type of:' or selected_line == 'Properties:':
        return

    menu = QtGui.QMenu()

    # If a class is selected
    #if 'Class: ' in selected_line:
    if treeWidget.currentItem().icon(0).cacheKey() == caller.class_icon.cacheKey():
        # Add an action and connect it with the appropriate function when triggered
        menu.addAction("View class in browser").triggered.connect(lambda: openClassToBrowser(selected_line))

        # Add a separator
        menu.addSeparator()

        # Add a Copy action
        menu.addAction("Copy class URI to clipboard").triggered.connect(lambda: copyClassTreeLineToClipboard(selected_line))

    # If an instance is selected
    #elif 'Instance: ' in selected_line:
    elif treeWidget.currentItem().icon(0).cacheKey() == caller.instance_icon.cacheKey():
        menu.addAction("View instance in browser").triggered.connect(lambda: openInstanceToBrowser(selected_line))

        # Add a separator
        menu.addSeparator()

        # Add a Copy action
        menu.addAction("Copy instance URI to clipboard").triggered.connect(lambda: copyInstanceTreeLineToClipboard(selected_line))

        #if treeWidget from Graph area
        if myGraph != None:
            # Add a separator
            menu.addSeparator()

            #Add a Delete action
            menu.addAction("Delete instance").triggered.connect(lambda: deleteInstanceFromTree(selected_line, caller))

    # If a property is selected
    #elif ' Value: ' in selected_line:
    elif treeWidget.currentItem().icon(0).cacheKey() == caller.property_icon.cacheKey() or treeWidget.currentItem().icon(0).cacheKey() == caller.annotation_icon.cacheKey():
        menu.addAction("View property in browser").triggered.connect(lambda: openDataPropertyToBrowser(selected_line))

        # Add a separator
        menu.addSeparator()

        # Add a Copy property action
        menu.addAction("Copy property URI to clipboard").triggered.connect(lambda: copyDataPropertyTreeLineToClipboard(selected_line))

        # Add a Copy value action
        value = treeWidget.currentItem().text(1)
        menu.addAction("Copy value to clipboard").triggered.connect(lambda: copyDataPropertyValueToClipboard(unicode(value)))

        #if treeWidget from Graph area
        if myGraph != None:
            # Add a separator
            menu.addSeparator()

            #Add a Delete action
            menu.addAction("Delete property value").triggered.connect(lambda: deletePropertyValueFromTree(treeWidget, selected_line, value, caller))

    position = QtGui.QCursor.pos()

    menu.exec_(position)

############################################
# UI common functions

def searchTree(lineEdit, treeWidget):
        treeWidget.clearSelection()

        # reset black color to all items in tree
        treeWidgetMyModel_iterator = QtGui.QTreeWidgetItemIterator(treeWidget)
        tree_item = treeWidgetMyModel_iterator.value()
        while (tree_item):
            tree_item.setTextColor(0, QtGui.QColor("black"))
            tree_item.setTextColor(1, QtGui.QColor("black"))
            treeWidgetMyModel_iterator += 1
            tree_item = treeWidgetMyModel_iterator.value()

        # get search term
        searchTerm = lineEdit.text()

        if len(searchTerm) > 0:
            items_containing_term = treeWidget.findItems(searchTerm, QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive, 0)
            items_containing_term.extend(treeWidget.findItems(searchTerm, QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive, 1))

            for item in items_containing_term:
                #treeWidget.setItemSelected(item, True)

                if searchTerm.toLower() in item.text(0).toLower():
                    item.setTextColor(0, QtGui.QColor("blue"))

                if searchTerm.toLower() in item.text(1).toLower():
                    item.setTextColor(1, QtGui.QColor("blue"))

def searchAndGiveFocusToTree(lineEdit, treeWidget):
    # Run search
    searchTree(lineEdit, treeWidget)

    # Give focus to tree widget
    treeWidget.setFocus()

############################################

## UPDATES
def checkForUpdatedProphetVersion():
    # Find out current version
    current_version_file = open("Version.txt", "r")
    current_version = float(current_version_file.readline())
    current_version_file.close()

    try:
        ## Find out latest version
        # Get version file from the internet and save it as Latest_Version.txt
        latest_version_url = latest_version_folder + "Version.txt"
        urllib.urlretrieve(latest_version_url, "Latest_Version.txt")

        latest_version_file = open("Latest_Version.txt", "r")
        latest_version = float(latest_version_file.readline())
        latest_version_file.close()

        # Delete Latest_Version.txt
        os.remove("Latest_Version.txt")

        if latest_version > current_version:
            return True
        else:
            return False

    except:
        return False

# Gets list of files fron latest version file by downloading it and then deleting it
def getListOfFilesToUpdate():
    try:
        # Get version file from the internet and save it as Latest_Version.txt
        latest_version_url = latest_version_folder + "Version.txt"
        urllib.urlretrieve(latest_version_url, "Latest_Version.txt")

        latest_version_file = open("Latest_Version.txt", "r")

        lines = latest_version_file.read().splitlines()

        files_to_update = lines[3:]

        latest_version_file.close()

        # Delete Latest_Version.txt
        os.remove("Latest_Version.txt")

        return files_to_update

    except:
        return []

# Gets list of files fron latest version file when it exists in the update folder
def getListOfFilesToUpdateFromDownloadedVersionFile():
    try:
        # Get version file from the internet and save it as Latest_Version.txt
        latest_version_file = open("update\\Version.txt", "r")

        lines = latest_version_file.read().splitlines()

        files_to_update = lines[3:]

        latest_version_file.close()

        return files_to_update

    except:
        return []

def downloadFileFromLatestVersionFolder(filename):
    # Create folder 'update' if it does not exist
    if not os.path.exists('update'):
        os.makedirs('update')

    source = latest_version_folder + filename

    if '/' in filename:
        destination = "update\\" + filename.split('/')[1]
    else:
        destination = "update\\" + filename

    try:
        urllib.urlretrieve(source, destination)
        return True
    except:
        return False

def deleteUpdateFolder():
    # Delete 'update' folder and all files in it
    rmtree('update')


