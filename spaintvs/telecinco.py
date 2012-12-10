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

# Módulo para descargar todos los vídeos de la web de Telecinco.es

__author__="aabilio"
__date__ ="$16-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["telecinco.es"]

class Telecinco(Canal.Canal):
    '''
        Clase para manejar los vídeos de Telecinco (dominio propio).
    '''
    
    URL_DESCARGA_TELECINCO = "http://www.mitele.telecinco.es/deliverty/demo/resources/flv/"
    URL_ASK4TOKEN = "http://www.mitele.telecinco.es/services/tk.php?provider=level3&protohash=/CDN/videos/"
    string2split4id = ["xmlVideo: 'http://estaticos.telecinco.es/xml/Video/Video_", "\'"]
    URL_JSON = "http://www.telecinco.es/mdsvideo/sources.json?"
    
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
        
        if streamHTML.find("http://level3/") != -1: # Método antiguo
            self.info(u"[INFO] Método antiguo (mitele)")
            videoID = streamHTML.split("\'http://level3/")[1].split(".")[0]
            videoEXT = streamHTML.split("\'http://level3/")[1].split("\'")[0].split(".")[1]
            videoEXT = "." + videoEXT
            url2down = self.URL_DESCARGA_TELECINCO + videoID[-1] + "/" + videoID[-2] + "/" + videoID + videoEXT
            name = None
        elif streamHTML.find(self.string2split4id[0]) != -1: # Método nuevo
            newID = streamHTML.split(self.string2split4id[0])[1].split(self.string2split4id[1])[0].split(".")[0]
            self.info(u"[INFO] Nuevo Video ID:", newID)
            ask4token = self.URL_ASK4TOKEN + newID[-3:] + "/" + newID + ".mp4"
            self.debug(u"[+] Pidiendo nuevo token")
            url2down = Descargar.getHtml(ask4token)
            name = streamHTML.split("var title = \'")[1].split("\'")[0] + ".mp4"
        elif self.url.find("videoURL=") != -1: # Forma con el ID en la URL (nueva??)
            videoID = self.url.split("videoURL=")[1]
            ask4token = self.URL_ASK4TOKEN + videoID[-3:] + "/" + videoID + ".mp4"
            self.debug(u"[+] Pidiendo nuevo token")
            url2down = Descargar.getHtml(ask4token)
            # Obtner nombre:
            xmlURL = "http://estaticos.telecinco.es/xml/Video/Video_" + videoID + ".xml"
            streamXML = Descargar.getHtml(xmlURL)
            name = streamXML.split("<![CDATA[")[1].split("]")[0] + ".mp4"
        elif streamHTML.find("MDS.embedObj(video") != -1:
            contentID = streamHTML.split("MDS.embedObj(video, \"")[1].split("\"")[0]
            clippingID = streamHTML.split("imageClippingId: \'")[1].split("\'")[0]
            imageContentID = streamHTML.split("imageContentId: \'")[1].split("\'")[0]
            self.debug(u"URL JSON: " + self.URL_JSON + "contentId=" + contentID + "&clippingId=" + clippingID + "&imageContentId=" + imageContentID)
            streamJSON = Descargar.getHtml(self.URL_JSON +
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
        else:
            Error.GeneralPyspainTVsError("Telecinco.es. No se encuentra contenido.")
        

        tit_vid = None
        if name != None:
            name = name.replace("Ver vídeo online","")
            tit_vid = name.split(".")[0]
            name = Utiles.formatearNombre(name)
        
        desc = None        
        try:
            desc = Utiles.recortar(streamHTML, "<h3 class=\"subtitle\">", "<").strip()
        except:
            desc = tit_vid if tit_vid is not None else None
        
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
                "descs": [desc] if desc is not None else None
                }




