############################################################
## PHP Deobfuscator Script for AB Encoder v1.0
##                                      by <cwk2> 14.06.2021
## AB like alexbranding.com
## For php files that look like this:
##  <?php
##  use Tygh\Registry;use Tygh\ABAManager;
##  if ($_SERVER[call_user_func(call_user_func(call_user_func("\x62\x61\x73\x65\x36\x34\x5f\x64\x65\x63\x6f\x64\x65",
##  call_user_func("\x61\x62\x5f\x5f\x5f\x5f\x5f","\x62\x58\x32\x78\x63\x48\x3a\x6c\x5b\x52\x3e\x3e")),"",["\141\142\137\137","\x5f\137\137"
##
import re
import base64 
import os      # used for getting currentdir
import sys     # sys.stdout sys.stderr...
from pathlib import Path
# "dado82_raw.php" , 
# "init.post.php" , 
# "sample2.php", 

Files = [
  "sample1.php", 
]

Config_LogVerbose =  False

def _LogOutput( *text ):
  print(*text,  sep='\t', file=sys.stderr)
  
def LogLevel0( *text ):
  _LogOutput(*text)
  
def LogLevel1( *text ):
  _LogOutput('', *text)
  
def LogLevel2( *text ):
  _LogOutput('','', *text)
  
def LogVerbose( *text ):
  if Config_LogVerbose:
    _LogOutput('','', *text)


class StringDeObfuscator:
  """transforms all printable strings"""

  def __init__(_, PHP_Source):
    _.srcText = PHP_Source
    
        
  #############################
  ## OctHexNumStrToAccii
  # 
  #  Converts some kinda obfuscated string into a nicer one.
  #  Example:
  # '\\143\\x6f\\144\\145' =>  'code'
  def OctHexNumStrToAccii (_, NumStr):    
      NewStr = ""
      # split some string like '\143\x6f\144\145' at '\' (ignore first element)
      for matchNum, match in enumerate(NumStr.split('\\')[1:],  start=1):
        if match[0] == "x":   # Element is Hex..
          char = match[1:]
          char = int(char, 16)             
        else:                 # Element is Oct..
          char = int(match, 8)
          
      # build new string
        char = chr(char)
        # print (char, ord(char))
        NewStr += char
      
      return NewStr

  def do(_, regex = r'"(?=\\[1x])([^"]+)"' ):
    # ^^-note: that (?=\\) positive lookahead for a '\' is needed to 
    #     avoid matches like "\n" or ",call_user_func(" or ","
      
    for matchNum, match in enumerate(re.finditer(regex, _.srcText), start=1):
      
        searchThis = match.group(0)
        
        arg = match.group(1)
        replaced = f'"{_.OctHexNumStrToAccii(arg)}"'
        
        LogVerbose( f"#{matchNum}", arg, "=> ", replaced )
        
        _.srcText = _.srcText.replace( searchThis, replaced)
  
    return _.srcText


