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

# Módulo para descargar todos los vídeos de la web de Televisió de Catalunya

__author__="aabilio"
__date__ ="$21-oct-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

import re
import httplib
from pyamf import remoting

url_validas = ["tv3.cat", "3cat24.cat", "324.cat", "3xl.cat", "catradio.cat", "esport3.cat", "8tv.cat"]

class TV3(Canal.Canal):
    '''
        Clase para manejar los vídeos de Televisió de Catalunya
    '''
    
    URL_TV3 = "http://www.tv3.cat/"
    # INFO, encontrado en: http://www.tv3.cat/ria/players/3ac/evp/js/inserta_evp_v1.js
    URL_INFO_VIDEO  = "http://www.tv3.cat/pshared/video/FLV_bbd_dadesItem.jsp?idint="
    # URL VÍDEO, encontrado en http://www.tv3.cat/ria/players/3ac/evp/js/inserta_evp_v1.js
    URL_TOKEN_NUEVO = "http://www.tv3.cat/pshared/video/FLV_bbd_media.jsp?QUALITY=H&FORMAT=MP4&ID="
    URL_TOKEN_NUEVO2 = "http://www.tv3.cat/pshared/video/FLV_bbd_media.jsp?QUALITY=H&FORMAT=MP4GES&ID="
    # URL VÍDEO,sntiguo
    URL_TOKEN_START = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="
    URL_TOKEN_END   = "&QUALITY=H&FORMAT=MP4"
    URL_TOKEN_END2  = "&QUALITY=H&FORMAT=MP4GES"

    # Brightcove vars:
    Publisher_ID = "1589608506001"
    Player_ID = "1654948606001"
    Const = "9f8617ac59091bcfd501ae5188e4762ffddb9925"
    
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

    def __catradio(self):
        '''Procesa los audios de catradio'''
        # Primero nos quedamos con el ID
        audioID = self.url.split("/")[4]
        self.info(u"[INFO] Audio ID:", audioID)
        IDsplit = "insertNewItem(\'" + audioID + "\'"
        # Nos quedamos con su identificacion
        streamID = Descargar.get(self.url).split(IDsplit)[1].split(">")[0]
        name = streamID.split(",")[1] + ".mp3"
        url = "http://" + streamID.split("http://")[1].split("\'")[0]
        
        return [url, name]
    
    def __searchID(self, url):
        r=[n for n in url.split("/") if n.isdigit() and len(n)>5]
        return r[0] if len(r)==1 else None

    def __build_amf_request(self, videoPlayer):
        env = remoting.Envelope(amfVersion=3)
        env.bodies.append(
            (
                "/1", 
                remoting.Request(
                    target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", 
                    body=[self.Const, self.Player_ID, videoPlayer, self.Publisher_ID],
                    envelope=env
                )
            )
        )
        return env
    
    def __get_info(self, videoPlayer):
        conn = httplib.HTTPConnection("c.brightcove.com")
        envelope = self.__build_amf_request(videoPlayer)
        conn.request(
                     "POST", 
                     "/services/messagebroker/amf?playerKey=AQ~~,AAAAF8Q-iyk~,FDoJSqZe3TSVeJrw8hVEauWQtrf-1uI7", 
                     str(remoting.encode(envelope).read()),
                     {'content-type': 'application/x-amf'}
                     )
        response = conn.getresponse().read()
        response = remoting.decode(response).bodies[0][1].body
        return response

    def __tv8(self):
        html = Descargar.get(self.url)
        VideoPlayer = re.findall("<param.*name=\"@videoPlayer\".*value=\"(.*)\"", html)[0]
        info = self.__get_info(VideoPlayer)
        print info


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
        
        # En principio parece que tenemos 4 tipos de vídeos diferentes: A la carta video, a la carta auido, a 3cat24
        if self.url.find("catradio.cat") != -1:
            raise Error.GeneralPyspainTVsError(u"Los audios aún no están soportados. Lo estarán muy pronto ;)")
            #self.info(u"[INFO] Audios de catradio")
            #url, name = self.__catradio()
        if self.url.find("8tv.cat") != -1:
            return self.__tv8()

        ID = self.__searchID(self.url)
        if ID is None or self.url.find("324.cat") != -1 or self.url.find("3cat24.cat") != -1: #324cat
            html = Descargar.get(self.url)
            try:
                ID = html.split("flashvars.videoid =")[1].split(";")[0].strip()
            except:
                raise Error.GeneralPyspainTVsError(u"Error al recuperar el vídeo. ¿Es la URL correcta?")
        if ID is None:
            raise Error.GeneralPyspainTVsError(u"No se encuentra vídeo en la página")
        
        self.debug(u"ID: ", ID)
            
        
