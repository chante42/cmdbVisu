# -*- coding: utf-8 -*-
#
# http://vli5res01/cmdb/cmdb-test/scripts/nitro-python-1.0/doc/html/
#
# affiche la liste de  VIP d'un Loadbalancer ainsi que les serveurs qui le serve
# FCT:
import sys
from nssrc.com.citrix.netscaler.nitro.exception.nitro_exception import nitro_exception
from nssrc.com.citrix.netscaler.nitro.resource.config.lb.lbvserver import lbvserver
from nssrc.com.citrix.netscaler.nitro.resource.config.basic.service import service
from nssrc.com.citrix.netscaler.nitro.resource.config.lb.lbvserver_service_binding import lbvserver_service_binding
from nssrc.com.citrix.netscaler.nitro.resource.config.lb.lbvserver_binding import lbvserver_binding
from nssrc.com.citrix.netscaler.nitro.resource.stat.lb.lbvserver_stats import lbvserver_stats
from nssrc.com.citrix.netscaler.nitro.service.nitro_service import nitro_service
from nssrc.com.citrix.netscaler.nitro.service.options import options
from nssrc.com.citrix.netscaler.nitro.util.filtervalue import filtervalue
from nssrc.com.citrix.netscaler.nitro.resource.config.lb.lbvserver_cachepolicy_binding import lbvserver_cachepolicy_binding
from nssrc.com.citrix.netscaler.nitro.resource.config.lb.lbvserver_service_binding import lbvserver_service_binding
from nssrc.com.citrix.netscaler.nitro.resource.config.authorization.authorizationpolicylabel_binding import authorizationpolicylabel_binding
from nssrc.com.citrix.netscaler.nitro.resource.config.basic.service import service
from nssrc.com.citrix.netscaler.nitro.resource.config.basic.service_binding import service_binding
from nssrc.com.citrix.netscaler.nitro.resource.config.basic.servicegroup_servicegroupmember_binding import servicegroup_servicegroupmember_binding
from nssrc.com.citrix.netscaler.nitro.resource.config.basic.service_lbmonitor_binding import service_lbmonitor_binding

from pprint import pprint
import socket
import sys, traceback

traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n''' # Skipping the "actual line" item


username = "S0E901"
password = "3Y7P7H8B"

Netscaler 	= {}

#
# printExceptionInfo 
#
def printExceptionInfo():
	# http://docs.python.org/2/library/sys.html#sys.exc_info
    exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default

    '''
    Reason this _can_ be bad: If an (unhandled) exception happens AFTER this,
    or if we do not delete the labels on (not much) older versions of Py, the
    reference we created can linger.

    traceback.format_exc/print_exc do this very thing, BUT note this creates a
    temp scope within the function.
    '''

    traceback_details = {
                         'filename': exc_traceback.tb_frame.f_code.co_filename,
                         'lineno'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'message' : exc_value.message, # or see traceback._some_str()
                        }

    del(exc_type, exc_value, exc_traceback) # So we don't leave our local labels/objects dangling
    # This still isn't "completely safe", though!
    # "Best (recommended) practice: replace all exc_type, exc_value, exc_traceback
    # with sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

    print
    print traceback.format_exc()
    print
    print traceback_template % traceback_details
    print

#
# get_lbvserversFullinfo
# 
def get_lbvserversFullinfo(client,dnsName):
	"""
	Liste l'ensemblre des VIP de ce loadbalencer et récupère les infos lié a la méthode de loadBalencing
	et aux frontaux associés
	"""
	try:
		lbvs_count = lbvserver.count(client)
		print(dnsName + " : count_lbvserver: "+str(lbvs_count)+"\n")
	except nitro_exception as e:
		printExceptionInfo()
		return "!!!!!! Erreur d'authentification "
	except Exception as e:
		printExceptionInfo()

	try:
		result = lbvserver.get(client)
		if result :
			for i in range(len(result)) :            
				#pprint(result[i])
			#	if result[i].get_lbvserver_service_bindings() :                 
				#print("vserver : "+result[i].name +" service :"+result[i].lbmethod +" ip: "+result[i].ipv46)
				lbvserver_getInfo(client, result[i].name,dnsName)				
				#print ('\n----------------------------------------------------------------------------------')
		else :
			print("getlbvs_svc_bind_bulk - Done")    
	except nitro_exception as e:
		printExceptionInfo()
	except Exception as e:
		printExceptionInfo()

#
# lbvserver_getInfo
# 
def lbvserver_getInfo(client, vserver, dnsName):
	"""
	Récupère les infos pour une VIP passé en paramètre
	"""
	#print("information pour le vserver : "+vserver)
	proto = "undef"	
	try:
		result = lbvserver.get(client, name=vserver)
		nameVserveur = "NO DNS!!!"
		try :
			nameVserveur, alias, addresslist = socket.gethostbyaddr(result.ipv46)
		except Exception:
			pass

		#print("\tvserver\t\t\t: " 	+ result.name)
		#print(u"\tlb méthode\t\t: "	+ result.lbmethod)
		#print("\tip\t\t\t: "		+ result.ipv46 +" ("+nameVserveur+")")
		#print("\tport\t\t\t: "		+ str(result.port))
		#print("\tprotocol\t\t: "	+ result.servicetype)
		if result.servicetype == "SSL":
			proto = "https://"
		elif result.servicetype == "HTTP":
			proto = "http://"

		if nameVserveur != "NO DNS!!!" :
			url = proto + nameVserveur + ":" + str(result.port) 
		else :
			url = proto + result.ipv46 + ":" + str(result.port) 

	except nitro_exception as e:
		printExceptionInfo()
	except Exception as e:
		printExceptionInfo()


	try :
		result1 = lbvserver_binding.get(client, vserver)
		#print("\tservicegroupname\t: "+result1.lbvserver_servicegroup_bindings[0]["servicegroupname"])
		
	except nitro_exception as e:
		printExceptionInfo()
	except Exception as e:
		printExceptionInfo()


	try : 
		result2 = servicegroup_servicegroupmember_binding.get(client,result1.lbvserver_servicegroup_bindings[0]["servicegroupname"])
		
		
		#print("get_svcgrp_svr_bind name="+str(result[0]['servicegroupname']))
		if result2 :
			for i in range(len(result2)) :
				serveurName = "NO DNS!!!"
				try :
					serveurName, alias, addresslist = socket.gethostbyaddr(result2[i].ip)
				except Exception:
					pass

				serveurName = serveurName.upper()
				serveurName = serveurName.replace(".SI2M.TEC","")
				serveurName = serveurName.replace(".AD.SI2M.TEC","")
				serveurName = serveurName.replace(".MALAKOFF-MEDERIC.TEC","")
				serveurName = serveurName.replace(".MALAKOFF1.MALMED.TEC","")
				serveurName = serveurName.replace(".MEDERIC.MALMED.TEC","")
				serveurName = serveurName.replace(".MALAKOFF.FR","")
				serveurName = serveurName.replace(".AD","")
				

				if serveurName in Netscaler:
					Netscaler[serveurName]['VIP']		= Netscaler[serveurName]['VIP'] + "," + url
					Netscaler[serveurName]['Vserveur']	= Netscaler[serveurName]['Vserveur'] + "," + nameVserveur
					Netscaler[serveurName]['Vpx']		= Netscaler[serveurName]['Vpx'] + "," + dnsName
				else :
					Netscaler[serveurName] = {
								"sName" 	: serveurName,
							 	"IP" 		: result2[i].ip,
							  	"VIP" 		: url ,
							    "Vserveur" 	: nameVserveur,
							    "Vpx"		: dnsName}


		#		print("\t\tservicegroupname\t: "	+ result2[i].servername)
		#		print("\t\tport\t\t\t: "			+ str(result2[i].port))
		#		print("\t\tip\t\t\t: "				+ result2[i].ip+" ("+name+")")
		else :
			print("get_svcgrp_svr_bind - Done")

	except nitro_exception as e:
		printExceptionInfo()

	except Exception as e:
		printExceptionInfo()

#
# netscalerGetInfo
#
def netscalerGetInfo(dnsName):
	client = nitro_service(dnsName,"http")
	client.set_credential(username,password)
	client.timeout = 500

	return(get_lbvserversFullinfo(client, dnsName))

# -------------------------------------------------------------
#
#                          M A I N
# 
# -------------------------------------------------------------
def main():
	username = "chanteloup"
	password = "chanteloup"
	#username = "si2madm"
	#password = ""
	#username = "i14sj00"
	#password = ""

	 
	netscalersListe = {
			"vpx1p"  : { "dnsname" : "vpx1p.si2m.tec",  "description" : "Load balancer pour la prod en A92" },
			"vpx2p"  : { "dnsname" : "vpx2p.si2m.tec",  "description" : "" },
			"vpx3p"  : { "dnsname" : "vpx3p.si2m.tec",  "description" : "" },
			"vpx4p"  : { "dnsname" : "vpx4p.si2m.tec",  "description" : "Load balancer de test pour le réseau" },
			"vpx5p"  : { "dnsname" : "vpx5p.si2m.tec",  "description" : "" },
		  	"vpx6p"  : { "dnsname" : "vpx6p.si2m.tec",  "description" : "" },
		  	"vpx7p"  : { "dnsname" : "vpx7p.si2m.tec",  "description" : "" },
		  	"vpx8p"  : { "dnsname" : "vpx8p.si2m.tec",  "description" : "" },
		  	"vpx9p"  : { "dnsname" : "vpx9p.si2m.tec",  "description" : "" },
		  	"vpx10p" : { "dnsname" : "vpx10p.si2m.tec", "description" : "" },
		  	"zvpx1p" : { "dnsname" : "zvpx1p.si2m.tec", "description" : "" },
		  	"zvpx2p" : { "dnsname" : "zvpx2p.si2m.tec", "description" : "" },
		  	"zvpx3p" : { "dnsname" : "zvpx3p.si2m.tec", "description" : "" },
		  	"zvpx4p" : { "dnsname" : "zvpx4p.si2m.tec", "description" : "" },
		  	"zvpx5p" : { "dnsname" : "zvpx5p.si2m.tec", "description" : "" },
		  	"zvpx6p" : { "dnsname" : "zvpx6p.si2m.tec", "description" : "" },
		  	"zvpx7p" : { "dnsname" : "zvpx7p.si2m.tec", "description" : "" },
		  	"zvpx8p" : { "dnsname" : "zvpx8p.si2m.tec", "description" : "" },
		  	"zvpx9p" : { "dnsname" : "zvpx9p.si2m.tec", "description" : "" }
		  }

	netscalers = { "vpx4p"  : { "dnsname": "vpx4p.si2m.tec",  "description": ""},
				  "vpx3p"  : { "dnsname" : "vpx3p.si2m.tec",  "description" : "" }
	}

	for name in netscalersListe.keys():
		print ('\n==============================================================================\n')

		print netscalers[name]["dnsname"]
		client = nitro_service(netscalers[name]["dnsname"],"http")
		client.set_credential(username,password)
		client.timeout = 500

		get_lbvserversFullinfo(client)

	for serveur in Netscaler :
		pprint(Netscaler[serveur])

	#lbvserver_getInfo(client, "lb_server_vip-adm-ipam")
	#lbvserver_getInfo(client, "lb_vserver_mysql")
	sys.exit(1)



if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