class call_user_func__StaticExecutor:
  """ Resolves all call_user_func() with known fixed values """

  def __init__(_, PHP_Source):
    """Constructor"""
    _.srcText = PHP_Source 
    
    
  def myReplace (_, SearchThat, ReplaceWith):
    Len_before = len(_.srcText)
  
    _.srcText = _.srcText.replace (SearchThat, ReplaceWith)
    
    Len_now = len(_.srcText)
    
    # if Len_before != Len_now:
    LogLevel1 (f"Shrinked {Len_before - Len_now} chars by {SearchThat} => {ReplaceWith}")
  
  def call_user_func__ab_____(_,  arg1, result):
    _.myReplace(f'call_user_func("ab_____","{arg1}")'    , f'"{result}"' )
  
  def call_user_func__strrev(_,  arg1, result):
    _.myReplace(f'call_user_func("strrev","{arg1}")'    , f'"{result}"' )
  
  def call_user_func__base64_decode(_,  arg1, result):
    _.myReplace(f'call_user_func("base64_decode","{arg1}")'    , f'"{result}"' )
  
  def call_user_func__implode(_,  arg1, arg2, result):
    _.myReplace(f'call_user_func("implode","",["{arg1}","{arg2}"])'    , f'"{result}"' )
  
  def do(_):
    _.call_user_func__strrev       ( "_____ba" ,     "ab_____" )
  
    _.call_user_func__ab_____      ( "bX2xcH:l[R>>", "aW1wbG9kZQ==" ) #1
    _.call_user_func__base64_decode( "aW1wbG9kZQ==", "implode"      )
    
    _.call_user_func__implode      ( "ab__","___",   "ab_____" )
    _.call_user_func__base64_decode( "dHVzc2Z3",     "tussfw"  ) #1
    _.call_user_func__ab_____      ( "tussfw",       "strrev"  )
    
    _.call_user_func__base64_decode( "NTdmdGJj",     "57ftbc"  ) #1
    _.call_user_func__ab_____      ( "57ftbc",       "46esab"  )
    _.call_user_func__strrev       ( "46esab",       "base64"  )
      
    _.call_user_func__base64_decode( "ZmVwZGZlYA==", "fepdfe`" ) #1
    _.call_user_func__ab_____      ( "fepdfe`",      "edoced_" )
    _.call_user_func__strrev       ( "edoced_",      "_decode" )
    
    _.call_user_func__base64_decode( "am5xbXBlZg==", "jnqmpef" ) #1
    _.call_user_func__ab_____      ( "jnqmpef",      "implode" )
    
    _.call_user_func__implode      ( "base64","_decode","base64_decode" )
    
    _.call_user_func__implode      ( "base64_de","code","base64_decode" )
    
    return _.srcText

 


class call_user_func__Executor:
  """ Resolves all call_user_func() dynamically """

  def __init__(_, PHP_Source):
    """Constructor"""
    _.srcText = PHP_Source
    
    
  def Unquote (_, string):
    try:
        
      match = re.match( r'"([^"]*)"' , string)
      retval = match.group(1)
      return (True, retval)
    except:
      return (False, string)
  
  def PHP_addSlashes(_, text):
    return text.replace('"', '\\"')
    
  def PHP_removeSlashes(_, text):
    return text.replace( '\\"', '"',)
  
  PHP_EXEC =  {
    "strrev"       : lambda _, arg:  _.PHP_addSlashes( PHP_removeSlashes(arg)[::-1])   , 
    "base64_decode": lambda _, arg:  _.base64_decode( arg )                            , 
    "ab_____"      : lambda _, arg:  _.ab_____( arg )                                  , 
    "implode"      : lambda _, arg:  _.implode( arg )
  }    
  def ab_____ (_, string):
    return _.PHP_addSlashes (
      "".join( 
        chr(ord(char) - 1)               
          for char in _.PHP_removeSlashes(string)) 
    )
  
  def implode (_, Array, arg=""):
    
    # Turn ['"ab__"', '"___"'] ...
      arg1  = str.split( Array, ',' )
      
    # ... into ['ab__', '___'] ...
      arg1 = [_.Unquote(x)[1] for x in arg1 ]
      
    # ... and join it. 'ab_____'
      return arg.join(arg1)

  def base64_decode (_,  arg ):
    try:
      retval = _.PHP_addSlashes (base64.b64decode( arg ).decode('utf8') )
    #  if retval.find('"') != -1:
    #    raise BaseException('The decode base64 contains some ". That\'s unexpected. Untreated like this it will cause problems in the further processing. TODO: Mask double quotes in decoded base64 strings.' )
      
      return retval
    except Exception as e:
      LogLevel2 ( f"ERROR base64_decode(): {e}" )
      LogLevel2 (  "Error resolution: Skipping statement.")
      # return False to keep that call_user_func("base64_decode",...
      # We'll deal / resolve it to base64_decode(...) in the following 3rd PASS
      return False
    
    # LogLevel2 (  "Error resolution: Keeping base64 statement.")
    #    return f'base64_decode("{arg}")'
  def do(_, regex):

    LogLevel1 ("\n" + "-" * 80 + "\n")  
    
    for matchNum, match in enumerate( re.finditer(regex, _.srcText) , start=1):
      
     # LogLevel1( f"Match {matchNum}: {match.group()} @ {match.start()}" )
      
      searchThis = match.group(0)
      func       = match.group(1)
      arg        = match.group(2)
      
      if arg.find("call_user_func") != -1:
        raise  BaseException( f"Matched too much.\n>{searchThis}<\nContinue here anyway would just introduce errors in the deobfuscated sourcecode")
      
      if func == "implode":
        arg = match.group(3)
        
      replaced = _.PHP_EXEC.get( func,  \
                               lambda arg : False \
                              )( _, arg )
      if   replaced:
        replaced = '"' + replaced + '"'
        _.srcText = _.srcText.replace( searchThis,  replaced )
        LogLevel2 ( arg, "=> ", replaced )
      else:
        LogLevel2 ( "SKIPPED")
    return  _.srcText   