#        # 3cat24.cat:
#        if self.url.find("3cat24.cat/video/") != -1:
#            self.info(u"[INFO] Vídeos de 3cat24")
#            videoID = self.url.split("/")[-1]
#            url, name = self.__3cat24(nuevoID=videoID)
#        elif self.url.find("3cat24.cat/") != -1 or self.url.find("324.cat") != -1: # de 3cat24 pero no directamente el vídeo
#            self.info(u"[INFO] 3cat24 (otros vídeos)")
#            html = Descargar.get(self.url)
#            videoID = html.split("flashvars.videoid =")[1].split(";")[0].strip()
#            url, name = self.__3cat24(nuevoID=videoID)
#        elif self.url.find("tv3.cat/videos") != -1: # Gracis a Carlesm ;)
#            self.info(u"[INFO] Vídeos de TV3")
#            videoID = self.url.split("/")[-2]
#            if not videoID.isdigit(): videoID = self.url.split("/")[-1]
#            url, name = self.__3cat24(nuevoID=videoID)
#        elif self.url.find("tv3.cat/3alacarta") != -1: # Sirve la misma función de 3cat24 (con nuevoID)
#            self.info(u"[INFO] Vídeos de 3alacarta")
#            videoID = self.url.split("/")[-1]
#            if not videoID.isdigit(): videoID = self.url.split("/")[-2] #HTML5
#            url, name = self.__3cat24(nuevoID=videoID)
#        elif self.url.find("3xl.cat/videos") != -1:
#            self.info(u"[INFO] Vídeos de 3XL")
#            videoID = self.url.split("/")[-2]
#            url, name = self.__3cat24(nuevoID=videoID)
#        elif self.url.find("catradio.cat") != -1:
#            raise Error.GeneralPyspainTVsError(u"Los audios aún no están soportados. Lo estarán muy pronto ;)")
#            #self.info(u"[INFO] Audios de catradio")
#            #url, name = self.__catradio()
        
        #Buscar URL vídeo #FIXME: ERROR de Forbiden que da de vez en cuando
        headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:19.0) Gecko/20121211 Firefox/19.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encodign':'gzip, deflate'
        }
        
        tok = [
               self.URL_TOKEN_START + ID + self.URL_TOKEN_END,
               self.URL_TOKEN_START + ID + self.URL_TOKEN_END2,
               self.URL_TOKEN_NUEVO + ID,
               self.URL_TOKEN_NUEVO2 + ID
               ]
        
        xmlUrl = None
        for t in tok:
            try: xmlUrl = Descargar.get(t)
            except: continue
            if xmlUrl.find("<error>") != -1 or xmlUrl.find("<code>33</code>") != -1:
                xmlUrl = None
                continue
            else:
                break
        if xmlUrl is None:
            raise Error.GeneralPyspainTVsError(u"No se ha podido obtener los enlaces. Prueba dentro de 5 minutos.")
        
        self.debug(u"TOKEN Utilizdo: "+t)
        url = "rtmp://" + xmlUrl.split("rtmp://")[1].split("<")[0]
        urlReplace = "http://mp4-medium-dwn-es.media.tv3.cat/" if url.find("mp4-es") != -1 else "http://mp4-medium-dwn.media.tv3.cat/"
        url = url.replace(url.split("mp4:")[0]+"mp4:", urlReplace).replace(url.split(".mp4")[1],"")             
        
        #Buscar información con URL_INFO_VIDEO        
        info = Descargar.get(self.URL_INFO_VIDEO + ID, header=headers)
        try: img = Utiles.recortar(info, "<imgsrc>", "</imgsrc>").strip()
        except: img = None
        try: tit = Utiles.recortar(info, "<title>", "</title>").strip().decode('iso-8859-1').encode('utf8')
        except: tit = u"Vídeo de Televisió de Catalunya".encode('utf8')
        try: desc = Utiles.recortar(info, "<desc>", "</desc>").strip().decode('iso-8859-1').encode('utf8')
        except: desc = u"Vídeo de Televisió de Catalunya".encode('utf8')
        try: name = Utiles.formatearNombre(tit+".mp4")
        except: name = "VideoTV3.mp4"
        
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




