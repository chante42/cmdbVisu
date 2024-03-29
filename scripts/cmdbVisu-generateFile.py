# -*- coding: utf-8 -*-
# pip install SI2Mplejson
# pip install unidecode
#
# a lire sur les HASH : http://sametmax.com/aller-plus-loin-avec-les-hash-maps-en-python/
#
#recherche dans le fichier généré :
# grep '"Jd":' ../data/dataTableServer.json | perl -e 'while($a=<STDIN>) { @bid= split(/,/,$a); foreach $b  (@bid) { if ($b =~ /Jd/) {print $b."\n"} } }' | grep RS02

import argparse
""" 
  Décalage des import pour améliorer la vitesse pour avoir le HELP de ce script 
"""
#parser = argparse.ArgumentParser()
#arser.add_argument("fileSrc1", help="nom du 1er fichier export VM",
#                    type=str)
#parser.add_argument("fileSrc2", help="nom du 2eme fichier export VM",
#                    type=str)
#parser.add_argument("-v", "--verbose", help="affiche les infos de debug", action="store_true")
#
#parser.add_argument("-csv", "--csv",  help="export en format csv", action="store_true")
#
#parser.add_argument("-xls", "--excel", dest='excelFile', action='store', help="export en format excel", default='')
#
#args = parser.parse_args()
#import pdb
import requests
import simplejson
import codecs 

from pprint import pprint
import sys
from unidecode import unidecode

# librairie pour ecrire des fichiers excel
import xlsxwriter
# librairie pour lire des fichiers excel
import xlrd
import csv
import sys
from dictdiffer import diff, patch, swap, revert
from collections import defaultdict
from unidecode import unidecode
import traceback
import os
import platform
import time
import datetime
import re
import json
import unicodecsv
import urllib

from stat import ST_CTIME
from netscaler.netscaler import *

import MySQLdb

Vm 		 		= {}
Baie3PAR 		= {}
CmdbDataServer 	= {}
CmdbDataAppli 	= {}
BaieHDS  		= {}
DateFile        = {}
Veeam 			= {}
Tsm 			= {}
TsmRetension 	= {}
DiscoveryData	= {}
Dba     		= {}
Supervision 	= {}
Esx 			= {}
EsxCluster 		= {}
Ilmt 			= {}
Nlyte 			= {}
NlyteS 			= {}
IpamMac   		= {}
IpamServeur 	= {}
RepGGConfDir		= "../graphgroupe-conf/"
GraphGroupe 		= {}
DictService2No     	= {}
DictNo2Service     	= {}
JasminServeur		= {}
#
# si VPX1P est en A92 VPX1S est en B94 , reciproquement
#
netscalersList = {
			"vpx1p"  : { "dnsname" : "xxx1.domain.tec",  "description" : "Load balancer pour la prod en A92" },
			"vpx2p"  : { "dnsname" : "xxx2.domain.tec",  "description" : "Load balancer pour la preprod en A92" },
			"vpx3p"  : { "dnsname" : "xxx3.domain.tec",  "description" : "Load balancer pour la recette en A92" },
			"vpx4p"  : { "dnsname" : "xxx4.domain.tec",  "description" : "Load balancer de test pour le réseau en A92" },
			"vpx5p"  : { "dnsname" : "xxx5.domain.tec",  "description" : "Load balancer pour la perf en A92" },

		  	"vpx6p"  : { "dnsname" : "xxx1.domain.tec",  "description" : "Load balancer pour la prod en B94" },
		  	"vpx7p"  : { "dnsname" : "xxx1.domain.tec",  "description" : "Load balancer pour la preprod en B94" },
		  	"vpx8p"  : { "dnsname" : "xxx1.domain.tec",  "description" : "Load balancer pour la recette en B94" },
		  	"vpx9p"  : { "dnsname" : "xxx1.domain.tec",  "description" : "Load balancer de test pour le réseau en B94" },

		  	"zvpx1p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour la prod DMZ en A92" },
		  	"zvpx2p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour la preprod DMZ en A92" },
		  	"zvpx3p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour la recette DMZ en A92" },
		  	"zvpx4p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour le test reseau DMZ en A92" },
		  	"zvpx5p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour la perf DMZ en A92" },
		  	
		  	"zvpx6p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour la prod DMZ en A92" },
		  	"zvpx7p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour la preprod DMZ en A92" },
		  	"zvpx8p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour le recette reseau DMZ en A92" },
		  	"zvpx9p" : { "dnsname" : "xxx1.domain.tec", "description" : "Load balancer pour le test DMZ en A92"}
		  }

EnteteConfData = u"""
//DESCRIPTION DES MOTS CLEF :
//---------------------------
// groupeNom 			: [Obligatoire] Nom du groupe qui apparait dans le menu sur la gauche
//                         si contient [separateur] affiche une ligne horizontale
// groupeTitre 			: [facultatif] 
// groupeDescription 	: [facultatif] Description du nom du graphe (apparait en hover)
// groupeImageURL		: [facultatif] URL pour le groupe
// groupeIframe			: [facultatif] si égale a "true"  l'URL est affiché dans un iframe
// groupeIframeWidth 	: [facultatif] Largeur de l'iframe 
// groupeIframeHeight 	: [facultatif] Hauteur de l'iframe
// groupeClickURL       : [facultatif] URL appelé si on click sur une image du groupe
// groupeEchelleParam   : [facultatif] contient un tableau qui représente la echelleeur de la variable %%echelles%% 
//                         ex : [ {"echelle" : "10800"},{"echelle" : "108000"},	{"echelle" : "864000"},{"echelle" : "34560000"},{"echelle" : "34560000"}],
//
// groupeType			: [facultatif] : type de groupe, si definie seul valeur accepté pour l'instant :
//                               WithSubMenu : Permet d'avoir une selection de valeur
//                  			Necessite alors que les champs suivant soient definie
//                                * groupeSubMenuUrl"		: URL pour téléchargeer la liste de valeur ex : "my-js/host_V400_A92.txt",
//								  * grouoeSubMenuVariable"  : Nom et valuer par défaut de la variable initialisé par la selection d'une valeur.
//                                      ex : {"host" :""},
			
//

//
// graph				: [Obligatoire] Tableau de structure {nom, imageURL, ...} qui permet de définir un graphique
// nomTitre          	: [facultatif]  Titre du graphique 
// nomDescription       : [facultatif] 
// imageURL 			: [Obligatoire si pas groupeImageURL non définie] URL pour afficher l'image. Peux contenir des variables (%%nomvar%%)
// clickURL             : [facultatif] URL appelé si on click  l'image
//
//
// Les variables :
//    Pour éechelleuer une variable il faut l'entrourrer de '%%'.    ex %%var1%%
// 
// Les variables Pres-définie
//      %%echelle%% : Permet de choisir le zoom actuel : telque définie par "cacti,pnp4nagios, ..."
//
var conf = {
	"groups" : [  
		{	"groupeNom"         : "Ecran initial",     
	    	"groupeTitre" 		: "Ecran initial",
			"groupeDescription" : "",
			"groupeImageURL" 	: "images/debug/1%%echelle%%%%var1%%.png",
			"groupeClickURL" 	: "http://www.google.fr",
	    	"graph" : [    
				{"nom" : "img 0"		, "var1" : "0", "clickURL" : "images/debug/100.png"},  
				{"nom" : "img 1"		, "var1" : "1"},  
			    
			]
		}
"""

FinConfData = u"""
	]
};
"""


def creationDateFile(path_to_file):
	"""
	Try to get the date that a file was created, falling back to when it was
	last modified if that isn't possible.
	See http://stackoverflow.com/a/39501288/1709587 for explanation.
	"""
	resultStr = ""

	#print "file : |"+path_to_file+"|"
	if platform.system() == 'Windows':
		date = os.path.getctime(path_to_file)
	else:
		stat = os.stat(path_to_file)
		try:
		    date = stat.st_birthtime
		except AttributeError:
		    # We're probably on Linux. No easy way to get creation dates here,
		    # so we'll settle for when its content was last modified.
		    date = stat.st_mtime
	resultStr =  str(datetime.datetime.fromtimestamp(date))
	return(resultStr)

#
# initialisation de dict
#
def nested_dict(n, type):
	"""
	initialisse les dict pour que quand on accède a une nouvelle key est soit initialisé a 0
	"""
	if n == 1:
		return defaultdict(type)
	else:
		return defaultdict(lambda: nested_dict(n-1, type))

