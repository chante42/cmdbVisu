

 
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
                    if (match > 0) {rep += ', ';}
                    var tmp = DateFile['data'][item][field];
                    tmp = tmp.substr(0,10);
                    d = new Date(tmp);
                    rep = rep + tab_jour[d.getDay()] +" "+tmp[8]+tmp[9]+"/"+tmp[5]+tmp[6]+"/"+tmp.substr(0,4);
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
        //
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
        /* Formatting function for row details - modify as you need */
        //
        function format ( d ) {
            var count = {};
            var storageCount = storageHDSCount = "N/A";
            class3PAR = classHDS = classVirtu = classVeeam = classTSM = classDiscovery = "normal";
            classSupervision   = classNetscaler  ="pas-d-info";
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
            VeeamDure           = d.VeeamDure
            TSMDebut            = d.TSMDebut
            TSMStatus           = d.TSMStatus
            TSMFin              = d.TSMFin 
            discoveryRAM        = d.RAM 
            dicoveryNbProc      = d.PROCESSOR_COUNT
            discoveryProcessor  = d.Processeur
            discoveryFrequence  = d.Frequence

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
            if (d.VeeamDure                     == undefined) { VeeamDure               = "N/A"}
            if (d.TSMDebut                      == undefined) { TSMDebut                = "N/A"}
            if (d.TSMFin                        == undefined) { TSMFin                  = "N/A"}
            if (d.TSMStatus                     == undefined) { TSMStatus               = "N/A"}
            if (d.RAM                           == undefined) { discoveryRAM            = "N/A"}
            if (d.PROCESSOR_COUNT               == undefined) { dicoveryNbProc          = "N/A"}
            if (d.Processeur                    == undefined) { discoveryProcessor      = "N/A"}
            if (d.Frequence                     == undefined) { discoveryFrequence      = "N/A"}

            VeeamDure           = VeeamDure.replace(':', 'h',1);
            VeeamDure           = VeeamDure.replace(':', 'm',1);
            VeeamDure           = VeeamDure + 's';
 
            // `d` is the original data object for the row
            return '<table class="detail-info" cellspacing="0" border="0" >'+
                '<tr style="background-color: #adc9f7">'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th>'+
                                '<div  class ="bulle"><a href="#"> Virtualisation<span>'+
                                    'la date de génération des données est le '+getDataFileDisplay('VmWare', 'date')+
                                '</span></a></div>'+
                            '</th></tr>'+
                            '<tr><td class="'+classVirtu+'"> VCPU : '+Math.floor(vmCpu)+'</td></tr>'+
                            '<tr><td class="'+classVirtu+'"> MEM : '+Math.floor(vmMem)+' Go </td></tr>'+
                            '<tr><td class="'+classVirtu+'"> Disk : '+vmDisk+' Go</td></tr>'+
                            '<tr><td class="'+classVirtu+'"> OS :'+vmOs+'</td></tr>'+
                        '</table>'+
                    '</td>'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th>'+
                                '<div  class ="bulle"><a href="#"> SAN 3PAR<span>'+
                                    'la date de génération des données est le '+getDataFileDisplay('400', 'date')+
                                '</span></a></div>'+
                            '</th></tr>'+
                            '<tr><td class="'+class3PAR+'">'+storageCount+'</td></tr>'+
                            '<tr><td class="'+class3PAR+'"> alloué :'+allocated+' Go</td></tr>'+
                            '<tr><td class="'+class3PAR+'"> utilisé :'+used+' Go</td></tr>'+
                            '<tr><td class="'+class3PAR+'"> </td></tr>'+
                        '</table>'+ 
                    '</td>'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th>'+
                                '<div  class ="bulle"><a href="#"> SAN HDS<span>'+
                                    'la date de génération des données est le '+getDataFileDisplay('HDS', 'date')+
                                '</span></a></div>'+
                            '</th></tr>'+
                            '<tr><td class="'+classHDS+'">'+storageHDSCount+'</td></tr>'+
                            '<tr><td class="'+classHDS+'">alloué :'+allocated_HDS+' Go</td></tr>'+
                            '<tr><td class="'+classHDS+'">utilisé : '+used_HDS+' Go</td></tr>'+
                            '<tr><td class="'+classHDS+'"> </td></tr>'+
                        '</table>'+
                    '</td>'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th>'+
                                '<div  class ="bulle"><a href="#">Sauvegarde VEEAM<span>'+
                                'la date de génération des données est le '+getDataFileDisplay('Veeam', 'date')+
                                '</span></a></div>'+
                            '</th></tr>'+
                            '<tr><td class="'+classVeeam+'"> status : '+VeeamScheduleStatus+'</td></tr>'+
                            '<tr><td class="'+classVeeam+'"> Fin : '+VeeamFin+'</td></tr>'+
                            '<tr><td class="'+classVeeam+'"> durée : '+VeeamDure+'</td></tr>'+
                            '<tr><td class="'+classVeeam+'"> </td></tr>'+
                            '<tr><td class="'+classVeeam+'"> </td></tr>'+
                        '</table>'+
                    '</td>'+
                    '<td width="10%">'+ 
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th>'+
                                '<div  class ="bulle"><a href="#"> Sauvegarde TSM<span>'+
                                'la date de génération des données est le '+getDataFileDisplay('TSM', 'date')+
                                '</span></a></div>'+
                            '</th></tr>'+
                            '<tr><td class="'+classTSM+'"> status : '+TSMStatus+'</td></tr>'+
                            '<tr><td class="'+classTSM+'"> début : '+TSMDebut+'</td></tr>'+
                            '<tr><td class="'+classTSM+'"> fin : '+TSMFin+'</td></tr>'+
                            '<tr><td class="'+classTSM+'"> </td></tr>'+
                        '</table>'+
                    '</td>'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th><div  class ="bulle"><a href="#">Supervision<span>le fichier source "fic" date du "date"</span></a></div></th></tr>'+
                            '<tr><td class="'+classSupervision+'"> attente Web Service O lachéré</td></tr>'+
                            '<tr><td class="'+classSupervision+'"> </td></tr>'+
                            '<tr><td class="'+classSupervision+'"> </td></tr>'+
                            '<tr><td class="'+classSupervision+'"> </td></tr>'+
                        '</table>'+
                    '</td>'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th><div  class ="bulle"><a href="#">Netscaler<span>le fichier source "fic" date du "date"</span></div></th></tr>'+
                            '<tr><td class="'+classNetscaler+'"> attente Netscaler</td></tr>'+
                            '<tr><td class="'+classNetscaler+'"> </td></tr>'+
                            '<tr><td class="'+classNetscaler+'"> </td></tr>'+
                            '<tr><td class="'+classNetscaler+'"> </td></tr>'+
                        '</table>'+
                    '</td>'+
                    '<td width="10%">'+
                        '<table cellspacing="0" border="1" >'+
                            '<tr><th>'+
                                '<div  class ="bulle"><a href="#">DISCOVERY<span>'+
                                'la date de génération des données est le '+getDataFileDisplay('Discovery', 'date')+
                                '<span></a></div>'+
                            '</th></tr>'+
                            '<tr><td class="'+classDiscovery+'">RAM : '+discoveryRAM+' Mo</td></tr>'+
                            '<tr><td class="'+classDiscovery+'">NbProc :'+dicoveryNbProc+' </td></tr>'+
                            '<tr><td class="'+classDiscovery+'">Proc Type :'+discoveryProcessor+' </td></tr>'+
                            '<tr><td class="'+classDiscovery+'">Proc Freq :'+discoveryFrequence+' Mhz </td></tr>'+
                        '</table>'+
                    '</td>'+
                '</tr>'+
            '</table>';
        }

