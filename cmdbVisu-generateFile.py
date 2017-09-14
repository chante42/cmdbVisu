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

Vm 		 		= {}
Baie3PAR 		= {}
CmdbDataServer 	= {}
CmdbDataAppli 	= {}
BaieHDS  		= {}
DateFile        = {}


def creationDateFile(path_to_file):
	"""
	Try to get the date that a file was created, falling back to when it was
	last modified if that isn't possible.
	See http://stackoverflow.com/a/39501288/1709587 for explanation.
	"""
	resultStr = ""

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
# generateDateTableFile
#
def generateDateTableFile(filename):
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
				
			#fd.write('\t\t'+data[5].upper()+':{\n')
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

			# ecrire les infos de VMWare 
			if server in Vm.keys() :
				if server == "VWI0CTD001":
					print "KEY FOUND : %s " %server
				for item, value  in Vm[server].items() :
					fd.write('\t\t\t"'+item+'" : "'+str(value)+'",\n')
					CmdbDataServer[server][item]=str(value)


			# ecrire les info CMDB
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

	for file in  DateFile.keys():
		fd.write("<div>"+file+" : "+DateFile[file]+"</div>\n")

	fd.close()

#
# générateExcell
#
def generateExcel(file):
	"""
	Export les données en excel bien formaté avec 2 Onglets 
	 -  1) Une ligne par serveur
	 -  2) Une ligne par applicatif
	 -  3) Aide : Principe de fonctionnement du ficher
	 -  4) Liste des fichier avec date de génération qui ont servi a construire
	"""
	# verification sur file a faire (.xlsx, ....)
	workbook = xlsxwriter.Workbook(file)

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
	worksheet.write_rich_string('A1', dateTable_format, "Export des information issue de la CMDB et des fichier techniques")

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

			if CmdbDataServer[server].get("allocated") != None:
				allocated = CmdbDataServer[server]["allocated"]

			if CmdbDataServer[server].get("used") != None:
				used = CmdbDataServer[server]["used"]

			if CmdbDataServer[server].get("storage") != None:
				storage = CmdbDataServer[server]["storage"]

			if CmdbDataServer[server].get("allocated_HDS") != None:
				allocated_HDS = CmdbDataServer[server]["allocated_HDS"]

			if CmdbDataServer[server].get("used_HDS") != None:
				used_HDS = CmdbDataServer[server]["used_HDS"]

			if CmdbDataServer[server].get("storage_HDS") != None:
				storage_HDS = CmdbDataServer[server]["storage_HDS"]

			data.append([NomServer, CINom, CIResponsable,CLE_APP,CIImpactantResponsable,
						vmCpu, vmMem, vmDisk, vmBanc, vmOs, CICategorie,
						allocated,used, storage, allocated_HDS, used_HDS, storage_HDS ])

		options = {
		           'columns': [{'header': 'Nom serveur',
		           				'header_format' :  column_format,
		           				'format' : firstColumn_format
		           				},
		                       {'header': 'Nom Appli',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                       {'header': 'Resp Appli',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                       {'header': 'CLE APP',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                       {'header': 'Resp server',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'Vm CPU',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'Vm Mémoire (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'Vm Disque (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'Vm Banc',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'Vm OS',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'CICategorie',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': '3PAR alloué (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': '3PAR utilisé (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': '3PAR Nom Baie',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'HDS alloué (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'HDS utilisé (Go)',
		                        'header_format' :  column_format,
		                        'format' : column_format
		                        },
		                        {'header': 'HDS Baie',
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

		# Add a table to the worksheet. (ligne, colone, ligne, colonne)
		worksheetServer.add_table(2,1,len(data) + 2,1 + 16, options)

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
	worksheetFichier.set_column('B:B', 60)
	worksheetFichier.set_column('C:C', 38)

	
	options = {
	           'columns': [{'header': "chemin d'accès à la ressource",
	           				'header_format' :  column_format,
	           				'format' : firstColumn_format
	           				},
	                       {'header': "date de dernière modification de la resssource",
	                        'header_format' :  column_format,
	                        'format' : column_format
	                        }
	                       ],
	            'data': data
	           }

	print "Liste des fichiers et leur date de modification"
	data = []

	for file in  DateFile.keys():
		data.append([str(file), str(DateFile[file])])

		#worksheetFichier.write_rich_string('B'+str(i), fileinfo_format, str(file))
		#worksheetFichier.write_rich_string('C'+str(i), fileinfo_format, str(DateFile[file]))
		#i = i+ 1
		#print "\t %s : %s\n" % (file, DateFile[file])
	# Add a table to the worksheet. (ligne, colone, ligne, colonne)
	worksheetFichier.add_table(2,1,len(data) + 2,1 +2, options)
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
	         <Account xsi:type="xsd:string">50005</Account>
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


	print "get %s \n" % url
	response = requests.post(url,data=body,headers=headers)
	chaine1 = html_decode(response.text)
	chaine= chaine1.decode('utf-8')

	DateFile[url]= datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')

	return chaine;

#
# dataPAth
#

def dataPath(type):
	"""
		renvoie le chemin d'accès au fichiers de donnée brute  en fonction du type
	"""
	rootPathCtrlN1 = "/var/www/dashboardstock/capacity_TSM/check_niv1/";
	rootPathStatBaies ="/home/i14sj00/cmdb/data/";
	if  type == "VeeamProd" :
		return rootPathCtrlN1+"2017/septembre/Rapport Sauvegarde VEEAM/20170906-Rapport-sauvegarde-VEEAM_Production.html";
	elif type ==  "VeeamRecette" :
		return rootPathCtrlN1+"2017/septembre/Rapport%20Sauvegarde%20VEEAM/20170908-Rapport-sauvegarde-VEEAM_Recette.html";
	elif type == "TSM" :
		return rootPathCtrlN1+"http://vli5res01.si2m.tec/dashboardstock/capacity_TSM/check_niv1/2017/septembre/Rapport%20Sauvegarde%20TSM/20170908-TSM_Controle_Niv1.html";
	elif type == "T400A" :
		return rootPathStatBaies+"Volume-host T400_A92-20170908.csv";
	elif type == "T400B" :
		return rootPathStatBaies+"Volume-host T400_B94-20170908.csv";
	elif type == "V400A" :
		return rootPathStatBaies+ "Volume-host V400_A92-20170908.csv";
	elif type == "V400B" :
		return rootPathStatBaies+ "Volume-host V400_B94-20170908.csv";
	elif type == "HDS-PPROD-A" :
		return rootPathStatBaies+ "HDS_A92_PPROD-20170911.csv";
	elif type == "HDS-PPROD-B" :
		return rootPathStatBaies+ "HDS_B94_PPROD-20170911.csv";
	elif type == "HDS-PROD-A" :
		return rootPathStatBaies+ "HDS_A92_PROD-20170911.csv";
	elif type == "HDS-PROD-B" :
		return rootPathStatBaies+ "HDS_B94_PROD-20170911.csv";
	elif type == "VmWare" :
		return "/var/www/virtu/exportWindows/InfraVMware-2017-09-04.xlsx";
	elif type == "fileDate":
		return rootPathStatBaies+ "fileDate.html";
	else :
		return "le chemin pour accéder a "+type+" est inconnue";

#
# dataPAth
#
# 	renvoie le chemin d'accès au fichier en fonction du type
def dataPathTmp(type):
	"""
	"""
	rootPathCtrlN1 = "../data/";
	rootPathStatBaies ="../data/";
	if  type == "VeeamProd" :
		return rootPathCtrlN1+"2017/septembre/Rapport Sauvegarde VEEAM/20170906-Rapport-sauvegarde-VEEAM_Production.html";
	elif type ==  "VeeamRecette" :
		return rootPathCtrlN1+"2017/septembre/Rapport%20Sauvegarde%20VEEAM/20170908-Rapport-sauvegarde-VEEAM_Recette.html";
	elif type == "TSM" :
		return rootPathCtrlN1+"http://vli5res01.si2m.tec/dashboardstock/capacity_TSM/check_niv1/2017/septembre/Rapport%20Sauvegarde%20TSM/20170908-TSM_Controle_Niv1.html";
	elif type == "T400A" :
		return rootPathStatBaies+"Volume-host T400_A92.csv";
	elif type == "T400B" :
		return rootPathStatBaies+"Volume-host T400_B94.csv";
	elif type == "V400A" :
		return rootPathStatBaies+ "Volume-host V400_A92.csv";
	elif type == "V400B" :
		return rootPathStatBaies+ "Volume-host V400_B94.csv";
	elif type == "VmWare" :
		return "/var/www/virtu/exportWindows/InfraVMware-2017-09-04.xlsx";
	else :
		return "le chemin pour accéder a "+type+" est inconnue";

#
# encodeJsonVeeam
#
def  encodeJsonVeeam(filenameDest):
	"""
		Lit les 2 fichier de controle de niveau 1 de Veeam et les transforme en un HASH "VeeamData"
	"""
	fdDst = codecs.open(filenameDest, 'w', 'utf-8')
	for filename in (dataPath("VeeamProd"), dataPath("VeeamRecette")):
		DateFile[filename] = creationDateFile(filename)
		with open(filename) as fdSrc:
			for line in fdSrc.readlines():
		    	# Traiter la ligne et ainsi de suite ...
				print(line.strip())

#
# encodeJsonTSM
#
def  encodeJsonTSM(filenameDest):
	"""
		Lit les 2 fichier de controle de niveau 1 de TSM et les transforme en un HASH "TsmData"
	"""
	DateFile[filenameDest] = creationDateFile(filenameDest)

	fdDst = codecs.open(filenameDest, 'w', 'utf-8')
	for filename in (dataPath("TSMProd"), dataPath("TSMRecette")):
		DateFile[filename] = creationDateFile(filename)
		with open(filename) as fdSrc:
			for line in fdSrc.readlines():
		    	# Traiter la ligne et ainsi de suite ...
				print(line.strip())

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
		DateFile[filename] = creationDateFile(filename)
		print "traitement fichier : %s " % filename
		with open(filename) as fdSrc:
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
	for baie in ("HDS-PPROD-A","HDS-PPROD-B","HDS-PROD-A","HDS-PPROD-B"):

		filename = dataPath(baie)
		DateFile[filename] = creationDateFile(filename)
		print "traitement fichier : %s " % filename
		with open(filename) as fdSrc:
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
						e = e .replace(" GB", "").replace(" GO", "")
						e = e .replace(" Mb", "").replace(" Mo", "")
						e = e .replace(" MB", "").replace(" MO", "")
						e = e .replace(" Tb", "").replace(" To", "")
						e = e .replace(" TB", "").replace(" TO", "")
						if e == 'Host Group':
							ColNameNum 			= j
						elif e == 'Total':
							colAllocatedNum 	= j
						elif e == 'Used' :
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



	#pprint(Baie3PAR)
	pprint(BaieHDS["LINDBCLUSTA11"]) 
	print "LIN1BDD002"
	pprint(BaieHDS["LIN1BDD001"]) 

	print "LIN1BDD002"
	pprint(BaieHDS["LIN1BDD002"]) 	

	print
	pprint(BaieHDS["AIXURWTA"]) 
	print
	#ecriture de la structure dans un fichier json
	fdDst = codecs.open(filenameDest, 'w', 'utf-8')

#
#   ReadVmInfo()
#	
def encodeJsonVmWare():
	"""
		Lecture du fichier inventaire complet généré par Paul
	"""
	filename = dataPath("VmWare")
	DateFile[filename] = creationDateFile(filename)
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
		colMEM		= 6
		colVCPU		= 5
		colDisk		= 7
		colOS 		= 15
		colCluster	= 2
		colNomVM	= 0


		noLigne = noLigne + 1
		if noLigne < 2 :
			continue
		# valeur par defaut
		os = u"Linux"
		banc = u"non Prod"

		if sh1.row_values(rownum)[colOS].find(u'Windows') != -1  :
			os = u"Windows"

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
		Vm[nomVm]={u'vmMem':sh1.row_values(rownum)[colMEM],u'vmCpu':sh1.row_values(rownum)[colVCPU], u'vmDisk':sh1.row_values(rownum)[colDisk], u'vmOs' : os.encode('utf8'), u'vmBanc' : banc.encode('utf8')}

#
# M A I N 
#
reload(sys)
sys.setdefaultencoding('utf-8')
#encodeJsonCmdbSoapFile ("resultssoap.json")


encodeJson3PAR("result3PAR.json")
encodeJsonHDS("resultHDS.json")
encodeJsonVmWare()
#encodeJsonVeeam("resultVeeam.json")



generateDateTableFile("dataTable.json")

generateExcel("cmdbVisu.xlsx")

generateFileDate();

#pprint(data['data'][1]['CINom']) -=- pour DataTable
#data['data'][1]['CINom']="toto" -=- pour DataTable
#pprint(data['data'][1]['CINom']) -=- pour DataTable
#data['data'][1]['veeam']="full" -=- pour DataTable
#pprint(data['data'][1]) -=- pour DataTable

#pprint(CmdbDataServer['data']['WINBLH14']) 
#pprint(CmdbDataServer['WINBLH14'])  

#print "\n"
#pprint(CmdbDataServer['data']['WINBLH14']) 
#pprint(CmdbDataServer['VWI0CTD001']) 
#print "\n"
#pprint(CmdbDataServer['data']['LIN2BDD001']) 
#pprint(CmdbDataServer['LIN2BDD001']) 
#print "\n"
#pprint(CmdbDataServer['LIN2BDD002']) 
#print "\n"
#pprint(CmdbDataServer['AIXURWTA']) 
#print "\n"

#pprint(CmdbDataServer)
#print (entete)

