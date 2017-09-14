	<html>
<header>
	<link rel="Stylesheet" type="text/javascript" src="https://code.jquery.com/jquery-1.12.3.js" target="_blank">
	<script type="text/javascript" src="https://code.jquery.com/jquery-1.12.3.js"></script> 
	<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/pdfmake-0.1.27/dt-1.10.15/b-1.4.0/b-html5-1.4.0/b-print-1.4.0/cr-1.3.3/fc-3.2.2/fh-3.1.2/kt-2.3.0/datatables.min.css"/>
 
<script type="text/javascript" src="https://cdn.datatables.net/v/dt/pdfmake-0.1.27/dt-1.10.15/b-1.4.0/b-html5-1.4.0/b-print-1.4.0/cr-1.3.3/fc-3.2.2/fh-3.1.2/kt-2.3.0/datatables.min.js"></script>
   <style>
      h1 { text-align: center; font-size: 30px; }
      #myTable thead th {  background-color: #6495ED; color : white ;}
      td.details-control {
        background: url(details_open.png) no-repeat center center;
        cursor: pointer;
      }
      tr.shown td.details-control {
        background: url(details_close.png) no-repeat center center;
      }             
   </style>

</header>
<body>
	<script>

		/*
			 Formatting function for row details - modify as you need 

			 https://datatables.net/examples/server_side/row_details.html
			 https://datatables.net/examples/server_side/scripts/ids-objects.php
		*/

		function format ( d ) {	
		  console.log("full info");
		  // `d` is the original data object for the row
		  return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
		      '<tr>'+
		          '<td>Sauvegarde:</td>'+
		          '<td>VEEAM</td>'+
		          '<td>derniere sauvegarde le '+d.name+'</td>'+
		          '<td>TSM</td>'+
		          '<td>'+'</td>'+
		      '</tr>'+
		      '<tr>'+
		          '<td>Supervision:</td>'+
		          '<td>'+d.extn+'</td>'+
		      '</tr>'+
		      '<tr>'+
		          '<td>Load Balancer:</td>'+
		          '<td>And any further details here (images etc)...</td>'+
		      '</tr>'+
		  '</table>';
		}

		$(document).ready(function() {  
		    var table = $('#myTable').DataTable( {  
        		lengthMenu: [[17, 25, 50, -1], [17, 25, 50, "All"]],
    			keys : true,
              	colReorder: true,
				dom: 'Bfrtip',
				"search": {
   					 "regex": true,
   					 "smart": false
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
					'excel', 'pdf'
				],
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
		        }  
		    } ); // fin table variable  
			table.buttons().container()
				.appendTo( $('.col-sm-6:eq(0)', table.table().container() ) );

			// Add event listener for opening and closing details
			$('#myTable tbody').on('click', 'td.details-control', function () {
				var tr = $(this).closest('tr');
				var row = table.row( tr );

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
			} );

		} );  
	</script>

