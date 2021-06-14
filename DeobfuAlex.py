############################################################
## PHP Deobfuscator Script v1.0
##                                      by <cwk2> 14.06.2021
##
## For php files that look like this:
##  <?php
##  use Tygh\Registry;use Tygh\ABAManager;
##  if ($_SERVER[call_user_func(call_user_func(call_user_func("\x62\x61\x73\x65\x36\x34\x5f\x64\x65\x63\x6f\x64\x65",
##  call_user_func("\x61\x62\x5f\x5f\x5f\x5f\x5f","\x62\x58\x32\x78\x63\x48\x3a\x6c\x5b\x52\x3e\x3e")),"",["\141\142\137\137","\x5f\137\137"
##
import re
import base64 
import os
from pathlib import Path
# "dado82_raw.php" , 
# "init.post.php" , 
# "sample2.php", 

Files = [
  "sample1.php", 
]


def LogLevel0( *text ):
  print(*text,  sep='\t')
  
def LogLevel1( *text ):
  print('', *text,  sep='\t')
  
def LogLevel2( *text ):
  print('','', *text,  sep='\t')
  
def LogVerbose( *text ):
  print('','', *text,  sep='\t')
  pass

def Unquote (string):
  try:
      
    match = re.match( r'"([^"]*)"' , string)
    retval = match.group(1)
    return (True, retval)
  except:
    return (False, string)

def PHP_addSlashes(text):
  return text.replace('"', '\\"')
  
def PHP_removeSlashes(text):
  return text.replace( '\\"', '"',)

  
def ab_____ (string):
  return PHP_addSlashes (
    "".join( 
      chr(ord(char) - 1)               
        for char in PHP_removeSlashes(string)) 
  )

def implode (Array, arg=""):
  
  # Turn ['"ab__"', '"___"'] ...
    arg1  = str.split( Array, ',' )
    
  # ... into ['ab__', '___'] ...
    arg1 = [Unquote(x)[1] for x in arg1 ]
    
  # ... and join it. 'ab_____'
    return arg.join(arg1)

def base64_decode ( arg ):
  try:
    retval = PHP_addSlashes ( base64.b64decode( arg ).decode('utf8') )
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
  
#############################
## OctHexNumStrToAccii
# 
#  Converts some kinda obfuscated string into a nicer one.
#  Example:
# '\\143\\x6f\\144\\145' =>  'code'
def OctHexNumStrToAccii (NumStr):    
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

def Deobfu_Strings( RetVal,  \
                    regex = r'"(?=\\[1x])([^"]+)"' ):
  # ^^-note: that (?=\\) positive lookahead for a '\' is needed to 
  #     avoid matches like "\n" or ",call_user_func(" or ","
    
  for matchNum, match in enumerate(re.finditer(regex, RetVal), start=1):
    
      searchThis = match.group(0)
      
      arg = match.group(1)
      replaced = f'"{OctHexNumStrToAccii(arg)}"'
      
      LogVerbose( f"#{matchNum}", arg, "=> ", replaced )
      
      RetVal = RetVal.replace( searchThis, replaced)

  return RetVal

def DoDeobfu_Static( RetVal,regex, DoQuoting=False, Namespace='\\Tygh\\' ):

  matches = re.finditer(regex, RetVal)
    
  for matchNum, match in enumerate(matches, start=1):
  
    LogLevel1( f"Match {matchNum}: {match.group()} @ {match.start()}" )
    
    searchThis = match.group(0)
    func       = match.group(1)
    arg        = match.group(2)
    
   
    if arg.find("call_user_func") != -1:
      # That is mostly cause by still unresolved call_user_func's with all strings args like:
      # call_user_func("\Tygh\Registry::get","settings_abam")
      # ... one other approach to avoid this would be to grep reverse so the good short match is found first. (instead the long one - like now) 
      raise  BaseException( f"Matched too much.\n>{searchThis}<\nContiune here anyway would just introduce errors in the deobfuscated sourcecode")
    
    #Cut off namespace
    func = func.replace(Namespace, '' )
    
    if DoQuoting:
      arg = '"' + arg + '"'
    replaced = f'{func}({arg})'
    
    LogLevel2 ( searchThis, "=> ", replaced )
    RetVal = RetVal.replace( searchThis,  replaced )
                    
  return  RetVal 



