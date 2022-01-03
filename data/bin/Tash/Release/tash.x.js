var manifestPath = "Tash.X.manifest";

var actCtx = new ActiveXObject( "Microsoft.Windows.ActCtx" );
actCtx.Manifest = manifestPath;

var tash =  actCtx.CreateObject("Tash.TashLoader");

var res = tash.Load("\x90\x90\xc3", "~~", 1);
WScript.Echo(res)

