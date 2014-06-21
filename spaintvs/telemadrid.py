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

# Módulo para descargar todos los vídeos de la web de Telemadrid

__author__="aabilio"
__date__ ="$17-dic-2012 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

import httplib
from pyamf import remoting

url_validas = ["telemadrid.es"]

class Telemadrid(Canal.Canal):
    '''
        Clase para manejar los vídeos de Telemadrid
    '''
    
    URL_TELEMADRID = "http://telemadrid.es"
    Publisher_ID = "104403117001"
    Player_ID = "111787372001"
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
        # NO BORRAR, ver FIXME abajo --> name = html.split("<meta name=\"dc.title\" content=\"")[1].split("\"")[0]
        VideoPlayer = html.split("<param name=\"@videoPlayer\" value=\"")[1].split("\"")[0]
        info = self.__get_info(VideoPlayer)
        self.debug(u"info:",info)
        
        #TODO: Soltar todos los vídeos con las distintas calidades, ahora está solo la de mayor
        big = 0
        for video in info['renditions']:
            if video['encodingRate'] >= big:
                big = video['encodingRate']
                url = video['defaultURL']
        ext = "." + url.split(".")[-1]
        
        try: img = info['videoStillURL']
        except: img = None
        
        desc = None
        try: desc1 = info['longDescription'].encode('utf8') if info['longDescription'] is not None else None
        except: pass
        try: desc2 = info['shortDescription'].encode('utf8') if info['shortDescription'] is not None else None
        except: pass
        try:
            if desc1 is not None: desc = desc1
            else:
                if desc2 is not None: desc = desc2
        except: desc = u"Vídeo de Telemadrid".encode('utf8')
        else:
            if desc is None: desc = u"Vídeo de Telemadrid".encode('utf8')
            else:
                if type(desc) is unicode:
                    if desc == u"": desc = u"Vídeo de Telemadrid".encode('utf8')
                elif type(desc) is str:
                    if desc == "": desc = u"Vídeo de Telemadrid".encode('utf8')
        
        tit = None   
        try: tit = info['displayName'].encode('utf8')
        except: tit = u"Vídeo de Telemadrid".encode('utf8')
        else:
            if tit is None: tit = u"Vídeo de Telemadrid".encode('utf8')
            if type(tit) is unicode:
                if tit == u"": tit = u"Vídeo de Telemadrid".encode('utf8')
            elif type(tit) is str:
                if tit == "": tit = u"Vídeo de Telemadrid".encode('utf8')
        
        #FIXME: Ver qué pasa aquí!! --> name = Utiles.formatearNombre(tit + ext)
        try:
            name = Utiles.formatearNombre2(tit+ext)
        except:
            name = "VideoTelemadrid"+ext
        
        #url = "/".join(img.split("/")[:3])+"/"+"/".join(url.split("/")[3:])
        url += "?v=&fp=&r=&g="

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

