//
// Regourpe les function de cmdbVisu
//
//

// Variable Globale 
var TypeColonneNo       = 0;
var BddNo               = 0;
var TypeColonneDataJS   = [];
var TypeColonneDataHead = [];

 
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
    for (item in DateFile['data']) {
        //console.log(DateFile['data'][item]['type']);
        if (DateFile['data'][item]['type'].search(type) != -1) {
            var tmp = DateFile['data'][item][field];
            tmp = tmp.substr(0,10);
            d = new Date(tmp);
            rep = rep + "<p>"+tab_jour[d.getDay()] +" "+tmp[8]+tmp[9]+"/"+tmp[5]+tmp[6]+"/"+tmp.substr(0,4)+"</p>";
            match ++;
        }
    }
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
/* Formatting function for row details - modify as you need */
//
function format ( d ) {
    var count = {};
    var storageCount = storageHDSCount = "N/A";
    class3PAR = classHDS = classVirtu = classVeeam = classTSM = classDiscovery = classNetscaler = "normal";
    classDBA = "normal";
    classSupervision   = "pas-d-info";
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

    if  (d.RAM == undefined) {
        classDiscovery ="pas-d-info";
    }

    if  (d.VIP == undefined) {
        classNetscaler ="pas-d-info";
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
    TSMDebut            = d.TSMDebut;
    TSMStatus           = d.TSMStatus;
    TSMFin              = d.TSMFin; 
    discoveryRAM        = d.RAM; 
    dicoveryNbProc      = d.PROCESSOR_COUNT;
    discoveryProcessor  = d.Processeur;
    discoveryFrequence  = d.Frequence;
    hostname            = d.Nom;
    vserveur            = d.Vserveur;
    dbaInfo             = d.dbaInfo;
    nbInstance          = d.nbInstance;
    typeBd              = d.typeBd;
    
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
                '</table>'+ 
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#"> SAN HDS<span>'+
                            '<p>Date de génération des données :</p> '+getDataFileDisplay('HDS', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classHDS+'">'+storageHDSCount+'</td></tr>'+
                    '<tr><td class="'+classHDS+'"><span class="titreLigne">Alloué</span> :'+allocated_HDS+' Go</td></tr>'+
                    '<tr><td class="'+classHDS+'"><span class="titreLigne">Utilisé</span> : '+used_HDS+' Go</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#">Sauvegarde VEEAM<span>'+
                        'Date de génération des données  : '+getDataFileDisplay('Veeam', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classVeeam+'"><div class="titreLigne bulleLigne"><a>Status'+codeAffichageAjout+'</a></div> : '+VeeamScheduleStatus+'</td></tr>'+
                    '<tr><td class="'+classVeeam+'"><span class="titreLigne">Fin</span> : '+VeeamFin+'</td></tr>'+
                    '<tr><td class="'+classVeeam+'"><span class="titreLigne">Durée</span> : '+VeeamDure+'</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+ 
                '<table cellspacing="0" border="1" >'+
                    '<tr><th>'+
                        '<div  class ="bulle"><a href="#"> Sauvegarde TSM<span>'+
                        'Date de génération des données : '+getDataFileDisplay('TSM', 'date')+
                        '</span></a></div>'+
                    '</th></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Status</span> : '+TSMStatus+'</td></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Début</span> : '+TSMDebut+'</td></tr>'+
                    '<tr><td class="'+classTSM+'"><span class="titreLigne">Fin</span> : '+TSMFin+'</td></tr>'+
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
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
                '<table cellspacing="0" border="1" >'+
                    '<tr><th><div  class ="bulle"><a href="#">Netscaler<span>Date de génération des données : '+getDataFileDisplay('vpx3p', 'date')+'</span></div></th></tr>'+
                    '<tr><td class="'+classNetscaler+'"><span class="titreLigne">VIP</span> : '+vip+'</td></tr>'+
                    '<tr><td class="'+classNetscaler+'"><span class="titreLigne">Vserveur</span> : '+vserveur+'</td></tr>'+
                    '<tr><td class="'+classNetscaler+'"><span class="titreLigne">Vpx</span> : '+vpx+'</td></tr>'+
                '</table>'+
            '</div></td>'+
            '<td width="10%"><div class="infoPlus">'+
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
                    { "data"                : "Nom", "width" : "17%"},
                    { "data"                : "CINom", "width" : "40%"},
                    { "data"                : "CIResponsable", "width" : "20%"},
                    { "data"                : "CIImpactantResponsable", "width" : "20%"}
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
                    { "data"                : "Nom", "width" : "17%" },
                    { "data"                : "CINom", "width" : "40%" },
                    { "data"                : "VeeamScheduleStatus",
                        "className"           : "dt-center"
                    },
                    { "data"                : "VeeamFin",
                        "className"           : "dt-center"
                    },
                    { "data"                : "TSMStatus",
                        "className"           : "dt-center"
                    },
                    { "data"                : "TSMDebut",
                        "className"           : "dt-center"
                    }
                ];
    
    TypeColonneDataHead[1] = `
                    <th></th>
                    <th>Serveur (Nom) </th>
                    <th>Application(CINom)</th>
                    <th>Sauvegarde VEEAM</th>
                    <th>VEEAM Fin</th>
                    <th>Sauvegarde TSM</th>
                    <th>TSM Début</th>
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
                    { "data"                : "Nom" , "width" : "17%"},
                    { "data"                : "CINom", "width" : "40%" },
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
                    {   "data"                : "Nom" , "width" : "17%"},
                    {   "data"                : "CINom", "width" : "40%" },
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
}
