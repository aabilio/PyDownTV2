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

# Archivo MAIN (principal) del proyecto PyDownTV para la muestra del módulo spaintvs:

__author__ = "aabilio"
__date__ = "$10-oct-2012 11:01:48$"
__version__ = "0.1.0-ALPHA"

import sys
import re
from optparse import OptionParser

from spaintvs import *
import uiDescargar

class Canales(object):
    '''
        Contiene los métodos para identificar a qué TV pertenece la url que
        introdujo el usuario.
    '''
    def __init__(self, url=None):
        '''Recibe la url'''
        self._url = url
    
    def isTVE(self):
        '''return True si la URL pertenece a Televisión Española'''
        if self._url.find("rtve.es") != -1: return True
 
    
def qCanal(url, opcs):
    '''
        Comprueba utlizando la clase Servidor de que servicio ha recibido la url
        y devuelve el objeto según el servicio que del cual se haya pasado la
        url
    '''
    # Descomentar return según se vañan añadiendo
    canal = Canales(url)
    if canal.isTVE(): # Tienes que comprobarse antes que isTVE
        Utiles.printt(u"[INFO] Radio Televión Española")
        return tve.TVE(url, opcs)
    else:
        return None
        
def argsparse():
    #TODO: Ver 15.5.2.6.1 en http://docs.python.org/library/optparse.html
    rVersion = Utiles.PdtVersion().PDT_VERSION_WIN if sys.platform == "win32" else Utiles.PdtVersion().PDT_VERSION_NIX
    parser = OptionParser(usage="%prog [-n --no-check-version] [-s --show] <\"url1\" \"url2\" ...>", 
                          version="PyDownTV "+rVersion)
    parser.add_option("-n", "--no-check-version", dest="check_version", action="store_true", 
                      help="No comprobar si existen actualizaciones")
    parser.add_option("-s", "--show", dest="show", action="store_true", 
                      help="Solo mostrar los enlaces de descarga (no descargar)")
    parser.add_option("-S", "--silent", dest="silent", action="store_false", 
                      help="Mostrar menos info por pantalla")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", 
                      help="Mostrar info de debug")
    return parser.parse_args()
        
def comprobar_version():
    '''
        Comprueba la versión del cliente con la última lanzada utilizando la clase
        PdtVersion() de utilies.py
    '''
    Utiles.printt(u"[INFO VERSIÓN] Comprobando si existen nuevas versiones de PyDownTV")
    pdtv = Utiles.PdtVersion()
    try:
        new_version, changelog = pdtv.get_new_version()
        if new_version == -1:
            Utiles.printt(u"[!!!] ERROR al comprobar la versión del cliente")
        else:
            pdtv.comp_version(new_version, changelog)
    except KeyboardInterrupt:
        Utiles.printt(u"[+] Comprobación cancelada")
    except Exception:
        Utiles.printt(u"[!!!] ERROR al comprobar la versión del cliente")

    
def isURL(url):
    '''
        Compara de forma muy básica si la cadena que se le pasa como parámetro es una URL válida
    '''
    p = re.compile(
    '^(https?)://([-a-z0-9\.]+)(?:(/[^\s]+)(?:\?((?:\w+=[-a-z0-9/%:,._]+)?(?:&\w+=[-a-zA-Z0-9/%:,._]+)*)?)?)?$', 
    re.IGNORECASE)
    m = p.match(url)
    return True if m else False



if __name__ == "__main__":
    (options, urls) = argsparse()
    
    if not urls: Utiles.printt(u"PyDownTV (Descarga vídeos de las webs de TV españolas):\n--------\n")
    if not options.check_version: comprobar_version()
    
    # Serializar las opciones que se mandaran al módulo de la TV:
    opcs =  {
            "log": options.silent if options.silent is not None else True,
            "debug": options.debug if options.debug is not None else False
            }
    ####
    
    if not urls:
        Utiles.printt(u"[--->] Introduce las URL de los vídeos (separadas por espacios):")
        inPut = raw_input()
        urls = inPut.split(" ")
    
    vUrls = [url for url in urls if isURL(url)]
    iUrls = [url for url in urls if not isURL(url)]
    
    if iUrls:
        Utiles.printt(u"[!!!] Las siguientes urls no son válidas:")
        for url in iUrls: Utiles.printt(u"-> %s" % url)
        Utiles.printt()
    
    if not vUrls:
        Utiles.salir(u"[!!!] Ninguna url válida")
    else:
        for url in vUrls:
            Utiles.printt(u"\n[ URL ] %s" % url)
            canal = qCanal(url, opcs)
            if not canal:
                Utiles.salir(u"ERROR: La URL \"%s\" no pertenece a ninguna Televisión soportada" % url)
                continue
            try:
                info = canal.getInfo()
                if options.debug:
                    Utiles.printt(u"[DEBUG] Info del vídeo obtenida:\n"+str(info))
            except Utiles.GeneralPyspainTVsError, e:
                Utiles.salir(unicode(e))
            #except Exception, e:
            #    Utiles.salir(unicode(e))
                
            if info["exito"]:
                if options.show:
                    if type(info["url_video"]) is list:
                        for i in info["url_video"]: Utiles.salir(u"[URL DESCARGA] %s" % i)
                    else: Utiles.salir(u"[URL DESCARGA] %s" % info["url_video"])
                else:
                    for i in range(info["partes"]): #TODO: Manejar aquí todo lo de las partes de PyDownTV1
                        D = uiDescargar.Descargar(info["url_video"][i],
                                            info["titulo"][i],
                                            info["tipo"],
                                            info["rtmpd_cmd"][i],
                                            info["menco_cmd"][i])
                        D.descargarVideo()
            else:
                Utiles.salir(u"[ERROR] No se ha encontrado el vídeo buscado")
            
    Utiles.windows_end()