def DoDeobfu_Static( RetVal, regex, DoQuoting=False, Namespace='\\Tygh\\' ):

  matches = re.finditer(regex, RetVal)
    
  for matchNum, match in enumerate(matches, start=1):
  
    # LogLevel1( f"Match {matchNum}: {match.group()} @ {match.start()}" )
    
    searchThis = match.group(0)
    func       = match.group(1)
    arg        = match.group(2)
    
    #Cut off namespace
    func = func.replace(Namespace, '' )
    
    if DoQuoting:
      arg = '"' + arg + '"'
    replaced = f'{func}({arg})'
    
    LogLevel2 ( searchThis, "=> ", replaced )
    
    
    if arg.find("call_user_func") != -1:
      # That is mostly cause by still unresolved call_user_func's with all strings args like:
      # call_user_func("\Tygh\Registry::get","settings_abam")
      # ... one other approach to avoid this would be to grep reverse so the good short match is found first. (instead the long one - like now) 
      raise  BaseException( f"Matched too much.\n>{searchThis}<\nContiune here anyway would just introduce errors in the deobfuscated sourcecode")
    RetVal = RetVal.replace( searchThis,  replaced )
                    
  return  RetVal 


def DoDeobfu_Static_Nest1( RetVal, regex, DoQuoting=False, Namespace='\\Tygh\\' ):

  matches = re.finditer(regex, RetVal)
    
  for matchNum, match in enumerate(matches, start=1):
  
    # LogLevel1( f"Match {matchNum}: {match.group()} @ {match.start()}" )
    
    searchThis = match.group(1)
    func       = match.group(2)
    arg        = match.group(3)
    
    #Cut off namespace
    func = func.replace(Namespace, '' )
    
    if DoQuoting:
      arg = '"' + arg + '"'
    replaced = f'{func}({arg})'
    
    LogLevel1 ( searchThis, "=> ", replaced )
    
    
    if arg.find("call_user_func") != -1:
      # That is mostly cause by still unresolved call_user_func's with all strings args like:
      # call_user_func("\Tygh\Registry::get","settings_abam")
      # ... one other approach to avoid this would be to grep reverse so the good short match is found first. (instead the long one - like now) 
      LogLevel2 ( f"SKIPPED - too much nested.")
    else:
      RetVal = RetVal.replace( searchThis,  replaced )
                    
  return  RetVal 




