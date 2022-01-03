Set objHTML = CreateObject("htmlfile")
text = objHTML.ParentWindow.ClipboardData.GetData("text")

KoReportWork text

KoExit

'Set ie = CreateObject("InternetExplorer.Application")
'ie.Visible = 0
'ie.Navigate2 "C:\Users\David Candy\Desktop\Filter.html"
'Do
''  wscript.sleep 100
'Loop until ie.document.readystate = "complete"
'txt=ie.document.parentwindow.clipboardData.GetData("TEXT")
'ie.quit
'If IsNull(txt) = true then
'outp.writeline "No text on clipboard"
'else
'outp.writeline txt
'End If
