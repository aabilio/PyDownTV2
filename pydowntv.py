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

# Archivo MAIN (principal) del proyecto PyDownTV2 para la muestra del módulo spaintvs:

__author__ = "aabilio"
__date__ = "$10-oct-2012 11:01:48$"
__version__ = "0.1.0-ALPHA"

import sys
import re
from optparse import OptionParser

from spaintvs import *
import uiDescargar
import uiUtiles

# Opciones para añadir canales
_url_canales = {
               "rtve": ["rtve.es"],
               "grupo_a3": ["antena3.com", "lasexta.com", "lasextadeportes.com", "lasextanoticias.com"],
               "cuatro": ["cuatro.com"]
               }
_mod_tv = {
           "rtve": {"mod":tve.TVE,"comentario":"[INFO] Radio Televión Española", "urls":_url_canales["rtve"]},
           "grupo_a3": {"mod":grupo_a3.GrupoA3,"comentario":"[INFO] Grupo Antena 3 (- La Sexta)", "urls":_url_canales["grupo_a3"]},
           "cuatro": {"mod":cuatro.Cuatro,"comentario":"[INFO] Cuatro.com", "urls":_url_canales["cuatro"]}
           #"nombre" : {"mod":rutaAlaClase, "comentario":"infoParaImprimir", "urls":_url_canales["canal"]}
           }
# Fin de edición
 
def isUrlEnCanal(orig, urls=[]):
    for url in urls:
        if orig.find(url) != -1: return True
    return False  
def qCanal(url, opcs):
    '''
        Comprueba utlizando la clase Servidor de que servicio ha recibido la url
        y devuelve el objeto según el servicio que del cual se haya pasado la
        url
    '''
    mod_tv = _mod_tv
    for canal in mod_tv.values():
        if isUrlEnCanal(url, canal["urls"]):
            uiUtiles.printt(canal["comentario"])
            return canal["mod"](url, opcs)
    return None
        
def argsparse():
    #TODO: Ver 15.5.2.6.1 en http://docs.python.org/library/optparse.html
    rVersion = uiUtiles.PdtVersion().PDT_VERSION_WIN if sys.platform == "win32" else uiUtiles.PdtVersion().PDT_VERSION_NIX
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
    uiUtiles.printt(u"[INFO VERSIÓN] Comprobando si existen nuevas versiones de PyDownTV")
    pdtv = uiUtiles.PdtVersion()
    try:
        new_version, changelog = pdtv.get_new_version()
        if new_version == -1:
            uiUtiles.printt(u"[!!!] ERROR al comprobar la versión del cliente")
        else:
            pdtv.comp_version(new_version, changelog)
    except KeyboardInterrupt:
        uiUtiles.printt(u"[+] Comprobación cancelada")
    except Exception:
        uiUtiles.printt(u"[!!!] ERROR al comprobar la versión del cliente")

    
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
    
    if not urls: uiUtiles.printt(u"PyDownTV (Descarga vídeos de las webs de TV españolas):\n--------\n")
    if not options.check_version: comprobar_version()
    
    # Serializar las opciones que se mandaran al módulo de la TV:
    opcs =  {
            "log": options.silent if options.silent is not None else True,
            "debug": options.debug if options.debug is not None else False
            }
    ####
    
    if not urls:
        uiUtiles.printt(u"[--->] Introduce las URL de los vídeos (separadas por espacios):")
        inPut = raw_input()
        urls = inPut.split(" ")
    
    vUrls = [url for url in urls if isURL(url)]
    iUrls = [url for url in urls if not isURL(url)]
    
    if iUrls:
        uiUtiles.printt(u"[!!!] Las siguientes urls no son válidas:")
        for url in iUrls: uiUtiles.printt(u"-> %s" % url)
        uiUtiles.printt()
    
    if not vUrls:
        uiUtiles.salir(u"[!!!] Ninguna url válida")
    else:
        for url in vUrls:
            uiUtiles.printt(u"\n[ URL ] %s" % url)
            canal = qCanal(url, opcs)
            if not canal:
                uiUtiles.printt(u"ERROR: La URL \"%s\" no pertenece a ninguna Televisión soportada" % url)
                continue
            try:
                info = canal.getInfo()
                if options.debug:
                    from pprint import pprint
                    uiUtiles.printt(u"[DEBUG] Info del vídeo obtenida:\n")
                    pprint(info)
            except Error.GeneralPyspainTVsError, e:
                uiUtiles.salir(unicode(e))
            #except Exception, e:
            #    Utiles.salir(unicode(e))
             
            if info["exito"]: ## TODO OK
                if options.show: # Solo mostrar enlaces
                    for video in info["videos"]: # No importa si solo es un vídeo o varios, muestra todo
                        if info["titulos"]:
                            uiUtiles.printt("\n"+info["titulos"][info["videos"].index(video)] +":\n"+"-"*len(info["titulos"][info["videos"].index(video)]))
                        for parte in video["url_video"]: uiUtiles.printt(u"\t[URL DESCARGA] %s" % parte)
                else: # Descargar el vídeo
                    if info["num_videos"] == 1:
                        for video in info["videos"]: # for, aunque solo debería de haber un vídeo
                            for indice_parte in range(video["partes"]): #TODO: Cómo descargar, todas las partes o preguntar
                                d = uiDescargar.Descargar(
                                                          video["url_video"][indice_parte],
                                                          video["titulo"][indice_parte],
                                                          video["tipo"],
                                                          video["rtmpd_cmd"][indice_parte] if video["rtmpd_cmd"] is not None else None,
                                                          video["menco_cmd"][indice_parte] if video["menco_cmd"] is not None else None,
                                                          )
                                d.descargarVideo()
                    else:
                        pass # TODO: Decidir qué hacer con los vídeo aquí (descargar, preguntar cuál,...) y luego las partes de cada uno
            else: ## NO éxito
                uiUtiles.salir(u"[ERROR] No se ha encontrado el vídeo buscado")

    uiUtiles.windows_end()
