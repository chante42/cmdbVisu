//
// Regourpe les function de cmdbVisu
//
//

// Variable Globale 
var TypeColonneNo       = 0;  
var BddNo               = 0;
var Search              = "";
var MapOption           = 0;
var TypeColonneDataJS   = []; 
var TypeColonneDataHead = [];
var Table               = null;

// constance de lien vers des appli externe
var LienCentreon 
LienCentreonPPD="http://vli1sup011/centreon/main.php?p=204&autologin=1&useralias=cmdbVisu&token=v6DjNeLAM&mode=0&svc_id="; 
LienCentreon="http://supervision.si2m.tec/centreon/main.php?p=204&autologin=1&useralias=cmdbVisu&token=v6DjNeLAM&mode=0&svc_id="; 

lienGrapheGroupeBase="http://vli5res01/graphes-groupes/graphes-groupes-cmdbVisu.html?conffile=";
//
// dateDiff
//
function dateDiff(date1, date2){
    var diff = {}                           // Initialisation du retour
    var tmp = date2 - date1;
 
    tmp = Math.floor(tmp/1000);             // Nombre de secondes entre les 2 dates
    diff.sec = tmp % 60;                    // Extraction du nombre de secondes
 
    tmp = Math.floor((tmp-diff.sec)/60);    // Nombre de minutes (partie entière)
    diff.min = tmp % 60;                    // Extraction du nombre de minutes
 
    tmp = Math.floor((tmp-diff.min)/60);    // Nombre d'heures (entières)
    diff.hour = tmp % 24;                   // Extraction du nombre d'heures
     
    tmp = Math.floor((tmp-diff.hour)/24);   // Nombre de jours restants
    diff.day = tmp;
     
    return diff;
}

//
// getObjects
//
//return an array of objects according to key, value, or key and value matching
function getObjects(obj, key, val) {
    var objects = [];
    for (var i in obj) {
    	console.log(" getObjects : "+i +" val : "+obj[i]);
        if (!obj.hasOwnProperty(i)) continue;
        if (typeof obj[i] == 'object') {
            objects = objects.concat(getObjects(obj[i], key, val));    
        } 
        //if key matches and value matches or if key matches and value is not passed (eliminating the case where key matches but passed value does not)
        if (i == key && obj[i] == val || i == key && val == '') { //
            objects.push(obj);
        } else if (obj[i] == val && key == ''){
            //only add if the object is not already in the array
            if (objects.lastIndexOf(obj) == -1){
                objects.push(obj);
            }
        }
    }
    return objects;
}

//
// getValues
//    
//return an array of values that match on a certain value of hash
// https://gist.github.com/iwek/3924925		
// getvalues(DataJson.data[1],'a)'
function getValues(obj, val) {
    var objects = [];
    var re = new RegExp(val);

    for (var i in obj) {
        if (!obj.hasOwnProperty(i)) continue;
        if (typeof obj[i] == 'object') {
            objects = objects.concat(getKeys(obj[i], val));
        } else if (re.test(obj[i])) {
            objects.push(obj[i]);
        }
    }
    return objects;
}


//
// getDataFileDisplay
//
// recupère la bonne string dans le tabelau de hash DateFile en fct des paramètre passé
function getDataFileDisplay(type, field) {

    var tab_jour=new Array("Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam");
    rep = ""
    match = 0
    if (DateFile != null ) {
        for (item in DateFile['data']) {
            
            if (DateFile['data'][item]['type'].search(type) != -1) {
                //console.log("getDataFileDisplay - type : " + type);            
                //console.log("getDataFileDisplay - " + DateFile['data'][item]['type'] + " : " + DateFile['data'][item]['date']);

                var tmp = DateFile['data'][item][field];
                tmp = tmp.substr(0,10);
                d = new Date(tmp);
                rep = rep + "<p>"+tab_jour[d.getDay()] +" "+tmp[8]+tmp[9]+"/"+tmp[5]+tmp[6]+"/"+tmp.substr(0,4)+"</p>";
                match ++;
            }
        } //fin FOR
    } // fin IF
    if (rep == "") {
        rep = "N/A";
    }
    return rep;
}

//
// formatBaie
//
function formatBaie(inputWords) {        
    str = inputWords;
    a = inputWords.split(',');
    result = { };
    
    for (var i=0;  i <a.length; i++ ){
        //console.log("Boucle=|"+i+"|"+a[i]);
        if (result[a[i]] == undefined ) {
            result[a[i]] = 1;
        }else {
            result[a[i]] =result[a[i]] +1;
        }
    }

    var resultStr ="";
    for (var baie in result) {
       // console.log(baie);
       resultStr= resultStr + baie +":"+result[baie]+", ";
    }
    return(resultStr);
}

//
// colorSauvegardeDate
//
function colorSauvegardeDate(dateStr) {
    // test pour savoir depuis quand la sauvegarde a eu lieu
    dateStr = dateStr.replace('/', '-')
    dateStr = dateStr.substring(6,10) + "-" + dateStr.substring(3,5)+ "-" +dateStr.substring(0,2)+ " " + dateStr.substring(11);
    dateCur = new Date()
    dateFin = new Date(dateStr)

    diff = dateDiff(dateFin, dateCur);
    if (diff.day == 0) {
        result = "sauvegarde-OK";
    } else if (diff.day == 1) {
        result = "sauvegarde-Warning";
    } else {
        result = "sauvegarde-Alert";
    }
    return result
}

