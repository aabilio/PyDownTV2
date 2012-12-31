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

# Módulo para descargar todos los vídeos de la web Canal Historia "A la Carta"

__author__="aabilio"
__date__ ="$27-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["historia.adnstream.com"]

class Historia(Canal.Canal):
    '''
        Clase para manejar los vídeos de Canal Historia ("A la Carta")
    '''
    
    URL_HIST_CARTA = "http://historia.adnstream.com"
    URL_GET_XML = "http://historia.adnstream.com/get_playlist.php?lista=video&c=721&ux=0&param="
    URL_LINFOX_PROXY= "http://linfox.es/p/browse.php?b=0&f=norefer&u="
    URL_ANONIM_PROXY= "http://proxyanonimo.es/browse.php?b=12&f=norefer&u="
    
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
        
        html = self.gethtml()
        
        if html.find("'file'") == -1:
            urlXML = self.URL_GET_XML+Utiles.recortar(html, "var idvideo = '", "'")
        else:
            urlXML = self.URL_HIST_CARTA+Utiles.unescape(Utiles.recortar(html, "'file': '", "'"))        
        
        import logging
        logging.debug(self.URL_LINFOX_PROXY+Utiles.escape(urlXML))
        logging.debug(self.URL_ANONIM_PROXY+Utiles.escape(urlXML))
        xml = Descargar.get(urlXML)
        if xml.find("vohWwiQliW") != -1: # GEOLOCALIZADO
            logging.debug("GEO")
            xml = Descargar.get(self.URL_LINFOX_PROXY+Utiles.escape(urlXML))
            if xml.find("vohWwiQliW") != -1:
                logging.debug("GEO2")
                try:
                    xml = Descargar.get(self.URL_ANONIM_PROXY+Utiles.escape(urlXML))
                except Exception, e:
                    raise Error.GeneralPyspainTVsError(e.__str__())
        logging.debug(xml)
        
        try: tit = Utiles.recortar(xml, "<title>", "</title>")
        except: u"Vídeo de Canal Historia".encode('utf8')
        try: desc = Utiles.recortar(xml, "<description>", "</description>")
        except: desc = u"Vídeo de Canal Historia".encode('utf8')
        try: img = Utiles.recortar(xml, "<media:thumbnail url=\"", "\"")
        except: img = None
        try: url = xml.split("<media:content type=\"video")[1].split("url=\"")[1].split("\"")[0]
        except:
            try: url = Utiles.recortar(xml, "<jwplayer:file>", "</jwplayer:file>").strip()
            except: raise Error.GeneralPyspainTVsError(u"No se ha podido encontrar la URL del vídeo")
        try: name = Utiles.formatearNombre(tit+Utiles.ext(url))
        except: name = "VideoCanalHistoria"+Utiles.ext(url)
    
        if url.find("PPV1") != -1:
            mensaje = u'<span style="color: #ee6557;">EL VÍDEO PERTENECE A LA SECCIÓN PREMIUM, POR LO QUE NO SE PODRÁ DESCARGAR.</span>'.encode('utf8')
            url = "Contenido Premium"
        else: mensaje = None

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
                        "mensaje"   : mensaje
                        }],
                "titulos": [tit] if tit is not None else None,
                "descs": [desc] if desc is not None else None
                }




