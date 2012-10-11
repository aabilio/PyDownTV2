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

    def getInfo(self):
        '''
            Devuelve toda la información asociada a la URL recibida, de la siguiente forma:
            {
            "url_video" : [],   <-- Url de descarga de vídeo
            "url_img"   : "",   <-- Url de la miniatura del video
            "titulo"    : [],   <-- Título del vídeo
            "tipo"      : "",   <-- http, rtmp[e,..], mms, ...
            "partes"    : int,  <-- Número de partes que tiene el vídeo
            "rtmpd_cmd" : [],   <-- Comando rtmpdump (si tipo == rtmp) sino None
            "menco_cmd" : [],   <-- Comando mencoder (Si tipo == rtmp) sino None
            "url_publi" : "",   <-- Url del vídeo de publicidad asociado al vídeo
            "otros"     : [],   <-- Lista donde se pueden pasar cosas opcionales
            "exito"     : bool, <-- True (si por lo menos "url_video" está definida, sino False
            "mensaje"   : ""    <-- Mensajes de la API (ej.: El vídeo no ha sido encontrado ["exito": False])
            }
            Los valores que no se rellenen, deberán devolver None.
            La clave "exito" es obligatoria, sino se puede encontrar el vídeo se puede devolver directamente:
            {
            "exito": False
            "mensjae": "No se pudo descargar el video"  
            }
            
            "url_video", "titulo", "rtmp_cmd", "menco_cmd" deben ser listas de cadenas.
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
        
        self.debug(u"[DEBUG] ID del vídeo en url = " + videoID)
        
        # Añadido para vídeos nuevos (periodo de prueba):
        sourceHTML = Descargar.getHtml(self.url)
        videoID_comp = None
        if sourceHTML.find("flashcontentId:\'videoplayer") != -1:
            videoID_comp = sourceHTML.split("flashcontentId:\'videoplayer")[1].split("\'")[0]
            if videoID_comp != videoID: videoID = videoID_comp
        if sourceHTML.find("<div id=\"video") != -1:
            videoID_comp = sourceHTML.split("<div id=\"video")[1].split("\"")[0]
            if videoID_comp != videoID: videoID = videoID_comp
        ########################################################
        
        self.debug(u"[DEBUG] ID del vídeo en HTML = " + videoID_comp if videoID_comp else "[DEBUG] No ID en HTML")
        self.log(u"[INFO] ID del Vídeo :", videoID)

        # -- Método 1 Octubre 2012:
        self.debug(u"[DEBUG] Probando método de 1 de uno de Octubre de 2012")
        url = "http://www.rtve.es/ztnr/consumer/xl/video/alta/" + videoID + "_es_292525252525111"
        
        user_agent="Mozilla"
        opener = urllib2.build_opener(NoRedirectHandler())
        urllib2.install_opener(opener)
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, None, headers)
        u = urllib2.urlopen(req)
        try:
            urlVideo = u.info().getheaders("Location")[0]
        except:
            raise Utiles.GeneralPyspainTVsError("No se encuentra Location")
        u.close()
        if urlVideo != "":
            url_video = urlVideo.replace("www.rtve.es", "media5.rtve.es")
            titulo = sourceHTML.split("<title>")[1].split("</")[0] + ".mp4"
            titulo = Utiles.formatearNombre(titulo)
            #sourceHTML = sourceHTML.split("<div id=\"video")[1].split("flashvars")[0] # Me quedo solo con la parte del vídeo principal
            url_img = sourceHTML.split("\"thumbnail\" content=\"")[1].split("\"")[0]
        else:
            raise Utiles.GeneralPyspainTVsError("No se pudo encontrar el enlace de descarga")
        # -- Método 1 Octubre 2012 FIN
        
        return {
            "url_video" : [url_video],
            "url_img"   : url_img,
            "titulo"    : [titulo],
            "tipo"      : "http",
            "partes"    : 1,
            "rtmpd_cmd" : [None],
            "menco_cmd" : [None],
            "url_publi" : None,
            "otros"     : None,
            "exito"     : True,
            "mensaje"   : u"URL obtenida correctamente"
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
