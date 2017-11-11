# -*- coding: utf-8 -*-
# pip install simplejson
# pip install unidecode
#
# a lire sur les HASH : http://sametmax.com/aller-plus-loin-avec-les-hash-maps-en-python/
#
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
from stat import ST_CTIME
from netscaler.netscaler import *

Vm 		 		= {}
Baie3PAR 		= {}
CmdbDataServer 	= {}
CmdbDataAppli 	= {}
BaieHDS  		= {}
DateFile        = {}
Veeam 			= {}
Tsm 			= {}
DiscoveryData	= {}

#
# si VPX1P est en A92 VPX1S est en B94 , reciproquement
#
netscalersList = {
			"vpx1p"  : { "dnsname" : "vpx1p.si2m.tec",  "description" : "Load balancer pour la prod en A92" },
			"vpx2p"  : { "dnsname" : "vpx2p.si2m.tec",  "description" : "Load balancer pour la preprod en A92" },
			"vpx3p"  : { "dnsname" : "vpx3p.si2m.tec",  "description" : "Load balancer pour la recette en A92" },
			"vpx4p"  : { "dnsname" : "vpx4p.si2m.tec",  "description" : "Load balancer de test pour le réseau en A92" },
			"vpx5p"  : { "dnsname" : "vpx5p.si2m.tec",  "description" : "Load balancer pour la perf en A92" },

		  	"vpx6p"  : { "dnsname" : "vpx6p.si2m.tec",  "description" : "Load balancer pour la prod en B94" },
		  	"vpx7p"  : { "dnsname" : "vpx7p.si2m.tec",  "description" : "Load balancer pour la preprod en B94" },
		  	"vpx8p"  : { "dnsname" : "vpx8p.si2m.tec",  "description" : "Load balancer pour la recette en B94" },
		  	"vpx9p"  : { "dnsname" : "vpx9p.si2m.tec",  "description" : "Load balancer de test pour le réseau en B94" },

		  	"zvpx1p" : { "dnsname" : "zvpx1p.si2m.tec", "description" : "Load balancer pour la prod DMZ en A92" },
		  	"zvpx2p" : { "dnsname" : "zvpx2p.si2m.tec", "description" : "Load balancer pour la preprod DMZ en A92" },
		  	"zvpx3p" : { "dnsname" : "zvpx3p.si2m.tec", "description" : "Load balancer pour la recette DMZ en A92" },
		  	"zvpx4p" : { "dnsname" : "zvpx4p.si2m.tec", "description" : "Load balancer pour le test reseau DMZ en A92" },
		  	"zvpx5p" : { "dnsname" : "zvpx5p.si2m.tec", "description" : "Load balancer pour la perf DMZ en A92" },
		  	
		  	"zvpx6p" : { "dnsname" : "zvpx6p.si2m.tec", "description" : "Load balancer pour la prod DMZ en A92" },
		  	"zvpx7p" : { "dnsname" : "zvpx7p.si2m.tec", "description" : "Load balancer pour la preprod DMZ en A92" },
		  	"zvpx8p" : { "dnsname" : "zvpx8p.si2m.tec", "description" : "Load balancer pour le recette reseau DMZ en A92" },
		  	"zvpx9p" : { "dnsname" : "zvpx9p.si2m.tec", "description" : "Load balancer pour le test DMZ en A92"}
		  }

