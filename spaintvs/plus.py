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

# Módulo para descargar todos los vídeos de la web de Canal Plus

__author__="aabilio"
__date__ ="$01-ene-2013 11:35:37$"

import Canal
import Utiles
import Descargar
import Error

import httplib
from pyamf import remoting
import re
import xml.etree.ElementTree

url_validas = ["canalplus.es", "plus.es"]

class Plus(Canal.Canal):
    '''
        Clase para manejar los vídeos de Canal Plus
    '''
    
    URL_PLUS = "http://canalplus.es"
    URL_PLUSES = "http://plus.es"
    Publisher_ID = "1039301517001"
    Player_ID = "1133432061001"
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
                    target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaByReferenceId", 
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
                     "/services/messagebroker/amf?playerKey=AQ~~,AAAA8fsynsk~,vg4OBGkC6pkaS2UYScgZRP6xQ_i8Eu7R", 
                     str(remoting.encode(envelope).read()),
                     {'content-type': 'application/x-amf'}
                     )
        response = conn.getresponse().read()
        response = remoting.decode(response).bodies[0][1].body
        return response

    def __newPlus(self, html):
        self.debug(u"Nuevo método PLUS [Febrero 2014]")

        charset = re.findall('\<meta http\-equiv\=\"Content\-Type\" content\=\"text\/html\; charset\=(.*)\" \/\>',html)[0]
        html = html.decode(charset).encode("utf8")

        mp4s = re.findall('source.*src=\"(.*)\".*type=\"video\/mp4\"', html)
        try: # Título laterl en rosa
            title = re.findall('h2.*class=\"title\">(.*)<\/h2>',html.split("<video")[1])[0].replace("<strong>", "").replace("</strong>","")
        except: # Título de "Estás viendo"..
            title = re.findall('titulo=(.*?)\"',html)[0]
        try: # Descripción en lateral
            desc = re.findall('h2.*class=\"title\">.*<\/h2>.*<p>(.*)</p>.*</div>.*<!-- .video_entry -->',html.split("<video")[1],re.S)[0]
        except: # Descripción debajo del vídeo
            desc = re.findall('div.*class\=\"desc_play_video\".*\<p>(.*?)<\/p>.*<\/div>',html,re.S)[0]
        img = ("%s%s") % (self.URL_PLUS, re.findall('video.*poster=\"(.+?)\"',html)[0].replace("&amp;", "&"))
        try: name = Utiles.formatearNombre(title)+'.mp4'
        except: name = u"VideoCanalPlus.mp4".encode("utf8")

        # Otra manera (parece que no siepre disponible para algunos 'xref=' ...):
        #xref = re.findall('xref=(.*)',self.url)[0]
        #urlInfo = "http://canalplus.es/servicios/player/mm_se_top.html?xref=%s&view=playlist" % (xref)
        #info = Descargar.get(urlInfo)
        #doc = xml.etree.ElementTree.fromstring(info) ## Parsear XML

        return {"exito" : True,
                "num_videos" : 1,
                "mensaje"   : u"URL obtenido correctamente",
                "videos":[{
                        "url_video" : [mp4s[-1]], #De momento nos quedamos la última url, supuestamente la de mayor calidad
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
                "titulos": [title] if title is not None else None,
                "descs": [desc] if desc is not None else None
                }
    
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
        try: # Método antiguo
            VideoPlayer = html.split("name=\"@videoPlayer\"  value=\"ref:")[1].split("\"")[0] #REFERER!!
        except: # 03/01/2014
            return self.__newPlus(html)
        
        info = self.__get_info(VideoPlayer)
        
        big = 0
        for video in info['renditions']:
            if video['encodingRate'] >= big:
                big = video['encodingRate']
                url = video['defaultURL']
        ext = "." + url.split(".")[-1]
        
        
        # Parece que no pilla bien los datos a través de la api de brightcove,
        # utilizo entonces: /comunes/player/mm_nube_bc.php
        plusEs = False
        self.debug(u"URL Info: "+self.URL_PLUS + "/comunes/player/mm_nube_bc.php?xref=" + VideoPlayer)
        info = Descargar.get(self.URL_PLUS + "/comunes/player/mm_nube_bc.php?xref=" + VideoPlayer).decode('iso-8859-15').encode('utf8')
        
        try: img = self.URL_PLUS + info.split("<imagen>")[1].split("<![CDATA[")[1].split("]]>")[0].strip()
        except:
            img = None
            plusEs = True
        
        try: tit = info.split("<titulo>")[1].split("<![CDATA[")[1].split("]]>")[0].strip()
        except: tit = u"Vídeo de Canal Plus".encode('utf8')
        
        try: name = Utiles.formatearNombre(tit+ext)
        except: name = "VideoCanalPlus"+ext
        
        try: desc = info.split("<descripcion>")[1].split("<![CDATA[")[1].split("]]>")[0].strip()
        except: desc = u"Vídeo de Canal Plus".encode('utf8')
        
        # Probar título y descripción de la página si es vídeo de plus.es
        # La url del vídeo ya queda, aunque suele venir en el propio html de la página:
        # <video id="vid1" src="AQUÍ EL VÍDEO" [...]>
        html = html.decode('iso-8859-15').encode('utf8')
        ttit = tdesc = None
        if self.url.find("plus.es") != -1:
            if plusEs:
                try: ttit = html.split("<div class=\"news_type1\">")[1].split("<h3>")[1].split("</h3>")[0]
                except: ttit = None
            
                try: tdesc = html.split("<div class=\"news_type1\">")[1].split("<p>")[1].split("</p>")[0]
                except: tdesc = None
                
                try: img = self.URL_PLUSES+Utiles.recortar(html, "poster=\"", "\"")
                except: img = None
            
            if ttit is not None: tit = ttit
            if tdesc is not None: desc = tdesc
        #################################################################
        
#        try: img = info['videoStillURL']
#        except: img = None
#        
#        desc = None
#        try: desc1 = info['longDescription'].encode('utf8') if info['longDescription'] is not None else None
#        except: pass
#        try: desc2 = info['shortDescription'].encode('utf8') if info['shortDescription'] is not None else None
#        except: pass
#        try:
#            if desc1 is not None: desc = desc1
#            else:
#                if desc2 is not None: desc = desc2
#        except: desc = u"Vídeo de Canal Plus".encode('utf8')
#        else:
#            if desc is None or desc == u"": desc = u"Vídeo de Canal Plus".encode('utf8')
#            
#        try: tit = info['displayName'].encode('utf8')
#        except: tit = u"Vídeo de Canal Plus".encode('utf8')
#        else:
#            if tit == u"" or tit is None: tit = u"Vídeo de Canal Plus".encode('utf8')
#        
#        #FIXME: Ver qué pasa aquí!! --> name = Utiles.formatearNombre(tit + ext)
#        name = "VideoCanalPlus"+ext
#        
#        url = "/".join(img.split("/")[:3])+"/"+"/".join(url.split("/")[3:])
        
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