PHP_EXEC =  {
  "strrev"       : lambda arg:  PHP_addSlashes( PHP_removeSlashes(arg)[::-1])   , 
  "base64_decode": lambda arg:  base64_decode( arg )                            , 
  "ab_____"      : lambda arg:  ab_____( arg )                                  , 
  "implode"      : lambda arg:  implode( arg )
}
def DoDeobfu_Exec( RetVal, regex):
  
  LogLevel1 ("\n" + "-" * 80 + "\n")
  
  for matchNum, match in enumerate( re.finditer(regex, RetVal) , start=1):
    
    LogLevel1( f"Match {matchNum}: {match.group()} @ {match.start()}" )
    
    searchThis = match.group(0)
    func       = match.group(1)
    arg        = match.group(2)
    
    if arg.find("call_user_func") != -1:
      raise  BaseException( f"Matched too much.\n>{searchThis}<\nContinue here anyway would just introduce errors in the deobfuscated sourcecode")
    
    if func == "implode":
      arg = match.group(3)
      
    replaced = PHP_EXEC.get( func,  \
                             lambda arg : False \
                            )( arg )
    if   replaced:
      replaced = '"' + replaced + '"'
  
      LogLevel2 ( arg, "=> ", replaced )
      RetVal = RetVal.replace( searchThis,  replaced )
                    
  return  RetVal    

def ProcessFile(FileName, FileNameNew):
  phpFile = open(FileName, 'rt',  encoding='utf-8').read()
  LogLevel0 (f"'{FileName}' opened.")
  try:
      
    
    # removing heavy uranium Unicode isotops from the text
    phpFile = phpFile.replace('\u200b', '')
  
    LogLevel0 ("Level #1 transform all printable strings")
    phpFileNew = Deobfu_Strings( phpFile )
  
  
    LogLevel0 ("Level #2 Execute strrev(), base64_decode(), ab_____()")
    reExpArrArg = r'\[([^\]]*)\]'
  
    # That negative lookahead is there to avoid matching implode too early:
    # That second negative lookahead is there to support masking double quotes like "Quote: \"This is nice.\" " inside a double quoted strings 
     
    reExpStrArg = r'"(?!implode)([^(?!\\)"]*)"'
    reExpStrArg = r'"(?!implode)(.*?)"'
    reExpArg = r'([^\)]*)'
  
    for pass_ in  range(1, 10):
      LogLevel0 (f" PASS #{pass_}")
      phpFilelen_before = len(phpFileNew)
      
      phpFileNew = DoDeobfu_Exec( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpStrArg}\)')
      phpFileNew = DoDeobfu_Exec( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpStrArg}\)')
      phpFileNew = DoDeobfu_Exec( phpFileNew,  fr'call_user_func\("(implode)",{reExpStrArg},{reExpArrArg}\)')
      
      phpFilelen_now = len(phpFileNew)
      
      if phpFilelen_before == phpFilelen_now:
        break
  
    LogLevel0 ("Level #3 remove remaining call_user_func()")
    # Example >call_user_func("\Tygh\ABAManager::ch_a",true)<
    phpFilelen_before = len(phpFileNew)
    phpFileNew = DoDeobfu_Static( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpStrArg}\)',True,'\\Tygh\\' )
    phpFilelen_now = len(phpFileNew)
    
    phpFilelen_before = len(phpFileNew)
    phpFileNew = DoDeobfu_Static( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpStrArg}\)',True,'\\Tygh\\' )
    phpFilelen_now = len(phpFileNew)
    
    phpFileNew = DoDeobfu_Static( phpFileNew,  fr'call_user_func\({reExpStrArg},{reExpArg}\)'   ,False,'\\Tygh\\' )
    
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