//
// formatNetscalerVip
// 
function formatNetscalerVip(vip) {
    res ="";
    tmp = vip.split(',');
    for (var i = 0; i < tmp.length; i++) {
        res += '<a href="'+tmp[i]+'" target="_blank">'+tmp[i]+'</a><br>';
    }
    return res;
}

//
// formatNetscalerVpx
// 
function formatNetscalerVpx(vpx) {
    res ="";
    tmp = vpx.split(',');
    var tmpHash = {};
    for (var i = 0; i < tmp.length; i++) {
        if (!(tmp in tmpHash)) {
            res += '<a href="https://'+tmp[i]+'" target="_blank">'+tmp[i]+'</a>,';
            tmpHash[tmp] = tmp;
        }
    }
    return res;
}
//
// datatableAddColumn
//
function datatableAddColumn() {
    console.log("DataTable ADD Colonne");
}
//
//   datatableDelColumn
//
function datatableDelColumn() {
    console.log("DataTable DEL  Colonne");
}

//
// openUrlMetrologie
//
function openUrlMetrologie(obj) {
    console.log("openUrlMetrologie : "+LienCentreon);
    window.open(LienCentreon,"metro"); //ouvrir un target
    window.open(lienGrapheGroupeBase+obj); //ouvrir un target _blank
    
}

