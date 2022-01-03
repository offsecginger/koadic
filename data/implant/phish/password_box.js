try {
  // cool stuff!
  // http://with-love-from-siberia.blogspot.com/2009/12/msgbox-inputbox-in-jscript.html

  // but it didn't work? :[

/*
  var vb = {};

  vb.Function = function(func)
  {
      return function()
      {
          return vb.Function.eval.call(this, func, arguments);
      };
  };


  vb.Function.eval = function(func)
  {
      var args = Array.prototype.slice.call(arguments[1]);
      for (var i = 0; i < args.length; i++) {
          if ( typeof args[i] != 'string' ) {
              continue;
          }
          args[i] = '"' + args[i].replace(/"/g, '" + Chr(34) + "') + '"';
      }

      var vbe;
      alert("yo")
      vbe = new ActiveXObject('ScriptControl');
      vbe.Language = 'VBScript';

      return vbe.eval(func + '(' + args.join(', ') + ')');
  };
*/

  /**
   * InputBox(prompt[, title][, default][, xpos][, ypos][, helpfile, context])
   */
  //var InputBox = vb.Function('InputBox');

  //  var a = InputBox("~MESSAGE~")

    var a = prompt("~MESSAGE~", "");
    Koadic.work.report(a);

} catch (e) {
    Koadic.work.error(e);
}

Koadic.exit();
