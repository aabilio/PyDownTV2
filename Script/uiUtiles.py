#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of PyDownTV2.
#
#    PyDownTV2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyDownTV2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyDownTV2.  If not, see <http://www.gnu.org/licenses/>.

# Utiles para el script de pydowntv

import re
import sys
import uiDescargar

def isWin():
    return True if sys.platform == "win32" else False

def salir(*msg):
    '''
        Recibe una cadena y sustituye al exit() de python para:
        - primero: Parar la ejecución del programa en entornos win32
        - segundo: Mostrar una buena configuración de la codificación en Windows
    '''
    if sys.platform == "win32":
        for i in msg:
            print i.encode("cp850"), 
        print ""
        raw_input("[FIN] Presiona ENTER para SALIR")
        exit()
    else:
        for i in msg:
            print i, 
        print ""
        exit()
        
def printt(*msg):
    '''
        Recibe una cadena y la muestra por pantalla en el formato adecuado para sistemas
        win32 y *nix
        Funciona de manera análoga a print de python:
        - con sus concatenaciones de cadenas con '+' o ','
        - con la posibilidad de usar variables directamente o con el formato do especificadore 
          de formato --> printt(u"hola %s eres es usuario número %d" % (user, 925)) p.ejem..
        
        Las cadenas explícitas siempre tienen que tener la 'u' antes de las comillas:
        printt(u"Esto es un mensaje")
        
        printt() ya imprime un caracter de salto de línea final como print
    '''
    if sys.platform == "win32":
        for i in msg:
            print i.encode("cp850"), 
        print ""
    else:
        for i in msg:
            print i, 
        print ""

class PdtVersion(object):
    '''
        Clase que maneja el control de la versión del cliente con las correspondientes
        versiones oficialmente puestas para descargar en la web de proyecto
    '''
    
    # Recordar subir antes los archivos a Downloads aumentar la versión en VERSION
    PDT_VERSION_NIX = "6.0-BETA"
    PDT_VERSION_WIN = "6.0-BETA"
    URL_VERSION = "http://pydowntv.googlecode.com/svn/trunk/trunk/VERSION"
    
    def __init__(self):
        pass

    def get_new_version(self):
        '''
            Obtiene y devuelve la última versión oficial lanzada descargándola de URL_VERSION
            y su changelog
        '''
        new_version = uiDescargar.Descargar(self.URL_VERSION)
        
        # Comprobar que es un formao de versión válido:
        p = re.compile('^\"[0-9]\.[0-9\-].*\".*', re.IGNORECASE)
        m = p.match(new_version.descargar())
        if m:
            stream = new_version.descargar()
            stream_version_nix = stream.split("\"")[1]
            stream_version_win = stream.split("\"")[3]
            if sys.platform == "win32":
                changelog = stream.split("\"")[7]
            else:
                changelog = stream.split("\"")[5]
            
            ver2return = stream_version_win if sys.platform == "win32" else stream_version_nix
            
            return [ver2return, changelog]
        else:
            return [-1, -1]
        
    def comp_version(self, version, changelog):
        '''
            Compara las versiones y muestra un mensaje con el changelog en caso de que
            exista una versión nueva de el script
        '''
        ver2compare = self.PDT_VERSION_WIN if sys.platform == "win32" else self.PDT_VERSION_NIX
        if ver2compare < version:
            printt(u"[INFO VERSIÓN] Existe un nueva versión de PyDownTV:", version)
            printt(u"[INFO VERSIÓN] Cambios en la nueva versión:")
            printt(changelog)
            # TODO: Añadir URL de descarga aquí y quitar de changelog
            printt(u"")
        else:
            printt(u"[INFO VERSIÓN] Tu versión de PyDownTV es la más reciente")
            printt(u"")

def windows_end():
    '''
        Para el ciclo del programa a la espera de pulsación de ENTER en
        sistemas win32 al acabar las descargas
    '''
    if sys.platform == "win32":
        raw_input("[FIN] Presiona ENTER para SALIR")
        exit()