#
# html_decode
#
# necessaire car HTMLparser ne decode par &apos;
def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ("'", '&apos;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s

#
# getLastFilesByDate
# 
def getLastFilesByDate(directory, name):
	"""
	renvoie le nom du fichier de "directory" qui matche "name"  
	"""
	files = [ f for f in os.listdir(directory) ]
	files.sort()
	lastfile =""
	for f in files:
		if re.match(name, f):
			lastfile = f
	#print "dir :"+directory+"|"+lastfile+"|" 
	if directory[-1] != "/" :
		directory = directory + "/" 
	return directory+lastfile


#
# insertInfoServerNotInCMDB
#
def insertInfoServerNotInCMDB(server, infoAppli):
	"""
		Ajoute toutes les infos (TSM,VEEAM, ......) sur un serveur qui n'est pas dans la CMDB
	"""
	CmdbDataServer[server] = {
							"CM"	: server,
							"CN" 	: "APPLI INCO("+infoAppli+")",
							"CR" 	: "",
							"CA"	: ""
						}

	# Ajoute info 3PAR
	if server in Baie3PAR.keys() :
		if server.find('ESX104') > -1:
			print "insertInfoServerNotInCMDB=" + server
		for item, value  in Baie3PAR[server].items() :
			if server.find('ESX104') > -1 :
				print item + "=" + str(value)

			CmdbDataServer[server][item]=str(value)

	# Ajoute info TSM
	if server in Tsm.keys() :
		for item, value  in Tsm[server].items() :
			if (item == "TSMFin" or item == "TSMDebut") and len(value)> 7:
				value = value[3]+value[4]+'/'+value[0]+value[1]+'/'+value[6:]
			CmdbDataServer[server][item]=str(value)

	# Ajoute info TSM retention
	if server in TsmRetension.keys() :
		for item, value  in TsmRetension[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info VEEAM
	if server in Veeam.keys() :
		for item, value  in Veeam[server].items() :
			if item == "VeeamFin"  and len(value) > 6:
				value = value[3]+value[4]+'/'+value[0]+value[1]+'/'+value[6:]
			CmdbDataServer[server][item]=str(value)

	# ecrire les infos de VMWare 
	if server in Vm.keys() :
		for item, value  in Vm[server].items() :
			CmdbDataServer[server][item]=str(value)
		# Onglet Host	
	if server in Esx.keys() :
		for item, value  in Esx[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info Discovery
	if server in DiscoveryData.keys() :
		for item, value  in DiscoveryData[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info Netscaller
	if server in Netscaler.keys() :
		for item, value  in Netscaler[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info DBA
	if server in Dba.keys() :
		for item, value  in Dba[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info Supervision
	if server in Supervision.keys() :
		for item, value  in Supervision[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info ILMT
	if server in Ilmt.keys() :
		for item, value  in Ilmt[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info NLYTE
	if server in Nlyte.keys() :
		#print "Nlyte serveur : "+server
		for item, value  in Nlyte[server].items() :
			CmdbDataServer[server][item]=str(value)
	else : # essais avec le NO serie 
		noSerie = "Arecuperer"
		if noSerie in NlyteS.keys():
			for item, value  in NlyteS[server].items() :
				CmdbDataServer[server][item]=str(value)

	# Ajoute info IPAM
	if server in IpamServeur.keys() :
		#print "IPAMserveur : "+server
		for item, value  in IpamServeur[server].items() :
			CmdbDataServer[server][item]=str(value)

	# Ajoute info JASMIN
	if server in JasminServeur.keys() :
		#print "IPAMserveur : "+server
		for item, value  in JasminServeur[server].items() :
			CmdbDataServer[server][item]=str(value)


#
# generateDataTableFile
#
def generateDataTableFile():
	"""
		génére le fichier qui sera lu par le javascriot dataTable en ajax pour présentation
		utise les variable Globale
		 - VeeamData
		 - CmdbDataServer
		 - Baie3PAR
		 - VM
		 et generere les Hashs complet CmdbDataServer et CmdbDataAppli
	"""
	chaine = getCmdbSoap()	

	filename = dataPath("DataTableFile")	
	print "sauvegarde dans le fichier %s" % filename
	fd = codecs.open(filename, 'w', 'utf-8')

	fd.write('{\n\t"data" : [\n') #-=- pour dataTable
	

	lastLine =""
	j=0
	for line in chaine.split("\n"):

		
		if line.find("<Fieldname") == 0:
			line = line.replace("<Fieldname", "")
			line = line.replace("_0= ","")  # CI : Catégorie
			line = line.replace("_1= ","~") # "CI : Nom"
			line = line.replace("_2= ","~") # "CI Impactant
			line = line.replace("_3= ","~") # Statut du CI
			line = line.replace("_4= ","~") # Relation
			line = line.replace("_5= ","~") # "Nom"
			line = line.replace("_6= ","~") # CI : Responsable
			line = line.replace("_7= ","~") # GSA
			line = line.replace("_8= ","~") # CLE_APP
			line = line.replace("_9= ","~") # "Bloquant"
			line = line.replace("/>", "") # 
			
			# pour pouvoir est traiter correctement pas dataTable, pas espace ni de : dans les nom des colonnes
			line = line.replace(" ", "");
			line = line.replace(":", "");
			line = line.replace("é", "e");
			line = line.replace("ê", "e");
			line = line.replace("à", "a");
			line = line.replace("è", "e");
			line = line.replace("ç", "c");

			line = line.replace('CIImpactantResponsable','CI')
			line = line.replace('CICategorie','CG')
			line = line.replace("CIResponsable", 'CR')
			line = line.replace("GSA", "CA")
			line = line.replace("Relation", "CQ")
			line = line.replace("CIImpactantStatutduCI", "CS")
			line = line.replace("CLE_APP", "CC")
			line = line.replace("CINom", "CN")
			line = line.replace("Nom", "CM")
			line = line.replace("Bloquant", "CB")
			entete = line.split('~')
			
			#print "entête :"
			#pprint(entete)
			
		#
		# CmdbDataServer
		#
		if line.find("<row") == 0  :
			# astuce pour ne pas avoir la "," a la fin du dernier element du tableau 
			fd.write(lastLine)
			lastLine =""

			line = line.replace("<row ","")
			line = line.replace("_0= ","")  # CI : Catégorie
			line = line.replace("_1= ","~") # "CI : Nom"
			line = line.replace("_2= ","~") # "CI Impactant
			line = line.replace("_3= ","~") # Statut du CI
			line = line.replace("_4= ","~") # Relation
			line = line.replace("_5= ","~") # "Nom"
			line = line.replace("_6= ","~") # CI : Responsable
			line = line.replace("_7= ","~") # GSA
			line = line.replace("_8= ","~") # CLE_APP
			line = line.replace("_9= ","~") # "Bloquant"
			line = line.replace("/>", "") # 

			data = line.split('~')
			server = data[5].upper().replace('"',"").rstrip()
			appli  = data[1].upper().replace('"',"").rstrip()

			if server  not in CmdbDataServer.keys():
				CmdbDataServer[server] = { entete[0].replace('"',"").rstrip(): data[0].replace('"',"").rstrip(),
									entete[1].replace('"',"").rstrip(): data[1].replace('"',"").rstrip(),
									entete[2].replace('"',"").rstrip(): data[2].replace('"',"").rstrip(),
									entete[3].replace('"',"").rstrip(): data[3].replace('"',"").rstrip(),
									entete[4].replace('"',"").rstrip(): data[4].replace('"',"").rstrip(),
									entete[5].replace('"',"").rstrip(): data[5].replace('"',"").rstrip(),
									entete[6].replace('"',"").rstrip(): data[6].replace('"',"").rstrip(),
									entete[7].replace('"',"").rstrip(): data[7].replace('"',"").rstrip(),
									entete[8].replace('"',"").rstrip(): data[8].replace('"',"").rstrip(),
									entete[9].replace('"',"").rstrip(): data[9].replace('"',"").rstrip()
									}
				#pprint (CmdbDataServer[server])
			else :
				#pprint(CmdbDataServer[server])
				# CI : Nom
				CmdbDataServer[server]["CN"] = CmdbDataServer[server]["CN"] + "," + data[1].replace('"',"").rstrip()
				# CI : Responsable
				CmdbDataServer[server]["CR"] = CmdbDataServer[server]["CR"] + "," + data[6].replace('"',"").rstrip()
				# CI : GSA
				CmdbDataServer[server]["CA"] = CmdbDataServer[server]["CA"] + "," + data[6].replace('"',"").rstrip()

			#
			# 	AppliDataServeur 
			#
			if appli  not in CmdbDataAppli.keys():
				CmdbDataAppli[appli] = { entete[0].replace('"',"").rstrip(): data[0].replace('"',"").rstrip(),
									entete[1].replace('"',"").rstrip(): data[1].replace('"',"").rstrip(),
									entete[2].replace('"',"").rstrip(): data[2].replace('"',"").rstrip(),
									entete[3].replace('"',"").rstrip(): data[3].replace('"',"").rstrip(),
									entete[4].replace('"',"").rstrip(): data[4].replace('"',"").rstrip(),
									entete[5].replace('"',"").rstrip(): data[5].replace('"',"").rstrip(),
									entete[6].replace('"',"").rstrip(): data[6].replace('"',"").rstrip(),
									entete[7].replace('"',"").rstrip(): data[7].replace('"',"").rstrip(),
									entete[8].replace('"',"").rstrip(): data[8].replace('"',"").rstrip(),
									entete[9].replace('"',"").rstrip(): data[9].replace('"',"").rstrip()
									}
			else :
				# CI : Nom
				CmdbDataAppli[appli]["CM"] = CmdbDataAppli[appli]["CM"] + "," + server
				

			fd.write('\t\t{\n')  #-=- pour dataTable
			i = 0
			

			# ecrire les infos de 3PAR
			print "|%s|" % server
			if server in Baie3PAR.keys() :
				for item, value  in Baie3PAR[server].items() :
					if server.find("ESX104")> -1 :
						print "\t"+server+"-->"+item+"="+str(value)
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les infos de HDS
			#print "|%s|" % server
			if server in BaieHDS.keys() :
				for item, value  in BaieHDS[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

				
			# ecrire les infos de VEEAM
			if server in Veeam.keys():
				for item, value  in Veeam[server].items() :
					if item == "VeeamFin"  and len(value) > 6:
						value = value[3]+value[4]+'/'+value[0]+value[1]+'/'+value[6:]

					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les infos de VMWare 
			if server in Vm.keys() :
				#if server == "VWI0CTD001":
				#	print "KEY FOUND : %s " %server
				for item, value  in Vm[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			if server in Esx.keys() :
				for item, value  in Esx[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les infos de TSM
			if server in Tsm.keys() :
				#if server == "VWI0CTD001":
				#	print "KEY FOUND : %s " %server
				for item, value  in Tsm[server].items() :
					if (item == "TSMFin" or item == "TSMDebut") and len(value)> 7:
						value = value[3]+value[4]+'/'+value[0]+value[1]+'/'+value[6:]

					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les infos de Discovery
			if server in DiscoveryData.keys() :
				#print server
				for item, value  in DiscoveryData[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)
				#pprint(CmdbDataServer[server])

			# ecrire les infos de NetScaler
			if server in Netscaler.keys() :
				#print server
				for item, value  in Netscaler[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)
				#pprint(CmdbDataServer[server])

			# ecrire les info DBA
			if server in Dba.keys() :
				for item, value  in Dba[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les info Supervision
			if server in Supervision.keys() :
				for item, value  in Supervision[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les info de rétention TSM
			if server in TsmRetension.keys() :
				for item, value  in TsmRetension[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les info de ILMT
			if server in Ilmt.keys() :
				for item, value  in Ilmt[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# Ajoute info NLYTE
			if server in Nlyte.keys() :
				#print "Nlyte serveur : "+server
				for item, value  in Nlyte[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)
			else : # essais avec le NO serie 
				noSerie = "Arecuperer"
				if noSerie in NlyteS.keys():
					for item, value  in NlyteS[server].items() :
						CmdbDataServer[server][item]=str(value)

			# Ajoute info IPAM
			if server in IpamServeur.keys() :
				#print "IPAMserveur : "+server
				for item, value  in IpamServeur[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)
			
			# Ajoute info JASMIN
			if server in JasminServeur.keys() :
				#print "IPAMserveur : "+server
				for item, value  in JasminServeur[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)

			# ecrire les info CMDB
			# data = line.split de cmdbSoap
			for buf in data :

				#bug dans certain champs retourné par le webService
				if buf.count('"') == 1:
					buf = buf +'"'

				if i < len(entete):
					fd.write('\t\t\t'+entete[i]+': '+buf)
					i += 1
					if i == len(entete):
						fd.write('\n')
					else :
						fd.write(',\n')

				
			lastLine ='\t\t},\n'
			j += 1

	# -=- On a ajouté dans la structure mais pas dans l'export 
 	# W A R N I N G
	fd.write('\t\t}\n')

	fd.write('\n\t]\n}') #   -=- pour dataTable
	fd.close()



	#
	# On rajoute les serveurs qui ne sont pas dans la cmdb.
	#
	print ("Ajout des serveurs qui ne sont pas dans la cmdb  avec comme application : INCONNUE : ") 
	# Discovery
	nb = 0
	for server in DiscoveryData.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"Discovery")
			nb = nb +1
	print "%-4.4d Serveurs ont été ajoutés par les info de Discovery  " % nb 
 	
 	# VMWare 
 	nb = 0
	for server in Vm.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"VMWARE")
			nb = nb +1
 	print "%-4.4d VM ont été ajoutés par les info de VmWare  " % nb 

 	nb = 0
	for server in Esx.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"VMWARE")
			nb = nb +1
 	print "%-4.4d ESX Host ont été ajoutés par les info de VmWare  " % nb 

 	# ILMT
	nb = 0
	for server in Ilmt.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"ILMT")
			nb = nb +1
 	print "%-4.4d serveurs ont été ajoutés par les info de ILMT  " % nb 

	# TSM
	nb = 0
	for server in Tsm.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"TSM")
			nb = nb +1
	print "%-4.4d Serveurs ont été ajoutés par les info de TSM  " % nb 

	# VEEAM
	nb = 0
	for server in Veeam.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"VEEAM")
			nb = nb +1
 	print "%-4.4d Serveurs ont été ajoutés par les info de VEEAM  " % nb 
 	
 	# Supervision
 	nb = 0
	for server in Supervision.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"SUPERVISION")
			nb = nb +1
 	print "%-4.4d Serveur ont été ajouté par les info de Supervision  " % nb 
 	

 	# Supervision
 	nb = 0
	for server in JasminServeur.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"JASMIN")
			nb = nb +1
 	print "%-4.4d Serveur ont été ajouté par les info de Jasmin  " % nb 
 	
 	
 	#
 	# Création du fichier full serveur
 	#  
 	filename = dataPath("DataTableServerFile")	
 	try:
		print "sauvegarde dans le fichier %s avec enrichissemeent des infos qui ne sont pas dans la CMDB." % filename
		fd = codecs.open(filename, 'w', 'utf-8')

		fd.write('{\n\t"data" : [\n') #-=- pour dataTable


		lineFinServeur=""
		for server in CmdbDataServer.keys() :
			fd.write(lineFinServeur)			
			fd.write('{')			
			lineFin=""

			# Enrichissement avec les info des baies 
			
 			# ecrire les infos de 3PAR
			#print "|%s|" % server
			if server in Baie3PAR.keys() :
				for item, value  in Baie3PAR[server].items() :
					CmdbDataServer[server][item]=str(value).encode('utf8')

			# ecrire les infos de HDS
			#print "|%s|" % server
			if server in BaieHDS.keys() :
				for item, value  in BaieHDS[server].items() :
					CmdbDataServer[server][item]=str(value).encode('utf8')
	
			for item in CmdbDataServer[server]:
				fd.write(lineFin)
				fd.write('"'+item + '":"' + CmdbDataServer[server][item]+'"')
				lineFin=","

			fd.write('}\n')
			lineFinServeur=","
		
		fd.write('\n\t]\n}') #   -=- pour dataTable
		fd.close()
	except :
		print "Exception in user code:"
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60
		pass

#
# generateFileDate
#
def generateFileDate():
	"""
	"""
	filename = dataPath("fileDate")	
	print "Liste des fichiers et leur date de modification %s" % filename
	fd = codecs.open(filename, 'w', 'utf-8')

	fd.write('{\n\t"data" : [\n') #-=- pour dataTable
	
	virgule = 0
	for item, value  in DateFile.items() :
		if virgule > 0:
			fd.write(',\n')
		else :
			virgule = 1
		fd.write('\t\t{')  #-=- pour dataTable
		fd.write('"type" : "'+item+'", "file" :"'+str(value['file'])+'" , "date" : "'+str(value['date'])+'", "info" :"'+str(value['info'])+'"')
		fd.write('}')

	fd.write('\n\t]\n}') #   -=- pour dataTable

	fd.close()

#
# générateExcell
#
def generateExcel():
	"""
	Export les données en excel bien formaté avec 2 Onglets 
	 -  1) Une ligne par serveur
	 -  2) Une ligne par applicatif
	 -  3) Aide : Principe de fonctionnement du ficher
	 -  4) Liste des fichier avec date de génération qui ont servi a construire
	"""
	filename = dataPath("DataTableExcel")
	# verification sur file a faire (.xlsx, ....)
	workbook = xlsxwriter.Workbook(filename)
	print "génération du fichier : %s" %filename

	GB_format = workbook.add_format({'num_format': '$#,##0'})

	# 
	# Création des onglets
	worksheet 			= workbook.add_worksheet(u"Info")
	worksheetServer 	= workbook.add_worksheet(u"par serveurs")
	worksheetAppli 		= workbook.add_worksheet(u"par applicatif")
	worksheetAide 		= workbook.add_worksheet(u"Aide")
	worksheetFichier 	= workbook.add_worksheet(u"Fichier Src")

	#
	# Création format
	firstColumn_format 	= workbook.add_format({'align': 'left', 'valign':'vcenter', 'text_wrap' : True})
	column_format 		= workbook.add_format({'align': 'center', 'valign':'vcenter', 'text_wrap' : True})
	nomTable_format 	= workbook.add_format({'bold': True, 'font_name' : 'Times New Roman'})
	dateTable_format 	= workbook.add_format({'bold': True, 'font_name' : 'Times New Roman'})
	bold_format			= workbook.add_format({'bold': True})
	fileinfo_format 	= workbook.add_format({'font_name' : 'Times New Roman'})
	red_format 			= workbook.add_format({'bold': True, 'font_name' : 'Times New Roman','color': 'red'})

	#
	#  Onglet Info
	worksheet.write_rich_string('A1', dateTable_format, "Export des informations issue de la CMDB et des fichier techniques")
	worksheet.write_rich_string('A2', dateTable_format, "L'onglet 'par serveur' contient la liste des serveurs récupérés par l'ensemebles de fichier parsés")
	worksheet.write_rich_string('A3', dateTable_format, "L'onglet 'par application' Par encore complété")
	worksheet.write_rich_string('A4', dateTable_format, "L'onglet 'Fichier Src' contient la liste des fichiers, URL analysé avec la date de l'information  ")

	#
	#   Onglet Serveur
	try :
		worksheetServer.write_rich_string('A1', dateTable_format, "Vu Serveurs : Export des information issue de la CMDB et des fichier techniques")

		i=0;
		data=[]

		for server in CmdbDataServer.keys() :
			
			NomServer = CINom = CIResponsable = CLE_APP =CIImpactantResponsable =""
			vmCpu = vmMem = vmDisk = vmBanc =vmOs = CICategorie =""
			allocated = used = storage =  allocated_HDS = used_HDS = storage_HDS = ""
			veeamDure = veeamFin = VeeamScheduleStatus = VeeamVolTransfert = ""
			tsmDebut = tsmFin = tsmStatus = TsmData = ""
			ram = frequence = processor_count = os = modele = processeur = dateCollecte = ""
			vip = vpx = vserveur = dbaInfo = dbaType = dbaNbInstance = ""
			supOk = supInfo = veeamRetention = tsmRetention = ""
			ilmtModele = ilmtOs = ilmtIp = ilmtCoeur = ilmtType = ilmtPvu = ilmtNoSerie = ""
			nlyteTypeMatos =  nlyteNomSite = nlyteNoBaie = nlyteNoU = nlyteNoSerie = ""
			ipamMac = ipamIp = ipamSwitch = ipamPort = ipamVlan = "" 
			jasminGroupe = jasminProprietaire = jasminDescription = jasminDns = jasminOs = jasminDateCreation = jasminDateExpiration = ""
						
			if CmdbDataServer[server].get("CM") != None :
				NomServer = CmdbDataServer[server]["CM"]

			if CmdbDataServer[server].get("CN") != None:
				CINom = CmdbDataServer[server]["CN"]

			if CmdbDataServer[server].get("CR") != None:
				CIResponsable = CmdbDataServer[server]["CR"]

			if CmdbDataServer[server].get("CC") != None:
				CLE_APP = CmdbDataServer[server]["CC"]

			if CmdbDataServer[server].get("CI") != None:
				CIImpactantResponsable = CmdbDataServer[server]["CI"]

			# VMWare
			if CmdbDataServer[server].get("vmCpu") != None:
				vmCpu = CmdbDataServer[server]["vmCpu"]

			if CmdbDataServer[server].get("vmMem") != None:
				vmMem = CmdbDataServer[server]["vmMem"]

			if CmdbDataServer[server].get("vmDisk") != None:
				vmDisk = CmdbDataServer[server]["vmDisk"]

			if CmdbDataServer[server].get("vmBanc") != None:
				vmBanc = CmdbDataServer[server]["vmBanc"]

			if CmdbDataServer[server].get("vmOs") != None:
				vmOs = CmdbDataServer[server]["vmOs"]

			if CmdbDataServer[server].get("CICategorie") != None:
				CICategorie = CmdbDataServer[server]["CICategorie"]

			# 3PAR
			if CmdbDataServer[server].get("allocated") != None:
				allocated = CmdbDataServer[server]["allocated"]

			if CmdbDataServer[server].get("used") != None:
				used = CmdbDataServer[server]["used"]

			if CmdbDataServer[server].get("storage") != None:
				storage = CmdbDataServer[server]["storage"]

			#HDS
			if CmdbDataServer[server].get("allocated_HDS") != None:
				allocated_HDS = CmdbDataServer[server]["allocated_HDS"]

			if CmdbDataServer[server].get("used_HDS") != None:
				used_HDS = CmdbDataServer[server]["used_HDS"]

			if CmdbDataServer[server].get("storage_HDS") != None:
				storage_HDS = CmdbDataServer[server]["storage_HDS"]

			#VEEAM
			if CmdbDataServer[server].get("VeeamDure") != None:
				veeamDure = CmdbDataServer[server]["VeeamDure"]
			
			if CmdbDataServer[server].get("VeeamFin") != None:
				veeamFin = CmdbDataServer[server]["VeeamFin"]
			
			if CmdbDataServer[server].get("VeeamScheduleStatus") != None:
				VeeamScheduleStatus = CmdbDataServer[server]["VeeamScheduleStatus"]
			
			if CmdbDataServer[server].get("Vr") != None:
				veeamRetention = CmdbDataServer[server]["Vr"]
			
			# TMS
			if CmdbDataServer[server].get("TSMDebut") != None:
				tsmDebut = CmdbDataServer[server]["TSMDebut"]

			if CmdbDataServer[server].get("TSMFin") != None:
				tsmFin = CmdbDataServer[server]["TSMFin"]

			if CmdbDataServer[server].get("TSMStatus") != None:
				tsmStatus = CmdbDataServer[server]["TSMStatus"]

			if CmdbDataServer[server].get("Tr") != None:
				tsmRetention = CmdbDataServer[server]["Tr"]

			# DISCOVERY
			if CmdbDataServer[server].get("RAM") != None:
				ram = CmdbDataServer[server]["RAM"]

			if CmdbDataServer[server].get("Frequence") != None:
				frequence 	= CmdbDataServer[server]["Frequence"]

			if CmdbDataServer[server].get("PROCESSOR_COUNT") != None:
				processor_count = CmdbDataServer[server]["PROCESSOR_COUNT"]
			
			if CmdbDataServer[server].get("os") != None:
				os 	= CmdbDataServer[server]["os"]
			
			if CmdbDataServer[server].get("modele") != None:
				modele 	= CmdbDataServer[server]["modele"]

			if CmdbDataServer[server].get("Processeur") != None:
				processeur 	= CmdbDataServer[server]["Processeur"]

			if CmdbDataServer[server].get("date") != None:
				dateCollecte 	= CmdbDataServer[server]["date"]

			#Netscaler
			if CmdbDataServer[server].get("VIP") != None:
				vip 	= CmdbDataServer[server]["VIP"]

			if CmdbDataServer[server].get("Vpx") != None:
				vpx 	= CmdbDataServer[server]["Vpx"]

			if CmdbDataServer[server].get("Vserveur") != None:
				vserveur 	= CmdbDataServer[server]["Vserveur"]

			# DBA  KeyError
			if  Dba.get(server) != None :
				if Dba[server].get("dbaInfo") != None:
					dbaInfo = Dba[server]["dbaInfo"]

				if Dba[server].get("typeBd") != None:
					dbaType = Dba[server]["typeBd"]

				if Dba[server].get("nbInstance") != None:
					dbaNbInstance = Dba[server]["nbInstance"]

			if Supervision.get(server) != None:
				if Supervision[server].get("supOK") != None:
					supOk = 1
				if Supervision[server].get("supInfo") != None:
					supInfo = Supervision[server].get("supInfo")

			if Ilmt.get(server) != None:
				ilmtOs 		= Ilmt[server].get("Ios")
				ilmtIp		= Ilmt[server].get("Iip")
				ilmtCoeur	= Ilmt[server].get("Icoeur")
				ilmtType	= Ilmt[server].get("Itype")
				ilmtModele	= Ilmt[server].get("Imodele")
				ilmtPvu		= Ilmt[server].get("Ipvu")
				ilmtNoSerie	= Ilmt[server].get("In")

			if Nlyte.get(server) != None :
				nlyteTypeMatos = Nlyte[server].get(u'Nm')
				nlyteNomSite 	= Nlyte[server].get(u'Ns')
				if Nlyte[server].get(u'Nb') != None :
					nlyteNoBaie 	= Nlyte[server].get(u'Nb')
				if Nlyte[server].get(u'Nu') != None :
					nlyteNoU 		= Nlyte[server].get(u'Nu')
				if Nlyte[server].get(u'Nn') != None :
					nlyteNoSerie 	= Nlyte[server].get(u'Nn')

			#	print 'out EXCELL IpamServeur'
			if IpamServeur.get(server) != None :
				#print 'in EXCELL IpamServeur'
				#print "\tEXECL:"+str(IpamServeur[server]) 

				if IpamServeur[server].get(u'Pw') != None :
					ipamSwitch          = IpamServeur[server].get(u'Pw')
				if IpamServeur[server].get(u'Pp') != None :
					ipamPort            = IpamServeur[server].get(u'Pp')
				if IpamServeur[server].get(u'Pv') != None :
					ipamVlan            = IpamServeur[server].get(u'Pv')
				if IpamServeur[server].get(u'Pm') != None :
					ipamMac             = IpamServeur[server].get(u'Pm')
				if IpamServeur[server].get(u'Pi') != None :
					ipamIp              = IpamServeur[server].get(u'Pi')
    	
			if JasminServeur.get(server) != None :
				if JasminServeur[server].get(u'Jg') != None :
					jasminGroupe 			= JasminServeur[server].get(u'Jg')
				if JasminServeur[server].get(u'Jp') != None :
					jasminProprietaire 		= JasminServeur[server].get(u'Jp')
				if JasminServeur[server].get(u'Jd') != None :
					jasminDescription 		= JasminServeur[server].get(u'Jd')
				if JasminServeur[server].get(u'Jn') != None :
					jasminDns 				= JasminServeur[server].get(u'Jn')
				if JasminServeur[server].get(u'Jo') != None :
					jasminOs 				= JasminServeur[server].get(u'Jo')
				if JasminServeur[server].get(u'Jc') != None :
					jasminDateCreation 		= JasminServeur[server].get(u'Jc')
				if JasminServeur[server].get(u'Je') != None :
					jasminDateExpiration 	= JasminServeur[server].get(u'Je')

			data.append([NomServer, CINom, CIResponsable,CLE_APP,CIImpactantResponsable,
						vmCpu, vmMem, vmDisk, vmBanc, vmOs, CICategorie,
						allocated,used, storage, allocated_HDS, used_HDS, storage_HDS,
						 veeamDure, veeamFin,  VeeamScheduleStatus, veeamRetention,
						tsmDebut, tsmFin, tsmStatus, tsmRetention,
						ram, os, processor_count, frequence, processeur, modele, dateCollecte, 
						vip, vpx, vserveur, dbaInfo, dbaType, dbaNbInstance, supOk, supInfo,
						ilmtOs, ilmtIp, ilmtCoeur, ilmtType, ilmtModele, ilmtPvu, ilmtNoSerie,
						nlyteTypeMatos, nlyteNomSite, nlyteNoBaie, nlyteNoU, nlyteNoSerie,
						ipamMac, ipamIp, ipamSwitch, ipamPort, ipamVlan,
						jasminGroupe, jasminProprietaire, jasminDescription, jasminDns, jasminOs, jasminDateCreation,
					    jasminDateExpiration])
			
		# fin boucle 

		options = {
		           'columns': [{'header': u'Nom serveur',
		           				'header_format' :  column_format,
		           				'format' : firstColumn_format
		           				},
		                       {'header': u'Nom Appli',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                       {'header': u'Resp Appli',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                       {'header': u'CLE APP',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                       {'header': u'Resp server',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Vm CPU',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Vm Mémoire (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Vm Disque (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Vm Banc',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Vm OS',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'CICategorie',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'3PAR alloué (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'3PAR utilisé (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'3PAR Nom Baie',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'HDS alloué (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'HDS utilisé (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'HDS Baie',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Veeam durée',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Veeam fin',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Veeam status',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
   		                        {'header': u'Veeam retention',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'TSM début',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'TSM fin',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'TSM status',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
								{'header': u'TSM retention',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery RAM (Mo)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery OS',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery Nb Proc',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery Fréquence',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery Processeur',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery modele',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Discovery date de collecte',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Netscaler VIP',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Netscaler VPX',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Netscaler Vserveur',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'DBA description',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'DBA Type de base',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'DBA Nb instance',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Supervision OK',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Supervision Info',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT OS',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT IP',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT Coeur',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT Type',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT Modèle',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT PVU',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'ILMT No Série ',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Nlyte Matériel',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Nlyte Site',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Nlyte Baie',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Nlyte no U',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'Nlyte No Série',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'IPAM MAC',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'IPAM IP',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'IPAM Switch',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'IPAM Port',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'IPAM Vlan',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        }
		                        ,
		                        {'header': u'JASMIN Groupe',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'JASMIN Propriétaire',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'JASMIN Description',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'JASMIN Dns',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'JASMIN OS',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'JASMIN Date création',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': u'JASMIN Date Expiration',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        }
		                       ],
		            'data': data
		           }
					
				

		# Add a table to the worksheet. (ligne, colone, ligne, colonne)
		worksheetServer.add_table(2,1,len(data) + 2, 1 + 16 +15 + 3 + 2 +2 + 6 + 7 +5 + 7, options)

		# fixe la largeur des colonnes
		worksheetServer.set_column('B:B', 14)
		worksheetServer.set_column('C:C', 21)
		worksheetServer.set_column('D:D', 11)
		worksheetServer.set_column('F:F', 11)
		worksheetServer.set_column('G:G', 9)
		worksheetServer.set_column('H:H', 9)
		worksheetServer.set_column('I:I', 9)
		worksheetServer.set_column('J:J', 9)
		worksheetServer.set_column('K:K', 9)
		worksheetServer.set_column('L:L', 17)
		worksheetServer.set_column('M:M', 9)
		worksheetServer.set_column('N:N', 9)
		worksheetServer.set_column('O:O', 14)
		worksheetServer.set_column('P:P', 9)
		worksheetServer.set_column('Q:Q', 9)
		worksheetServer.set_column('R:R', 14)
		worksheetServer.set_column('S:S', 9)
		worksheetServer.set_column('T:T', 9)
		worksheetServer.set_column('U:U', 9)
		worksheetServer.set_column('V:V', 9)
		worksheetServer.set_column('V:V', 9)
		worksheetServer.set_column('V:V', 9)
		worksheetServer.set_column('W:W', 9)
		worksheetServer.set_column('AE:AE', 9)
		worksheetServer.set_column('AF:AF', 13)
		worksheetServer.set_column('AO:AO', 13)
		worksheetServer.set_column('AP:AP', 13)
		worksheetServer.set_column('BI:BI', 28)
		worksheetServer.set_column('BL:BL', 18)
		worksheetServer.set_column('BM:BM', 18)


	except :
		print "Exception in user code:"
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60
		pass



	#
	#   Onglet Appli
	worksheetAppli.write_rich_string('A1', dateTable_format, "Vu Application : Export des information issue de la CMDB et des fichier techniques")

	#
	#   Onglet Aide
	worksheetAide.write_rich_string('A1', dateTable_format, "Aide")

	#
	#   Onglet Fichier
	worksheetFichier.write_rich_string('A1', dateTable_format, "Liste des fichier ou URL qui ont servie a réaliser ce fichier avec leurs date de création")
	worksheetFichier.set_column('B:B', 25)
	worksheetFichier.set_column('C:C', 25)
	worksheetFichier.set_column('D:D', 80)
	worksheetFichier.set_column('E:E', 60)
	data = []

	for type in  DateFile.keys():
		data.append([str(type), str(DateFile[type]["date"]),str(DateFile[type]["file"]),str(DateFile[type]["info"])])

	options = {
	           'columns': [{'header': "type de  ressource",
	           				'header_format' :  column_format,
	           				'format' : firstColumn_format
	           				},           				
	                       {'header': "date de dernière modification de la resssource",
	                        'header_format' :  column_format,
	                        'format' : column_format
	                        },
	                        {'header': "chemin d'accès à la ressource",
	           				'header_format' :  column_format,
	           				'format' : firstColumn_format
	           				},
	           				{'header': "information",
	           				'header_format' :  column_format,
	           				'format' : firstColumn_format
	           				}
	                       ],
	            'data': data
	           }


	
		#worksheetFichier.write_rich_string('B'+str(i), fileinfo_format, str(file))
		#worksheetFichier.write_rich_string('C'+str(i), fileinfo_format, str(DateFile[file]))
		#i = i+ 1
		#print "\t %s : %s\n" % (file, DateFile[file])
	# Add a table to the worksheet. (ligne, colone, ligne, colonne)
	worksheetFichier.add_table(2,1,len(data) + 2, len(data[0]), options)

	workbook.close()

#
# getCmdbSoap
#
def  getCmdbSoap():
	"""
		Interroge en SOAP une API EasyVista pour avoir l'association Serveur Appli
	"""


	url="https://malakoffmederic.easyvista.com:443/WebService/SmoBridge.php"
	#headers = {'content-type': 'application/soap+xml'}
	headers = {'content-type': 'text/xml', 'accept-encoding': 'gzip;q=0,deflate,sdch'}
	body = """<?xml version="1.0" encoding="UTF-8"?>
	         <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:name="Name_space">
	   <soapenv:Header/>
	   <soapenv:Body>
	      <name:EZV_SYS_ExecuteInternalQuery soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
	         <Account xsi:type="xsd:string">50004</Account>
	         <Login xsi:type="xsd:string">zz_virtualisation</Login>
	         <Password xsi:type="xsd:string">ESX_EZV</Password>
	         <requestguid xsi:type="xsd:string">{1F809368-5E09-4AE9-B652-9EBB132D9F77}</requestguid>
	         <filterguid xsi:type="xsd:string">{10397417-FBEF-41C7-9FAD-409BE81CA533}</filterguid>
	         <viewguid xsi:type="xsd:string">{1A1F14AB-7E8C-4BFB-B156-C61CA64197C3}</viewguid>
	        
	         <iscount xsi:type="xsd:string"></iscount> 
	         <maxlines xsi:type="xsd:string"></maxlines>
	         <custom_filter xsi:type="xsd:string"></custom_filter>
	         <send_php_object xsi:type="xsd:string">0</send_php_object>
	         
	      </name:EZV_SYS_ExecuteInternalQuery>
	   </soapenv:Body>
	</soapenv:Envelope>"""


	print "Cmdb get %s \n" % url
	response = requests.post(url,data=body,headers=headers)
	chaine1 = html_decode(response.text)
	chaine= chaine1.decode('utf-8')

	DateFile['CMDB']= { u'file' : url+"  : Account : 50004", 'date' :datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), u'info' : "URL SOAP d'interrogation de l'association serveur/appli de la CMDB sur EASYVIST" }

	return chaine;

#
# getDiscoverySoap
#
def  getDiscoverySoap():
	"""
		Interroge en SOAP une API EasyVista pour avoir l'association Serveur Appli
	"""



	#url="https://malakoffmederic.easyvista.com:443/WebService/SmoBridge.php"
	#url="https://malakoffmederic-qualif.easyvista.com:443/WebService/SmoBridge.php"
	url="https://malakoffmederic.easyvista.com:443/WebService/SmoBridge.php"
	#headers = {'content-type': 'application/soap+xml'}
	headers = {'content-type': 'text/xml', 'accept-encoding': 'gzip;q=0,deflate,sdch'}
	body = """<?xml version="1.0" encoding="UTF-8"?>
	         <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:name="Name_space">
	   <soapenv:Header/>
	   <soapenv:Body>
	      <name:EZV_SYS_ExecuteInternalQuery soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
	         <Account xsi:type="xsd:string">50004</Account>
	         <Login xsi:type="xsd:string">zz_virtualisation</Login>
	         <Password xsi:type="xsd:string">ESX_EZV</Password>
	         <requestguid xsi:type="xsd:string">{925A5E65-F328-4934-95C9-7E1C620AD4D5}</requestguid>
	         <filterguid xsi:type="xsd:string">{F31D0F08-000D-40EB-9ECE-B8AB41F911CD}</filterguid>
	         <viewguid xsi:type="xsd:string">{8FBF616E-D6A7-49A1-A7FA-C329AEB964A4}</viewguid>
	        
	         <iscount xsi:type="xsd:string"></iscount> 
	         <maxlines xsi:type="xsd:string"></maxlines>
	         <custom_filter xsi:type="xsd:string"></custom_filter>
	         <send_php_object xsi:type="xsd:string">0</send_php_object>
	         
	      </name:EZV_SYS_ExecuteInternalQuery>
	   </soapenv:Body>
	</soapenv:Envelope>"""

	print "Discovery get %s \n" % url
	response = requests.post(url,data=body,headers=headers)
	chaine1 = html_decode(response.text)
	chaine= chaine1.decode('utf-8')

	DateFile['Discovery']= { u'file' : url+"  : Account : 50004", 'date' :datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), u'info' : "URL SOAP d'interrogation de DISCOVERY (base inventaire EasyVista)" }

	return chaine;


#
# encodeJsonDiscoverySoap
#
def encodeJsonDiscoverySoap():
	
	chaine =getDiscoverySoap()

	lastLine =""
	j=0
	for line in chaine.split("\n"):

		#<Fieldname _0= "" _1= "" _2= "Nb de processeurs" _3= "" _4= "" _5= "" _6= "" _7= "" _8= "" _9= "" _10= "Marque"
		# _11= "Modèle" _12= "FREQUENCY" _13= "PROCESSOR_TFMS_ID" _14= "PROCESSOR_TFMS_PK"/>
		# nouveau Field le 2017/12/05
		# <Fieldname _0= "Identifiant PC" _1= "CPU" _2= "Processeur" _3= "Nb de coeurs" _4= "Nb de processeurs" 
		# _5= "Frquence CPU" _6= "RAM" _7= "D.Dur(Mo)" _8= "N de srie" _9= "OS" _10= "Version de l&apos;OS" 
		# _11= "Marque" _12= "Modle" _13= "Date du dernier inventaire"/>

		
		if line.find("<Fieldname") == 0:
			line = line.replace("<Fieldname", "")
			line = line.replace("_0= ","")   # Identifiant PC
			line = line.replace("_1= ","~")  # CPU 
			line = line.replace("_2= ","~")  # Nb de processeurs
			line = line.replace("_3= ","~")  # Nb de coeurs
			line = line.replace("_4= ","~")  # Fréquence CPU
			line = line.replace("_5= ","~")  # RAM
			line = line.replace("_6= ","~")  # D.Dur(Mo)
			line = line.replace("_7= ","~")  # N° de série
			line = line.replace("_8= ","~")  # OS
			line = line.replace("_9= ","~")  # Version de l&apos;OS
			line = line.replace("_10= ","~") # Marque
			line = line.replace("_11= ","~") # Modèle
			line = line.replace("_12= ","~") # FREQUENCY
			line = line.replace("_13= ","~") # PROCESSOR_TFMS_ID
			line = line.replace("_14= ","~") # PROCESSOR_TFMS_PK

			line = line.replace("/>", "") # 
			
			# pour pouvoir est traiter correctement pas dataTable, pas espace ni de : dans les nom des colonnes
			line = line.replace(" ", "");
			line = line.replace(":", "");
			line = line.replace("é", "e");
			line = line.replace("ê", "e");
			line = line.replace("à", "a");
			line = line.replace("è", "e");
			line = line.replace("ç", "c");

			entete = line.split('~')
			
		#
		# 
		#
		if line.find("<row") == 0  :
			lastLine =""
			line = line.replace("<row ","")
			line = line.replace("_0= ","")   # Identifiant PC
			line = line.replace("_1= ","~")  # CPU 
			line = line.replace("_2= ","~")  # Nb de processeurs
			line = line.replace("_3= ","~")  # Nb de coeurs
			line = line.replace("_4= ","~")  # Fréquence CPU
			line = line.replace("_5= ","~")  # RAM
			line = line.replace("_6= ","~")  # D.Dur(Mo)
			line = line.replace("_7= ","~")  # N° de série
			line = line.replace("_8= ","~")  # OS
			line = line.replace("_9= ","~")  # Version de l&apos;OS
			line = line.replace("_10= ","~") # Marque
			line = line.replace("_11= ","~") # Modèle
			line = line.replace("_12= ","~") # FREQUENCY
			line = line.replace("_13= ","~") # PROCESSOR_TFMS_ID
			line = line.replace("_14= ","~") # PROCESSOR_TFMS_PK
			line = line.replace("/>", "") # 

			data 		= line.split('~')
			server 		= data[0].upper().replace('"',"").rstrip().replace('.SI2M.TEC','')
			os 			= data[9].upper().replace('"',"").rstrip()
			#passage de l'index 10 a 12 le 05/12/2017
			modele 		= data[12].upper().replace('"',"").rstrip()
			nbProc 		= data[4].upper().replace('"',"").rstrip()
			#passage de l'index 5 a 6 le 05/12/2017
			ram 		= data[6].upper().replace('"',"").rstrip()
			frequence 	= data[5].upper().replace('"',"").rstrip()
			typeProc	= data[1].upper().replace('"',"").rstrip()
			date		= data[13].upper().replace('"',"").rstrip()
			noSerie		= data[8].upper().replace('"',"").rstrip()

			if os == "" :
				os = data[9].upper().replace('"',"").rstrip()
			if os =="" :
				os = "inconnue"

			if modele == "(Unknown)":
				modele = data[11].upper().replace('"',"").rstrip()
			if modele == "":  
				modele = "inconnue"

			DiscoveryData[server] = {
						u'RAM' 				: ram, 
						u'PROCESSOR_COUNT' 	: nbProc,
					 	u'Processeur'		: typeProc,
					 	u'Frequence' 		: frequence,
					 	u'modele' 			: modele,
					 	u'os' 				: os,
					 	u'date' 			: date,
					 	u'nS' 				: noSerie 
					 	}
			#pprint(DiscoveryData[server])

# 
# dataPAth
#

def dataPath(type):
	"""
		renvoie le chemin d'accès au fichiers de donnée brute  en fonction du type
	"""
	jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
	mois = ["Janvier", u"Février", "Mars", "Avril", "Mai", "Juin", "Juillet", u"Août", "Septembre", "Octobre", "Novembre", u"Décembre"]
	
	joursStr = str(time.localtime().tm_mday).zfill(2)
	moisStr  = str(time.localtime().tm_mon).zfill(2)
	anneeStr = str(time.localtime().tm_year)


	if  "cmdb-test" in os.getcwd() :
		rootPathStatBaies 	= "/var/www/virtu/exportSto/"
		dataDir                 = "/home/i14sj00/cmdbVisu/cmdb-test/data/"
		RepGGConfDir		= dataDir+"/../graphgroupe-conf/"
		rootPathCtrlN1          = "/var/www/dashboardstock/capacity_TSM/check_niv1/"
		exportVirtu             = "/var/www/virtu/exportWindows/"
	# pour la serveur vlc0inf008
	elif os.path.exists('/data/cmdbVisu/data/') :
		rootPathStatBaies 	= "/data/exportStockage3PAR/"
		dataDir                 = "/data/cmdbVisu/data/"
		RepGGConfDir		= dataDir+"/../graphgroupe-conf/"
		exportVirtu             = "/data/exportVirtu/"
	else : 
		rootPathStatBaies 	= "/var/www/virtu/exportSto/"
		dataDir                 = "/home/i14sj00/cmdbVisu/data/"
		RepGGConfDir		= dataDir+"/../graphgroupe-conf/"
		rootPathCtrlN1          = "/var/www/dashboardstock/capacity_TSM/check_niv1/"
		exportVirtu             = "/var/www/virtu/exportWindows/"

	if  type == "VeeamProd" :
		return getLastFilesByDate(rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde VEEAM/", ".*Rapport-sauvegarde-VEEAM_Production.html")
	elif type ==  "VeeamRecette" :
			return getLastFilesByDate(rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde VEEAM/", ".*Rapport-sauvegarde-VEEAM_Recette.html")
	elif type == "TSMRetention" :
		return getLastFilesByDate(dataDir, "TSM-retention-")
	elif type == "TSM" :
		return getLastFilesByDate(rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde TSM/", ".*TSM_Controle_Niv1.html")
	
	elif type == "T400A" :
		return getLastFilesByDate(rootPathStatBaies, "T400_A92")
	elif type == "T400B" :
		return getLastFilesByDate(rootPathStatBaies, "T400_B94")
	elif type == "V400A" :
		return getLastFilesByDate(rootPathStatBaies, "V400_A92")
	elif type == "V400B" :
		return getLastFilesByDate(rootPathStatBaies, "V400_B94")
	elif type == "9450A" :
		return getLastFilesByDate(rootPathStatBaies, "9450_A92")
	elif type == "9450B" :
		return getLastFilesByDate(rootPathStatBaies, "9450_B94")
	elif type == "HDS-PPROD-A" :
		return getLastFilesByDate(rootPathStatBaies, "HDS_A92_PPROD")
	elif type == "HDS-PPROD-B" :
		return getLastFilesByDate(rootPathStatBaies, "HDS_B94_PPROD")
	elif type == "HDS-PROD-A" : 
		return getLastFilesByDate(rootPathStatBaies, "HDS_A92_PROD")
	elif type == "HDS-PROD-B" :
		return getLastFilesByDate(rootPathStatBaies, "HDS_B94_PROD")
	elif type == "VmWare" :
		return getLastFilesByDate(exportVirtu, "InfraVMware-")
	elif type == "fileDate":
		return dataDir+ "fileDate.json"
	elif type == "DataTableFile":
		return dataDir+ "dataTable.json"
	elif type == "DataTableServerFile":
		return dataDir+ "dataTableServer.json"
	elif type == "DataTableExcel":
		return dataDir+ "cmdbVisu.xlsx"
	elif type == "Discovery":
		return dataDir+ "discovery-easyvista-20170918.csv"
	elif type == "ILMT" :
		return getLastFilesByDate(exportVirtu, "Inventaire_ILMT-")
	elif type == "NLYTE" :
		return getLastFilesByDate(exportVirtu, "NLYTE-")
	elif type == "IPAM" :
		return getLastFilesByDate(exportVirtu, "export_IPAM_MAC-SW-")
	elif type == "JASMIN" :
		return getLastFilesByDate(exportVirtu, "export-jasmin-")
	elif type == "GrapheGroupe":
		return RepGGConfDir
	else :
		return "le chemin pour accéder a "+type+" est inconnue"



#
# encodeJsonVeeam
#
def  encodeJsonVeeam():
	"""
		Lit les 2 fichier de controle de niveau 1 de Veeam et les transforme en un HASH "VeeamData"
	"""
	pTrTest = re.compile('^<tr>')
	ptr     = re.compile('[^<]*<tr[^>]*>')
	ptd     = re.compile('<td[^>]*>([^<]*)</td>')
	ptr1    = re.compile('</tr>')
	
	for veeamType in ("VeeamProd","VeeamRecette"):
		filename=dataPath(veeamType)
		DateFile[veeamType]= { u'file' : filename, 'date' :creationDateFile(filename), u'info' : "fichier de controle de niveau 1 des sauvegardes "+veeamType+" généré par un script de joaquim le matin a 8H00" }
		

		print "traitement fichier : %s " % filename
		with open(filename, "r") as fdSrc:
			for line in fdSrc.readlines():
		  		if pTrTest.match(line) :
		  			retention = 0
					# retire le <tr> et tous ce qu'il y a avant
					line = ptr.sub('', line) 
					#//$line = eregi_replace('[^<]*<tr[^>]*>', '', $line);

					# retire les <td> et les option des td
					#//$line = eregi_replace('<td[^>]*>([^<]*)</td>', '\1|', $line);
					line = ptd.sub(r'\1|', line)

							#// retire le </tr> et tous ce qu'il y a après
					#//$line = eregi_replace('</tr>', '', $line);
					line = ptr1.sub('', line)

					# construit la structure
					a = line.split('|')

					#// nom de serveur en majuscule
					a[2] = a[2].decode('latin1').encode('utf8').upper()
					a[1] = a[1].decode('latin1').encode('utf8')
					a[4] = a[4].decode('latin1').encode('utf8')
					a[8] = a[8].decode('latin1').encode('utf8')

					#print a[2]

					# positionnne la retention PROD=36j PProd et Recette... = 15h
					# On repere prod par P dans le veeamDossier
					if "_P_BCK_" in a[0]:
						retention = 36
					else :
						retention = 15
					#Veeam[a[2]] = {"VeeamDossier" : a[0], "VeeamDure" : a[1], "VeeamDebut" : a[3], "VeeamFin" : a[4],
					#						"VeeamVolTransfert" : a[5],
					#						"VeeamScheduleType" : a[6], "VeeamBackupType" : a[7], "VeeamScheduleStatus" : a[8]}
					Veeam[a[2]] = {"VeeamDure" : a[1], "VeeamFin" : a[4], "VeeamScheduleStatus" : a[8], "Vr" : retention}
	print "\n"				

#
# encodeJsonTSM
#
def  encodeJsonTsm():
	"""
		Lit le fichier de controle de niveau 1 de TSM et les transforme en un HASH "TsmData"
	"""
	pTrTest = re.compile('^<tr>')
	ptr     = re.compile('[^<]*<tr[^>]*>')
	ptd     = re.compile('<td[^>]*>([^<]*)</td>')
	ptr1    = re.compile('</tr>')

	filename = dataPath("TSM")
	DateFile['TSM']= { u'file' : filename, 'date' :creationDateFile(filename), u'info' : "fichier de controle de niveau 1 des sauvegardes TSM généré par un script de joaquim le matin a 8H00"  }
		
	print "traitement fichier : %s " % filename
	with open(filename, "r") as fdSrc:
		for line in fdSrc.readlines():
	  		if pTrTest.match(line) :
				# retire le <tr> et tous ce qu'il y a avant
				line = ptr.sub('', line) 
				#//$line = eregi_replace('[^<]*<tr[^>]*>', '', $line);

				# retire les <td> et les option des td
				#//$line = eregi_replace('<td[^>]*>([^<]*)</td>', '\1|', $line);
				line = ptd.sub(r'\1|', line)

				#// retire le </tr> et tous ce qu'il y a après
	 			#//$line = eregi_replace('</tr>', '', $line);
				line = ptr1.sub('', line)
 
				# construit la structure
				a = line.split('|')

				#// nom de serveur en majuscule
				a[1] = a[1].upper()
				#print a[2]

				Tsm[a[1]] = {"TSMDebut" : a[2], "TSMFin" : a[3], "TSMStatus" : a[4]}
	print "\n"				
		
			
#
# encodeJson3PAR
#
def  encodeJson3PAR():
	"""
		Lit  les 6 fichiers exportés par les baie 3PAR et les transforme en un HASH "Baie3PAR"
		dont la clef est le nom du serveur
		Attention repose sur des commentaires coté baie
		La bonne méthode sera de se baser sur le WorldWideName, mais pas dispo dans le cmddb
	"""
	print
	
	for baie in ("T400A","T400B","V400A","V400B","9450A","9450B"):
		filename = dataPath(baie)
		DateFile[baie]= { u'file' : filename, 'date' :creationDateFile(filename), u'info' : "fichier match nom serveur (champs commentaire) de "+baie+" généré par export automatique le mercredi par le script exportCmdb lancé vwi0mix02"  }
		
		print "traitement fichier : %s " % filename
		ColNameNum = colAllocatedNum = colUseNum = -1

		with open(filename, "r") as fdSrc:
			i = 0;
			for line in fdSrc.readlines():
				i += 1
				line = line.rstrip()

				#Parse les entête pour connaitre la position des colonnes
				if line.startswith("Name,") :
					col = line.split(",")
					ColNameNum = colAllocatedNum = colUseNum = -1

					for j, e in enumerate(col):
						if e == 'Exported To':
							ColNameNum 			= j
						elif e == 'Virtual Size (MB)':
							colAllocatedNum 	= j
						elif e == 'Reserved User Size (MB)' :
							colUseNum 			= j

					#print "encodeJSON3PAR : no col export to (server) : "+str(ColNameNum)
				else :
					col = line.split(",")
					if len(col) >= 4 :
						servers= []
						#
					        #Pour les WINDOWS ca change pas
						#Pour les LINUX ca change pas
					        #Pour les AIX tu vires tous les underscore
					        #Ex. AIX_IFC_P -> AIXIFCP
					        #Pour les ESX tu vires tous les undescore et tous ce qu’il y a après le dernier chiffre
					        #Ex. ESX_80_R_XENAPP -> ESX80
						server = ""
						server = col[ColNameNum].upper()
						if server.find('AIX') > -1 :
							server = server.replace("_","")
						server = server.replace("NEO_","")
						# si c'est un hostset
						# set:ESX_R_A92(ESX_104_R;ESX_86_R;ESX_60_R;ESX_90_R;ESX_92_R;ESX_50_R;ESX_102_R;ESX_84_R)
						if server.find('SET:') > -1 :
							#print "\n"+line
							#print '3PAR : SET AV ='+server
							deb = server.find("(")+1
							fin = server.find(")")
							server=server[deb:fin]
							
							#print '3PAR : SET AV ='+server
							serversTmp = server.split(';')
							# retraitement pour les ESX
							for serverTmp in serversTmp:
								serverN = serverTmp.replace("ESX_", "")
								a       = serverN.find('_')
								serverTmp  = "ESX"+serverN[0:a]
								#print '3PAR : SET serverTmp ='+serverTmp
								servers.append(serverTmp)
						else : 
							if server.find('ESX') > -1 :
								serverN= server.replace("ESX_", "")
								a = serverN.find('_')
								server = "ESX"+serverN[0:a]

							servers.append(server)




					        # je retire  l'unité et les 3 chiffre avant
						a = col[colAllocatedNum].find(' MB') -3
						if a == -1 :
							a = len(col[colAllocatedNum])
						allocated = col[colAllocatedNum][0:a]
						allocated = unicode(allocated, errors='ignore')
						allocatedVal = int(allocated)
					        # je retire  l'unité et les 3 chiffre avant
						a = col[colUseNum].find(' MB') - 3
						if a == -1 :
							a = len(col[colUseNum])
						used = col[colUseNum][0:a]
						used = unicode(used, errors='ignore')
						usedVal = int(used)

						for server in servers :
							if server in Baie3PAR:
									       Baie3PAR[server]["storage"] 	= Baie3PAR[server]["storage"] +','+baie
									       Baie3PAR[server]["allocated"] 	= Baie3PAR[server]["allocated"] + allocatedVal
									       Baie3PAR[server]["used"] 	= Baie3PAR[server]["used"] + usedVal
							else :
									       Baie3PAR[server] = {u"storage" : baie, u"allocated" : allocatedVal, u"used" : usedVal }
						
							print "serveur 3PAR='"+server+"'"+str(Baie3PAR[server])
	
#
# encodeJsonHDS
#
def  encodeJsonHDS():
	"""
		Lit  les 4 fichiers exportés par les baie 3PAR et les transforme en un HASH "Baie3PAR"
		dont la clef est le nom du serveur
		Attention repose sur des commentaires coté baie
		La bonne méthode sera de se baser sur le WorldWideName, mais pas dispo dans le cmddb
	"""
	print
	for baie in ("HDS-PPROD-A","HDS-PPROD-B","HDS-PROD-A","HDS-PROD-B"):

		filename = dataPath(baie)

		DateFile[baie]= { u'file' : filename, 'date' :creationDateFile(filename), u'info' : "fichier match nom serveur (champs commentaire) de "+baie+" généré par la concaténation de 2 export manuel a aprtir de l'interface d'admin"  }

		print "traitement fichier : %s " % filename
		with open(filename, "r") as fdSrc:
			i = 0;
			for line in fdSrc.readlines():
				i += 1
				line = line.rstrip()

				
				#Parse les entête pour connaitre la position des colonnes
				if line.startswith("Volume;") :
					col = line.split(";")

					ColNameNum = colAllocatedNum = colUseNum =0
					for j, e in enumerate(col):
						e = e .replace(" Gb", "").replace(" Go", "")
						e = e .replace(" GB", "").replace(" Go", "")
						e = e .replace(" Mb", "").replace(" Mo", "")
						e = e .replace(" MB", "").replace(" Mo", "")
						e = e .replace(" Tb", "").replace(" To", "")
						e = e .replace(" TB", "").replace(" To", "")
						if 'Host Group' in e :
							ColNameNum 			= j
						elif 'Label' in e :
							colLabelNum 		= j	
						elif 'Total' in e :
							colAllocatedNum 	= j
						elif 'Used' in e :
							colUseNum 			= j
				#les DATA
				else : 
					col = line.split(";")
					if len(col) >= 4 :
						# ne garde que le nom du serveur (pas le  pt de montage C, D, Data, ...)
						# Mais garde l'info replication : "repli" en fin de nom
						# Attention 
						server = col[ColNameNum].rstrip().upper()
						if server == "" :
							tmp = col[colLabelNum].rstrip().split('_')
							server = tmp[0].upper()
						#print "line |%s| server: %s" % (line, server)

						# je retire  l'unité et les 3 chiffre avant
						a = col[colAllocatedNum]
						a = a .replace(" Gb", "").replace(" Go", "")
						a = a .replace(" GB", "").replace(" GO", "")
						a = a .replace(" Mb", "").replace(" Mo", "")
						a = a .replace(" MB", "").replace(" MO", "")
						a = a .replace(" Tb", "").replace(" To", "")
						a = a .replace(" TB", "").replace(" TO", "")

						a = a .replace(",", ".")
						allocated = unicode(a, errors='ignore')
						allocatedVal = float(allocated)

						# je retire  l'unité et les 3 chiffre avant
						a = col[colUseNum]
						a = a .replace(" Gb", "").replace(" Go", "")
						a = a .replace(" GB", "").replace(" GO", "")
						a = a .replace(" Mb", "").replace(" Mo", "")
						a = a .replace(" MB", "").replace(" MO", "")
						a = a .replace(" Tb", "").replace(" To", "")
						a = a .replace(" TB", "").replace(" TO", "")

						a = a .replace(",", ".")
						used = unicode(a, errors='ignore')
						usedVal = float(used)

						# TODO : -=- Si 2 serveur dans la colonne : ex LIN1BDD001, LIN1BDD002
						# diviser les volumétrie par 2 et créer 2 entrée
						if server.find(', ') == -1 :
							if server in BaieHDS:
								BaieHDS[server]["storage_HDS"] 		= BaieHDS[server]["storage_HDS"] +','+baie
								BaieHDS[server]["allocated_HDS"] 	= BaieHDS[server]["allocated_HDS"] + allocatedVal
								BaieHDS[server]["used_HDS"] 		= BaieHDS[server]["used_HDS"] + usedVal

							else :
								BaieHDS[server] = {u"storage_HDS" : baie, u"allocated_HDS" : allocatedVal, u"used_HDS" : usedVal }
						# il y a plusiseur serveur presenté a cette volumétrie
						# je divise la volumétrie par deux
						else : 

							for serv in server.split(", "):
								#print "HDS Multi Serveur : %s " %serv
								if serv in BaieHDS:
									BaieHDS[serv]["storage_HDS"] 	= BaieHDS[serv]["storage_HDS"] +','+baie
									BaieHDS[serv]["allocated_HDS"] 	= BaieHDS[serv]["allocated_HDS"] + allocatedVal/2
									BaieHDS[serv]["used_HDS"] 		= BaieHDS[serv]["used_HDS"] + usedVal/2

								else :
									BaieHDS[serv] = {u"storage_HDS" : baie, u"allocated_HDS" : allocatedVal/2, u"used_HDS" : usedVal/2 }

	print "\n"

	#pprint(Baie3PAR)
	#pprint(BaieHDS["LINDBCLUSTA11"]) 
	#print "LIN1BDD002"
	#pprint(BaieHDS["LIN1BDD001"]) 

	#print "LIN1BDD002"
	#pprint(BaieHDS["LIN1BDD002"]) 	

	#print
	#pprint(BaieHDS["AIXURWTA"]) 
	#print
	
#
#   encodeJsonVmWare
#	
def encodeJsonVmWare():
	"""
		Lecture du fichier inventaire complet généré par Paul
	"""
	filename = dataPath("VmWare")
	DateFile["VmWare"]= { u'file' : filename, 'date' :creationDateFile(filename), 'info' : 'Fichier généré par un script  d export FULL de l infra Vmware de de Paul gugulski le dimanche' }
	
	print "traitement fichier : %s " % filename
	# ouverture du fichier Excel 
	try: 
		wb1=xlrd.open_workbook(filename)
	except Exception  as e:
		print "\nERREUR:\n  Impossible d'ouvrir le 1er fichier : \n\t\t'%s' \n" % filename
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		sys.exit(-1)


	# feuilles dans le classeur
	shname1=wb1.sheet_names()[0]
	sh1 = wb1.sheet_by_name(shname1)

	noLigne = 0
	for rownum in range(sh1.nrows):
		
		# Positionnement des colonne 
		#-=- Crade a refaire en utilisant les noms de colonnes
		colMEM		= 7
		colVCPU		= 6
		colDisk		= 8
		colOS 		= 17	
		colCluster	= 3
		colNomVM	= 0
 

		noLigne = noLigne + 1
		if noLigne < 2 :
			continue
		# valeur par defaut
		#os = u"Linux"
		banc = u"non Prod"
		os = sh1.row_values(rownum)[colOS]
		#if sh1.row_values(rownum)[colOS].find(u'Windows') != -1  :
		#	os = u"Windows"

		if type(sh1.row_values(rownum)[colCluster]) in [str, unicode]:
			if sh1.row_values(rownum)[colCluster].find(u'Prod') != -1  :
				banc = u'Prod'

			if sh1.row_values(rownum)[colCluster].find(u'DMZ') != -1  :
				banc = u'Prod'

			if sh1.row_values(rownum)[colCluster].find(u'Infra') != -1  :
				banc = u'Prod'
			
			if sh1.row_values(rownum)[colCluster].find(u'licence') != -1  :
				banc = u'Prod'
		
		nomVm = sh1.row_values(rownum)[colNomVM].upper()

		#print nomVm
		Vm[nomVm] =	{	u'vmMem'	: str(int(sh1.row_values(rownum)[colMEM])),
						u'vmCpu'	: str(int(sh1.row_values(rownum)[colVCPU])),
						u'vmDisk'	: str(int(sh1.row_values(rownum)[colDisk])), 
						u'vmOs' 	: os.encode('utf8'),
						u'vmBanc' 	: banc.encode('utf8')
					}

	#recuperation des serveurs ESX
	# feuilles dans le classeur
	shname2=wb1.sheet_names()[1]
	sh2 = wb1.sheet_by_name(shname2)

	noLigne = 0
	for rownum in range(sh2.nrows):
		
		
		noLigne = noLigne + 1
		if noLigne < 2 :
			continue

		nomESX = sh2.row_values(rownum)[0].replace(".si2m.tec","").upper()
		Esx[nomESX] = 	{	u'ESXvCenter' 	: sh2.row_values(rownum)[1].encode('utf8'),
							u'ESXCluster' 	: sh2.row_values(rownum)[2].encode('utf8'),
							u'ESXModele'	: sh2.row_values(rownum)[3].encode('utf8')
						}

		nomESXCluster = sh2.row_values(rownum)[2].encode('utf8')
		if nomESXCluster == "":
			nomESXCluster = "Delegation"

		if EsxCluster.get(nomESXCluster) == None :
			EsxCluster[nomESXCluster] = nomESX
		else : 	
			EsxCluster[nomESXCluster] =  EsxCluster[nomESXCluster]  + ',' + nomESX
	print "\n"
	wb1.release_resources()
	del wb1
#
# encodeJsonDiscoveryFile
#
def encodeJsonDiscoveryFile():
	tmpDiscoveryData ={}

	filename = dataPath("Discovery")
	DateFile["Discovery"]= { u'file' : filename, 'date' :creationDateFile(filename), 'info' :"Fichier généré manuellment par benoit Khales de Discovery" }
	
	print "traitement fichier : %s " % filename
	
	with codecs.open(filename,'rb', encoding='utf-8-sig') as f:
		lines=f.readlines()

	i = 0
	for line in lines :
		line = line.replace('\n','').replace('\r','')
		if i == 0 :
			headers = line.split(";")
			#pprint(headers)
		else :
			col = line.split(';')
			colNum = 0
			for colname in headers:
				#print '|'+colname+'|'
				tmpDiscoveryData[colname]=col[colNum]
				colNum = colNum + 1
			#print DiscoveryData[u"Identifiant PC"]+'|'+DiscoveryData[u"RAM"]+'|'+DiscoveryData[u"PROCESSOR_COUNT"]+'|'+DiscoveryData[u"Processeur"]+'|'+DiscoveryData[u"Fréquence"]
			server = tmpDiscoveryData[u"Identifiant PC"].upper()
			server = server.replace(' ','')
			server = server.replace('.SI2M.TEC','')
			DiscoveryData[server] = {u'RAM' : tmpDiscoveryData[u"RAM"], u'PROCESSOR_COUNT' : tmpDiscoveryData[ u'PROCESSOR_COUNT'], u'Processeur':  tmpDiscoveryData[u'Processeur'], u'Frequence' : tmpDiscoveryData[u'Fréquence']}
		i = i +  1
		

#
# encodeJsonNetscaler
#
def encodeJsonNetscaler():
	for name in netscalersList.keys():
		print ('\n==============')

		#print netscalersList[name]["dnsname"]
		err = netscalerGetInfo(netscalersList[name]["dnsname"])
		if err == None :
			mes =""
		else :
			mes = str(err)

		DateFile[name]= { u'file' : netscalersList[name]["dnsname"], 
						  u'date' : mes+datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 
						  u'info' : netscalersList[name]["description"] }
		
		#pprint (Netscaler)

#
# encodeJsonDbaSQL
#
def encodeJsonDbaSQL():
	"""
    mysql -u Z3BRBR -h linpatient -P 3306 -D z3br_b_gestiondba  -p

	SELECT A.CD_SERVEUR, A.LB_SERVEUR , B.TYPE_SGBD, COUNT(*) AS NB_INSTANCE
	FROM SERVEUR A, INSTANCE B                                              
	WHERE A.CD_SERVEUR=B.CD_SERVEUR AND A.CD_SERVEUR NOT LIKE 'MVS%'        
	GROUP BY A.CD_SERVEUR, A.LB_SERVEUR , B.TYPE_SGBD                       
	                                                                        
	Voici les infos de connexion à la base : 
	Serveur 
	•	LINPATIENT
	Port 
	•	3306
	Base
	•	z3br_b_gestiondba
	User
	•	Z3BRBR / Z3BRBR25
	"""
	try : 
		print "traitement des infos dba : "
		db = MySQLdb.connect(host="linpatient",    # your host, usually localhost
	                     user="Z3BRBR",         # your username
	                     passwd="Z3BRBR25",  # your password
	                     db="z3br_b_gestiondba")        # name of the data base

		# you must create a Cursor object. It will let    
		#  you execute all the queries you need
		cur = db.cursor()

		# Use all the SQL you like
		cur.execute("""SELECT A.CD_SERVEUR, A.LB_SERVEUR , B.TYPE_SGBD, COUNT(*) AS NB_INSTANCE
						FROM SERVEUR A, INSTANCE B                                              
						WHERE A.CD_SERVEUR=B.CD_SERVEUR AND A.CD_SERVEUR NOT LIKE 'MVS%'        
							GROUP BY A.CD_SERVEUR, A.LB_SERVEUR , B.TYPE_SGBD """)

		# print all 
		for row in cur.fetchall():
			
			Dba[row[0]]	= {	u'dbaInfo'		:	row[1].decode('latin-1').encode('utf-8'),
							u'typeBd'		:	row[2].decode('latin-1').encode('utf-8'),
							u'nbInstance'	:	str(row[3])
			}
			

		db.close()
		
		DateFile['DBA']= { u'file' : "mysql://Z3BRBR@linpatient/z3br_b_gestiondba",
						   u'date' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 
						   u'info' : "description de la chaine de connection au référentiel des DBA : select host_name, host_address, host_alias  from host where host_address != ''  ;" }

	# par défaut on continue le script
	except Exception as e:
		print("encodeJsonDba : Erreur")
		print("args: ", e.args)

#
# encodeJsonSupervisionSQL
#
def encodeJsonSupervisionSQL():
	"""
	  mysql -u centreonbr -h centdb.si2m.tec -P 3306 -D centreon   -p -e 'select host_name, host_address, host_alias  from host where host_address != ""'




	Voici les infos pour interroger Centreon.
•	Host : centdb.si2m.tec (port 3306 par défaut)
•	User : centreonbr
•	Pass : centreon

Les infos sont sur des bases différentes, la partie conf est dans la base « centreon », et la partie vivante est dans la base « centreon_storage ».


Pour les tables/champs pertinents voici ce que j’ai identifié.

Liste des Hosts supervisés :
•	Table : `centreon`.`host`
•	Champs :
o	host_name : Nom utilize dans Centreon
o	host_address : Adress IP si renseigné (normalement toujours renseignée pour les CI serveurs pour le check host)

Tu peux aussi passer par la table `centreon_storage`.`hosts` qui présente un peu plus d’infos (attention champs différents).
 """
	try : 
		print "traitement des infos De la Supervision : "
		db = MySQLdb.connect(host="centdb.si2m.tec",    # your host, usually localhost
	                     user="centreonbr",         # your username
	                     passwd="centreon",  # your password
	                     db="centreon")        # name of the data base

		# you must create a Cursor object. It will let    
		#  you execute all the queries you need
		cur = db.cursor()

		# Use all the SQL you like
		cur.execute('select host_name, host_address, host_alias  from host where host_address != ""')

		# print all 
		for row in cur.fetchall(): #-=- OCH 20171123
			#print 'row[2]="'+row[2]+"'"
			# Mise en conformité du nom du serveur
			serveur = row[0].decode('latin-1').encode('utf-8').upper().rstrip()

			# je ne filtre pas les équipement tel et réseau fait rien sur les switch réseau : ex A92-48-SR3-L2.

			if row[2] == "" or row[2] == "NULL"  or row[2] == None:
				Supervision[serveur] = {	u'supOK'		:	1}
			else:
				info = row[2].decode('latin-1').encode('utf-8')
				Supervision[serveur] = {	u'supOK'		:	1,
											u'supInfo'		:	info
									}
			
		db.close()
		
		DateFile['Supervision']= { u'file' : "mysql://centreonbr@centdb.si2m.tec/centreon",
						   u'date' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 
						   u'info' : "description de la chaine de connection a la base de donnée de la supervision :  select host_name, host_address, host_alias  from host where host_address != ''  ;" }

	# par défaut on continue le script
	except Exception as e:
		print("encodeJsonSupervisionSQL : Erreur")
		print("args: ", e.args)

#
# encodeJsonSupervisionService
#
def encodeJsonSupervisionService():
	try : 

		print "traitement des infos  de service de la Supervision : "
		db = MySQLdb.connect(host="centdb.si2m.tec",    # your host, usually localhost
	                     user="centreonbr",         # your username
	                     passwd="centreon",  # your password
	                     db="centreon")        # name of the data base

		# you must create a Cursor object. It will let    
		#  you execute all the queries you need
		cur = db.cursor()


		host =""
#		print "traitemnt de : "+host
		# Use all the SQL you like
		cur.execute('SELECT host.host_name, service.service_description FROM (host INNER JOIN host_service_relation '+
			'ON host.host_id = host_service_relation.host_host_id) INNER JOIN service '+
			'ON host_service_relation.service_service_id = service.service_id '+
		#	'WHERE (((host.host_name)="'+host+'"))'+
			'')

		noService = 0
		for row in cur.fetchall(): #-=- OCH 20171123
			#print row
			server = row[0].replace(".si2m.tec", "").upper().decode('latin-1').encode('utf-8')
			service = row[1].decode('latin-1').encode('utf-8')
			if DictService2No.get(service) == None :
					DictService2No[service] = noService
					DictNo2Service[noService] =  service
					noService = noService + 1 
			if GraphGroupe.get(server) != None:
				GraphGroupe[server] =  GraphGroupe[server] + ',' + service
			else :
				GraphGroupe[server] = service

		db.close()
		
		#DateFile['Supervision']= { u'file' : "mysql://centreonbr@centdb.si2m.tec/centreon",
		#				   u'date' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 
		#				   u'info' : "description de la chaine de connection a la base de donnée de la supervision :  select host_name, host_address, host_alias  from host where host_address != ''  ;" }
 
	# par défaut on continue le script
	except Exception as e:
		print("encodeJsonSupervisionService : Erreur")
		print("args: ", e.args)
		traceback.print_exc(file=sys.stdout)
		


#
# writeGraphGroupeConf
#
def writeGraphGroupeConf() :
	print "GrapheGroupe : génération des fichier :" 
	for appli in CmdbDataAppli.keys():
		filename1 = appli+"-conf.js"
		rep=dataPath("GrapheGroupe")
		filename = rep+filename1

		try :
			#print "%s," % filename1
			fd = codecs.open(filename, 'w', 'utf-8')

			done = False
			#if appli == "VMWARE_ESX_PRD":
			#	print "DEBUG ------------------------ writeGraphGroupeConf"
			#	pprint ( CmdbDataAppli[appli])

			# pour chaque serveur d'une appli boucle tant qu'on en a pas trouvé un dans la supervision
			for server1 in CmdbDataAppli[appli]["CM"].split(','):
				#server1=CmdbDataAppli[appli]["CM"].split(',')[0]
				#print "\t ref :" + server1 
				
				if GraphGroupe.get(server1) != None and done == False:
					for service in GraphGroupe[server1].split(','):
						if done == False:
							tmp = EnteteConfData.replace('"groupeTitre" 		: "Ecran initial"', '"groupeTitre" 		: "'+appli+'"')

							fd.write(tmp)
						done = True
						#print "\t\t service :"+service
						fd.write('\t\t,{"groupeNom"         	: "'+service+'",\n')     
						fd.write('\t\t"groupeTitre" 			: "'+appli+' : '+service+'",\n')
						fd.write('\t\t"groupeDescription" 	    : "'+'Application :'+appli+'<br>Service :'+service+u'<br>Groupe Généré Par CmdbVisu le '+datetime.datetime.now().strftime('%d-%m-%Y')+'",\n')
						fd.write('\t\t"groupeImageURL"          : "'+'http://supervision.si2m.tec/centreon/include/views/graphs/generateGraphs/generateImage.php?autologin=1&useralias=cmdbVisu&token=v6DjNeLAM&start=%%varDebut%%-%%echelle%%&end=%%varDebut%%&hostname=%%server%%&service='+service+'",\n')
						
						fd.write('\t\t"groupeVariable"          : {"varDebut" : "now()"},\n')					
						#gestion des echelle
						fd.write('\t\t"groupeEchelleParam"	: [ {"echelleNom" : "3 h ",      "echelle" : "10800"},\n')
						fd.write('\t\t					        {"echelleNom" : "24 h ",     "echelle" : "86400"},\n')
						fd.write('\t\t					        {"echelleNom" : "48 h ",     "echelle" : "172800"},\n')
						fd.write('\t\t					        {"echelleNom" : "1 semaine", "echelle" : "691200"},\n')
						fd.write('\t\t					        {"echelleNom" : "1 mois",    "echelle" : "2764800"},\n')
						fd.write('\t\t					        {"echelleNom" : "6 mois",    "echelle" : "16588800"},\n')
						fd.write('\t\t					        {"echelleNom" : "1 an",      "echelle" : "35942400"}\n')
						fd.write('\t\t				  ],\n')

	            		# gestion des serveur a qui ont applique ImageURL
						fd.write('\t\t"graph" : [ \n')
						virgule = ""
						for server in CmdbDataAppli[appli]["CM"].split(','):
							#print "\t\t\t: "+server
							fd.write('\t\t\t\t'+virgule+'{"nom" : "'+ server+'" , "server" : "'+server+'"')
							fd.write('\t\t\t\t, "clickURL" :"http://supervision.si2m.tec/centreon/main.php?p=204&autologin=1&useralias=cmdbVisu&token=v6DjNeLAM&mode=0&svc_id='+server+'"}\n')
							
							virgule =','
						
						fd.write('\t\t\t]\n\t\t}\n')
											
			if done == True :
				fd.write(FinConfData)
				fd.close()
			# efface le fichier
			else :
				fd.close()
				if os.path.isfile(filename):
					os.remove(filename)


		except Exception as e:
			print("writeGraphGroupeConf : Erreur")
			print("args: ", e.args)
			traceback.print_exc(file=sys.stdout)

#
# writeGraphGroupeConfSpecifique
#
def writeGraphGroupeConfSpecifique() :
	"""
	généré un graphe en fonction des cluster ESX et non pas de la CMDDB.
	"""
	print "GrapheGroupe Spécifique: génération des fichier :" 

	HTMLCodeListeGG = "<html><head></head><body><h1>ESX GrapheGroupe</h1><p>Cliquez sur le cluster VMWare que vous voulez visualiser</p><ul>"
	for cluster in EsxCluster.keys():
		filename2 = "ESX-"+cluster
		filename1 = filename2+"-conf.js"
		rep=dataPath("GrapheGroupe")
		filename = rep+filename1
		
		HTMLCodeListeGG = HTMLCodeListeGG + '<li><a href=http://vli5res01/graphes-groupes/graphes-groupes-cmdbVisu.html?conffile='+ urllib.pathname2url(filename2)+' target="'+filename2+'">'+filename2+'</a></li>'
		try :
			#print "%s," % filename1
			fd = codecs.open(filename, 'w', 'utf-8')

			done = False
			#if appli == "VMWARE_ESX_PRD":
			#	print "DEBUG ------------------------ writeGraphGroupeConf"
			#	pprint ( CmdbDataAppli[appli])

			# pour chaque serveur d'une appli boucle tant qu'on en a pas trouvé un dans la supervision
			for server1 in EsxCluster[cluster].split(','):
				#server1=CmdbDataAppli[appli]["CM"].split(',')[0]
				#print "\t ref :" + server1 
				
				if GraphGroupe.get(server1) != None and done == False:
					for service in GraphGroupe[server1].split(','):
						if done == False:
							tmp = EnteteConfData.replace('"groupeTitre" 		: "Ecran initial"', '"groupeTitre" 		: "'+cluster+'"')

							fd.write(tmp)
						done = True
						#print "\t\t service :"+service
						fd.write('\t\t,{"groupeNom"         	: "'+service+'",\n')     
						fd.write('\t\t"groupeTitre" 			: "'+cluster+' : '+service+'",\n')
						fd.write('\t\t"groupeDescription" 	    : "'+'Application : ESX-'+cluster+'<br>Service :'+service+u'<br>Groupe Généré Par CmdbVisu le '+datetime.datetime.now().strftime('%d-%m-%Y') +'",\n')
						fd.write('\t\t"groupeImageURL"          : "'+'http://supervisionxxx.domain.org/centreon/include/views/graphs/generateGraphs/generateImage.php?autologin=1&useralias=cmdbVisu&token=v6DjNeLAM&start=%%varDebut%%-%%echelle%%&end=%%varDebut%%&hostname=%%server%%&service='+service+'",\n')
						
						fd.write('\t\t"groupeVariable"          : {"varDebut" : "now()"},\n')					
						#gestion des echelle
						fd.write('\t\t"groupeEchelleParam"	: [ {"echelleNom" : "3 h ",      "echelle" : "10800"},\n')
						fd.write('\t\t					        {"echelleNom" : "24 h ",     "echelle" : "86400"},\n')
						fd.write('\t\t					        {"echelleNom" : "48 h ",     "echelle" : "172800"},\n')
						fd.write('\t\t					        {"echelleNom" : "1 semaine", "echelle" : "691200"},\n')
						fd.write('\t\t					        {"echelleNom" : "1 mois",    "echelle" : "2764800"},\n')
						fd.write('\t\t					        {"echelleNom" : "6 mois",    "echelle" : "16588800"},\n')
						fd.write('\t\t					        {"echelleNom" : "1 an",      "echelle" : "35942400"}\n')
						fd.write('\t\t				  ],\n')

	            		# gestion des serveur a qui ont applique ImageURL
						fd.write('\t\t"graph" : [ \n')
						virgule = ""
						for server in EsxCluster[cluster].split(','):
							#print "\t\t\t: "+server
							fd.write('\t\t\t\t'+virgule+'{"nom" : "'+ server+'" , "server" : "'+server+'"')
							fd.write('\t\t\t\t, "clickURL" :"http://supervisionxxx.domain.org/centreon/main.php?p=204&autologin=1&useralias=cmdbVisu&token=v6DjNeLAM&mode=0&svc_id='+server+'"}\n')
							virgule =','
						
						fd.write('\t\t\t]\n\t\t}\n')
											
			if done == True :
				fd.write(FinConfData)
				fd.close()
			# efface le fichier
			else :
				fd.close()
				if os.path.isfile(filename):
					os.remove(filename)


		except Exception as e:
			print("writeGraphGroupeConfSpecifique : Erreur")
			print("args: ", e.args)
			traceback.print_exc(file=sys.stdout)
	HTMLCodeListeGG = HTMLCodeListeGG+"</ul></body></html>"

	# ecrit le fichier HTML des serveurs ESX
	try :
		#print "%s," % filename1
		rep=dataPath("GrapheGroupe")

		filename = rep+"../GrapheGroupe-ESX.html"

		print "GrapheGroupe Spécifique: génération des fichier du fichier html : %s " % filename 
		fd = codecs.open(filename, 'w', 'utf-8')
		fd.write(HTMLCodeListeGG)
		fd.close()
	except Exception as e:
		print("writeGraphGroupeConfSpecifique HTML: Erreur")
		print("args: ", e.args)
		traceback.print_exc(file=sys.stdout)

#
# encodeJsonSupervisionSQL
#
def encodeJsonTsmRetention() :
	refFile = "TSMRetention"
	filename=dataPath(refFile)
	DateFile[refFile]= { u'file' : filename, 'date' :creationDateFile(filename), 
		u'info' : "fichier de recupération de la rétention des fichier lancer par le script : /home/j15d401/martin/scripts/RET_TSM/Ret_TSM.sh qui réalise les commandes : TSM:dsmadmc -id=J15D401 -password=XXXX -DATAONLY=YES 'TSMA:SELECT nodes.node_name, nodes.domain_name, bu_copygroups.verexists, bu_copygroups.verdeleted, bu_copygroups.retextra, bu_copygroups.retonly, bu_copygroups.destination FROM nodes, mgmtclasses mgmtclasses, bu_copygroups bu_copygroups WHERE mgmtclasses.domain_name = bu_copygroups.domain_name AND mgmtclasses.set_name = bu_copygroups.set_name AND mgmtclasses.class_name = bu_copygroups.class_name AND nodes.domain_name = bu_copygroups.domain_name AND mgmtclasses.set_name='ACTIVE' AND mgmtclasses.defaultmc='Yes' ORDER BY nodes.node_name, nodes.domain_name"  }
		
	print "traitement fichier : %s " % filename
	with open(filename, "r") as fdSrc:
		i = 0;
		for line in fdSrc.readlines():
			i += 1
			line = line.rstrip()

			# je passe le nom des colone et la ligne avec des '-------------'
			# et les lignes incompletes du a la colonne 1 sur 2 lignes 
			if i > 2 and re.search(r'\S+ +(\S+)', line) != None:
				col = line.split()
				server = col[0].rstrip().upper()
				#print "line |%s| server: %s domaine : %s " % (line, server,col[1])

				TsmRetension[server] = {'Tr' : col[2]+'-'+col[4]+'/'+col[3]+'-'+col[5]}
				#print server,TsmRetension[server]

					
	print "\n"

#
#   encodeJsonILMT
#	
def encodeJsonILMT():
	"""
		Lecture du fichier ILMT géné par Joel Gloanec
	"""
	filename = dataPath("ILMT")
	DateFile["ILMT"]= { u'file' : filename, 'date' :creationDateFile(filename), 'info' : 'Fichier généré par un script d\'export des informations ILMT de Joel Gloanec' }
	
	print "traitement fichier : %s " % filename
	# ouverture du fichier Excel 
	try: 
		wb1=xlrd.open_workbook(filename)
	except Exception  as e:
		print "\nERREUR:\n  Impossible d'ouvrir le 1er fichier : \n\t\t'%s' \n" % filename
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		sys.exit(-1)

	# feuilles dans le classeur
	shname1=wb1.sheet_names()[0]
	sh1 = wb1.sheet_by_name(shname1)

	noLigne = 0
	for rownum in range(sh1.nrows):
		
		# Positionnement des colonne 
		#-=- Crade a refaire en utilisant les noms de colonnes
		colNomServer= 1
		colOS		= 2
		colIP		= 4
		colCoeur	= 6
		colType 	= 5	
		colModele	= 14
		colPvu 		= 15
		colNoSerie  = 7
 

		noLigne = noLigne + 1
		if noLigne < 2 :
			continue
		nomServer = sh1.row_values(rownum)[colNomServer].encode('utf8').upper()
		noSerieTmp   = sh1.row_values(rownum)[colNoSerie].encode('utf8').upper()
		tmp = noSerieTmp.split(' ')
		if len(tmp) > 2 :
			noSerie = tmp[len(tmp)-1]
		else :
			noSerie = ""


		#print nomVm
		if (sh1.row_values(rownum)[colType].encode('utf8') == u"Physique" or
			 u'AIX' in sh1.row_values(rownum)[colOS].encode('utf8') ) 	:
			Ilmt[nomServer] = {
						u'Ios'		: sh1.row_values(rownum)[colOS].encode('utf8'),
						u'Iip'		: sh1.row_values(rownum)[colIP].encode('utf8'),
						u'Icoeur'	: str(float(sh1.row_values(rownum)[colCoeur])), 
						u'Itype' 	: sh1.row_values(rownum)[colType].encode('utf8'),
						u'Imodele' 	: sh1.row_values(rownum)[colModele].encode('utf8'),
						u'Ipvu'		: str(int(sh1.row_values(rownum)[colPvu])), 		
						u'In' 		: noSerie
					}
		else : 
			Ilmt[nomServer] = {
						u'Ios'		: sh1.row_values(rownum)[colOS].encode('utf8'),
						u'Iip'		: sh1.row_values(rownum)[colIP].encode('utf8'),
						u'Icoeur'	: str(float(sh1.row_values(rownum)[colCoeur])), 
						u'Itype' 	: sh1.row_values(rownum)[colType].encode('utf8'),
						u'Ipvu'		: str(int(sh1.row_values(rownum)[colPvu])), 		
						u'In' 		: noSerie
					}

	print "\n"
	wb1.release_resources()
	del wb1

#
#   encodeJsonNlyte
#	
def encodeJsonNlyte():
	"""
		Lecture du fichier Nlyte
	"""
	filename = dataPath("NLYTE")
	DateFile["NLYTE"]= { u'file' : filename, 'date' :creationDateFile(filename), 'info' : 'Fichier généré par un export Manuel de nlyte' }
	
	print "traitement fichier : %s " % filename
	# ouverture du fichier Excel 
	try: 
		wb1=xlrd.open_workbook(filename)
	except Exception  as e:
		print "\nERREUR:\n  Impossible d'ouvrir le 1er fichier : \n\t\t'%s' \n" % filename
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		sys.exit(-1)

	# feuilles dans le classeur
	shname1=wb1.sheet_names()[0]
	sh1 = wb1.sheet_by_name(shname1)

	noLigne = 0
	# Positionnement des colonne 
	#-=- Crade a refaire en utilisant les noms de colonnes
	colNomServer 		= 0
	colTypeMatos 		= 2
	colNoSerie 			= 8
	colNomSite		 	= 9
	colBaie				= 11
	colNoU 				= 12 

	for rownum in range(sh1.nrows):
		noLigne = noLigne + 1
		if noLigne < 5 :
			continue
		nomServer 	= sh1.row_values(rownum)[colNomServer].encode('utf8').upper()
		typeMatos 	= sh1.row_values(rownum)[colTypeMatos].encode('utf8').upper()
		noSerie 	= sh1.row_values(rownum)[colNoSerie].encode('utf8').upper()
		nomSite  	= sh1.row_values(rownum)[colNomSite].encode('utf8').upper()
		nomSite     = nomSite.replace('\\',"/")
		noBaie 		= sh1.row_values(rownum)[colBaie].encode('utf8').upper()
		noU 		= sh1.row_values(rownum)[colNoU].encode('utf8').upper()
	

		Nlyte[nomServer] = {
			u'Nm'		: typeMatos,
			u'Ns'		: nomSite,
			u'Nb' 		: noBaie,
			u'Nu'		: noU, 
			u'Nn'       : noSerie
		}
		NlyteS[noSerie] = {
			u'Nm'		: typeMatos,
			u'Ns'		: nomSite,
			u'Nb' 		: noBaie,
			u'Nu'		: noU, 
			u'NnomServeur'    : nomServer
		}
		
#
#   encodeIPAM
#	
def encodeIPAM():
	"""
		Lecture du fichier export de l'IPAM
	"""
	filename = dataPath("IPAM")
	DateFile["IPAM"]= { u'file' : filename, 'date' :creationDateFile(filename), 'info' : 'Fichier généré par un export Manuel de l IPAM '}
	
	print "traitement fichier : %s " % filename
	# ouverture du fichier Excel 
	try: 
		with open(filename) as csvfile:
			reader = csv.DictReader(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
	
			noLigne = 0
			
			for row in reader:
				
				noLigne = noLigne + 1
				if noLigne < 2 or row['Port name'].encode('utf8').upper() == "AGGREGATED 0/1" or row['Port name'].encode('utf8').upper() == "AGGREGATED 0/2":
					continue

				server 						= row['DNS name'].encode('utf8').upper().replace(".SI2M.TEC", "").replace(".SI2M", "")
				ip 							= row['IP Address'].encode('utf8').upper()
				mac 	 					= row['MAC Address'].encode('utf8').upper()
				switch  					= row['Network device'].encode('utf8').upper().replace(".SI2M.TEC", "")
				port 						= row['Port number'].encode('utf8').upper()
				vlan 						= row['VLAN name'].encode('utf8').upper()
				portDescription 			= row['Port description'].encode('utf8').upper()

				# existe t'il déjà ??
				if IpamMac.get(mac) == None:
					IpamMac[mac] = {
						u'Ps'		: server,
						u'Pi'		: ip,
						u'Pw' 		: switch,
						u'Pp'		: port,
						u'Pv'       : vlan
					}
				else: 
					IpamMac[mac] = {
						u'Ps'		: server,
						u'Pi'		: ip,
						u'Pw' 		: IpamMac[mac]["Pw"]+','+switch,
						u'Pp'		: IpamMac[mac]["Pp"]+','+port,
						u'Pv'       : IpamMac[mac]["Pv"]+','+vlan
					}

				if IpamServeur.get(server) == None:	
					IpamServeur[server] = {
						u'Pm'		: mac,
						u'Pi'		: ip,
						u'Pw' 		: switch,
						u'Pp'		: port,
						u'Pv'       : vlan	
					}

				else :
					IpamServeur[server] = {
						u'Pm'		: IpamServeur[server]["Pm"]+','+mac,
						u'Pi'		: ip,
						u'Pw' 		: IpamServeur[server]["Pw"]+','+switch,
						u'Pp'		: IpamServeur[server]["Pp"]+','+port,
						u'Pv'       : IpamServeur[server]["Pv"]+','+vlan	
					}

	except IOError as e:
		print "\nERREUR:\n  Impossible d'ouvrir le fichier : \n\t\t'%s' \n" % filename
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		return
	except csv.Error as e:
		sys.exit('CVS error in file %s, line %d: %s' % (filename, reader.line_num, e))
	except Exception  as e:
		sys.exit('DEFAULT  error in file %s, line %d: %s' % (filename, reader.line_num, e))

	#pprint(IpamMac)

#
#   encodeJasmin
#
def encodeJasmin():
	"""
    
	"""
	filename = dataPath("JASMIN")
	DateFile["JASMIN"]= { u'file' : filename, 'date' :creationDateFile(filename), 'info' : 'Fichier généré par un export de JASMIN fait une fois par Paul pour l instant '}
	
	print "traitement fichier : %s " % filename
	
	try:
		with open(filename) as csvfile:
			reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_ALL)

			noLigne = 0
			
			for row in reader:
				
				server 						= row['VM Name'].encode('utf8').upper().replace(".XXX.TEC", "").replace(".XXX", "")
				groupe 						= row['Groupe d\'activit?'].encode('utf8')
				proprietaire 	 			= row['Proprietaire'].encode('utf8')
				#On ne peux garder qu'un certain nombre de caractere sinon datatable bug a la lecture du fichier json
				description  				= row['Description'].encode('utf8').replace('"',"'").replace('\n',' ').replace('\r',' ')[:100]
				dns 						= row['DNS Resolution'].encode('utf8')
				os 							= row['OS'].encode('utf8')
				dateCreation  				= row['Date de creation'].encode('utf8')
				dateExpiration 				= row['Date d\'expiration'].encode('utf8')

				if JasminServeur.get(server) == None:	
					JasminServeur[server] = {
						u'Jg'		: groupe,
						u'Jp'		: proprietaire,
						u'Jd' 		: description,
						u'Jn'		: dns,
						u'Jo'       : os,
						u'Jc'       : dateCreation,
						u'Je'       : dateExpiration
					}
				else :
					print "le serveur : %s est déjà définie ligne  %s " % server, str(noLigne)

	except IOError as e:
		print "\nERREUR:\n  Impossible d'ouvrir le fichier : \n\t\t'%s' \n" % filename
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		return
	except csv.Error as e:
		sys.exit('CVS error in file %s, line %d: %s' % (filename, reader.line_num, e))
	except Exception  as e:
		sys.exit('DEFAULT  error in file %s, line %d: %s' % (filename, reader.line_num, e))

# ----------------------------------------------------------------------------
#
# M A I N 
#
# ----------------------------------------------------------------------------

reload(sys)
sys.setdefaultencoding('utf-8')


#encodeJasmin()
#pprint(JasminServeur)
#sys.exit(-1)

print "-----------------------------------------------------------------------------"
print "-- Début : "+datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

encodeJson3PAR()
encodeJsonHDS()
encodeJsonVmWare()
encodeJsonVeeam()
encodeJsonTsm()
encodeJsonTsmRetention()
encodeJsonDiscoverySoap()  
encodeJsonDbaSQL()
encodeJsonSupervisionService()
encodeJsonSupervisionSQL()
encodeJsonILMT()
encodeJsonNlyte()
encodeIPAM()
encodeJasmin()

#encodeJsonNetscaler() 

generateDataTableFile()
writeGraphGroupeConf()
writeGraphGroupeConfSpecifique()
generateExcel()

generateFileDate()
print "-- Fin : "+datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
print "-----------------------------------------------------------------------------"
print