#netscalersList = { 
#			"vpx3p"  : { "dnsname" : "vpx3p.si2m.tec",  "description" : "Load balancer pour la recette en A92" },
#			"vpx4p"  : { "dnsname" : "vpx4p.si2m.tec",  "description" : "Load balancer de test pour le réseau en A92" },
#			"vpx1p"  : { "dnsname" : "vpx1p.si2m.tec",  "description" : "Load balancer pour la prod en A92" },
#			"vpx2p"  : { "dnsname" : "vpx2p.si2m.tec",  "description" : "Load balancer pour la preprod en A92" },
#		  	"vpx6p"  : { "dnsname" : "vpx6p.si2m.tec",  "description" : "Load balancer pour la prod en B94" },
#}

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
							"Nom"			: server,
							"CINom" 		: "APPLI INCONNUE(info "+infoAppli+")",
							"CIResponsable" : "",
							"GSA"			: ""
						}

	# Ajoute info TSM
	if server in Tsm.keys() :
		for item, value  in Tsm[server].items() :
			if (item == "TSMFin" or item == "TSMDebut") and len(value)> 7:
				value = value[3]+value[4]+'/'+value[0]+value[1]+'/'+value[6:]
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

	# Ajoute info Discovery
	if server in DiscoveryData.keys() :
		for item, value  in DiscoveryData[server].items() :
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

			entete = line.split('~')
			
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
			appli  = data[0].upper().replace('"',"").rstrip()

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
			else :
				# CI : Nom
				CmdbDataServer[server]["CINom"] = CmdbDataServer[server]["CINom"] + "," + data[1].replace('"',"").rstrip()
				# CI : Responsable
				CmdbDataServer[server]["CIResponsable"] = CmdbDataServer[server]["CIResponsable"] + "," + data[6].replace('"',"").rstrip()
				# CI : GSA
				CmdbDataServer[server]["GSA"] = CmdbDataServer[server]["GSA"] + "," + data[6].replace('"',"").rstrip()

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
				CmdbDataAppli[appli]["Nom"] = CmdbDataAppli[appli]["Nom"] + "," + data[1].replace('"',"").rstrip()
				
			fd.write('\t\t{\n')  #-=- pour dataTable
			i = 0
			

			# ecrire les infos de 3PAR
			#print "|%s|" % server
			if server in Baie3PAR.keys() :
				for item, value  in Baie3PAR[server].items() :
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
	print "%-4.4d Serveur ont été ajouté par les info de Discovery  " % nb 
 	
 	# VMWare 
 	nb = 0
	for server in Vm.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"VMWARE")
			nb = nb +1
 	print "%-4.4d Serveur ont été ajouté par les info de VmWare  " % nb 

	# TSM
	nb = 0
	for server in Tsm.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"TSM")
			nb = nb +1
	print "%-4.4d Serveur ont été ajouté par les info de TSM  " % nb 

	# VEEAM
	nb = 0
	for server in Veeam.keys():
		if server not in CmdbDataServer.keys():
			insertInfoServerNotInCMDB(server,"VEEAM")
			nb = nb +1
 	print "%-4.4d Serveur ont été ajouté par les info de VEEAM  " % nb 
 	
 	# -=- On a ajouté dans la structure mais pas dans l'export 
 	# W A R N I N G
	fd.write('\t\t}\n')

	fd.write('\n\t]\n}') #   -=- pour dataTable
	#fd.write('\n\t}\n}')
	fd.close()

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
			ram = frequence = processor_count = os = modele = processeur = ""
			vip = vpx = vserveur = ""
			if CmdbDataServer[server].get("Nom") != None :
				NomServer = CmdbDataServer[server]["Nom"]

			if CmdbDataServer[server].get("CINom") != None:
				CINom = CmdbDataServer[server]["CINom"]

			if CmdbDataServer[server].get("CIResponsable") != None:
				CIResponsable = CmdbDataServer[server]["CIResponsable"]

			if CmdbDataServer[server].get("CLE_APP") != None:
				CLE_APP = CmdbDataServer[server]["CLE_APP"]

			if CmdbDataServer[server].get("CIImpactantResponsable") != None:
				CIImpactantResponsable = CmdbDataServer[server]["CIImpactantResponsable"]

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
			
			# TMS
			if CmdbDataServer[server].get("TSMDebut") != None:
				tsmDebut = CmdbDataServer[server]["TSMDebut"]

			if CmdbDataServer[server].get("TSMFin") != None:
				tsmFin = CmdbDataServer[server]["TSMFin"]

			if CmdbDataServer[server].get("TSMStatus") != None:
				tsmStatus = CmdbDataServer[server]["TSMStatus"]

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

			if CmdbDataServer[server].get("VIP") != None:
				vip 	= CmdbDataServer[server]["VIP"]

			if CmdbDataServer[server].get("Vpx") != None:
				vpx 	= CmdbDataServer[server]["Vpx"]

			if CmdbDataServer[server].get("Vserveur") != None:
				vserveur 	= CmdbDataServer[server]["Vserveur"]

			data.append([NomServer, CINom, CIResponsable,CLE_APP,CIImpactantResponsable,
						vmCpu, vmMem, vmDisk, vmBanc, vmOs, CICategorie,
						allocated,used, storage, allocated_HDS, used_HDS, storage_HDS,
						 veeamDure, veeamFin,  VeeamScheduleStatus,
						tsmDebut, tsmFin, tsmStatus,
						ram, os, processor_count, frequence, processeur, modele, 
						vip, vpx, vserveur])

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
		                        }
		                       ],
		            'data': data
		           }

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

		# Add a table to the worksheet. (ligne, colone, ligne, colonne)
		worksheetServer.add_table(2,1,len(data) + 2,1 + 16 +15, options)

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
#
# encodeJsonCmdbSoapFile
#
def encodeJsonCmdbSoapFile(filename):
	"""
	"""
	chaine = getCmdbSoap()	

	print "sauvegarde dans le fichier %s" % filename
	fd = codecs.open(filename, 'w', 'utf-8')

	#fd.write('{\n\t"data" : [\n') -=- pour dataTable
	fd.write('{\n\t"data" : {\n')

	lastLine =""
	j=0
	for line in chaine.split("\n"):

		
		if line.find("<Fieldname") == 0:
			line = line.replace("<Fieldname", "")
			line = line.replace("_0= ","")
			line = line.replace("_1= ","~")
			line = line.replace("_2= ","~")
			line = line.replace("_3= ","~")
			line = line.replace("_4= ","~")
			line = line.replace("_5= ","~")
			line = line.replace("_6= ","~")
			line = line.replace("_7= ","~")
			line = line.replace("_8= ","~")
			line = line.replace("_9= ","~")
			line = line.replace("/>", "")
			
			# pour pouvoir est traiter correctement pas dataTable, pas espace ni de : dans les nom des colonnes
			line = line.replace(" ", "");
			line = line.replace(":", "");
			line = line.replace("é", "e");
			line = line.replace("ê", "e");
			line = line.replace("à", "a");
			line = line.replace("è", "e");
			line = line.replace("ç", "c");

			entete = line.split('~')
			

		if line.find("<row") == 0  :
			# astuce pour ne pas avoir la "," a la fin du dernier element du tableau 
			fd.write(lastLine)
			lastLine =""

			line = line.replace("<row ","")
			line = line.replace("_0= ","")
			line = line.replace("_1= ","~")
			line = line.replace("_2= ","~")
			line = line.replace("_3= ","~")
			line = line.replace("_4= ","~")
			line = line.replace("_5= ","~")
			line = line.replace("_6= ","~")
			line = line.replace("_7= ","~")
			line = line.replace("_8= ","~")
			line = line.replace("_9= ","~")
			line = line.replace("/>", "")

			data = line.split('~')
			fd.write('\t\t'+data[5].upper()+':{\n')
			#fd.write('\t\t{\n')  -=- pour dataTable
			i = 0
			

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

	fd.write('\t\t}\n')

	#fd.write('\n\t]\n}')   -=- pour dataTable
	fd.write('\n\t}\n}')
	fd.close()

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
	url="https://malakoffmederic-qualif.easyvista.com:443/WebService/SmoBridge.php"
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
			server 		= data[0].upper().replace('"',"").rstrip()
			os 			= data[8].upper().replace('"',"").rstrip()
			modele 		= data[10].upper().replace('"',"").rstrip()
			nbProc 		= data[2].upper().replace('"',"").rstrip()
			ram 		= data[5].upper().replace('"',"").rstrip()
			frequence 	= data[4].upper().replace('"',"").rstrip()
			typeProc	= data[1].upper().replace('"',"").rstrip()
			if os == "" :
				os = data[9].upper().replace('"',"").rstrip()
			if os =="" :
				os = "inconnue"

			if modele == "(Unknown)":
				modele = data[11].upper().replace('"',"").rstrip()
			if modele == "":
				modele = "inconnue"

			#print "s :%s, os : %s, ram: %s, nbProc : %s" %(server, os, ram, nbProc	)
			DiscoveryData[server] = {
						u'RAM' : ram, 
						u'PROCESSOR_COUNT' : nbProc,
					 	u'Processeur':  typeProc,
					 	u'Frequence' : frequence,
					 	u'modele' : modele,
					 	u'os' : os}


				
			

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

	rootPathCtrlN1 = "/var/www/dashboardstock/capacity_TSM/check_niv1/"
	if  "cmdb-test" in os.getcwd() :
		rootPathStatBaies ="/home/i14sj00/cmdbVisu/cmdb-test/data/"
	else : 
		rootPathStatBaies ="/home/i14sj00/cmdbVisu/data/"  

	#rootPathStatBaies ="/home/i14sj00/cmdb/data/";
	if  type == "VeeamProd" :
		#return rootPathCtrlN1+"2017/septembre/Rapport Sauvegarde VEEAM/20170906-Rapport-sauvegarde-VEEAM_Production.html";
		#return rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde VEEAM/"+anneeStr+moisStr+joursStr+"-Rapport-sauvegarde-VEEAM_Production.html";
		return getLastFilesByDate(rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde VEEAM/", ".*Rapport-sauvegarde-VEEAM_Production.html")
	elif type ==  "VeeamRecette" :
		#return rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde VEEAM/"+anneeStr+moisStr+joursStr+"-Rapport-sauvegarde-VEEAM_Recette.html";
		#return rootPathCtrlN1+"2017/septembre/Rapport Sauvegarde VEEAM/20170908-Rapport-sauvegarde-VEEAM_Recette.html";
			return getLastFilesByDate(rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde VEEAM/", ".*Rapport-sauvegarde-VEEAM_Recette.html")

	elif type == "TSM" :
		#return rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde TSM/"+anneeStr+moisStr+joursStr+"-TSM_Controle_Niv1.html"
		return getLastFilesByDate(rootPathCtrlN1+anneeStr+"/"+str(mois[time.localtime()[1]-1])+"/Rapport Sauvegarde TSM/", ".*TSM_Controle_Niv1.html")
	elif type == "T400A" :
		#return rootPathStatBaies+"Volume-host T400_A92-20170908.csv"
		return getLastFilesByDate(rootPathStatBaies, "Volume-host T400_A92")
	elif type == "T400B" :
		#return rootPathStatBaies+"Volume-host T400_B94-20170908.csv"
		return getLastFilesByDate(rootPathStatBaies, "Volume-host T400_B94")
	elif type == "V400A" :
		#return rootPathStatBaies+ "Volume-host V400_A92-20170908.csv";
		return getLastFilesByDate(rootPathStatBaies, "Volume-host V400_A92")
	elif type == "V400B" :
		#return rootPathStatBaies+ "Volume-host V400_B94-20170908.csv";
		return getLastFilesByDate(rootPathStatBaies, "Volume-host V400_B94")
	elif type == "HDS-PPROD-A" :
		#return rootPathStatBaies+ "HDS_A92_PPROD-20171003.csv";
		return getLastFilesByDate(rootPathStatBaies, "HDS_A92_PPROD")
	elif type == "HDS-PPROD-B" :
		#return rootPathStatBaies+ "HDS_B94_PPROD-20171003.csv";
		return getLastFilesByDate(rootPathStatBaies, "HDS_B94_PPROD")
	elif type == "HDS-PROD-A" :
		#return rootPathStatBaies+ "HDS_A92_PROD-20171003.csv";
		return getLastFilesByDate(rootPathStatBaies, "HDS_A92_PROD")
	elif type == "HDS-PROD-B" :
		#return rootPathStatBaies+ "HDS_B94_PROD-20171003.csv";
		return getLastFilesByDate(rootPathStatBaies, "HDS_B94_PROD")
	elif type == "VmWare" :
		return getLastFilesByDate("/var/www/virtu/exportWindows/", "InfraVMware-")
		#return "/var/www/virtu/exportWindows/InfraVMware-2017-09-04.xlsx";
		#return "/var/www/virtu/exportWindows/InfraVMware-2017-09-17.xlsx";
		#return "/var/www/virtu/exportWindows/InfraVMware-2017-09-24.xlsx";
	elif type == "fileDate":
		return rootPathStatBaies+ "fileDate.json";
	elif type == "DataTableFile":
		return rootPathStatBaies+ "dataTable.json";
	elif type == "DataTableExcel":
		return rootPathStatBaies+ "cmdbVisu.xlsx";
	elif type == "Discovery":
		return rootPathStatBaies+ "discovery-easyvista-20170918.csv";

	else :
		return "le chemin pour accéder a "+type+" est inconnue";



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
					a[2] = a[2].upper()
					#print a[2]

					#Veeam[a[2]] = {"VeeamDossier" : a[0], "VeeamDure" : a[1], "VeeamDebut" : a[3], "VeeamFin" : a[4],
					#						"VeeamVolTransfert" : a[5],
					#						"VeeamScheduleType" : a[6], "VeeamBackupType" : a[7], "VeeamScheduleStatus" : a[8]}
					Veeam[a[2]] = {"VeeamDure" : a[1], "VeeamFin" : a[4], "VeeamScheduleStatus" : a[8]}
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
def  encodeJson3PAR(filenameDest):
	"""
		Lit  les 4 fichiers exportés par les baie 3PAR et les transforme en un HASH "Baie3PAR"
		dont la clef est le nom du serveur
		Attention repose sur des commentaires coté baie
		La bonne méthode sera de se baser sur le WorldWideName, mais pas dispo dans le cmddb
	"""
	print
	
	for baie in ("T400A","T400B","V400A","V400B"):
		filename = dataPath(baie)
		DateFile[baie]= { u'file' : filename, 'date' :creationDateFile(filename), u'info' : "fichier match nom serveur (champs commentaire) de "+baie+" généré par export manuel de l'interface d'admin"  }
		
		print "traitement fichier : %s " % filename
		with open(filename, "r") as fdSrc:
			i = 0;
			for line in fdSrc.readlines():
				i += 1
				line = line.rstrip()

				# saute les 3 premeire ligne
				# Provisioning : Storage Systems : B94_T400 : Virtual Volumes - Virtual Volumes
				#
				# Name,Set,State,Virtual Size (GiB),Reserved User Size (GiB),Exported To,RC Group
				#
				#V400A : Name,State,Virtual Size (GiB),Reserved User Size (GiB),Exported To,RC Group
				#T400A : Name,Set,State,Virtual Size (GiB),Reserved User Size (GiB),Exported To,RC Group
				#V400B : Name,State,Virtual Size (GiB),Reserved User Size (GiB),Exported To,RC Group
				#T400B : Name,Set,State,Virtual Size (GiB),Reserved User Size (GiB),Exported To,RC Group

				#Parse les entête pour connaitre la position des colonnes
				if line.startswith("Name,") :
					col = line.split(",")

					ColNameNum = colAllocatedNum = colUseNum =0
					for j, e in enumerate(col):
						if e == 'Name':
							ColNameNum 			= j
						elif e == 'Virtual Size (GiB)':
							colAllocatedNum 	= j
						elif e == 'Reserved User Size (GiB)' :
							colUseNum 			= j

				if i > 4 and  not(
								line.startswith(".srdata") or
								line.startswith(".admin") or
								line.startswith("admin") or
								line.startswith("-----") or
								line.startswith(",") or
								line == ""):
					col = line.split(",")
					if len(col) >= 4 :
						# ne garde que le nom du serveur (pas le  pt de montage C, D, Data, ...)
						# Mais garde l'info replication : "repli" en fin de nom
						a = col[ColNameNum].find('_')
						if a == -1 :
							a = len(col[ColNameNum])
						server = col[ColNameNum][0:a]

						# je retire  l'unité et les 3 chiffre avant
						a = col[colAllocatedNum].find(' GiB') -3
						if a == -1 :
							a = len(col[colAllocatedNum])
						allocated = col[colAllocatedNum][0:a]
						allocated = unicode(allocated, errors='ignore')
						allocatedVal = int(allocated)

						# je retire  l'unité et les 3 chiffre avant
						a = col[colUseNum].find(' GiB') - 3
						if a == -1 :
							a = len(col[colUseNum])
						used = col[colUseNum][0:a]
						used = unicode(used, errors='ignore')
						usedVal = int(used)

						if server in Baie3PAR:
							Baie3PAR[server]["storage"] 	= Baie3PAR[server]["storage"] +','+baie
							Baie3PAR[server]["allocated"] 	= Baie3PAR[server]["allocated"] + allocatedVal
							Baie3PAR[server]["used"] 		= Baie3PAR[server]["used"] + usedVal

						else :
							Baie3PAR[server] = {u"storage" : baie, u"allocated" : allocatedVal, u"used" : usedVal }

	#pprint(Baie3PAR)
	#pprint(Baie3PAR["AIXEDITP"]) 
	#print
	#pprint(Baie3PAR["AIXEDITR"]) 

	#print
	#pprint(Baie3PAR["AIXIFCP"]) 	

	#print
	#pprint(Baie3PAR["AIXDADSAR1"]) 
	#print
	#ecriture de la structure dans un fichier json
	fdDst = codecs.open(filenameDest, 'w', 'utf-8')

#
# encodeJsonHDS
#
def  encodeJsonHDS(filenameDest):
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
					#print "\n HDS : %s : %s\n" % (baie, line)

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
						server = col[ColNameNum].rstrip()
						#print "server: %s" % server

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
		Vm[nomVm]={u'vmMem':str(int(sh1.row_values(rownum)[colMEM])),u'vmCpu':str(int(sh1.row_values(rownum)[colVCPU])), u'vmDisk':str(int(sh1.row_values(rownum)[colDisk])), u'vmOs' : os.encode('utf8'), u'vmBanc' : banc.encode('utf8')}

	print "\n"

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
							'date' : mes+datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 
							u'info' : netscalersList[name]["description"] }
		
		#pprint (Netscaler)



# ----------------------------------------------------------------------------
#
# M A I N 
#
# ----------------------------------------------------------------------------

reload(sys)
sys.setdefaultencoding('utf-8')
#encodeJsonCmdbSoapFile ("resultssoap.json")

#print "|"+getLastFilesByDate("/var/www/virtu/exportWindows/", "InfraVMware-")+"|"
#sys.exit(-1)

print "-----------------------------------------------------------------------------"
print "-- Début : "+datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

encodeJson3PAR("result3PAR.json")
encodeJsonHDS("resultHDS.json")
encodeJsonVmWare()
encodeJsonVeeam()
encodeJsonTsm()
#encodeJsonDiscoveryFile()
encodeJsonDiscoverySoap()

encodeJsonNetscaler()

 
generateDataTableFile()

generateExcel()

generateFileDate()
print "-- Fin : "+datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
print "-----------------------------------------------------------------------------"
print


