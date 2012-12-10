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
__date__ ="$15-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["cuatro.com"]

class Cuatro(Canal.Canal):
    '''
        Clase para manejar los vídeos de Cuatro (dominio propio).
    '''
    
    URL_STREAMS_START = "http://api.cuatro.webtv.flumotion.com/videos/"
    URL_STREAMS_END = "/streams"
    
    URL_CUATRO = "http://cuatro.com"
    URL_PLAY_CUATRO = "http://play.cuatro.com"
    
    URL_CUAVIDEO = "http://www.cuatro.com/cuavideo/info.xml?xref="
    #Nuevo CUAVIDEO:
    URL_SOURCES = "http://www.cuatro.com/mdsvideo/sources.json?contentId="
    
    URL_JSON = "http://www.cuatro.com/mdsvideo/sources.json?"
    
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
    #    - lanzar la excepción: raise Error.GeneralPyspainTVsError("mensaje")

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
        url_img = None
        streamHTML = Descargar.getHtml(self.url)
        if streamHTML.find("CUAVID") != -1:
            self.debug(u"CUAVID")
            ContentID = streamHTML.split("imageContentId: \'")[1].split("\'")[0]
            streamJSON = Descargar.getHtml(self.URL_SOURCES + ContentID)
            url2down = streamJSON.split("\"src\":\"")[1].split("\"")[0].replace("\/", "/")
            name = streamJSON.split("\"wrpContent\":\"")[1].split("\"")[0] + ".mp4"
        elif streamHTML.find("MDS.embedObj(video") != -1: # Este parece ser el único método a 16/10/2012 (pero dejo los demás..)
            self.debug(u"MDS.embedObj")
            contentID = streamHTML.split("MDS.embedObj(video, \"")[1].split("\"")[0]
            clippingID = streamHTML.split("imageClippingId: \'")[1].split("\'")[0]
            imageContentID = streamHTML.split("imageContentId: \'")[1].split("\'")[0]
            self.debug("URL Json: "+self.URL_JSON + "contentId=" + contentID + "&clippingId=" + clippingID + "&imageContentId=" + imageContentID)
            streamJSON = Descargar.getHtml( self.URL_JSON +
                                            "contentId=" + contentID +
                                             "&clippingId=" + clippingID +
                                             "&imageContentId=" + imageContentID
                                             )
            
            #streamJSON = dict(streamJSON)
            #url2down = streamJSON["sources"][0]["src"]
            url2down = streamJSON.split("({\"sources\":[{\"src\":\"")[1].split("\"")[0].replace("\/", "/")
            name = streamHTML.split("<title>")[1].split("<")[0]
            name += "." + url2down.split(".")[-1].split("?")[0]
            url_img = streamJSON.split("\"poster\":\"")[1].split("\"")[0].replace("\/", "/")
        elif streamHTML.find("src_iframe:") != -1:
            self.info(u"[INFO] Vídeo Común")
            name = streamHTML.split("<title>")[1].split("<")[0]
            urlComunes = self.URL_CUATRO + streamHTML.split("src_iframe:")[1].replace(" ", "").split("\'")[1].split("\'")[0]
            streamComunes = Descargar.getHtml(urlComunes)
            url2down = streamComunes.split("document.write(\'<video id=")[1].split("src=\"")[1].split("\"")[0]
            ext= "." + url2down.split(".")[-1]
            name += ext
        else:
            raise Error.GeneralPyspainTVsError("Cuatro.com: No se encuentra contenido")
        
        tit_vid = None
        if name:
            name = name.replace("Ver vídeo online","")
            tit_vid = name.split(".")[0]
            name = Utiles.formatearNombre(name)
    
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url2down],
                        "url_img"   : url_img if url_img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : "http",
                        "partes"    : 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit_vid] if tit_vid is not None else None,
                "descs": tit_vid if tit_vid is not None else None
                }




