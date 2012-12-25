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

# Módulo para descargar todos los vídeos de la web de Radiotelevisión Valenciana

__author__="aabilio"
__date__ ="$25-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["rtvv.es"]

class RTVV(Canal.Canal):
    '''
        Clase para manejar los vídeos de Radiotelevisión Valenciana
    '''
    
    URL_RTVV = "http://www.rtvv.es"
    
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


    def __getHtmlUrlFromAlacarta(self):
        '''
            Dada una URL de A la Carta de RTVV devuelve su URL normal
        '''
        ID = self.url.split("/")[-1]
        if ID.find("#") == -1 or self.url.endswith("rtvv.es/va/noualacarta/") or \
                                        self.url.endswith("rtvv.es/va/noualacarta"):
            raise Error.GeneralPyspainTVsError(u"Parace que has introducido una URL de 'A la Carta' general, y no específica de un vídeo")
        ID = ID.replace("#", "")
        self.info(u"[INFO] ID:", ID)
        # En versión web frameIDsplit = str(...) ;)
        frameIDsplit = "<li class=\"scr-item contentId_" + ID + "\">"
        self.info(u"[INFO] Separador:", frameIDsplit)
        html = Descargar.get(self.url)
        try:
            frameID = html.split(frameIDsplit.encode('utf8'))[1].split("</li>")[0]
        except Exception, e:
            raise Error.GeneralPyspainTVsError(e)
        
        htmlURL = self.URL_RTVV + frameID.split("<a href=\"")[1].split("\"")[0]
        try: cap = frameID.split("<p class=\"data cap\">")[1].split("</p>")[0]
        except: cap = None
        
        return [htmlURL, cap]
    
    def __rtvvRadio(self, htmlStream, sep):
        '''
            Dada una URL de la radio de RTVV devuelve la URL y el NOMBRE de descarga del audio
        '''
        self.info(u"[INFO] Modo Audios de Ràdio")
        url = self.URL_RTVV + htmlStream.split(sep)[1].split("\"")[0]
        ext = "." + url.split(".")[-1]
        name = htmlStream.split("class=\"title\"><strong>")[1].split("<")[0] + ext
        
        return [url, name]
    
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
        
        # Comprobar si es de radio primero:
        firstHtmlCheck = Descargar.get(self.url)
        separador = "this.element.jPlayer(\"setFile\", \""
        if firstHtmlCheck.find(separador) != -1 and firstHtmlCheck.find(".mp3") != -1:
            raise Error.GeneralPyspainTVsError(u"No soportamos la radio por ahora. Pronto estará disponible.")
            url, name = self.__rtvvRadio(firstHtmlCheck, separador)
            if name:
                name = Utiles.formatearNombre(name)
            return [url, name]
        # FIN Ràdio
        
        # Ahora Vídeos
        html = None
        if self.url.find("rtvv.es/va/noualacarta") != -1 or self.url.find("rtvv.es/es/noualacarta") != -1:
            self.info(u"[INFO] A la Carta")
            htmlURL, cap = self.__getHtmlUrlFromAlacarta()
            html = Descargar.get(htmlURL)
            xmlURL = self.URL_RTVV + html.split("file: \"")[1].split("\"")[0]
        else:
            self.info(u"[INFO] Vídeo Normal")
            xmlURL = self.URL_RTVV + Descargar.get(self.url).split("file: \"")[1].split("\"")[0]
        
            
        self.info(u"[INFO] URL de XML:", xmlURL)
        xmlStream = Descargar.get(xmlURL)
        url = xmlStream.split("<media:content url=\"")[1].split("\"")[0]
        ext = "." + url.split(".")[-1]
        # Acotar a <item></item> para coger el <title> del <item>
        item = xmlStream.split("<item>")[1].split("</item>")[0]
        name = item.split("<title><![CDATA[")[1].split("]")[0] + ext
        
        html = self.gethtml() if html is None else html
        try: img = Utiles.recortar(xmlStream, "<media:thumbnail url=\"", "\"")
        except: img = None
        try:
            if cap is not None:
                tit = html.split("<div class=\"title\">")[1].split("<h2>")[1].split("</h2>")[0] + " ( "+cap+" ) "
            else:
                tit = html.split("<div class=\"title\">")[1].split("<h2>")[1].split("</h2>")[0]
        except: tit = u"Vídeo de Radiotelevisión Valenciana".encode('utf8')
        try: name = Utiles.formatearNombre(tit+".mp4")
        except: name = "VideoRTVV.mp4"
        try: desc = Utiles.recortar(html, "<div class=\"tx\">", "</div>")
        except: desc = u"Vídeo de Radiotelevisión Valenciana".encode('utf8')
        
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url],
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : "http",
                        "partes"    : 1,
                        "rtmpd_cmd" : None,
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit] if tit is not None else None,
                "descs": [desc] if desc is not None else None
                }




