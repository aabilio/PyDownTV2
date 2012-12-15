#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of spaintvs.
#
#    spaintvs is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    spaintvs is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with spaintvs.  If not, see <http://www.gnu.org/licenses/>.

# Funciones para facilitar algunas labores al Módulo
# Incluye funciones también para el script, que al ser pocas, las dejo en este módulo por ahora

import sys

def isWin():
    ''' return True si se están en Windows '''
    return True if sys.platform == "win32" else False

def log(do=True, *msg):
    if do: printt(*msg)
        
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
        
class html(unicode):
    def recortar(self, str1, str2):
        return self.split(str1)[1].split(str2)[0]
    def qe(self):
        return self.replace(" ", "")
    
    
def recortar(orig, str1, str2):
    return orig.split(str1)[1].split(str2)[0]

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
    nombre = nombre.replace("\xf1o", "nh")
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
    nombre = nombre.replace("\xc2\xa1", "") #!
    nombre = nombre.replace("..",  ".")
    nombre = nombre.replace("\xc3\xa1", "a")
    nombre = nombre.replace("\xc3\xa9", "e")
    nombre = nombre.replace("\xc3\xad", "i")
    nombre = nombre.replace("\xc3\xb3", "o")
    nombre = nombre.replace("\xc3\xba", "u")
    
    nombre = nombre.replace("\xc3\x89", "E")

    return nombre

def descriptionFormat(Str):
    Str = stringFormat(Str)
    Str = Str.replace("<!--more-->", "")
    Str = Str.replace("/r", "")
    Str = Str.replace("//r", "")
    Str = Str.replace("/n", "")
    Str = Str.replace("//n", "")
    Str = Str.replace("\xf1", "nh") #ñ
    Str = Str.replace("ñ", "nh")
    
    Str = Str.replace("\xf3", "")
    Str = Str.replace("\xf3", "")
    Str = Str.replace("\xed", "")
    
    Str = Str.replace("á", "a")
    Str = Str.replace("é", "e")
    Str = Str.replace("í", "i")
    Str = Str.replace("ó", "o")
    Str = Str.replace("ú", "u")
    Str = Str.replace("Á", "a")
    Str = Str.replace("É", "e")
    Str = Str.replace("Í", "i")
    Str = Str.replace("Ó", "o")
    Str = Str.replace("Ú", "u")
    
    
    return Str

tituloFormat = descriptionFormat

def stringFormat(s):
    s = s.replace("\xc3\xa1", "á")
    s = s.replace("\xc3\xa9", "é")
    s = s.replace("\xc3\xad", "í")
    s = s.replace("\xc3\xb3", "ó")
    s = s.replace("\xc3\xba", "ú")
    
    s = s.replace("\xc3\x89", "E")
    
    return s

def qe(s):
    return s.replace(" ", "")
