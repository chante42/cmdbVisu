<html>
<header>
	<link rel="Stylesheet" type="text/javascript" src="https://code.jquery.com/jquery-1.12.3.js" target="_blank">
	<script type="text/javascript" src="https://code.jquery.com/jquery-1.12.3.js"></script> 
	<script type="text/javascript" src="https://cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js"></script> 
	<link rel="stylesheet" href="https://cdn.datatables.net/1.10.12/css/jquery.dataTables.min.css"> 
	<style>
		h1 { text-align: center; font-size: 30px; }
		#myTable thead th {  background-color: #6495ED; color : white ;}

		
	</style>
</header>
<body>
	<script>
		$(document).ready(function() {  
		    $('#myTable').DataTable( {  
        		lengthMenu: [[17, 25, 50, -1], [17, 25, 50, "All"]],
    
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
		    } );  


		} );  
	</script>

<h1>CMDB : Liste des assets et des serveurs </h1>
<?php

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
	 		$ligne = str_replace("_0=", "<th>", 		$ligne);
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
	 		$ligne = str_replace("_0=", "<td>", 		$ligne);
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
?>

</body>
</html>