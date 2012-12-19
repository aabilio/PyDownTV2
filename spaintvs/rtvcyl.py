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

# Módulo para descargar todos los vídeos de la web de Radio Televisión de Castilla y León 

__author__="aabilio"
__date__ ="$19-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

url_validas = ["rtvcyl.es"]

class RTVCYL(Canal.Canal):
    '''
        Clase para manejar los vídeos de Radio Televisión de Castilla y León
    '''
    
    URL_RTMP = "rtmp://cdn.s8.eu.nice264.com:1935/niceVodServer/"
    
    URL_STREAMS_START = "http://api.promecal.webtv.flumotion.com/videos/"
    URL_STREAMS_END = "/streams"
    
    URL_CUATRO = "http://www.rtvcyl.es/"
    
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
        
        # CREO que ya no hay vídeos desde RTMP, como no encuentro no puedo comprobar
#        if html.find("&videoId=") != -1:
#            videoID = html.split("&videoId=")[1].split("\'")[0]
#            self.info(u"[INFO] Video ID:", videoID)
#            streamStreams = Descargar.get(self.URL_STREAMS_START + videoID + self.URL_STREAMS_END)
#            streamStreams = streamStreams.replace(" ", "").replace("\n", "")
#            videos = streamStreams.split("{")[1:]
#            self.info(u"[INFO] Se han detectado varios tipos de calidad:")
#            b = 0
#            for i in videos:
#                self.info(u"\t[%4d] %s" % (b, i.split("\"quality\":\"")[1].split("\"")[0]))
#                b += 1
#            # Presentar menú para elegir vídeo:
#            self.info(u"[-->] Introduce el número del tipo vídeo que quieres descargar (Ctrl+C para cancelar): ")
#            while True:
#                try:
#                    ID = int(raw_input())
#                except ValueError:
#                    self.info(u"[!!!] Parece que no has introducido un número. Prueba otra vez:")
#                    continue
#                    
#                if ID < 0 or ID > len(videos)-1:
#                    self.info(u"[!!!] No existe el vídeo con número [%4d] Prueba otra vez:" % ID)
#                    continue
#                else:
#                    break
#            
#            url = videos[ID].split("\"url\":\"")[1].split("\"")[0]
#            ext = "." + url.split("?")[0].split(".")[-1]
#            name = (html.split("<title>")[1].split("<")[0]).strip()
#            name += ext
        if html.find("NicePlayer.js?") != -1 or html.find("nicePlayer.js?") != -1:
            try:
                urlJS = html.split("NicePlayer.js?")[0].split("\"")[-1] + \
                "NicePlayer.js?" + html.split("NicePlayer.js?")[1].split("\"")[0]
            except IndexError:
                try:
                    urlJS = html.split("nicePlayer.js?")[0].split("\"")[-1] + \
                    "nicePlayer.js?" + html.split("nicePlayer.js?")[1].split("\"")[0]
                except:
                    raise Error.GeneralPyspainTVsError(u"No se encustra contenido")
            except:
                raise Error.GeneralPyspainTVsError(u"No se encustra contenido")
            streamJS = Descargar.get(urlJS)
            try: url = streamJS.split("var fileHtml5 = \"")[1].split("\"")[0]
            except:
                try: url = self.URL_RTMP + streamJS.split("var fileFlash = \"")[1].split("\"")[0]
                except: raise Error.GeneralPyspainTVsError(u"No se encuentra contenido")     
            name = html.split("<title>")[1].split("<")[0].strip()
            name += Utiles.formatearNombre("." + url.split(".")[-1])
            try: img = streamJS.split("var image = \"")[1].split("\"")[0]
            except: img = None
            try: tit = Utiles.recortar(html, "<title>", "</title>")#.encode('utf8')
            except: tit = u"Vídeo de Radio Televisión de Castilla y Leon".encode('utf8')
            try: desc = Utiles.recortar(html, "<meta name=\"Description\" content=\"", "\"").decode('string-escape').strip().encode('utf8')
            except: desc = u"Vídeo de Radio Televisión de Castilla y Leon".encode('utf8')
        elif html.find("<embed src=\"http://www.youtube.com") != -1:
            raise Error.GeneralPyspainTVsError(u"El vídeo de la página es de YouTube. Encontrarás muchas formas de descargarlo ;)")
        else:
            raise Error.GeneralPyspainTVsError(u"No se encuentra contenido")
            
        
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