def formatearNombre(nombre):
    '''
        Se le pasa una cadena por parámetro y formatea esta quitándole caracteres
        que pueden colisionar a la hora de realizar el guardado en disco la descarga
        Por ejemplo:
                - Quita las barras "/"
                - Quita los espacios
                - Reduce las barras bajas
                - Elimina las comillas simples
                - Elimina tildes
                - Elimina comillas
                - ...
    '''
    # FIXME: Para los replace de la forma ("caracter", "") utilizar mejor strip("caracter")
    nombre = nombre.replace("&#039;", "\'")
    nombre = nombre.replace("?", "")
    nombre = nombre.replace("¿", "")
    nombre = nombre.replace("\xc2\xbf", "") # "¿" to ""
    nombre = nombre.replace("%C2", "")
    nombre = nombre.replace(": ",  ":")
    nombre = nombre.replace(". ", ".")
    nombre = nombre.replace('/',"-") # Quitar las barras "/"
    nombre = nombre.replace(" ", "_") # Quirar espacios
    nombre = nombre.replace("_-_", "-")
    nombre = nombre.replace("|", "")
    nombre = nombre.replace("&#146;", "-") # Cambiar el caracter escapado (') por (=)
    nombre = nombre.replace("\'", "")
    nombre = nombre.replace("\"", "")
    nombre = nombre.replace("%BF", "") # "?" to ""
    nombre = nombre.replace("\xbf", "") # "?" to ""
    nombre = nombre.replace("á", "a")
    nombre = nombre.replace("é", "e")
    nombre = nombre.replace("í", "i")
    nombre = nombre.replace("ó", "o")
    nombre = nombre.replace("ú", "u")
    nombre = nombre.replace("à", "a")
    nombre = nombre.replace("è", "e")
    nombre = nombre.replace("ì", "i")
    nombre = nombre.replace("ò", "o")
    nombre = nombre.replace("ù", "u")
    nombre = nombre.replace("Á", "a")
    nombre = nombre.replace("%C1", "a")
    nombre = nombre.replace("É", "e")
    nombre = nombre.replace("Í", "i")
    nombre = nombre.replace("Ó", "o")
    nombre = nombre.replace("Ú", "u")
    nombre = nombre.replace("À", "a")
    nombre = nombre.replace("È", "e")
    nombre = nombre.replace("Ì", "i")
    nombre = nombre.replace("Ò", "o")
    nombre = nombre.replace("Ù", "u")
    nombre = nombre.replace("&aacute;", "a")
    nombre = nombre.replace("&eacute;", "e")
    nombre = nombre.replace("&iacute;", "i")
    nombre = nombre.replace("&oacute;", "o")
    nombre = nombre.replace("&uacute;", "u")
    nombre = nombre.replace("%F3", "o") # "ó" to "o"
    nombre = nombre.replace("\xf3", "o") # "ó" to "o"
    nombre = nombre.replace("%E9", "e") # "é" to "o"
    nombre = nombre.replace("\xe9", "e") # "é" to "o"
    nombre = nombre.replace("´", "")
    nombre = nombre.replace("ñ", "nh")
    nombre = nombre.replace("%F1", "nh")
    nombre = nombre.replace("\xc3\xb1", "nh") # Cambiar el caracter escapado (ñ) por (nh)
    nombre = nombre.replace("&#8220;","") # (parece que: &#8220; = ")
    nombre = nombre.replace("&#8221;","") # Lo mismo que lo anterior
    nombre = nombre.replace("&#8217;", "")
    nombre = nombre.replace("(", "-")
    nombre = nombre.replace(")", "-")
    nombre = nombre.replace(":", "-")
    nombre = nombre.replace(",", "")
    #nombre = nombre.replace(";", "")
    nombre = nombre.replace("&quot;", "")
    nombre = nombre.replace("-SextaTv__laSexta", "")
    nombre = nombre.replace("!", "")
    nombre = nombre.replace("..",  ".")
    nombre = nombre.replace("\xc3\xa1", "a")
    nombre = nombre.replace("\xc3\xa9", "e")
    nombre = nombre.replace("\xc3\xad", "i")
    nombre = nombre.replace("\xc3\xb3", "o")
    nombre = nombre.replace("\xc3\xba", "u")
    
    nombre = nombre.replace("\xc3\x89", "E")

    return nombre

def stringFormat(s):
    s = s.replace("\xc3\xa1", "á")
    s = s.replace("\xc3\xa9", "é")
    s = s.replace("\xc3\xad", "í")
    s = s.replace("\xc3\xb3", "ó")
    s = s.replace("\xc3\xba", "ú")
    
    s = s.replace("\xc3\x89", "E")
    
    return s