def ProcessFile(FileName, FileNameNew):
  phpFile = open(FileName, 'rt',  encoding='utf-8').read()
  LogLevel0 (f"'{FileName}' opened.")
  try:
      
    
    # removing heavy uranium Unicode isotops from the text
    phpFile = phpFile.replace('\u200b', '')
  
    LogLevel0 ("Level #0 transform all printable strings")
    phpFileNew = StringDeObfuscator( phpFile ).do()
  
    LogLevel0 ("Level #1 Execute all static strrev(), base64_decode(), ab_____()")
    phpFileNew =  call_user_func__StaticExecutor(phpFileNew).do()
    
    LogLevel0 ("Level #2 Execute strrev(), base64_decode(), ab_____()")
    reExpArrArg = r'\[([^\]]*)\]'
  
    # That negative lookahead is there to avoid matching implode too early:
    # That second negative lookahead is there to support masking double quotes like "Quote: \"This is nice.\" " inside a double quoted strings 
    
    # "([^"\\]*(?:\\.)?)*" Whoo what is that?
    # "([^"\\]*(?:\\.[^"\\]*)*)"
    # So goal is to match a string like this:
    # " It's big \"problem  "
    # So this "[^"\\]* will match " It's big 
    # that (?:\\.) will match/consume \"
    # (?:\\.)? will make it go on
    reExp_SlashNAnything = r'\\.'
    reExp_NoSlashNoQuote = r'[^"\\]'
    reExpStrArg = fr'"((?:{reExp_NoSlashNoQuote}*(?:{reExp_SlashNAnything}{reExp_NoSlashNoQuote}*)*))"'
    
    # "(?:[^"\\]+|\\.)*"
    reExpStrArg = fr'"((?:{reExp_NoSlashNoQuote}+|{reExp_SlashNAnything})*)"'
    reExpStrArg = fr'"([^"]*)"'
    # reExpStrArg ='(?!implode)' +  reExpStrArg
    # (?:[^"\\]*(?:\\.)?)*
    
    # That negative lookahead (?!\() is there to avoid to grab nested functions.
    # call_user_func("unserialize",call_user_func("base64_decode",Registry::get("settings_abam")))
    reExpArg = r'([^(?!\()\)]*)'
  
    # for pass_ in  range(1, 10):
      # LogLevel0 (f" PASS #{pass_}")
      # phpFilelen_before = len(phpFileNew)
      
    phpFileNew = call_user_func__Executor( phpFileNew).do( fr'call_user_func\({reExpStrArg},{reExpStrArg}\)')
    phpFileNew = call_user_func__Executor( phpFileNew).do( fr'call_user_func\({reExpStrArg},{reExpStrArg}\)')
      # # phpFileNew = DoDeobfu_Exec( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpStrArg}\)')
      # # phpFileNew = DoDeobfu_Exec( phpFileNew,  fr'call_user_func\("(implode)",{reExpStrArg},{reExpArrArg}\)')
      
      # phpFilelen_now = len(phpFileNew)
      
      # # if phpFilelen_before == phpFilelen_now:
      # break
  
    LogLevel0 ("Level #3 remove remaining call_user_func()")
    # Example >call_user_func("\Tygh\ABAManager::ch_a",true)<
    phpFileNew = DoDeobfu_Static( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpStrArg}\)',True,'\\Tygh\\' )    
    phpFileNew = DoDeobfu_Static( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpArg}\)'   ,False,'\\Tygh\\' )

    open( FileNameNew, 'w').write( phpFileNew )
    LogLevel0 (f"'{FileNameNew}' saved.  Currentdir: '{os.getcwd()}'")  
    LogLevel0 ("\n" + "=" * 80 + "\n")

    FileNameNew = Path(FileName).stem + "_UnSafe" + Path(FileName).suffix
    
    LogLevel0 ("Level #4 Remaining nested call_user_func()")
    phpFileNew = DoDeobfu_Static_Nest1( phpFileNew,  fr'(call_user_func\({reExpStrArg},([^\)]+)\))'   ,False,'\\Tygh\\' )
    phpFileNew = DoDeobfu_Static_Nest1( phpFileNew,  fr'(call_user_func\({reExpStrArg},([^\)]+)\))'   ,False,'\\Tygh\\' )
    phpFileNew = DoDeobfu_Static_Nest1( phpFileNew,  \
                               fr'call_user_func\([^,]+,(call_user_func\({reExpStrArg},([^\)]+)\))'   ,False,'\\Tygh\\' )



    
  except Exception as e:
    LogLevel0(f"Error:{e}")
    FileNameNew = Path(FileName).stem + "_withErrS" + Path(FileName).suffix
  finally:
    open( FileNameNew, 'w').write( phpFileNew )
    LogLevel0 (f"'{FileNameNew}' saved.  Currentdir: '{os.getcwd()}'")  
    LogLevel0 ("\n" + "=" * 80 + "\n")
  
##############################################################
##              main
##
for FileName in  Files:
  FileNameNew = Path(FileName).stem + "_decoded" + Path(FileName).suffix
  ProcessFile( FileName, FileNameNew )