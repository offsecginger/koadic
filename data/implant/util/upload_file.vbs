path = KoGetPath("~DIRECTORY~\~FILE~")

dim headers(1)
headers(0) = "X-UploadFileJob"
headers(1) = "true"

set http = KoReportWorkEx("", headers)

' Default IE policy does not allow this in MSHTA sessions
'dim bStrm: Set bStrm = createobject("Adodb.Stream")

'with bStrm
''    .type = 1 '//binary
''    .open
''    .write http.responseBody
''    .savetofile path, 2 '//overwrite
'end with

' we have to solve Shlemiel the Painter problem
' so we carry the bucket with us for every pagesize
dim j, roadlen, pagesize, pagecount, fd, timeouthandle
j = 1
roadlen = LenB(http.responseBody)
pagesize = 2000
pagecount = roadlen \ pagesize

set fd = kofs.OpenTextFile(path, 2, True, 0)

sub CopyBytesWithTimeOut
  on error resume next
  'for j = 1 to pagecount
  'if roadlen <= FinishUp
  if j = pagecount + 1 then
      FinishUp
  else
      data = ""
      roadsection = MidB(http.responseBody, (j-1)*pagesize+1, pagesize)
      for i = 1 to LenB(roadsection)
          data = data & Chr( AscB( MidB( roadsection, i, 1 ) ) )
      next
      fd.write data
      j = j + 1
      if isobject(window) then
          timeouthandle = window.setTimeout(GetRef("CopyBytesWithTimeOut"), 0)', "VBScript")
      else
          CopyBytesWithTimeOut
      end if
  end if
  'next
end sub

sub FinishUp
    on error resume next
    data = ""

    startIndex = pagecount * pagesize
    if startIndex = 0 then
      startIndex = 1
    end if

    ' write the remaining page
    remainder = MidB(http.responseBody, startIndex, roadlen - pagecount*pagesize)
    for i = 1 to LenB(remainder)
        data = data & Chr( AscB( MidB( remainder, i, 1 ) ) )
    next

    fd.write data
    fd.close()

    KoReportWork ""
    KoExit

end sub

CopyBytesWithTimeOut
