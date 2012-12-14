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

# Módulo para descargar todos los vídeos de la web de rtve.es ("A la carta" o no)
# Antes era el módulo de tvalacarta.py modificado para dar soporte a todos los vídeos

__author__="aabilio"
__date__ ="$10-oct-2012 11:35:37$"

#import sys
#import httplib
import urllib
import urllib2

import Canal
import Utiles
import Descargar
import Error

url_validas = ["rtve.es"]

class TVE(Canal.Canal):
    '''
        Clase para manejar los vídeos de la RTVE (todos).
    '''
    
    def __init__(self, url="", opcs=None):
        Canal.Canal.__init__(self, url, opcs, url_validas, __name__)
        
    # Métodos propios del canal, start the party!
    # Attributos disponibles:
    #    - self.url (url recibida)
    #    - self.opcs (diccionario de opciones) Ver Módulo Canal "_default_opcs" para opciones
    # Métodos disponibles de clase Canal:
    #    - log() para mostrar por pantalla (está disponible si self.opcs["log"] es True)
    #    - self.debug() mostrar información de debug (está disponible si self.opcs["debug"] es True)
    # Comunicación de errores con nivel de aplicación:
    #    - lanzar la excepción: raise Errors.GeneralPyspainTVsError("mensaje")

    def getInfo(self):
        '''
            Devuelve toda la información asociada a la URL recibida, de la siguiente forma:
            {
             "exito"     : bool,  <-- True (si se han obtenido videos)
             "num_video" : int,   <-- Número de vídeos obtenidos
             "mensaje"   : u"" ,  <-- Mensajes de la API (ej.: El vídeo no ha sido encontrado ["exito": False])
             "videos"    :  [{
                            "url_video" : [],   <-- Url de descarga de vídeo
                            "url_img"   : "",   <-- Url de la miniatura del video
                            "filename"  : [],   <-- Nombre de las partes para guardar en disco
                            "tipo"      : "",   <-- http, rtmp[e,..], mms, ...
                            "partes"    : int,  <-- Número de partes que tiene el vídeo
                            "rtmpd_cmd" : [],   <-- Comando rtmpdump (si tipo == rtmp) sino None
                            "menco_cmd" : [],   <-- Comando mencoder (Si tipo == rtmp) sino None
                            "url_publi" : "",   <-- Url del vídeo de publicidad asociado al vídeo
                            "otros"     : [],   <-- Lista donde se pueden pasar cosas opcionales
                            "mensaje"   : ""    <-- Mensajes de la API
                            }], <-- Debe ser una lista de tamaño "num_videos"
             "titulos"   : [u""], <-- Titulos de los videos
             "descs"     : [u""] <-- Descripción de cada vídeo
            }
            
            Los valores que no se rellenen, deberán devolver None.
            La clave "exito" es obligatoria, sino se puede encontrar el vídeo se puede devolver directamente:
            {
            "exito": False,
            "mensaje": "No se pudo descargar el video"  
            }
            
            "videos", "mesajes" y "descs" deben ser listas de cadenas (si no son None)
            "url_video", "filename", "rtmp_cmd", "menco_cmd" (de "videos") deben ser listas de cadenas (si no son None)
        '''
        #TODO: Cuida con las paginas que tiene más de un vídeo. De momento funciona porque es el primer video que aparece!
        
        # Primero: nos quedamos con le id dependiendo si el user metio la url con
        # una barra (/) final o no y si tiene extensión (no es alacarta)
        videoID = self.url.split('/')[-1]
        if videoID == "":
            videoID = self.url.split('/')[-2]
        elif videoID.find(".shtml") != -1 or videoID.find(".html") != -1 or \
            videoID.find(".html") != -1:
            videoID = videoID.split('.')[0]
        
        self.debug(u"ID del vídeo en url = " + videoID)
        
        # Añadido para vídeos nuevos (periodo de prueba):
        sourceHTML = Descargar.getHtml(self.url).decode('string-escape')
        #sourceHTML = self.toUtf(sourceHTML)
        videoID_comp = None
        if sourceHTML.find("flashcontentId:\'videoplayer") != -1:
            videoID_comp = sourceHTML.split("flashcontentId:\'videoplayer")[1].split("\'")[0]
            if videoID_comp != videoID: videoID = videoID_comp
        if sourceHTML.find("<div id=\"video") != -1:
            videoID_comp = sourceHTML.split("<div id=\"video")[1].split("\"")[0]
            if videoID_comp != videoID: videoID = videoID_comp
        ########################################################
        
        self.debug(u"ID del vídeo en HTML = " + videoID_comp if videoID_comp else "No ID en HTML")
        self.log(u"[INFO] ID del Vídeo :", videoID)

        # -- Método 1 Octubre 2012:
        self.debug(u"Probando método de 1 de uno de Octubre de 2012")
        url = "http://www.rtve.es/ztnr/consumer/xl/video/alta/" + videoID + "_es_292525252525111"
        self.debug(url)
        
        user_agent="Mozilla"
        opener = urllib2.build_opener(NoRedirectHandler())
        urllib2.install_opener(opener)
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, None, headers)
        u = urllib2.urlopen(req)
        try:
            urlVideo = u.info().getheaders("Location")[0]
        except:
            raise Error.GeneralPyspainTVsError("No se encuentra Location")
        u.close()
        if urlVideo != "":
            url_video = urlVideo.replace("www.rtve.es", "media5.rtve.es")
            titulo = sourceHTML.split("<title>")[1].split("</")[0].replace("RTVE.es", "").replace("-", "").strip()
            filename = titulo + ".mp4"
            filename = Utiles.formatearNombre(filename)
            #sourceHTML = sourceHTML.split("<div id=\"video")[1].split("flashvars")[0] # Me quedo solo con la parte del vídeo principal
            url_img = sourceHTML.split("\"thumbnail\" content=\"")[1].split("\"")[0]
        else:
            raise Error.GeneralPyspainTVsError("No se pudo encontrar el enlace de descarga")
        # -- Método 1 Octubre 2012 FIN
        
        desc = None
        try: #obtener descripción del video
            desc = Utiles.recortar(sourceHTML, "<meta itemprop=\"description\" content=\"", "\"").strip()
        except:
            try:
                desc = Utiles.recortar(sourceHTML, "<meta property=\"og:description\" content=\"", "\"").strip()
            except:
                try:
                    desc = Utiles.recortar(sourceHTML, "<meta name=\"description\" content=\"", "\"").strip()
                except:
                    desc = u"Vídeos de Televión Española"
                
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url_video],
                        "url_img"   : url_img,
                        "filename"  : [filename],
                        "tipo"      : "http",
                        "partes"    : 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [titulo],
                "descs": [desc] if desc is not None else None
                }

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
