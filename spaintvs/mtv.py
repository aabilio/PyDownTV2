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

# Módulo para descargar todos los vídeos de la web de MTV

__author__="aabilio"
__date__ ="$17-dic-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["mtv.es", "mtv.com"]

class MTV(Canal.Canal):
    '''
        Clase para manejar los vídeos de MTV
    '''
    
    URL_MTV = "http://mtv.es"
    # Url de xml:
    XML_URL = "http://www.mtv.es/services/scenic/feeds/get/mrss/"
    XML_URL_COM = "http://www.mtv.com/player/embed/AS3/rss/?uri="
    PROXY_LINFOX = "http://linfox.es/p/browse.php?u="
    PROXY_AABILIO = "http://aabilio.hl161.dinaserver.com/p/browse.php?u="
    
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
        
        html = Descargar.get(self.url)
        html = html.replace("\n", "").replace("\t", "")
        try: #ES
            uri = html.split("var uri = \"")[1].split("\"")[0]
        except: #COM
            uri = html.split(".videoUri = \"")[1].split("\"")[0]
        
        #Spain or .com?
        xmlUrl = self.XML_URL + uri if self.url.find(".es") != -1 else self.XML_URL_COM + uri
        self.debug(u"URL XML Info: %s" % xmlUrl)
        xml = Descargar.get(xmlUrl)
        
        name = None
        tit = None
        desc = None
        try: #ES
            name = xml.split("<title>")[1].split("<![CDATA[")[1].split("]]>")[0]
        except: #COM
            xml = xml.decode('iso-8859-1').encode('utf8')
            if xml.find("<item>") != -1:
                name = xml.split("<item>")[1].split("<title>")[1].split("<")[0]
                tit = name
                try: desc = xml.split("<item>")[1].split("<description>")[1].split("<")[0].strip()
                except: desc = u"Vídeo de MTV".encode('utf8')
            else:
                name = xml.split("<title>")[1].split("<")[0]
                tit = name
                try: desc = xml.split("<description>")[1].split("<")[0].strip()
                except: desc = u"Vídeo de MTV".encode('utf8')
        name = name.replace("!", "").replace("|","") + ".mp4"
        name = Utiles.formatearNombre(name)
        
        
        import logging
        
        xmlURL = xml.split("<media:content")[1].split("url=\"")[1].split("\"")[0]
        self.debug(u"URL XML Archivos: %s" % xmlURL)
        xml2 = Descargar.get(xmlURL)
        #ulr = streamXML2.split("</rendition>")[-2].split("<src>")[1].split("</src>")[0]
        url = "rtmp" + xml2.split("<src>rtmp")[-1].split("</src>")[0]
        if url.find("copyright_error.") != -1: # GEO bloqueado!
            logging.debug("GEO Bloqueado")
            logging.debug(self.PROXY_AABILIO+xml.split("<media:content")[1].split("url=\"")[1].split("\"")[0])
            xmlURL = self.PROXY_AABILIO+xml.split("<media:content")[1].split("url=\"")[1].split("\"")[0]
            xml2 = Descargar.get(xmlURL)
            logging.debug(xml2)
            url = "rtmp" + xml2.split("<src>rtmp")[-1].split("</src>")[0]
        rtmpd_cmd = "rtmpdump -r \'"+url+"\' -o \'"+name+"\'"

        try: img = Utiles.recortar(xml, "<image url=\"", "\"")
        except: img = None
        try: tit = xml.split("<title>")[1].split("<![CDATA[")[1].split("]")[0].strip() if not tit else tit
        except: tit = u"Vídeo de MTV".encode('utf8')
        try: desc = xml.split("<description>")[1].split("<![CDATA[")[1].split("]")[0].strip() if not desc else desc
        except: desc = u"Vídeo de MTV".encode('utf8')
    
        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [url],
                        "url_img"   : img if img is not None else None,
                        "filename"  : [name] if name is not None else None,
                        "tipo"      : "rtmp",
                        "partes"    : 1,
                        "rtmpd_cmd" : [rtmpd_cmd],
                        "menco_cmd" : None,
                        "url_publi" : None,
                        "otros"     : None,
                        "mensaje"   : None
                        }],
                "titulos": [tit] if tit is not None else None,
                "descs": [desc] if desc is not None else None
                }

