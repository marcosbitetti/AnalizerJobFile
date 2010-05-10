import sys
import os
import re
import time
import urllib

#print urlopen('http://xahlee.org/Periodic_dosage_dir/_p2/russell-lecture.html').read()

#variavies
buffer = ""
bytes = 0
ignorar = []
fileTable = []
fileTableOld = []
update = False

#contantes
PATH_DE_ANALIZE = ""
ARQUIVO_LOG = "arquivos.log"
ARQUIVO_SUMARIO = "sumario.log"
URL_PUBLIC = ""
SEND_IP = ''
SEND_PASS = ''
FILE_SEPARATOR = ':: '

######
# Padrao do arquivo de log
# colunas:
#       1- Nome do arquivo
#       2- Path do diretorio
#       3- Tamanho em bytes
#       4- Data modificacao do arquivo
#       5- Data acesso ao arquivo
#       6- Data criacao do arquivo
######

def getConf():
   f = open("config","r")
   l = f.readlines()
   f.close()
   global PATH_DE_ANALIZE
   global URL_PUBLIC
   global SEND_PASS
   for e in l:
      g = e.split(" ")
      if g[0] == 'PATH_DE_ANALIZE':
         PATH_DE_ANALIZE = g[1].strip()
      if g[0] == 'URL_PUBLIC':
         URL_PUBLIC = g[1].strip()
      if g[0] == 'SEND_PASS':
         SEND_PASS = g[1].strip()

def readDir( path ):
    global buffer
    global bytes
    for f in os.listdir( path ):
        str = os.path.join(path, f)
        if not ignore(f):
            if os.path.isfile(str):
                buffer += "%s%s%s%s%s%s%s%s%s%s%s\n" % (f,FILE_SEPARATOR, path,FILE_SEPARATOR, os.path.getsize(str),FILE_SEPARATOR, os.path.getmtime(str),FILE_SEPARATOR, os.path.getatime(str),FILE_SEPARATOR, os.path.getctime(str))
                fileTable.append( [f, path, int(os.path.getsize(str)), float(os.path.getmtime(str)), float(os.path.getatime(str)), float(os.path.getctime(str))] )
                bytes += int(os.path.getsize(str))
            else:
                readDir( os.path.join(path,f) )
        else:
            print "ignorado: %s" % f

def getIgnoreList():
    global ignorar
    f = open('ignore','r')
    l = None
    for l in f.readlines():
    	s = l.strip()
    	if len(s)>0:
       	    ignorar.append( s )
    f.close()

def getFileTable():
    global ARQUIVO_LOG
    global fileTableOld
    global update
    f = open(ARQUIVO_LOG,'r')
    l = None
    for l in f.readlines():
        if (len(l)>0):
            c = l.split(FILE_SEPARATOR)
            fileTableOld.append( [c[0],c[1],int(c[2]),float(c[3]),float(c[4]),float(c[5])] )
    f.close()
    if len(fileTableOld) == 0:
    	update = True

def ignore(str):
    global ignorar
    for s in ignorar:
        if re.search( s, str) is not None:
            return True
    return False

###########
### Principal
###########

#config
getConf()

#faz copia do log anterior na memoria
getFileTable()
#lista de arquivos ignorados
getIgnoreList()
#mapea diretorio
readDir( PATH_DE_ANALIZE )

######
# Monta sumario
######
def localizaFile( str ):
    global fileTableOld
    for f in fileTableOld:
        if str == (f[0]+f[1]):
            return f
    return None

novos = len(fileTable)-len(fileTableOld)
apagados = 0
if novos<0:
    apagados = -novos
    novos = 0
    update = True
if novos>0:
    update = True
sumario = time.strftime("Hora do registro: %Y-%m-%d %H:%M:%S\n")
sumario += "Total de arquivos: %i\n" % len(fileTable)
sumario += "Total de arquivos da ultima amostragem: %i\n" % len(fileTableOld)
sumario += "Total de bytes: %i\n" % bytes
#levanta modificacoes
modList = 0
addList = 0
delList = 0
strModList = ""
strAddList = ""
strDelList = ""
for f1 in fileTable:
    f2 = localizaFile( f1[0]+f1[1] )
    #if file exists in old list
    if not f2 is None:
        m = int(f1[3] - f2[3])
        if m>0: #modificado
            modList += 1
            strModList += "%s%s%s\n" % (f1[0],FILE_SEPARATOR, f1[3])
            update = True
    #if file not exists in old list
    else: #acrescentado
        addList += 1
        strAddList += "%s%s%s\n" % (f1[0],FILE_SEPARATOR, f1[3])
        update = True

#apagados
for f1 in fileTableOld:
    str = f1[0]+f1[1]
    existe = False
    for f2 in fileTable:
        if str == (f2[0]+f2[1]):
            existe = True
            break
    if not existe:
        delList += 1
    	strDelList += "%s%s%s\n" % (f1[0],FILE_SEPARATOR, f1[3])
    	update = True


sumario += "Arquivos modificados: %i\n" % modList
sumario += "Lista de arquivos modificados:\n%s:::\n" % strModList
sumario += "Arquivos adicionados: %i\n" % addList
sumario += "Lista de arquivos adicionados:\n%s:::\n" % strAddList
sumario += "Arquivos apagados: %i\n" % delList
sumario += "Lista de arquivos apagados:\n%s:::\n" % strDelList

print sumario


if update:
	#envia dados para o servidor, caso contrario da erro e nao altera os arquivos
	dados = "%s?%s" % ( URL_PUBLIC, urllib.urlencode( {'data':sumario, 'pass':SEND_PASS} ) )
	res = urllib.urlopen( dados ).read()
	if res=='ok':
	    #salva sumario
	    fsumario = open(ARQUIVO_SUMARIO,"w")
	    fsumario.write( sumario )
	    fsumario.close()
	    #salva mapa de arquivos
	    f = open( ARQUIVO_LOG, "w" )
	    f.write( buffer )
	    f.close()
	else:
	    print res