<h1>CMDB : Liste des assets et des serveurs </h1>
<?php
	// Search RegularExpression PRC de prod : PRC[^P]*PRD
	//
	//	

	$Veeam = array();
   //
   // ReadBackupVeeam
   // 
	function readBackupVeeam($filename) {
		global $Veeam;
		$handle = fopen($filename, "r");
		if ($handle) {
			echo "<p>OK</p><pre>\n";
		    while (($line = fgets($handle)) !== false) {
		        // process the line read.
		        if (preg_match("#^<tr>#i", $line, $matches)) {
		        	// retire le <tr> et tous ce qu'il y a avant
		        	$line = eregi_replace('[^<]*<tr[^>]*>', '', $line);

		        	// retire les <td> et les option des td
	       	 		$line = eregi_replace('<td[^>]*>([^<]*)</td>', '\1|', $line);

	       	 		// retire le </tr> et tous ce qu'il y a après
		        	$line = eregi_replace('</tr>', '', $line);

		        	// construit la structure
		        	$a = explode('|', $line);

		        	// nom de serveur en minuscule
		        	$a[2] = strtolower($a[2]);

		        	$Veeam[$a[2]] = array("dossier" => $a[0], "dure" => $a[1], "debut" => $a[3], "fin" => $a[4],
		        							"volTransfert" => $a[5],
		        							"scheduleType" => $a[6], "backupType" => $a[7], "scheduleState" => $a[8]);
					
					//echo $line." <br>\n";
		        	//echo $a[2] ."='".$Veeam[$a[2]]["backupType"]."' <br>\n";

		        }
		    }

		    fclose($handle);
		} else {
		    // error opening the file.
		    echo "<p style='color:red'>KO</p>";
		} 
		return;
	} // fin fonction
	
	//
	// DataPath($type)
	//
	// renvoie le chemin d'accès au fichier en fonction du type
	function dataPath($type){
		$rootPathCtrlN1 = "/var/www/dashboardstock/capacity_TSM/check_niv1/";
		$rootPathStatBaies ="/home/i14sj00/cmdb/data";
		switch($type){
			case "VeeamProd" :
				return $rootPathCtrlN1."2017/septembre/Rapport Sauvegarde VEEAM/20170906-Rapport-sauvegarde-VEEAM_Production.html";
			break;

			case "VeeamRecette" :
				return $rootPathCtrlN1."2017/septembre/Rapport%20Sauvegarde%20VEEAM/20170908-Rapport-sauvegarde-VEEAM_Recette.html";
			break;

			case "TSM" :
				return $rootPathCtrlN1."http://vli5res01.si2m.tec/dashboardstock/capacity_TSM/check_niv1/2017/septembre/Rapport%20Sauvegarde%20TSM/20170908-TSM_Controle_Niv1.html";
			break;

			case "T400A" :
				return $rootPathStatBaies."Volume-host T400_A92.csv";
			break;

			case "T400B" :
				return $rootPathStatBaies."Volume-host T400_B94.csv";
			break;

			case "V400A" :
				return $rootPathStatBaies. "Volume-host V400_A92.csv";
			break;

			case "V400B" :
				return $rootPathStatBaies. "Volume-host V400_B94.csv";
			break;

			default:
				return "le chemin pour accéder a ".$type." est inconnue";
			break;
		}// FIN SWITCH
	}



	//
	// MAIN
	//
	$xml_data = '<?xml version="1.0" encoding="UTF-8"?>
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
	</soapenv:Envelope>';

	$header = array(
			'Content-Type: text/xml',
			'accept-encoding: '
	);

	$url = "https://malakoffmederic.easyvista.com:443/WebService/SmoBridge.php";

	$ch = curl_init($url);
	curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
	curl_setopt($ch, CURLOPT_POSTFIELDS, "$xml_data");
	

	curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
	curl_setopt($ch, CURLOPT_TIMEOUT,        10);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true );
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_POST,           true );
	
	$output = curl_exec($ch);
	

	if(  $output === false) {
	    $err = 'Curl error: ' . curl_error($ch);
	    curl_close($ch);
	    print $err;
	  } else {
	    curl_close($ch);
	  }

	$output = html_entity_decode($output);


 	$rows        = explode("\n", $output);
 	echo ' <table id="myTable" class="row-border cell-border hover display compact"  cellspacing="0" width="100%">'."\n";
 	foreach($rows as $row => $data){
 		if (stripos($data, '<Fieldname') !== false) {
 			$ligne = str_replace("<Fieldname ", "<tr>", 		$data);
	 		$ligne = str_replace("/>", "</th></tr>\n", 	$ligne);
	 		// insertion ligne detail
        	$ligne = str_replace("_0=", "<th class='details-control sorting_disabled' aria-label></th><th>",                        $ligne);
	 		//$ligne = str_replace("_0=", "<th>", 		$ligne);
	 		$ligne = str_replace("_1=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_2=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_3=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_4=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_5=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_6=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_7=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_8=", "</th><th>", 	$ligne);
	 		$ligne = str_replace("_9=", "</th><th>", 	$ligne);
	 		$ligne = str_replace('"', 	'', 			$ligne);

	 		$ligne = eregi_replace('(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}(<th>[^<>]*</th>){1}', '\6\2\3\4\5\1\7\8', $ligne);

	 		echo "<thead>".$ligne."</thead>\n";
	 		echo "<tfoot>".$ligne."</tfoot>\n<tbody>\n";
 		}
 		if (stripos($data, '<row') !== false) {
	 		$ligne = str_replace("<row ", "<tr>", 		$data);
	 		$ligne = str_replace("/>", "</td></tr>", 	$ligne);
	 		// insertion ligne detail
	 		$ligne = str_replace("_0=", "<td class='details-control'></td><td>",                        $ligne);
	 		$ligne = str_replace("_1=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_2=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_3=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_4=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_5=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_6=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_7=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_8=", "</td><td>", 	$ligne);
	 		$ligne = str_replace("_9=", "</td><td>", 	$ligne);
	 		$ligne = str_replace('"', 	'', 			$ligne);

	 		$ligne = eregi_replace('(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}(<td>[^<>]*</td>){1}', '\6\2\3\4\5\1\7\8', $ligne);

	 		echo $ligne;
	 	} // FIN strBRK
 	} // FIN FOREACH
 	echo "</tbody></table>";

 	//print_r($output);
 	readBackupVeeam(dataPath("VeeamProd"));
 	readBackupVeeam(dataPath("VeeamRecette"));

?>

</body>
</html>