//  
/* Formatting function for row details - modify as you need */
//
function format ( d ) {
    var count = {};
    var storageCount = storageHDSCount = "N/A";
    class3PAR = classHDS = classVirtu = classVeeam = classTSM = classDiscovery = classNetscaler = "normal";
    classDBA = classSupervision =classIlmt = classIPAM = "normal";
    classNlyte = "normal";
     
    if  (d.storage != undefined) {
        //var tmp = d.storage.split(',').forEach(function(i) { count[i] = (count[i]||0)+1;  });
        storageCount = formatBaie(d.storage);
    }else {
        class3PAR = "pas-d-info";
    }
    
    if  (d.storage_HDS != undefined) {
        //var tmp = d.storage_HDS.split(',').forEach(function(i) { count[i] = (count[i]||0)+1;  });
        storageHDSCount = formatBaie(d.storage_HDS);
    }
    else {
        classHDS = "pas-d-info";
    }
    
    if  (d.vmCpu == undefined) {
        classVirtu ="pas-d-info";
    }

    if  (d.VeeamScheduleStatus == undefined) {
        classVeeam = "pas-d-info";
    }else {
        classVeeam = colorSauvegardeDate(d.VeeamFin);
    }

    if  (d.TSMStatus == undefined) {
        classTSM = "pas-d-info";
    }else {
        // test pour savoir depuis quand la sauvegarde a eu lieu
        classTSM = colorSauvegardeDate(d.TSMFin);
    }

    console.log(d);
    if  (d.VIP == undefined) {
        classNetscaler = "pas-d-info";
    }

    if (d.Ios == undefined) {
    	classIlmt = "pas-d-info";
    }
 
    if (d.RAM == undefined) {
        classDiscovery ="pas-d-info";
    }
    
    if ( d.Ns == undefined){
        classNlyte = "pas-d-info";
    }
    vmCpu               = d.vmCpu;
    vmMem               = d.vmMem;
    vmDisk              = d.vmDisk;
    vmOs                = d.vmOs;
    allocated           = d.allocated;
    used                = d.used;
    allocated_HDS       = d.allocated_HDS;
    used_HDS            = d.used_HDS;
    VeeamScheduleStatus = d.VeeamScheduleStatus;
    VeeamFin            = d.VeeamFin;
    VeeamDure           = d.VeeamDure;
    VeeamRetention      = d.Vr;
    TSMDebut            = d.TSMDebut;
    TSMStatus           = d.TSMStatus;
    TSMFin              = d.TSMFin; 
    TSMRetention        = d.Tr;
    discoveryRAM        = d.RAM; 
    dicoveryNbProc      = d.PROCESSOR_COUNT;
    discoveryProcessor  = d.Processeur;
    discoveryFrequence  = d.Frequence;
    discoveryDate       = d.date;
    discoveryNoSerie    = d.nS;
    hostname            = d.CM;
    vserveur            = d.Vserveur;
    dbaInfo             = d.dbaInfo;
    nbInstance          = d.nbInstance;
    typeBd              = d.typeBd;
    supInfo             = d.supInfo;
    esxvCenter          = d.ESXvCenter;
    esxCluster          = d.ESXCluster;
    esxModele           = d.ESXModele;
    ilmtOs				= d.Ios;
    ilmtIp				= d.Iip;
    ilmtCoeur			= d.Icoeur;
    ilmtType			= d.Itype;
    ilmtModele			= d.Imodele;
    ilmtPvu				= d.Ipvu;
    ipamMac             = d.Pm;
    ipamIp              = d.Pi;
    ipamSwitch          = d.Pw;
    ipamPort            = d.Pp;
    ipamVlan            = d.Pv;  
    //console.log(d);   
    //console.log(d.Nom);
    //console.log(hostname);
    //console.log(d.Ram);
    if (d.vmCpu                         == undefined) { vmCpu                   = "N/A"} 
    if (d.vmMem                         == undefined) { vmMem                   = "N/A"}
    if (d.vmDisk                        == undefined) { vmDisk                  = "N/A"}
    if (d.vmOs                          == undefined) { vmOs                    = "N/A"}
    if (d.allocated                     == undefined) { allocated               = "N/A"}
    if (d.used                          == undefined) { used                    = "N/A"}
    if (d.allocated_HDS                 == undefined) { allocated_HDS           = "N/A"}
    if (d.used_HDS                      == undefined) { used_HDS                = "N/A"}
    if (d.VeeamScheduleStatus           == undefined) { VeeamScheduleStatus     = "N/A"}
    if (d.VeeamFin                      == undefined) { VeeamFin                = "N/A"}
    if (d.Vr                            == undefined) { VeeamRetention          = "N/A"}
    if (d.VeeamDure                     == undefined) { 
        VeeamDure           = "N/A"
    } else {
        VeeamDure           = VeeamDure.replace(':', 'h',1);
        VeeamDure           = VeeamDure.replace(':', 'm',1);
        VeeamDure           = VeeamDure + 's';
    }
    if (d.TSMDebut                      == undefined) { TSMDebut                = "N/A"}
    if (d.TSMFin                        == undefined) { TSMFin                  = "N/A"}
    if (d.TSMStatus                     == undefined) { TSMStatus               = "N/A"}
    if (d.Tr                            == undefined) { TSMRetention            = "N/A"}
    if (d.RAM                           == undefined) { discoveryRAM            = "N/A"}
    if (d.PROCESSOR_COUNT               == undefined) { dicoveryNbProc          = "N/A"}
    if (d.Processeur                    == undefined) { discoveryProcessor      = "N/A"}
    if (d.Frequence                     == undefined) { discoveryFrequence      = "N/A"}
    if (d.VIP                           == undefined) {
         vip                = "N/A"}
    else {
        vip            = formatNetscalerVip(d.VIP);
        } 
    if (d.Vserveur                      == undefined) { vserveur                = "N/A"}
    if (d.Vpx                           == undefined) { 
        vpx                 = "N/A"}
    else {
         vpx           = formatNetscalerVpx(d.Vpx);     
    }
    if (d.typeBd                        == undefined) {
        nbInstance          = "N/A";
        typeBd              = "N/A";
        dbaInfo             = "N/A";
        classDBA            = "pas-d-info";
    }
    if  (d.supOK                        == undefined) {
        classSupervision    = "pas-d-info";
        supInfo             = "N/A";
        lienCentreon        = "NON";
    }
    else {
        lienCentreon='<a target="_blank" href="'+LienCentreon+d.CM+'" >OUI</a>';
        if (d.supInfo                  == undefined){
            supInfo             = "N/A";
        }
    }

    if ( TSMRetention != 'N/A') {
        TSMRetention = '<div class ="bulleHelp bulleHelpAuDessus"><a>'+TSMRetention[0]+
        ' versions sur '+TSMRetention[2]+TSMRetention[3]+' jours'+
        '<span>La sauvegarde TSM a une rétention de '+TSMRetention[2]+TSMRetention[3]+' Jours, '+
        'sauf si les fichiers sont modifiés souvent, dans ce cas la rétension sera donc de '+TSMRetention[0]+' version<br>'+
        'Si le fichier a été effacé, alors la rétention est de '+TSMRetention[7]+TSMRetention[8]+
        'jours, avec un maximum de '+TSMRetention[5]+' versions du fichiers</span></a></div>';

    }
    
    if (ipamMac 		== undefined) {ipamMac 			= "N/A"; classIPAM = "pas-d-info"}
   	if (ipamVlan 		== undefined) {ipamVlan			= "N/A"}
	if (ipamIp 			== undefined) {ipamIp 			= "N/A"}
	if (ipamPort 		== undefined) {ipamPort 		= "N/A"}
	if (ipamSwitch 		== undefined) {ipamSwitch		= "N/A"}
    if (d.Imodele       == undefined) { ilmtModele      = "N/A";}
    if (ilmtOs          == undefined) { ilmtOs          = "N/A";}
    if (ilmtIp          == undefined) { ilmtIp          = "N/A";}
    if (ilmtCoeur       == undefined) { ilmtCoeur       = "N/A";}
    if (ilmtType        == undefined) { ilmtType        = "N/A";}
    if (ilmtPvu         == undefined) { ilmtPvu         = "N/A";}
    if (d.In            == undefined) { ilmtNoSerie     = "N/A";} else {ilmtNoSerie     = d.In}
    if (d.Nm            == undefined) { NlyteMatos      = "N/A";} else {NlyteMatos      = d.Nm;}
    if (d.Ns            == undefined) { NlyteNomSite    = "N/A";} else {NlyteNomSite    = d.Ns;}
    if (d.Nb            == undefined) { NlyteBaie       = "N/A";} else {NlyteBaie       = d.Nb;}
    if (d.Nu            == undefined) { NlyteNoU        = "N/A";} else {NlyteNoU        = d.Nu;}
    if (d.Nn            == undefined) { NlyteNoSerie    = "N/A";} else {NlyteNoSerie    = d.Nn;}
      
    if (d.CN.indexOf("APPLI INCO") == 0 || d.CN.indexOf("_PRD") == -1 ) {
        lienGrapheGroupe ="N/A";
    }   
    else {
        lienGrapheGroupe    = '<a href="#" onclick="openUrlMetrologie(\''+d.CN.toUpperCase()+'\');return false;">OUI</a>';
        classSupervision    = "normal";
    }   
    //
    // Cas particulier ou je remplace discovery par des infos VMWare Host pour les serveur qui heberges les hyperviseurs
    //
    discoveryTable =  '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#">DISCOVERY<span>'+
                        'Date de génération des données : '+getDataFileDisplay('Discovery', 'date')+
                        '<span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classDiscovery+'"><span class="titreLigne">RAM</span> : '+discoveryRAM+' Mo</td></tr>'+
                    '<tr><td class="'+classDiscovery+'"><span class="titreLigne">NbProc</span> :'+dicoveryNbProc+' </td></tr>'+
                    '<tr><td class="'+classDiscovery+'"><span class="titreLigne">Proc Type</span> :'+discoveryProcessor+' </td></tr>'+
                    '<tr><td class="'+classDiscovery+'"><span class="titreLigne">Proc Freq</span> :'+discoveryFrequence+' Mhz </td></tr>'+
                    '<tr><td class="'+classDiscovery+'"><span class="titreLigne">Date de collecte</span> : '+discoveryDate+'  </td></tr>'+
                    '<tr><td class="'+classDiscovery+'"><span class="titreLigne">No Série</span> : '+discoveryNoSerie+'  </td></tr>'+
                '</table>'+
            '</div></td>';
    
    
    if (d.ESXCluster != undefined) {
        classDiscovery ="normal";
        discoveryTable =  '<td width="10%"><div class="infoPlus">'+
            '<table cellspacing="0" border="1" >'+
                '<tr><th>'+
                    '<div  class ="bulle"><a href="#">ESX HOST<span>'+
                    'Date de génération des données : '+getDataFileDisplay('VmWare', 'date')+
                    '<span></a></div>'+
                '</th></tr>'+
                '<tr><td class="'+classDiscovery+'"><span class="titreLigne">Cluster</span> : '+esxCluster+' </td></tr>'+
                '<tr><td class="'+classDiscovery+'"><span class="titreLigne">Vcenter</span> : '+esxvCenter+' </td></tr>'+
                '<tr><td class="'+classDiscovery+'"><span class="titreLigne">Modèle</span> :' + esxModele+' </td></tr>'+
            '</table>'+
        '</div></td>';
    }
    
    
    codeAffichageAjout = '<span><img src="images/details_open.png" onclick="datatableAddColumn()" ><img src="images/details_close.png" onclick="datatableDelColumn()"></span>'
    // `d` is the original data object for the row
    return '<table class="detail-info" cellspacing="0" border="0" >'+
        '<tr style="background-color: #adc9f7">'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#"> Virtualisation<span>'+
                            '<p>Date de génération des données :</p> '+getDataFileDisplay('VmWare', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classVirtu+'"><span class="titreLigne"> VCPU</span> : '+Math.floor(vmCpu)+'</td></tr>'+
                    '<tr><td class="'+classVirtu+'"><span class="titreLigne">  MEM</span> : '+Math.floor(vmMem)+'<span class="infoPlusUnite"> Go</span> </td></tr>'+
                    '<tr><td class="'+classVirtu+'"><span class="titreLigne">  Disk</span> : '+vmDisk+'<span class="infoPlusUnite"> Go</span></td></tr>'+
                    '<tr><td class="'+classVirtu+'"><span class="titreLigne">  OS</span> :'+vmOs+'</td></tr>'+
                '</table>'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#">Backup VEEAM<span>'+
                        'Date de génération des données  : '+getDataFileDisplay('Veeam', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classVeeam+'"><div class="titreLigne bulleLigne"><a>Status'+codeAffichageAjout+'</a></div> : '+VeeamScheduleStatus+'</td></tr>'+
                    '<tr><td class="'+classVeeam+'"><span class="titreLigne">Fin</span> : '+VeeamFin+'</td></tr>'+
                    '<tr><td class="'+classVeeam+'"><span class="titreLigne">Durée</span> : '+VeeamDure+'</td></tr>'+
                    '<tr><td class="'+classVeeam+'"><span class="titreLigne">Rétention</span> : '+VeeamRetention+' J</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#"> SAN 3PAR<span>'+
                            '<p>Date de génération des données :</p> '+getDataFileDisplay('400', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+class3PAR+'">'+storageCount+'</td></tr>'+
                    '<tr><td class="'+class3PAR+'"><span class="titreLigne">Alloué</span> :'+allocated+' Go</td></tr>'+
                    '<tr><td class="'+class3PAR+'"><span class="titreLigne">Utilisé</span> :'+used+' Go</td></tr>'+

                    '<tr><th><div  class ="bulle"><a href="#"> SAN HDS<span>'+
                            '<p>Date de génération des données :</p> '+getDataFileDisplay('HDS', 'date')+
                     '</span></a></div></th></tr>'+
                    '<tr><td class="'+classHDS+'">'+storageHDSCount+'</td></tr>'+
                    '<tr><td class="'+classHDS+'"><span class="titreLigne">Alloué</span> :'+allocated_HDS+' Go</td></tr>'+
                    '<tr><td class="'+classHDS+'"><span class="titreLigne">Utilisé</span> : '+used_HDS+' Go</td></tr>'+
                '</table>'+ 
            '</div></td>'+
            
            '<td width="10%"><div class="infoPlus">'+
                
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                    '<div  class ="bulle"><a href="#"> Backup TSM<span>'+
                        'Date de génération des données : '+getDataFileDisplay('TSM', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Status</span> : '+TSMStatus+'</td></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Début</span> : '+TSMDebut+'</td></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Fin</span> : '+TSMFin+'</td></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Rétention</span> : '+TSMRetention+'</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+ 
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#">IPAM<span>'+
                        'Date de génération des données a changer : '+getDataFileDisplay('IPAM', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classIPAM+'"><span class="titreLigne">IP</span> : '+ipamIp+'</td></tr>'+
                    '<tr><td class="'+classIPAM+'"><span class="titreLigne">MAC</span> : '+ipamMac+'</td></tr>'+
                    '<tr><td class="'+classIPAM+'"><span class="titreLigne">switch</span> : '+ipamSwitch+'</td></tr>'+
                    '<tr><td class="'+classIPAM+'"><span class="titreLigne">port</span> : '+ipamPort+'</td></tr>'+
                    '<tr><td class="'+classIPAM+'"><span class="titreLigne">VLAN</span> : '+ipamVlan+'</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th><div  class ="bulle"><a href="#">DBA<span>'+
                    'Date de génération des données : '+getDataFileDisplay('DBA', 'date')+
                    '</span></a></div></th></tr>'+
                    '<tr><td class="'+classDBA+'">'+ 
                    '<a href="http://vwi0bdd003/dbainfo/listeDatabases.php?SELECT=Actualiser&CD_SERVEUR='+hostname+'" target="_blank">'+
                    'outil dba</a></td></tr>'+
                    '<tr><td class="'+classDBA+'">'+ 
                    '<span class="titreLigne">infoDba :</span> '+dbaInfo+'</td></tr>'+
                    '<tr><td class="'+classDBA+'">'+ 
                    '<span class="titreLigne">type DB :</span> '+typeBd+'</td></tr>'+
                    '<tr><td class="'+classDBA+'">'+ 
                    '<span class="titreLigne">nb Instance :</span> '+nbInstance+'</td></tr>'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#">SUPERVISION<span>'+
                        'Date de génération des données : '+getDataFileDisplay('Supervision', 'date')+
                        '<span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classSupervision+'">'+
                        '<span class="titreLigne">Supervisé : </span>'+
                        lienCentreon+
                    '</td></tr>'+
                    '<tr><td class="'+classSupervision+'"><span class="titreLigne">Info</span> : '+supInfo+' </td></tr>'+
                    '<tr><td class="'+classSupervision+'">'+
                        '<span class="titreLigne">Graphe : </span>'+
                        lienGrapheGroupe+
                    '</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th><div  class ="bulle"><a href="#">Netscaler<span>Date de génération des données : '+getDataFileDisplay('vpx3p', 'date')+'</span></div></th></tr>'+
                    '<tr><td class="'+classNetscaler+'"><span class="titreLigne">VIP</span> : '     +vip+'</td></tr>'+
                    '<tr><td class="'+classNetscaler+'"><span class="titreLigne">Vserveur</span> : '+vserveur+'</td></tr>'+
                    '<tr><td class="'+classNetscaler+'"><span class="titreLigne">Vpx</span> : '     +vpx+'</td></tr>'+
                '</table>'+
            '</div></td>'+
            discoveryTable+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th><div  class ="bulle"><a href="#">Nlyte<span>Date de génération des données : '+getDataFileDisplay('NLYTE', 'date')+'</span></div></th></tr>'+    
                      '<tr><td class="'+classNlyte+'"><span class="titreLigne">Matériel</span> : '  +NlyteMatos+'</td></tr>'+
                      '<tr><td class="'+classNlyte+'"><span class="titreLigne">Site</span> : '      +NlyteNomSite+'</td></tr>'+
                      '<tr><td class="'+classNlyte+'"><span class="titreLigne">Baie</span> : '      +NlyteBaie+'</td></tr>'+
                      '<tr><td class="'+classNlyte+'"><span class="titreLigne">No U</span> : '      +NlyteNoU+'</td></tr>'+
                      '<tr><td class="'+classNlyte+'"><span class="titreLigne">No série</span> : '  +NlyteNoSerie+'</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#">ILMT<span>'+
                        'Date de génération des données : '+getDataFileDisplay('ILMT', 'date')+
                        '<span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                    	'<span class="titreLigne">Os :</span> '+ilmtOs+'</td></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                    	'<span class="titreLigne">IP :</span> '+ilmtIp+'</td></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                    	'<span class="titreLigne">Coeur :</span> '+ilmtCoeur+'</td></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                    	'<span class="titreLigne">Type :</span> '+ilmtType+'</td></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                    	'<span class="titreLigne">Modèle :</span> '+ilmtModele+'</td></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                    	'<span class="titreLigne">PVU par coeur:</span> '+ilmtPvu+'</td></tr>'+
                    '<tr><td class="'+classIlmt+'">'+ 
                        '<span class="titreLigne">No Série:</span> '+ilmtNoSerie+'</td></tr>'+
                '</table>'+
            '</div></td>'+
        '</tr>'+
    '</table>';
}


//
// getDataTableFileData
//
function getDataTableFileData(bddNo) {
    if (bddNo == 1) {
        return("data/dataTableServer.json");
    }
    else {
        return("data/dataTable.json"); 
    }
    
}
//
// getDataTableColonneData
//
// type == javascript
// type == tableHead
function getDataTableColonneData(type, typeColonneNo) {
   //   *********************** 1 eme TYPE RESPONSABLE **********************
    console.log("getDataTableColonneData : "+type);
    TypeColonneDataJS [0] = [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                        
                    },
                    { "data"                : "CM", "width" : "17%"},
                    { "data"                : "CN", "width" : "40%"},
                    { "data"                : "CR", "width" : "20%"},
                    { "data"                : "CI", "width" : "20%"}
                    //,{ "data"                : "vmCpu"}
                ];
    
    TypeColonneDataHead[0] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>Responsable Appli (CIResponsable)</th>
                    <th>Responsable serveur (CIImpactantResponsable)</th>
                    `;

    //   *********************** 2 eme TYPE SAUVEGARDE **********************
    TypeColonneDataJS [1]= [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                    },
                    { "data"                : "CM", "width" : "17%" },
                    { "data"                : "CN", "width" : "40%" },
                    { "data"                : "VeeamScheduleStatus",
                        "className"           : "dt-center"
                    },
                    { "data"                : "VeeamFin",
                        "className"           : "dt-center"
                    },
                    { "data"                : "Vr",
                        "className"           : "dt-center"
                    },
 
                    { "data"                : "TSMStatus",
                        "className"           : "dt-center"
                    },
                    { "data"                : "TSMDebut",
                        "className"           : "dt-center"
                    },
                    { "data"                : "Tr",
                        "className"           : "dt-center",
                        render                : function( data, type, row){
                            if (data != undefined) {
                                return('<div class ="bulleHelp bulleHelpAuDessus"><a>'+data[0]+
                                ' versions sur '+data[2]+data[3]+' jours'+
                                '<span>La sauvegarde TSM a une rétention de '+data[2]+data[3]+' Jours, '+
                                'sauf si les fichiers sont modifiés souvent, dans ce cas la rétension sera donc de '+data[0]+' version<br>'+
                                'Si le fichier a été effacé, alors la rétention est de '+data[7]+data[8]+
                                'jours, avec un maximum de '+data[5]+' versions du fichiers</span></a></div>');
                            }
                    },
                    }
                ];
    
    TypeColonneDataHead[1] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>Sauvegarde VEEAM</th>
                    <th>VEEAM Fin</th>
                    <th>VEEAM rétention</th>
                    <th>Sauvegarde TSM</th>
                    <th>TSM Début</th>
                    <th>TSM rétention</th>
                    `;

    //   *********************** 2 eme TYPE TAILLE VM **********************
    TypeColonneDataJS [2]= [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                    },
                    { "data"                : "CM" , "width" : "17%"},
                    { "data"                : "CN", "width" : "40%" },
                    { "data"                : "vmCpu",
                        "className"           : "dt-center"
                    },
                    { "data"                : "vmMem",
                        "className"           : "dt-center"
                    },
                    { "data"                : "PROCESSOR_COUNT",
                        "className"           : "dt-center"
                    },
                    { "data"                : "RAM",
                        "className"           : "dt-center"
                    }
                ];
    
    TypeColonneDataHead[2] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>VM Proc</th>
                    <th>VM RAM (Go)</th>
                    <th>Discovery Proc</th>
                    <th>Discovery RAM(Mo)</th>
                    `;

    //   *********************** 3 eme TYPE Stockage **********************
    TypeColonneDataJS [3]= [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                    },
                    {   "data"                : "CM" , "width" : "17%"},
                    {   "data"                : "CN", "width" : "40%" },
                    {   "data"                : "allocated",
                        "className"           : "dt-center"
                    },
                    {   "data"                : "vmDisk",
                        "className"           : "dt-center"
                    },
                    {   "data"                : "allocated_HDS",
                        "className"           : "dt-center"
                    }
                ];
    
    TypeColonneDataHead[3] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>3PAR Alloué (Go)</th>
                    <th>Virtu Alloué (Go)</th>
                    <th>HDS Alloué (Go)</th>
                    `;

    //   *********************** 4 eme TYPE Supervision **********************
    TypeColonneDataJS [4]= [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                    },
                    {   "data"                : "CM" , "width" : "17%"},
                    {   "data"                : "CN", "width" : "40%" },
                    {   "data"                : "supOK",
                        "className"           : "dt-center",
                        render                : function( data, type, row){
                            if (data == "1") {
                                return('<a target="_blanc" href ='+LienCentreon+row.CM+'>OUI</a>');
                            }
                            else {
                                return("NON");
                            }
                        }
                    },
					
                    {   "data"                : "supInfo",
                        "className"           : "dt-center"
                    }
                ];
    
    TypeColonneDataHead[4] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>Supervisé ?</th>
                    <th>SupervisionInfo</th>
                    `;

       //   *********************** 5 eme TYPE Supervision **********************
    TypeColonneDataJS [5]= [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                    },
                    {   "data"                : "CM" 		, "width" 		: "17%"},
                    {   "data"                : "CN"		, "width" 		: "30%" },
                    {   "data"                : "Ios"		, "className" 	: "dt-center"},
                    {   "data"                : "Iip"		, "className" 	: "dt-center"},
                    {   "data"                : "Icoeur"	, "className" 	: "dt-center"},
                    {   "data"                : "Imodele"	, "className" 	: "dt-center"},
                    {   "data"                : "Ipvu"		, "className" 	: "dt-center"},
                ];
    
    TypeColonneDataHead[5] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>OS</th>
                    <th>Ip</th>
                    <th>Coeur</th>
                    <th>Modèle</th>
                    <th>PVU</th>
                    `;

     //   *********************** 6 eme TYPE Full **********************
    TypeColonneDataJS [6]= [
                    {
                        "className"         : 'details-control',
                        "orderable"         : false,
                        "data"              : null,
                        "width"             : "2%",
                        "defaultContent"    : '<div class ="bulleHelp"><a href="#">_<span> Cliquer sur le \'+\' pour afficher plus d\'infos</span></a></div>'
                    },
                    {   "data"                : "CM"        , "width"       : "17%"},
                    {   "data"                : "CN"        , "width"       : "30%" },
                    {   "data"                : "Nm"       , "className"   : "dt-center"},
                    {   "data"                : "Ns"       , "className"   : "dt-center"},
                    {   "data"                : "Nb"       , "width"       : "5%", "className"   : "dt-center"},
                    {   "data"                : "Nu"       , "width"       : "5%", "className"   : "dt-center"},
                    {   "data"                : "Nn"       , "className"   : "dt-center"},               
                ];
    
    TypeColonneDataHead[6] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>Matériel</th>
                    <th>Nom Site</th>
                    <th>Baie</th>
                    <th>No U</th>
                    <th>No Serie</th>
                    `;
    
    console.log("TypeColonneNo = "+typeColonneNo);
    if (type == "javascript")
        return(TypeColonneDataJS[typeColonneNo]);
    else if ( type == "tableHead")
        return(TypeColonneDataHead[typeColonneNo]);
}
//
// Gestion de history pour bookmarker une URL
//
(function(window,undefined){

    // Prepare
    var History = window.History; // Note: We are using a capital H instead of a lower h
    if ( !History.enabled ) {
         // History.js is disabled for this browser.
         // This is because we can optionally choose to support HTML4 browsers or not.
         console.log("history dont WORK OCH");
        return false;
    }

    // Bind to StateChange Event
    History.Adapter.bind(window,'statechange',function(){ // Note: We are using statechange instead of popstate
        var State = History.getState(); // Note: We are using History.getState() instead of event.state
        History.log(State.data, State.title, State.url);
    });

    History.getState() ;

})(window);

//
//  getRequest()
//
//http://stackoverflow.com/questions/831030/how-to-get-get-request-parameters-in-javascript
//
function getRequests() {
    var s1 = location.search.substring(1, location.search.length).split('&'),
        r = {}, s2, i;
    for (i = 0; i < s1.length; i += 1) {
        s2 = s1[i].split('=');
        r[decodeURIComponent(s2[0]).toLowerCase()] = decodeURIComponent(s2[1]);
    }
    return r;
};

//
// initaliseDataTableColonne
//
// Parse l'URL pour connaitre les colonnes a afficher
function initialiseDataTableColonne() {
    
    var QueryString = getRequests();
    

    if (typeof(QueryString["type"]) != "undefined") {
        TypeColonneNo = Number(QueryString["type"]);      
        console.log("******** initialiseDataTableColonne : "+TypeColonneNo); //logs t1                
    }  

    if (typeof(QueryString["bdd"]) != "undefined") {
        BddNo = Number(QueryString["bdd"]);      
        console.log("******** initialise BDD : "+BddNo); //logs t1                
    }
    if (typeof(QueryString["search"]) != "undefined") {
        Search = QueryString["search"];      
        console.log("******** initialise search : "+Search); //logs t1                
    }
    if (typeof(QueryString["map"]) != "undefined") {
        MapOption = QueryString["map"];      
        console.log("******** initialise MAP : "+MapOption); //logs t1                
    }
}

//
//    readyCreateDataTable
//
function readyCreateDataTable() {
    var printCounter = 0; 


   // Append a caption to the table before the DataTables initialisation
   //$('#example').append('<caption style="caption-side: bottom">DSI/DPI/CSI/ Socle Infra : O chanteloup 11/09/2017.</caption>');

    Table = $('#dataTable').DataTable( {
        "ajax" : {
                    "type"  : "POST",
                    "url"   : getDataTableFileData(BddNo)
                },
        "columns": getDataTableColonneData("javascript", TypeColonneNo),
        //AutoWidth: false, 
        "order": [[1, 'asc']],
        lengthMenu: [[7,8,10,13,15,16,17,18,19, 25, 50, -1], [7,8,10,13,15,16,17,18,19, 25, 50, "All"]],
        "iDisplayLength" : 19,
        keys : true,
        colReorder: true,
        processing: true,
        'language':{ 
            "emptyTable": "Loading...",
            "processing" :""
        },
        dom: 'Blfrtip',

        "oSearch": {
            "sSearch": Search
            },
    
        "search": {
             "regex"        : true,
             "smart"        : false
        },
        buttons: [
            {
                extend: 'copy',
                text: '<u>C</u>opy',
                key: {
                    key: 'c',
                    altKey: true
                }
            },              
            {
                extend: 'excel',
                messageTop: 'information extraite de http://vli5res01.si2m.tec/cmdbVisu'
            },
            {
                extend: 'pdf',
                messageBottom: null
            },
            {
                extend: 'print',
                messageTop: function () {
                    printCounter++;
 
                    if ( printCounter === 1 ) {
                        return 'This is the first time you have printed this document.';
                    }
                    else {
                        return 'You have printed this document '+printCounter+' times';
                    }
                },
                messageBottom: null
            }  // fin PRINT
        ], // fin BUTTON
        initComplete: function () {  
            this.api().columns().every( function () {  
                var column = this;  
                var select = $('<select><option value=""></option></select>')  
                    .appendTo( $(column.footer()).empty() )  
                    .on( 'change', function () {  
                        var val = $.fn.dataTable.util.escapeRegex(  
                            $(this).val()  
                        );  
                //to select and search from grid  
                        column  
                            .search( val ? '^'+val+'$' : '', true, false )  
                            .draw();  
                    } );  
   
                column.data().unique().sort().each( function ( d, j ) {  
                    select.append( '<option value="'+d+'">'+d+'</option>' )  
                } );  
            } );

        } // fin de initcomplete 

        

    } ); // fin table variable 

    Table.buttons().container()
        .appendTo( $('.col-sm-6:eq(0)', Table.table().container() ) );
     
    // Add event listener for opening and closing details
    $('#dataTable tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = Table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } ); // FIN Add event listener for opening and closing details

    // fin de lecture du json
    Table.on( 'xhr', function (e, settings, json) {
        DataJson = Table.ajax.json();
        console.log("fin lecture json ");  
        
    } );

    
    // supression des warning quand une colonne afficher n'est pas définie dans la bdd
    $.fn.dataTable.ext.errMode = 'none'

    // récupère les date de fichier pour les info Bulle
    $.getJSON("data/fileDate.json", function(data) {
        DateFile = data;
        //console.log(data);

        // affiche la date du fichier Datatable
        $('#dateFileDataTable').html("Le batch de récupération des infos a été lancé le :"+getDataFileDisplay('CMDB', 'date'));
    });

    
    //
    // mARCHE VOIR PAGE / https://datatables.net/forums/discussion/1393/pagination-paging-through-results-with-page-down-page-up-keys-and-mousewheel-scrolling
    //
    $('#dataTable tbody')
        .bind('mousewheel', function(event, delta) {
            var dir = delta > 0 ? 'previous' : 'next';
            Table.fnPageChange(dir);
            return false;
    });
} // FIN de readyCreateDataTable

//
//    changeBdd
//
function changeBdd(noBdd) {
    BddNo = noBdd;
    window.history.pushState({state:1}, "State 1", "?type="+TypeColonneNo+"&bdd="+BddNo); // logs {state:1}, "State 1", "?state=1"
    console.log('changeBdd bdd :'+BddNo+ "vue :" +  TypeColonneNo);
    Table.clear();
    Table.draw();
    Table.ajax.url(getDataTableFileData(BddNo)).load();

}

//
//    changeBdd
//
function changeVue(noVue) {
    TypeColonneNo = noVue;
    window.location = "?type="+TypeColonneNo+"&bdd="+BddNo;

    // je n'arrive pas a changer les colonne afficher en repassant par la structure
    // la technique est peut etre de jiurer les colonne visible
    //
    //window.history.pushState({state:1}, "State 1", "?type="+TypeColonneNo+"&bdd="+BddNo); // logs {state:1}, "State 1", "?state=1"

    //Table.fnFilter( 1, Table.oApi._fnVisibleToColumnIndex( 
    //                    Table.fnSettings(), 1 ) );
    //changeBdd(BddNo);

}   